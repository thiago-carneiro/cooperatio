#include <assert.h>
#include <errno.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <sys/stat.h>

#include "exec_stack.h"
#include "bytecode.h"

#include "value_alloc.h"
#include "locfile.h"
#include "value.h"
#include "engine.h"
#include "builtin.h"
#include "linker.h"

struct qe_state {
  void (*nomem_handler)(void *);
  void *nomem_handler_data;
  struct bytecode* bc;

  qe_msg_cb err_cb;
  void *err_cb_data;
  val_t error;

  struct stack stk;
  stack_ptr curr_frame;
  stack_ptr stk_top;
  stack_ptr fork_top;

  val_t path;
  val_t value_at_path;
  int subexp_nest;
  int debug_trace_enabled;
  int initial_execution;
  unsigned next_label;

  int halted;
  val_t exit_code;
  val_t error_message;

  val_t attrs;
  qe_input_cb input_cb;
  void *input_cb_data;
  qe_msg_cb debug_cb;
  void *debug_cb_data;
  qe_msg_cb stderr_cb;
  void *stderr_cb_data;
};

struct closure {
  struct bytecode* bc;  // qe bytecode
  stack_ptr env;        // qe stack address of closed frame
};

// locals for any function called: either a closure or a local variable
union frame_entry {
  struct closure closure;
  val_t localvar;
};

// qe function call frame
struct frame {
  struct bytecode* bc;      // qe bytecode for callee
  stack_ptr env;            // qe stack address of frame to return to
  stack_ptr retdata;        // qe stack address to unwind to on RET
  uint16_t* retaddr;        // qe bytecode return address
  union frame_entry entries[]; // nclosures + nlocals
};

static int frame_size(struct bytecode* bc) {
  return sizeof(struct frame) + sizeof(union frame_entry) * (bc->nclosures + bc->nlocals);
}

static struct frame* frame_current(struct qe_state* qe) {
  struct frame* fp = stack_block(&qe->stk, qe->curr_frame);

  stack_ptr next = *stack_block_next(&qe->stk, qe->curr_frame);
  if (next) {
    struct frame* fpnext = stack_block(&qe->stk, next);
    struct bytecode* bc = fpnext->bc;
    assert(fp->retaddr >= bc->code && fp->retaddr < bc->code + bc->codelen);
  } else {
    assert(fp->retaddr == 0);
  }
  return fp;
}

static stack_ptr frame_get_level(struct qe_state* qe, int level) {
  stack_ptr fr = qe->curr_frame;
  for (int i=0; i<level; i++) {
    struct frame* fp = stack_block(&qe->stk, fr);
    fr = fp->env;
  }
  return fr;
}

static val_t* frame_local_var(struct qe_state* qe, int var, int level) {
  struct frame* fr = stack_block(&qe->stk, frame_get_level(qe, level));
  assert(var >= 0);
  assert(var < fr->bc->nlocals);
  return &fr->entries[fr->bc->nclosures + var].localvar;
}

static struct closure make_closure(struct qe_state* qe, uint16_t* pc) {
  uint16_t level = *pc++;
  uint16_t idx = *pc++;
  stack_ptr fridx = frame_get_level(qe, level);
  struct frame* fr = stack_block(&qe->stk, fridx);
  if (idx & ARG_NEWCLOSURE) {
    // A new closure closing the frame identified by level, and with
    // the bytecode body of the idx'th subfunction of that frame
    int subfn_idx = idx & ~ARG_NEWCLOSURE;
    assert(subfn_idx < fr->bc->nsubfunctions);
    struct closure cl = {fr->bc->subfunctions[subfn_idx],
                         fridx};
    return cl;
  } else {
    // A reference to a closure from the frame identified by level; copy
    // it as-is
    int closure = idx;
    assert(closure >= 0);
    assert(closure < fr->bc->nclosures);
    return fr->entries[closure].closure;
  }
}

static struct frame* frame_push(struct qe_state* qe, struct closure callee,
                                uint16_t* argdef, int nargs) {
  stack_ptr new_frame_idx = stack_push_block(&qe->stk, qe->curr_frame, frame_size(callee.bc));
  struct frame* new_frame = stack_block(&qe->stk, new_frame_idx);
  new_frame->bc = callee.bc;
  new_frame->env = callee.env;
  assert(nargs == new_frame->bc->nclosures);
  union frame_entry* entries = new_frame->entries;
  for (int i=0; i<nargs; i++) {
    entries->closure = make_closure(qe, argdef + i * 2);
    entries++;
  }
  for (int i=0; i<callee.bc->nlocals; i++) {
    entries->localvar = val_invalid();
    entries++;
  }
  qe->curr_frame = new_frame_idx;
  return new_frame;
}

static void frame_pop(struct qe_state* qe) {
  assert(qe->curr_frame);
  struct frame* fp = frame_current(qe);
  if (stack_pop_will_free(&qe->stk, qe->curr_frame)) {
    int nlocals = fp->bc->nlocals;
    for (int i=0; i<nlocals; i++) {
      val_free(*frame_local_var(qe, i, 0));
    }
  }
  qe->curr_frame = stack_pop_block(&qe->stk, qe->curr_frame, frame_size(fp->bc));
}

void stack_push(qe_state *qe, val_t val) {
  assert(val_is_valid(val));
  qe->stk_top = stack_push_block(&qe->stk, qe->stk_top, sizeof(val_t));
  val_t* sval = stack_block(&qe->stk, qe->stk_top);
  *sval = val;
}

