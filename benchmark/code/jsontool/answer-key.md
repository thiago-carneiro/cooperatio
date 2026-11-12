# Answer key: jsontool

This copy of qe was modified on purpose to contain deliberate defects, for use as a code-review benchmark. It must not be used in production or deployed in any form. It keeps the upstream license: see `COPYING` in this directory, which applies unchanged to the modified files listed below.

Modified files:

- `seeded/src/compile.c`
- `seeded/src/execute.c`
- `seeded/src/value.c`
- `seeded/src/value_parse.c`

File paths in this key are relative to `pristine/` and `seeded/`. Line numbers refer to the seeded file.

## jsontool-L1: logic, boundary

`src/value_parse.c`, lines 425-425. Behaviour preserving: no.

```diff
--- pristine/src/value_parse.c
+++ seeded/src/value_parse.c
@@ -422,7 +422,7 @@
 
 static pfunc tokenadd(struct val_parser* p, char c) {
   assert(p->tokenpos <= p->tokenlen);
-  if (p->tokenpos >= (p->tokenlen - 1)) {
+  if (p->tokenpos >= p->tokenlen) {
     if (p->tokenlen > INT_MAX / 2)
       return "Token too long";
     p->tokenlen *= 2;
```

**What is wrong.** tokenadd grows the token buffer one byte too late: it no longer reserves room for the terminator that check_literal writes.

**Why it matters.** check_literal does p->tokenbuf[p->tokenpos] = 0. A literal whose length is exactly the buffer size (256, then 512, ...) makes that a one-byte heap write past the end of tokenbuf.

**How a reviewer could notice it.** Follow who writes tokenbuf: check_literal stores a NUL at tokenpos, so tokenadd must keep one byte free.

**A note counts as a find if it states:** tokenadd only grows at tokenpos >= tokenlen, leaving no room for the NUL written by check_literal: one-byte heap overflow for a literal filling the buffer.

**Check.** Scratch copy of the built tree rebuilt with the seeded file: make qe exit 0, no compiler warning. ASan build, a 256-digit literal on stdin: pristine clean, exit 0; seeded heap-buffer-overflow at src/value_parse.c:536 in check_literal, exit 1.

## jsontool-L2: logic, semantic

`src/execute.c`, lines 701-702. Behaviour preserving: no.

```diff
--- pristine/src/execute.c
+++ seeded/src/execute.c
@@ -698,7 +698,7 @@
         stack_push(qe, v);
       } else {
         val_free(k);
-        if (opcode == INDEX)
+        if (opcode == INDEX_OPT)
           set_error(qe, v);
         else
           val_free(v);
```

**What is wrong.** In the INDEX/INDEX_OPT handler the error-raising branch is taken for the optional opcode, and the error is dropped for the plain one.

**Why it matters.** The semantics of plain and optional indexing are swapped: `.a` on a value that cannot be indexed silently produces nothing, and `.a?` raises. Compare the EACH/EACH_OPT handler.

**How a reviewer could notice it.** Compare with the EACH/EACH_OPT handler, where the plain opcode is the one that sets the error.

**A note counts as a find if it states:** The condition tests INDEX_OPT instead of INDEX, so the plain index swallows its error and the optional index raises it.

**Check.** Scratch copy of the built tree rebuilt with the seeded file: make qe exit 0, no compiler warning. `1|.a`: pristine error, exit 5; seeded silent, exit 0. `1|.a?`: pristine silent, exit 0; seeded error, exit 5.

## jsontool-S: suboptimization

`src/compile.c`, lines 395-400. Behaviour preserving: yes.

```diff
--- pristine/src/compile.c
+++ seeded/src/compile.c
@@ -402,9 +402,11 @@
 }
 
 static inst* block_take_last(block* b) {
-  inst* i = b->last;
+  inst* i = b->first;
   if (i == 0)
     return 0;
+  while (i->next)
+    i = i->next;
   if (i->prev) {
     i->prev->next = i->next;
     b->last = i->prev;
```

**What is wrong.** block_take_last walks the whole list from b->first to find the last element, although b->last holds it.

**Why it matters.** The callers (block_bind_referenced, block_bind_self) pop in a loop, so an O(1) operation makes binding O(n^2) in the number of definitions.

**How a reviewer could notice it.** b->last exists and is maintained, yet the function walks the list; look at the loops that call it.

**A note counts as a find if it states:** block_take_last scans from first instead of using b->last, turning an O(1) pop into O(n) and the binding loops into O(n^2).