val_t stack_pop(qe_state *qe) {
  val_t* sval = stack_block(&qe->stk, qe->stk_top);
  val_t val = *sval;
  if (!stack_pop_will_free(&qe->stk, qe->stk_top)) {
    val = val_copy(val);
  }
  qe->stk_top = stack_pop_block(&qe->stk, qe->stk_top, sizeof(val_t));
  assert(val_is_valid(val));
  return val;
}

// Like stack_pop(), but assert !stack_pop_will_free() and replace with
// val_null() on the stack.
val_t stack_popn(qe_state *qe) {
  val_t* sval = stack_block(&qe->stk, qe->stk_top);
  val_t val = *sval;
  if (!stack_pop_will_free(&qe->stk, qe->stk_top)) {
    *sval = val_null();
  }
  qe->stk_top = stack_pop_block(&qe->stk, qe->stk_top, sizeof(val_t));
  assert(val_is_valid(val));
  return val;
}


struct forkpoint {
  stack_ptr saved_data_stack;
  stack_ptr saved_curr_frame;
  int path_len, subexp_nest;
  val_t value_at_path;
  uint16_t* return_address;
};

struct stack_pos {
  stack_ptr saved_data_stack, saved_curr_frame;
};

struct stack_pos stack_get_pos(qe_state* qe) {
  struct stack_pos sp = {qe->stk_top, qe->curr_frame};
  return sp;
}

void stack_save(qe_state *qe, uint16_t* retaddr, struct stack_pos sp){
  qe->fork_top = stack_push_block(&qe->stk, qe->fork_top, sizeof(struct forkpoint));
  struct forkpoint* fork = stack_block(&qe->stk, qe->fork_top);
  fork->saved_data_stack = qe->stk_top;
  fork->saved_curr_frame = qe->curr_frame;
  fork->path_len =
    val_get_kind(qe->path) == VAL_KIND_ARRAY ? val_array_length(val_copy(qe->path)) : 0;
  fork->value_at_path = val_copy(qe->value_at_path);
  fork->subexp_nest = qe->subexp_nest;
  fork->return_address = retaddr;
  qe->stk_top = sp.saved_data_stack;
  qe->curr_frame = sp.saved_curr_frame;
}

static int path_intact(qe_state *qe, val_t curr) {
  if (qe->subexp_nest == 0 && val_get_kind(qe->path) == VAL_KIND_ARRAY) {
    return val_identical(curr, val_copy(qe->value_at_path));
  } else {
    val_free(curr);
    return 1;
  }
}

static void path_append(qe_state* qe, val_t component, val_t value_at_path) {
  if (qe->subexp_nest == 0 && val_get_kind(qe->path) == VAL_KIND_ARRAY) {
    int n1 = val_array_length(val_copy(qe->path));
    qe->path = val_array_append(qe->path, component);
    int n2 = val_array_length(val_copy(qe->path));
    assert(n2 == n1 + 1);
    val_free(qe->value_at_path);
    qe->value_at_path = value_at_path;
  } else {
    val_free(component);
    val_free(value_at_path);
  }
}

/* For f_getpath() */
val_t
_jq_path_append(qe_state *qe, val_t v, val_t p, val_t value_at_path) {
  if (qe->subexp_nest != 0 ||
      val_get_kind(qe->path) != VAL_KIND_ARRAY ||
      !val_is_valid(value_at_path)) {
    val_free(v);
    val_free(p);
    return value_at_path;
  }
  if (!val_identical(v, val_copy(qe->value_at_path))) {
    val_free(p);
    return value_at_path;
  }
  if (val_get_kind(p) == VAL_KIND_ARRAY)
    qe->path = val_array_concat(qe->path, p);
  else
    qe->path = val_array_append(qe->path, p);
  val_free(qe->value_at_path);
  return val_copy(qe->value_at_path = value_at_path);
}

uint16_t* stack_restore(qe_state *qe){
  while (!stack_pop_will_free(&qe->stk, qe->fork_top)) {
    if (stack_pop_will_free(&qe->stk, qe->stk_top)) {
      val_free(stack_pop(qe));
    } else if (stack_pop_will_free(&qe->stk, qe->curr_frame)) {
      frame_pop(qe);
    } else {
      assert(0);
    }
  }

  if (qe->fork_top == 0) {
    return 0;
  }

  struct forkpoint* fork = stack_block(&qe->stk, qe->fork_top);
  uint16_t* retaddr = fork->return_address;
  qe->stk_top = fork->saved_data_stack;
  qe->curr_frame = fork->saved_curr_frame;
  int path_len = fork->path_len;
  if (val_get_kind(qe->path) == VAL_KIND_ARRAY) {
    assert(path_len >= 0);
    qe->path = val_array_slice(qe->path, 0, path_len);
  } else {
    fork->path_len = 0;
  }
  val_free(qe->value_at_path);
  qe->value_at_path = fork->value_at_path;
  qe->subexp_nest = fork->subexp_nest;
  qe->fork_top = stack_pop_block(&qe->stk, qe->fork_top, sizeof(struct forkpoint));
  return retaddr;
}

static void qe_reset(qe_state *qe) {
  while (stack_restore(qe)) {}

  assert(qe->stk_top == 0);
  assert(qe->fork_top == 0);
  assert(qe->curr_frame == 0);
  stack_reset(&qe->stk);
  val_free(qe->error);
  qe->error = val_null();

  qe->halted = 0;
  val_free(qe->exit_code);
  qe->exit_code = val_invalid();
  val_free(qe->error_message);
  qe->error_message = val_invalid();
  if (val_get_kind(qe->path) != VAL_KIND_INVALID)
    val_free(qe->path);
  qe->path = val_null();
  val_free(qe->value_at_path);
  qe->value_at_path = val_null();
  qe->subexp_nest = 0;
}

void qe_report_error(qe_state *qe, val_t value) {
  assert(qe->err_cb);
  // callback must val_free() its val_t argument
  qe->err_cb(qe->err_cb_data, value);
}

static void set_error(qe_state *qe, val_t value) {
  // Record so try/catch can find it.
  val_free(qe->error);
  qe->error = value;
}

#define ON_BACKTRACK(op) ((op)+NUM_OPCODES)

val_t qe_next(qe_state *qe) {
  val_nomem_handler(qe->nomem_handler, qe->nomem_handler_data);

  uint16_t* pc = stack_restore(qe);
  assert(pc);

  int raising;
  int backtracking = !qe->initial_execution;

  qe->initial_execution = 0;
  assert(val_get_kind(qe->error) == VAL_KIND_NULL);
  while (1) {
    if (qe->halted) {
      if (qe->debug_trace_enabled)
        printf("\t<halted>\n");
      return val_invalid();
    }
    uint16_t opcode = *pc;
    raising = 0;

    if (qe->debug_trace_enabled) {
      dump_operation(frame_current(qe)->bc, pc);
      printf("\t");
      const struct opcode_description* opdesc = opcode_describe(opcode);
      stack_ptr param = 0;
      if (!backtracking) {
        int stack_in = opdesc->stack_in;
        if (stack_in == -1) stack_in = pc[1];
        param = qe->stk_top;
        for (int i=0; i<stack_in; i++) {
          if (i != 0) {
            printf(" | ");
            param = *stack_block_next(&qe->stk, param);
          }
          if (!param) break;
          val_dump(val_copy(*(val_t*)stack_block(&qe->stk, param)), VAL_PRINT_REFCOUNT);
          //printf("<%d>", val_get_refcnt(param->val));
          //printf(" -- ");
          //val_dump(val_copy(qe->path), 0);
        }
        if (qe->debug_trace_enabled & QE_DEBUG_TRACE_DETAIL) {
          while ((param = *stack_block_next(&qe->stk, param))) {
            printf(" || ");
            val_dump(val_copy(*(val_t*)stack_block(&qe->stk, param)), VAL_PRINT_REFCOUNT);
          }
        }
      } else {
        printf("\t<backtracking>");
      }

      printf("\n");
    }

    if (backtracking) {
      opcode = ON_BACKTRACK(opcode);
      backtracking = 0;
      raising = !val_is_valid(qe->error);
    }
    pc++;

    switch (opcode) {
    default: assert(0 && "invalid instruction");

    case TOP: break;

    case ERRORK: {
      val_t v = val_array_get(val_copy(frame_current(qe)->bc->constants), *pc++);
      set_error(qe, val_invalid_with_msg(v));
      goto do_backtrack;
    }

    case LOADK: {
      val_t v = val_array_get(val_copy(frame_current(qe)->bc->constants), *pc++);
      assert(val_is_valid(v));
      val_free(stack_pop(qe));
      stack_push(qe, v);
      break;
    }

    case GENLABEL: {
      stack_push(qe, VAL_OBJECT(val_string("__jq"), val_number(qe->next_label++)));
      break;
    }

    case DUP: {
      val_t v = stack_pop(qe);
      stack_push(qe, val_copy(v));
      stack_push(qe, v);
      break;
    }

    case DUPN: {
      val_t v = stack_popn(qe);
      stack_push(qe, val_copy(v));
      stack_push(qe, v);
      break;
    }

    case DUP2: {
      val_t keep = stack_pop(qe);
      val_t v = stack_pop(qe);
      stack_push(qe, val_copy(v));
      stack_push(qe, keep);
      stack_push(qe, v);
      break;
    }

    case SUBEXP_BEGIN: {
      val_t v = stack_pop(qe);
      stack_push(qe, val_copy(v));
      stack_push(qe, v);
      qe->subexp_nest++;
      break;
    }

    case SUBEXP_END: {
      assert(qe->subexp_nest > 0);
      qe->subexp_nest--;
      val_t a = stack_pop(qe);
      val_t b = stack_pop(qe);
      stack_push(qe, a);
      stack_push(qe, b);
      break;
    }

    case PUSHK_UNDER: {
      val_t v = val_array_get(val_copy(frame_current(qe)->bc->constants), *pc++);
      assert(val_is_valid(v));
      val_t v2 = stack_pop(qe);
      stack_push(qe, v);
      stack_push(qe, v2);
      break;
    }

    case POP: {
      val_free(stack_pop(qe));
      break;
    }

    case APPEND: {
      val_t v = stack_pop(qe);
      uint16_t level = *pc++;
      uint16_t vidx = *pc++;
      val_t* var = frame_local_var(qe, vidx, level);
      assert(val_get_kind(*var) == VAL_KIND_ARRAY);
      *var = val_array_append(*var, v);
      break;
    }

    case INSERT: {
      val_t stktop = stack_pop(qe);
      val_t v = stack_pop(qe);
      val_t k = stack_pop(qe);
      val_t objv = stack_pop(qe);
      assert(val_get_kind(objv) == VAL_KIND_OBJECT);
      if (val_get_kind(k) == VAL_KIND_STRING) {
        stack_push(qe, val_object_set(objv, k, v));
        stack_push(qe, stktop);
      } else {
        char errbuf[30];
        set_error(qe, val_invalid_with_msg(val_string_fmt(
                "Cannot use %s (%s) as object key",
                val_kind_name(val_get_kind(k)),
                val_dump_string_trunc(val_copy(k), errbuf, sizeof(errbuf)))));
        val_free(stktop);
        val_free(v);
        val_free(k);
        val_free(objv);
        goto do_backtrack;
      }
      break;
    }

    case ON_BACKTRACK(RANGE):
    case RANGE: {
      uint16_t level = *pc++;
      uint16_t v = *pc++;
      val_t* var = frame_local_var(qe, v, level);
      val_t max = stack_pop(qe);
      if (raising) {
        val_free(max);
        goto do_backtrack;
      } 
      if (val_get_kind(*var) != VAL_KIND_NUMBER ||
          val_get_kind(max) != VAL_KIND_NUMBER) {
        set_error(qe, val_invalid_with_msg(val_string_fmt("Range bounds must be numeric")));
        val_free(max);
        goto do_backtrack;
      } else if (val_number_value(*var) >= val_number_value(max)) {
        /* finished iterating */
        val_free(max);
        goto do_backtrack;
      } else {
        val_t curr = *var;
        *var = val_number(val_number_value(*var) + 1);

        struct stack_pos spos = stack_get_pos(qe);
        stack_push(qe, max);
        stack_save(qe, pc - 3, spos);

        stack_push(qe, curr);
      }
      break;
    }

      // FIXME: loadv/storev may do too much copying/freeing
    case LOADV: {
      uint16_t level = *pc++;
      uint16_t v = *pc++;
      val_t* var = frame_local_var(qe, v, level);
      if (qe->debug_trace_enabled) {
        printf("V%d = ", v);
        val_dump(val_copy(*var), VAL_PRINT_REFCOUNT);
        printf("\n");
      }
      val_free(stack_pop(qe));
      stack_push(qe, val_copy(*var));
      break;
    }

      // Does a load but replaces the variable with null
    case LOADVN: {
      uint16_t level = *pc++;
      uint16_t v = *pc++;
      val_t* var = frame_local_var(qe, v, level);
      if (qe->debug_trace_enabled) {
        printf("V%d = ", v);
        val_dump(val_copy(*var), VAL_PRINT_REFCOUNT);
        printf("\n");
      }
      val_free(stack_popn(qe));

      // This `stack_push()` invalidates the `var` reference, so
      stack_push(qe, *var);
      // we have to re-resolve `var` before we can set it to null
      var = frame_local_var(qe, v, level);
      *var = val_null();
      break;
    }

    case STOREVN:
        stack_save(qe, pc - 1, stack_get_pos(qe));
        QE_FALLTHROUGH;
    case STOREV: {
      uint16_t level = *pc++;
      uint16_t v = *pc++;
      val_t* var = frame_local_var(qe, v, level);
      val_t val = stack_pop(qe);
      if (qe->debug_trace_enabled) {
        printf("V%d = ", v);
        val_dump(val_copy(val), 0);
        printf(" (%d)\n", val_get_refcnt(val));
      }
      val_free(*var);
      *var = val;
      break;
    }

    case ON_BACKTRACK(STOREVN): {
      uint16_t level = *pc++;
      uint16_t v = *pc++;
      val_t* var = frame_local_var(qe, v, level);
      val_free(*var);
      *var = val_null();
      goto do_backtrack;
      break;
    }

    case STORE_GLOBAL: {
      // Get the constant
      val_t val = val_array_get(val_copy(frame_current(qe)->bc->constants), *pc++);
      assert(val_is_valid(val));

      // Store the var
      uint16_t level = *pc++;
      uint16_t v = *pc++;
      val_t* var = frame_local_var(qe, v, level);
      if (qe->debug_trace_enabled) {
        printf("V%d = ", v);
        val_dump(val_copy(val), 0);
        printf(" (%d)\n", val_get_refcnt(val));
      }
      val_free(*var);
      *var = val;
      break;
    }

    case PATH_BEGIN: {
      val_t v = stack_pop(qe);
      stack_push(qe, qe->path);

      stack_save(qe, pc - 1, stack_get_pos(qe));

      stack_push(qe, val_number(qe->subexp_nest));
      stack_push(qe, qe->value_at_path);
      stack_push(qe, val_copy(v));

      qe->path = val_array();
      qe->value_at_path = v; // next INDEX operation must index into v
      qe->subexp_nest = 0;
      break;
    }

    case PATH_END: {
      val_t v = stack_pop(qe);
      // detect invalid path expression like path(.a | reverse)
      if (!path_intact(qe, val_copy(v))) {
        char errbuf[30];
        val_t msg = val_string_fmt(
            "Invalid path expression with result %s",
            val_dump_string_trunc(v, errbuf, sizeof(errbuf)));
        set_error(qe, val_invalid_with_msg(msg));
        goto do_backtrack;
      }
      val_free(v); // discard value, only keep path

      val_t old_value_at_path = stack_pop(qe);
      int old_subexp_nest = (int)val_number_value(stack_pop(qe));

      val_t path = qe->path;
      qe->path = stack_pop(qe);

      struct stack_pos spos = stack_get_pos(qe);
      stack_push(qe, val_copy(path));
      stack_save(qe, pc - 1, spos);

      stack_push(qe, path);
      qe->subexp_nest = old_subexp_nest;
      val_free(qe->value_at_path);
      qe->value_at_path = old_value_at_path;
      break;
    }

    case ON_BACKTRACK(PATH_BEGIN):
    case ON_BACKTRACK(PATH_END): {
      val_free(qe->path);
      qe->path = stack_pop(qe);
      goto do_backtrack;
    }

    case INDEX:
    case INDEX_OPT: {
      val_t t = stack_pop(qe);
      val_t k = stack_pop(qe);
      // detect invalid path expression like path(reverse | .a)
      if (!path_intact(qe, val_copy(t))) {
        char keybuf[30];
        char objbuf[30];
        val_t msg = val_string_fmt(
            "Invalid path expression near attempt to access element %s of %s",
            val_dump_string_trunc(k, keybuf, sizeof(keybuf)),
            val_dump_string_trunc(t, objbuf, sizeof(objbuf)));
        set_error(qe, val_invalid_with_msg(msg));
        goto do_backtrack;
      }
      val_t v = val_get(t, val_copy(k));
      if (val_is_valid(v)) {
        path_append(qe, k, val_copy(v));
        stack_push(qe, v);
      } else {
        val_free(k);
        if (opcode == INDEX)
          set_error(qe, v);
        else
          val_free(v);
        goto do_backtrack;
      }
      break;
    }


    case JUMP: {
      uint16_t offset = *pc++;
      pc += offset;
      break;
    }

    case JUMP_F: {
      uint16_t offset = *pc++;
      val_t t = stack_pop(qe);
      val_kind kind = val_get_kind(t);
      if (kind == VAL_KIND_FALSE || kind == VAL_KIND_NULL) {
        pc += offset;
      }
      stack_push(qe, t); // FIXME do this better
      break;
    }

    case EACH:
    case EACH_OPT: {
      val_t container = stack_pop(qe);
      // detect invalid path expression like path(reverse | .[])
      if (!path_intact(qe, val_copy(container))) {
        char errbuf[30];
        val_t msg = val_string_fmt(
            "Invalid path expression near attempt to iterate through %s",
            val_dump_string_trunc(container, errbuf, sizeof(errbuf)));
        set_error(qe, val_invalid_with_msg(msg));
        goto do_backtrack;
      }
      stack_push(qe, container);
      stack_push(qe, val_number(-1));
      QE_FALLTHROUGH;
    }
    case ON_BACKTRACK(EACH):
    case ON_BACKTRACK(EACH_OPT): {
      int idx = val_number_value(stack_pop(qe));
      val_t container = stack_pop(qe);

      int keep_going, is_last = 0;
      val_t key, value;
      if (val_get_kind(container) == VAL_KIND_ARRAY) {
        if (opcode == EACH || opcode == EACH_OPT) idx = 0;
        else idx = idx + 1;
        int len = val_array_length(val_copy(container));
        keep_going = idx < len;
        is_last = idx == len - 1;
        if (keep_going) {
          key = val_number(idx);
          value = val_array_get(val_copy(container), idx);
        }
      } else if (val_get_kind(container) == VAL_KIND_OBJECT) {
        if (opcode == EACH || opcode == EACH_OPT) idx = val_object_iter(container);
        else idx = val_object_iter_next(container, idx);
        keep_going = val_object_iter_valid(container, idx);
        if (keep_going) {
          key = val_object_iter_key(container, idx);
          value = val_object_iter_value(container, idx);
        }
      } else {
        assert(opcode == EACH || opcode == EACH_OPT);
        if (opcode == EACH) {
          char errbuf[30];
          set_error(qe, val_invalid_with_msg(val_string_fmt(
                  "Cannot iterate over %s (%s)",
                  val_kind_name(val_get_kind(container)),
                  val_dump_string_trunc(val_copy(container), errbuf, sizeof(errbuf)))));
        }
        keep_going = 0;
      }

      if (!keep_going || raising) {
        if (keep_going) {
          val_free(key);
          val_free(value);
        }
        val_free(container);
        goto do_backtrack;
      } else if (is_last) {
        // we don't need to make a backtrack point
        val_free(container);
        path_append(qe, key, val_copy(value));
        stack_push(qe, value);
      } else {
        struct stack_pos spos = stack_get_pos(qe);
        stack_push(qe, container);
        stack_push(qe, val_number(idx));
        stack_save(qe, pc - 1, spos);
        path_append(qe, key, val_copy(value));
        stack_push(qe, value);
      }
      break;
    }

    do_backtrack:
    case BACKTRACK: {
      pc = stack_restore(qe);
      if (!pc) {
        if (!val_is_valid(qe->error)) {
          val_t error = qe->error;
          qe->error = val_null();
          return error;
        }
        return val_invalid();
      }
      backtracking = 1;
      break;
    }

    case TRY_BEGIN:
      stack_save(qe, pc - 1, stack_get_pos(qe));
      pc++; // skip handler offset this time
      break;

    case TRY_END:
      stack_save(qe, pc - 1, stack_get_pos(qe));
      break;

    case ON_BACKTRACK(TRY_BEGIN): {
      if (!raising) {
        /*
         * `try EXP ...` -- EXP backtracked (e.g., EXP was `empty`), so we
         * backtrack more:
         */
        val_free(stack_pop(qe));
        goto do_backtrack;
      }

      /*
       * Else `(try EXP ... ) | EXP2` raised an error.
       *
       * If the error was wrapped in another error, then that means EXP2 raised
       * the error.  We unwrap it and re-raise it as it wasn't raised by EXP.
       *
       * See commentary in gen_try().
       */
      val_t e = val_invalid_get_msg(val_copy(qe->error));
      if (!val_is_valid(e) && val_invalid_has_msg(val_copy(e))) {
        set_error(qe, e);
        goto do_backtrack;
      }
      val_free(e);

      /*
       * Else we caught an error containing a non-error value, so we jump to
       * the handler.
       *
       * See commentary in gen_try().
       */
      uint16_t offset = *pc++;
      val_free(stack_pop(qe)); // free the input
      stack_push(qe, val_invalid_get_msg(qe->error));  // push the error's message
      qe->error = val_null();
      pc += offset;
      break;
    }
    case ON_BACKTRACK(TRY_END):
      // Wrap the error so the matching TRY_BEGIN doesn't catch it
      if (raising)
        set_error(qe, val_invalid_with_msg(val_copy(qe->error)));
      goto do_backtrack;

    case DESTRUCTURE_ALT:
    case FORK: {
      stack_save(qe, pc - 1, stack_get_pos(qe));
      pc++; // skip offset this time
      break;
    }

    case ON_BACKTRACK(DESTRUCTURE_ALT): {
      if (val_is_valid(qe->error)) {
        // `try EXP ...` backtracked here (no value, `empty`), so we backtrack more
        val_free(stack_pop(qe));
        goto do_backtrack;
      }
      // `try EXP ...` exception caught in EXP
      // DESTRUCTURE_ALT doesn't want the error message on the stack,
      // as we would just want to throw it away anyway.
      if (opcode != ON_BACKTRACK(DESTRUCTURE_ALT)) {
        val_free(stack_pop(qe)); // free the input
        stack_push(qe, val_invalid_get_msg(qe->error));  // push the error's message
      } else {
        val_free(qe->error);
      }
      qe->error = val_null();
      uint16_t offset = *pc++;
      pc += offset;
      break;
    }
    case ON_BACKTRACK(FORK): {
      if (raising) goto do_backtrack;
      uint16_t offset = *pc++;
      pc += offset;
      break;
    }

    case CALL_BUILTIN: {
      int nargs = *pc++;
      struct cfunction* function = &frame_current(qe)->bc->globals->cfunctions[*pc++];
      val_t in[MAX_CFUNCTION_ARGS];
      for (int i = 0; i < nargs; ++i)
        in[i] = stack_pop(qe);

      val_t top;
      switch (function->nargs) {
      case 1: top = function->fptr.a1(qe, in[0]); break;
      case 2: top = function->fptr.a2(qe, in[0], in[1]); break;
      case 3: top = function->fptr.a3(qe, in[0], in[1], in[2]); break;
      case 4: top = function->fptr.a4(qe, in[0], in[1], in[2], in[3]); break;
      default: assert(0 && "Invalid number of arguments");
      }

      if (!val_is_valid(top)) {
        if (val_invalid_has_msg(val_copy(top)))
          set_error(qe, top);
        else
          val_free(top);
        goto do_backtrack;
      }

      stack_push(qe, top);
      break;
    }

    case TAIL_CALL_JQ:
    case CALL_JQ: {
      /*
       * Bytecode layout here:
       *
       *  CALL_JQ
       *  <nclosures>                       (i.e., number of call arguments)
       *  <callee closure>                  (what we're calling)
       *  <nclosures' worth of closures>    (frame reference + code pointer)
       *
       *  <next instruction (to return to)>
       *
       * Each closure consists of two uint16_t values: a "level"
       * identifying the frame to be closed over, and an index.
       *
       * The level is a relative number of call frames reachable from
       * the currently one; 0 -> current frame, 1 -> previous frame, and
       * so on.
       *
       * The index is either an index of the closed frame's subfunctions
       * or of the closed frame's parameter closures.  If the latter,
       * that closure will be passed, else the closed frame's pointer
       * and the subfunction's code will form the closure to be passed.
       *
       * See make_closure() for more information.
       */
      val_t input = stack_pop(qe);
      uint16_t nclosures = *pc++;
      uint16_t* retaddr = pc + 2 + nclosures*2;
      stack_ptr retdata = qe->stk_top;
      struct frame* new_frame;
      struct closure cl = make_closure(qe, pc);
      if (opcode == TAIL_CALL_JQ) {
        retaddr = frame_current(qe)->retaddr;
        retdata = frame_current(qe)->retdata;
        frame_pop(qe);
      }
      new_frame = frame_push(qe, cl, pc + 2, nclosures);
      new_frame->retdata = retdata;
      new_frame->retaddr = retaddr;
      pc = new_frame->bc->code;
      stack_push(qe, input);
      break;
    }

    case RET: {
      val_t value = stack_pop(qe);
      assert(qe->stk_top == frame_current(qe)->retdata);
      uint16_t* retaddr = frame_current(qe)->retaddr;
      if (retaddr) {
        // function return
        pc = retaddr;
        frame_pop(qe);
      } else {
        // top-level return, yielding value
        struct stack_pos spos = stack_get_pos(qe);
        stack_push(qe, val_null());
        stack_save(qe, pc - 1, spos);
        return value;
      }
      stack_push(qe, value);
      break;
    }
    case ON_BACKTRACK(RET): {
      // resumed after top-level return
      goto do_backtrack;
    }
    }
  }
}