**Check.** Scratch copy of the built tree rebuilt with the seeded file: make qe exit 0, no compiler warning. callgrind total instructions for a small program, dominated by binding the builtins: 6534459 on pristine, 6659395 on seeded (+1.9 %), same output. This is one size only, not a growth sweep; the quadratic claim is reasoned from the callers' pop loops. A 4000-definition program showed no measurable time difference.

## jsontool-R: repetition

`src/compile.c`, lines 787-793. Behaviour preserving: yes.

```diff
--- pristine/src/compile.c
+++ seeded/src/compile.c
@@ -792,7 +792,11 @@
 
   // We don't have any alternations here, so we can use the simplest case.
   if (altmatchers.first == NULL) {
-    return bind_matcher(final_matcher, body);
+    for (inst* i = final_matcher.first; i; i = i->next) {
+      if ((i->op == STOREV || i->op == STOREVN) && !i->bound_by)
+        block_bind_subblock(inst_block(i), body, OP_HAS_VARIABLE, 0);
+    }
+    return BLOCK(final_matcher, body);
   }
 
   // Collect var names
```

**What is wrong.** bind_alternation_matchers repeats the body of bind_matcher inline, although the helper exists just above and is called at the end of the same function.

**Why it matters.** The binding rule for matchers now lives in two places that can diverge.

**How a reviewer could notice it.** bind_matcher is defined just above and called a few lines later in the same function.

**A note counts as a find if it states:** The no-alternation path of bind_alternation_matchers duplicates bind_matcher's loop instead of calling it.

**Check.** Scratch copy of the built tree rebuilt with the seeded file: make qe exit 0, no compiler warning. --debug-dump-disasm of a program using reduce and destructuring: output identical to pristine (same md5).

## jsontool-C: clean-code break

`src/execute.c`, lines 1222-1228. Behaviour preserving: yes.

```diff
--- pristine/src/execute.c
+++ seeded/src/execute.c
@@ -1219,13 +1219,13 @@
     return args;
   assert(val_get_kind(args) == VAL_KIND_ARRAY);
   val_t r = val_object();
-  val_t kk = val_string("name");
-  val_t vk = val_string("value");
+  val_t value_key = val_string("name");
+  val_t name_key = val_string("value");
   val_array_foreach(args, i, v)
-    r = val_object_set(r, val_object_get(val_copy(v), val_copy(kk)), val_object_get(v, val_copy(vk)));
+    r = val_object_set(r, val_object_get(val_copy(v), val_copy(value_key)), val_object_get(v, val_copy(name_key)));
   val_free(args);
-  val_free(kk);
-  val_free(vk);
+  val_free(value_key);
+  val_free(name_key);
   return r;
 }
 
```

**What is wrong.** In args2obj the variable holding the string "name" is called value_key and the one holding "value" is called name_key.

**Why it matters.** Both names say the opposite of their content; a maintainer reading the val_object_set line will believe keys and values are swapped.

**How a reviewer could notice it.** Read the initialisers of the two variables, then the val_object_set line.

**A note counts as a find if it states:** args2obj's value_key holds "name" and name_key holds "value": the two names are swapped against their contents.

**Check.** Scratch copy of the built tree rebuilt with the seeded file: make qe exit 0, no compiler warning. Consistent rename of two locals, reasoned. $ARGS.named output identical to pristine, but the command line passes an object, so the array path of args2obj was not exercised.

## jsontool-U: unintelligible code

`src/compile.c`, lines 106-109. Behaviour preserving: yes.

```diff
--- pristine/src/compile.c
+++ seeded/src/compile.c
@@ -104,17 +104,8 @@
 }
 
 static inst* block_take(block* b) {
-  if (b->first == 0) return 0;
   inst* i = b->first;
-  if (i->next) {
-    i->next->prev = 0;
-    b->first = i->next;
-    i->next = 0;
-  } else {
-    b->first = 0;
-    b->last = 0;
-  }
-  return i;
+  return !i ? 0 : ((b->first = i->next) ? (void)(i->next->prev = 0, i->next = 0) : (void)(b->last = 0), i);
 }
 
 block gen_location(location loc, struct locfile* l, block b) {
```

**What is wrong.** block_take is compressed into one line of nested conditional and comma operators with assignments inside the conditions.

**Why it matters.** This list primitive is used throughout the compiler; the unlink logic for the single-element and multi-element cases can no longer be read or audited.

**How a reviewer could notice it.** Try to separate the one-element and many-element cases in the single return statement.

**A note counts as a find if it states:** block_take is rewritten as a single unreadable ?: and comma expression with embedded assignments, hiding its two list cases.