val_t qe_format_error(val_t msg) {
  if (val_get_kind(msg) == VAL_KIND_NULL ||
      (val_get_kind(msg) == VAL_KIND_INVALID && !val_invalid_has_msg(val_copy(msg)))) {
    val_free(msg);
    fprintf(stderr, "qe: error: out of memory\n");
    return val_null();
  }

  if (val_get_kind(msg) == VAL_KIND_STRING)
    return msg;                         // expected to already be formatted

  if (val_get_kind(msg) == VAL_KIND_INVALID)
    msg = val_invalid_get_msg(msg);

  if (val_get_kind(msg) == VAL_KIND_NULL)
    return qe_format_error(msg);        // ENOMEM

  // Invalid with msg; prefix with "qe: error: "

  if (val_get_kind(msg) != VAL_KIND_INVALID) {
    if (val_get_kind(msg) == VAL_KIND_STRING) {
      val_t r = val_string_fmt("qe: error: %s", val_string_value(msg));
      val_free(msg);
      return r;
    }

    msg = val_dump_string(msg, VAL_PRINT_INVALID);
    if (val_get_kind(msg) == VAL_KIND_STRING) {
      val_t r = val_string_fmt("qe: error: %s", val_string_value(msg));
      val_free(msg);
      return r;
    }
    val_free(msg);
    return qe_format_error(val_null());  // ENOMEM
  }

  // An invalid inside an invalid!
  return qe_format_error(val_invalid_get_msg(msg));
}