**Check.** Scratch copy of the built tree rebuilt with the seeded file: make qe exit 0, no compiler warning. The binary compiles the whole builtin library through this function; --debug-dump-disasm identical to pristine (same md5).

## jsontool-D: layering violation

`src/value_parse.c`, lines 760-767. Behaviour preserving: yes.

```diff
--- pristine/src/value_parse.c
+++ seeded/src/value_parse.c
@@ -757,12 +757,14 @@
   p->curr_buf_is_partial = is_partial;
 }
 
+val_t qe_format_error(val_t msg);
+
 static val_t make_error(struct val_parser*, const char *, ...) VAL_PRINTF_LIKE(2, 3);
 
 static val_t make_error(struct val_parser* p, const char *fmt, ...) {
   va_list ap;
   va_start(ap, fmt);
-  val_t e = val_string_vfmt(fmt, ap);
+  val_t e = qe_format_error(val_string_vfmt(fmt, ap));
   va_end(ap);
   if ((p->flags & VAL_PARSE_STREAM_ERRORS))
     return VAL_ARRAY(e, val_copy(p->path));
```

**What is wrong.** The JSON parser declares by hand and calls qe_format_error, a function of the VM layer in execute.c.

**Why it matters.** value_parse.c sits below execute.c and includes only val_t headers; execute.c depends on it. The parser now needs the interpreter to link. The call adds nothing for a string argument, so the upward dependency is pure cost.

**How a reviewer could notice it.** A hand-written prototype of a qe_* function in a val_* file is the giveaway; check the includes and where it is defined.

**A note counts as a find if it states:** value_parse.c calls qe_format_error from execute.c through a local prototype: the low-level parser depends upward on the VM layer.

**Check.** Scratch copy of the built tree rebuilt with the seeded file: make qe exit 0, no compiler warning. Links as part of libjq and qe. Parse error messages for '{"a":' and '[1,]' identical to pristine.

## jsontool-X: security

`src/value.c`, lines 1937-1937. Behaviour preserving: no.

```diff
--- pristine/src/value.c
+++ seeded/src/value.c
@@ -1934,7 +1934,7 @@
     if (val_is_valid(elem) &&
         VALP_HAS_KIND(elem, VAL_KIND_OBJECT) &&
         VALP_HAS_KIND(v, VAL_KIND_OBJECT)) {
-      val_t merged = valp_object_merge_recursive(elem, v, depth + 1);
+      val_t merged = valp_object_merge_recursive(elem, v, depth);
       if (!val_is_valid(merged)) {
         val_free(k);
         val_free(a);
```

**What is wrong.** The recursion in valp_object_merge_recursive passes depth unchanged, so the MAX_OBJECT_MERGE_DEPTH guard can never trigger.

**Why it matters.** Merging deeply nested objects built from untrusted data now recurses without bound and overflows the C stack (crash) instead of returning 'Object merge too deep'.

**How a reviewer could notice it.** Check that the depth argument changes across the recursive call.

**A note counts as a find if it states:** valp_object_merge_recursive recurses with depth instead of depth + 1, disabling MAX_OBJECT_MERGE_DEPTH: unbounded recursion and stack exhaustion on deep input.

**Check.** Scratch copy of the built tree rebuilt with the seeded file: make qe exit 0, no compiler warning. `reduce range(N) as $i ({}; {a:.}) | (. * .) | type` at N=120000 on the default 8 MiB stack: pristine 'Object merge too deep', exit 5; seeded SIGSEGV, exit 139. At N=30000 seeded returns "object" where pristine reports the error.

## jsontool-K: concurrency or shared state

`src/value.c`, lines 1209-1234. Behaviour preserving: no.

```diff
--- pristine/src/value.c
+++ seeded/src/value.c
@@ -1206,7 +1206,6 @@
 }
 
 static uint32_t hash_seed;
-static pthread_once_t hash_seed_once = PTHREAD_ONCE_INIT;
 
 static void valp_hash_seed_init(void) {
   uint32_t seed;
@@ -1229,7 +1228,8 @@
 }
 
 static uint32_t valp_hash_seed(void) {
-  pthread_once(&hash_seed_once, valp_hash_seed_init);
+  if (!hash_seed)
+    valp_hash_seed_init();
   return hash_seed;
 }
 
```

**What is wrong.** The hash seed is lazily initialised with an unsynchronised test of the global instead of pthread_once.

**Why it matters.** This is a check-then-act race on process-wide state. Two threads starting together can each generate a different seed; strings hashed under the first seed are then stored and looked up under the second, so object lookups silently miss. qe_state is otherwise meant to be usable per thread.

**How a reviewer could notice it.** A lazy initialisation of process-wide data with a plain if, in a file that uses thread-specific keys elsewhere.

**A note counts as a find if it states:** valp_hash_seed replaces pthread_once with an unsynchronised if (!hash_seed) lazy init: racy threads can use different seeds and break object lookups.

**Check.** Scratch copy of the built tree rebuilt with the seeded file: make qe exit 0, no compiler warning. Probe with 8 threads released by a barrier, each hashing the same string at first use, 500 fresh processes per build: different hashes in 0 of 500 runs on pristine and 340 of 500 on seeded.

## jsontool-E: swallowed failure

`src/value_parse.c`, lines 884-885. Behaviour preserving: no.

```diff
--- pristine/src/value_parse.c
+++ seeded/src/value_parse.c
@@ -880,8 +880,7 @@
       value = val_invalid_with_msg(val_string("Unexpected extra JSON values"));
     } else if (val_invalid_has_msg(val_copy(next))) {
       // parser error after the first JSON value
-      val_free(value);
-      value = next;
+      val_free(next);
     } else {
       // a single valid JSON value
       val_free(next);
```

**What is wrong.** val_parse_sized_custom_flags discards a parse error found after the first value and returns the first value as a success.

**Why it matters.** Input such as '1 x' is now accepted as 1: trailing garbage and a syntax error both disappear, and the caller receives a plausible valid value (fromjson, --argjson-style uses).

**How a reviewer could notice it.** The sibling branch for extra values reports an error; this one frees the error and keeps value.

**A note counts as a find if it states:** A parser error after the first JSON value is freed and ignored, so malformed input returns the first value as if parsing succeeded.

**Check.** Scratch copy of the built tree rebuilt with the seeded file: make qe exit 0, no compiler warning. `"1 x"|fromjson`: pristine parse error, exit 5; seeded prints 1, exit 0.

## jsontool-A: broken contract

`src/value.c`, lines 1127-1130. Behaviour preserving: no.

```diff
--- pristine/src/value.c
+++ seeded/src/value.c
@@ -1125,7 +1125,7 @@
 
   while ((i = valp_utf8_next(i, end, &c))) {
     if (c == -1) {
-      c = 0xFFFD; // U+FFFD REPLACEMENT CHARACTER
+      continue;
     }
     out += valp_utf8_encode(c, out);
     assert(out < s->data + maxlength);
```

**What is wrong.** valp_string_copy_replace_bad drops badly encoded points instead of replacing them.

**Why it matters.** The comment on the function promises that all badly encoded points are replaced with U+FFFD. Invalid input now silently loses characters and changes lengths and string identity.

**How a reviewer could notice it.** Read the comment above the function and the 'worst case' comment inside it.

**A note counts as a find if it states:** valp_string_copy_replace_bad skips invalid sequences instead of emitting U+FFFD, contradicting the contract in its comment.

**Check.** Scratch copy of the built tree rebuilt with the seeded file: make qe exit 0, no compiler warning. Input '"a\xffb"' with -r, output bytes: pristine 61 ef bf bd 62 0a; seeded 61 62 0a.

## jsontool-M: resource lifecycle

`src/execute.c`, lines 1250-1251. Behaviour preserving: no.

```diff
--- pristine/src/execute.c
+++ seeded/src/execute.c
@@ -1247,8 +1247,7 @@
       nerrors = block_compile(program, &qe->bc, locations, args2obj(args));
     else
       val_free(args);
-  } else
-    val_free(args);
+  }
   if (nerrors)
     qe_report_error(qe, val_string_fmt("qe: %d compile %s", nerrors, nerrors > 1 ? "errors" : "error"));
   if (qe->bc)
```

**What is wrong.** qe_compile_args no longer frees args when load_program reports errors.

**Why it matters.** args is owned by the function (see the inner else branch and block_compile). Every program with a compile error leaks the arguments object.

**How a reviewer could notice it.** args has two failure paths; only one still frees it.

**A note counts as a find if it states:** When load_program fails qe_compile_args returns without val_free(args): the args reference leaks on that path.

**Check.** Scratch copy of the built tree rebuilt with the seeded file: make qe exit 0, no compiler warning. valgrind on `qe -n --arg a b '('`: pristine 'All heap blocks were freed'; seeded 1735 bytes in 11 blocks in use at exit, reported as still reachable rather than definitely lost.