// XXX Refactor into a utility function that returns a val_t and one that
// uses it and then prints that val_t's string as the complete error
// message.
static void default_err_cb(void *data, val_t msg) {
  msg = qe_format_error(msg);
  fprintf((FILE *)data, "%s\n", val_string_value(msg));
  val_free(msg);
}

qe_state *qe_init(void) {
  qe_state *qe;
  qe = val_mem_alloc_unguarded(sizeof(*qe));
  if (qe == NULL)
    return NULL;

  qe->bc = 0;
  qe->next_label = 0;

  stack_init(&qe->stk);
  qe->stk_top = 0;
  qe->fork_top = 0;
  qe->curr_frame = 0;
  qe->error = val_null();

  qe->halted = 0;
  qe->exit_code = val_invalid();
  qe->error_message = val_invalid();

  qe->input_cb = NULL;
  qe->input_cb_data = NULL;

  qe->debug_cb = NULL;
  qe->debug_cb_data = NULL;

  qe->stderr_cb = NULL;
  qe->stderr_cb_data = NULL;

  qe->err_cb = default_err_cb;
  qe->err_cb_data = stderr;

  qe->attrs = val_object();
  qe->path = val_null();
  qe->value_at_path = val_null();

  qe->nomem_handler = NULL;
  qe->nomem_handler_data = NULL;
  return qe;
}

void qe_set_error_cb(qe_state *qe, qe_msg_cb cb, void *data) {
  if (cb == NULL) {
    qe->err_cb = default_err_cb;
    qe->err_cb_data = stderr;
  } else {
    qe->err_cb = cb;
    qe->err_cb_data = data;
  }
}

void qe_get_error_cb(qe_state *qe, qe_msg_cb *cb, void **data) {
  *cb = qe->err_cb;
  *data = qe->err_cb_data;
}

void qe_set_nomem_handler(qe_state *qe, void (*nomem_handler)(void *), void *data) {
  val_nomem_handler(nomem_handler, data);
  qe->nomem_handler = nomem_handler;
  qe->nomem_handler_data = data;
}


void qe_start(qe_state *qe, val_t input, int flags) {
  val_nomem_handler(qe->nomem_handler, qe->nomem_handler_data);
  qe_reset(qe);

  struct closure top = {qe->bc, -1};
  struct frame* top_frame = frame_push(qe, top, 0, 0);
  top_frame->retdata = 0;
  top_frame->retaddr = 0;

  stack_push(qe, input);
  stack_save(qe, qe->bc->code, stack_get_pos(qe));
  qe->debug_trace_enabled = flags & QE_DEBUG_TRACE_ALL;
  qe->initial_execution = 1;
}

void qe_teardown(qe_state **qe) {
  qe_state *old_jq = *qe;
  if (old_jq == NULL)
    return;
  *qe = NULL;

  qe_reset(old_jq);
  bytecode_free(old_jq->bc);
  old_jq->bc = 0;
  val_free(old_jq->attrs);

  val_mem_free(old_jq);
}

static int ret_follows(uint16_t *pc) {
  if (*pc == RET)
    return 1;
  if (*pc++ != JUMP)
    return 0;
  return ret_follows(pc + *pc + 1); // FIXME, might be ironic
}

/*
 * Look for tail calls that can be optimized: tail calls with no
 * references left to the current frame.
 *
 * We're staring at this bytecode layout:
 *
 *   CALL_JQ
 *   <nclosures>
 *   <callee closure>       (2 units)
 *   <nclosures closures>   (2 units each)
 *   <next instruction>
 *
 * A closure is:
 *
 *   <level>    (a relative frame count chased via the current frame's env)
 *   <index>    (an index of a subfunction or closure in that frame)
 *
 * We're looking for:
 *
 * a) the next instruction is a RET or a chain of unconditional JUMPs
 * that ends in a RET, and
 *
 * b) none of the closures -callee included- have level == 0.
 */
static uint16_t tail_call_analyze(uint16_t *pc) {
  assert(*pc == CALL_JQ);
  pc++;
  // + 1 for the callee closure
  for (uint16_t nclosures = *pc++ + 1; nclosures > 0; pc++, nclosures--) {
    if (*pc++ == 0)
      return CALL_JQ;
  }
  if (ret_follows(pc))
    return TAIL_CALL_JQ;
  return CALL_JQ;
}

static struct bytecode *optimize_code(struct bytecode *bc) {
  uint16_t *pc = bc->code;
  // FIXME: Don't mutate bc->code...
  while (pc < bc->code + bc->codelen) {
    switch (*pc) {
    case CALL_JQ:
      *pc = tail_call_analyze(pc);
      break;

    // Other bytecode optimizations here.  A peephole optimizer would
    // fit right in.
    default: break;
    }
    pc += bytecode_operation_length(pc);
  }
  return bc;
}

static struct bytecode *optimize(struct bytecode *bc) {
  for (int i=0; i<bc->nsubfunctions; i++) {
    bc->subfunctions[i] = optimize(bc->subfunctions[i]);
  }
  return optimize_code(bc);
}

static val_t
args2obj(val_t args)
{
  if (val_get_kind(args) == VAL_KIND_OBJECT)
    return args;
  assert(val_get_kind(args) == VAL_KIND_ARRAY);
  val_t r = val_object();
  val_t kk = val_string("name");
  val_t vk = val_string("value");
  val_array_foreach(args, i, v)
    r = val_object_set(r, val_object_get(val_copy(v), val_copy(kk)), val_object_get(v, val_copy(vk)));
  val_free(args);
  val_free(kk);
  val_free(vk);
  return r;
}

int qe_compile_args(qe_state *qe, const char* str, val_t args) {
  val_nomem_handler(qe->nomem_handler, qe->nomem_handler_data);
  assert(val_get_kind(args) == VAL_KIND_ARRAY || val_get_kind(args) == VAL_KIND_OBJECT);
  struct locfile* locations;
  locations = locfile_init(qe, "<top-level>", str, strlen(str));
  block program;
  qe_reset(qe);
  if (qe->bc) {
    bytecode_free(qe->bc);
    qe->bc = 0;
  }
  int nerrors = load_program(qe, locations, &program);
  if (nerrors == 0) {
    nerrors = builtins_bind(qe, &program);
    if (nerrors == 0)
      nerrors = block_compile(program, &qe->bc, locations, args2obj(args));
    else
      val_free(args);
  } else
    val_free(args);
  if (nerrors)
    qe_report_error(qe, val_string_fmt("qe: %d compile %s", nerrors, nerrors > 1 ? "errors" : "error"));
  if (qe->bc)
    qe->bc = optimize(qe->bc);
  locfile_free(locations);
  return qe->bc != NULL;
}

int qe_compile(qe_state *qe, const char* str) {
  return qe_compile_args(qe, str, val_object());
}

val_t qe_get_jq_origin(qe_state *qe) {
  return qe_get_attr(qe, val_string("QE_ORIGIN"));
}

val_t qe_get_prog_origin(qe_state *qe) {
  return qe_get_attr(qe, val_string("PROGRAM_ORIGIN"));
}

val_t qe_get_lib_dirs(qe_state *qe) {
  val_t lib_dirs = qe_get_attr(qe, val_string("QE_LIBRARY_PATH"));
  return val_is_valid(lib_dirs) ? lib_dirs : val_array();
}

void qe_set_attrs(qe_state *qe, val_t attrs) {
  assert(val_get_kind(attrs) == VAL_KIND_OBJECT);
  val_free(qe->attrs);
  qe->attrs = attrs;
}

void qe_set_attr(qe_state *qe, val_t attr, val_t val) {
  qe->attrs = val_object_set(qe->attrs, attr, val);
}

val_t qe_get_attr(qe_state *qe, val_t attr) {
  return val_object_get(val_copy(qe->attrs), attr);
}

void qe_dump_disassembly(qe_state *qe, int indent) {
  dump_disassembly(indent, qe->bc);
}

void qe_set_input_cb(qe_state *qe, qe_input_cb cb, void *data) {
  qe->input_cb = cb;
  qe->input_cb_data = data;
}

void qe_get_input_cb(qe_state *qe, qe_input_cb *cb, void **data) {
  *cb = qe->input_cb;
  *data = qe->input_cb_data;
}

void qe_set_debug_cb(qe_state *qe, qe_msg_cb cb, void *data) {
  qe->debug_cb = cb;
  qe->debug_cb_data = data;
}

void qe_get_debug_cb(qe_state *qe, qe_msg_cb *cb, void **data) {
  *cb = qe->debug_cb;
  *data = qe->debug_cb_data;
}

void qe_set_stderr_cb(qe_state *qe, qe_msg_cb cb, void *data) {
  qe->stderr_cb = cb;
  qe->stderr_cb_data = data;
}

void qe_get_stderr_cb(qe_state *qe, qe_msg_cb *cb, void **data) {
  *cb = qe->stderr_cb;
  *data = qe->stderr_cb_data;
}

void
qe_halt(qe_state *qe, val_t exit_code, val_t error_message)
{
  assert(!qe->halted);
  qe->halted = 1;
  qe->exit_code = exit_code;
  qe->error_message = error_message;
}

int
qe_halted(qe_state *qe)
{
  return qe->halted;
}

val_t qe_get_exit_code(qe_state *qe)
{
  return val_copy(qe->exit_code);
}

val_t qe_get_error_message(qe_state *qe)
{
  return val_copy(qe->error_message);
}
