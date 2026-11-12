//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//


#include <stdint.h>
#include <stddef.h>
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <limits.h>
#include <math.h>
#include <float.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>

#include "value_alloc.h"
#include "value.h"
#include "value_unicode.h"
#include "util.h"

/*
 * Internal refcounting helpers
 */

typedef struct val_refcnt {
  int count;
} val_refcnt;

static const val_refcnt VAL_REFCNT_INIT = {1};

static void valp_refcnt_inc(val_refcnt* c) {
  c->count++;
}

static int valp_refcnt_dec(val_refcnt* c) {
  c->count--;
  return c->count == 0;
}

static int valp_refcnt_unshared(val_refcnt* c) {
  assert(c->count > 0);
  return c->count == 1;
}

#define KIND_MASK   0xF
#define PFLAGS_MASK 0xF0
#define PTYPE_MASK  0x70

typedef enum {
  VALP_PAYLOAD_NONE = 0,
  VALP_PAYLOAD_ALLOCATED = 0x80,
} payload_flags;

#define VALP_MAKE_PFLAGS(ptype, allocated) ((((ptype) << 4) & PTYPE_MASK) | ((allocated) ? VALP_PAYLOAD_ALLOCATED : 0))
#define VALP_MAKE_FLAGS(kind, pflags) ((kind & KIND_MASK) | (pflags & PFLAGS_MASK))

#define VALP_FLAGS(j)  ((j).kind_flags)
#define VALP_KIND(j)   (VALP_FLAGS(j) & KIND_MASK)

#define VALP_HAS_FLAGS(j, flags) (VALP_FLAGS(j) == flags)
#define VALP_HAS_KIND(j, kind)   (VALP_KIND(j) == kind)

#define VALP_IS_ALLOCATED(j) (j.kind_flags & VALP_PAYLOAD_ALLOCATED)

#define VALP_FLAGS_NULL      VALP_MAKE_FLAGS(VAL_KIND_NULL, VALP_PAYLOAD_NONE)
#define VALP_FLAGS_INVALID   VALP_MAKE_FLAGS(VAL_KIND_INVALID, VALP_PAYLOAD_NONE)
#define VALP_FLAGS_FALSE     VALP_MAKE_FLAGS(VAL_KIND_FALSE, VALP_PAYLOAD_NONE)
#define VALP_FLAGS_TRUE      VALP_MAKE_FLAGS(VAL_KIND_TRUE, VALP_PAYLOAD_NONE)

val_kind val_get_kind(val_t x) {
  return VALP_KIND(x);
}

const char* val_kind_name(val_kind k) {
  switch (k) {
  case VAL_KIND_INVALID: return "<invalid>";
  case VAL_KIND_NULL:    return "null";
  case VAL_KIND_FALSE:   return "boolean";
  case VAL_KIND_TRUE:    return "boolean";
  case VAL_KIND_NUMBER:  return "number";
  case VAL_KIND_STRING:  return "string";
  case VAL_KIND_ARRAY:   return "array";
  case VAL_KIND_OBJECT:  return "object";
  }
  assert(0 && "invalid kind");
  return "<unknown>";
}

const val_t VAL_NULL = {VALP_FLAGS_NULL, 0, 0, 0, {0}};
const val_t VAL_INVALID = {VALP_FLAGS_INVALID, 0, 0, 0, {0}};
const val_t VAL_FALSE = {VALP_FLAGS_FALSE, 0, 0, 0, {0}};
const val_t VAL_TRUE = {VALP_FLAGS_TRUE, 0, 0, 0, {0}};

val_t val_true(void) {
  return VAL_TRUE;
}

val_t val_false(void) {
  return VAL_FALSE;
}

val_t val_null(void) {
  return VAL_NULL;
}

val_t val_bool(int x) {
  return x ? VAL_TRUE : VAL_FALSE;
}

/*
 * Invalid objects, with optional error messages
 */

#define VALP_FLAGS_INVALID_MSG   VALP_MAKE_FLAGS(VAL_KIND_INVALID, VALP_PAYLOAD_ALLOCATED)

typedef struct {
  val_refcnt refcnt;
  val_t errmsg;
} valp_invalid;

val_t val_invalid_with_msg(val_t err) {
  valp_invalid* i = val_mem_alloc(sizeof(valp_invalid));
  i->refcnt = VAL_REFCNT_INIT;
  i->errmsg = err;

  val_t x = {VALP_FLAGS_INVALID_MSG, 0, 0, 0, {&i->refcnt}};
  return x;
}

val_t val_invalid(void) {
  return VAL_INVALID;
}

val_t val_invalid_get_msg(val_t inv) {
  assert(VALP_HAS_KIND(inv, VAL_KIND_INVALID));

  val_t x;
  if (VALP_HAS_FLAGS(inv, VALP_FLAGS_INVALID_MSG)) {
    x = val_copy(((valp_invalid*)inv.u.ptr)->errmsg);
  }
  else {
    x = val_null();
  }

  val_free(inv);
  return x;
}

int val_invalid_has_msg(val_t inv) {
  assert(VALP_HAS_KIND(inv, VAL_KIND_INVALID));
  int r = VALP_HAS_FLAGS(inv, VALP_FLAGS_INVALID_MSG);
  val_free(inv);
  return r;
}

/*
 * Numbers
 */

#ifdef USE_DECNUM
#include "value_dtoa.h"
#include "value_dtoa_tsd.h"

// we will manage the space for the struct
#define DECNUMDIGITS 1
#include "decNumber/decNumber.h"

enum {
  VALP_NUMBER_NATIVE = 0,
  VALP_NUMBER_DECIMAL = 1
};

#define VALP_FLAGS_NUMBER_NATIVE       VALP_MAKE_FLAGS(VAL_KIND_NUMBER, VALP_MAKE_PFLAGS(VALP_NUMBER_NATIVE, 0))
#define VALP_FLAGS_NUMBER_LITERAL      VALP_MAKE_FLAGS(VAL_KIND_NUMBER, VALP_MAKE_PFLAGS(VALP_NUMBER_DECIMAL, 1))

// the decimal precision of binary double
#define DEC_NUMBER_DOUBLE_PRECISION   (17)
#define DEC_NUMBER_STRING_GUARD       (14)
#define DEC_NUMBER_DOUBLE_EXTRA_UNITS ((DEC_NUMBER_DOUBLE_PRECISION - DECNUMDIGITS + DECDPUN - 1)/DECDPUN)

#include "value_thread.h"
#ifdef WIN32
#ifndef __MINGW32__
/* Copied from Heimdal: thread-specific keys; see lib/base/dll.c in Heimdal */

/*
 * This is an implementation of thread-specific storage with
 * destructors.  WIN32 doesn't quite have this.  Instead it has
 * DllMain(), an entry point in every DLL that gets called to notify the
 * DLL of thread/process "attach"/"detach" events.
 *
 * We use __thread (or __declspec(thread)) for the thread-local itself
 * and DllMain() DLL_THREAD_DETACH events to drive destruction of
 * thread-local values.
 *
 * When building in maintainer mode on non-Windows pthread systems this
 * uses a single pthread key instead to implement multiple keys.  This
 * keeps the code from rotting when modified by non-Windows developers.
 */

/* Logical array of keys that grows lock-lessly */
typedef struct tls_keys tls_keys;
struct tls_keys {
    void (**keys_dtors)(void *);    /* array of destructors         */
    size_t keys_start_idx;          /* index of first destructor    */
    size_t keys_num;
    tls_keys *keys_next;
};

/*
 * Well, not quite locklessly.  We need synchronization primitives to do
 * this locklessly.  An atomic CAS will do.
 */
static pthread_mutex_t tls_key_defs_lock = PTHREAD_MUTEX_INITIALIZER;
static tls_keys *tls_key_defs;

/* Logical array of values (per-thread; no locking needed here) */
struct tls_values {
    void **values; /* realloc()ed */
    size_t values_num;
};

#ifdef _MSC_VER
static __declspec(thread) struct nomem_handler nomem_handler;
#else
static __thread struct tls_values values;
#endif

#define DEAD_KEY ((void *)8)

static void
w32_service_thread_detach(void *unused)
{
    tls_keys *key_defs;
    void (*dtor)(void*);
    size_t i;

    pthread_mutex_lock(&tls_key_defs_lock);
    key_defs = tls_key_defs;
    pthread_mutex_unlock(&tls_key_defs_lock);

    if (key_defs == NULL)
        return;

    for (i = 0; i < values.values_num; i++) {
        assert(i >= key_defs->keys_start_idx);
        if (i >= key_defs->keys_start_idx + key_defs->keys_num) {
            pthread_mutex_lock(&tls_key_defs_lock);
            key_defs = key_defs->keys_next;
            pthread_mutex_unlock(&tls_key_defs_lock);

            assert(key_defs != NULL);
            assert(i >= key_defs->keys_start_idx);
            assert(i < key_defs->keys_start_idx + key_defs->keys_num);
        }
        dtor = key_defs->keys_dtors[i - key_defs->keys_start_idx];
        if (values.values[i] != NULL && dtor != NULL && dtor != DEAD_KEY)
            dtor(values.values[i]);
        values.values[i] = NULL;
    }
}

extern void val_tsd_dtoa_ctx_init();
extern void val_tsd_dtoa_ctx_fini();
void val_tsd_dec_ctx_fini();
void val_tsd_dec_ctx_init();

BOOL WINAPI DllMain(HINSTANCE hinstDLL,
                    DWORD fdwReason,
                    LPVOID lpvReserved)
{
    switch (fdwReason) {
    case DLL_PROCESS_ATTACH:
	/*create_pt_key();*/
	val_tsd_dtoa_ctx_init();
	val_tsd_dec_ctx_init();
	return TRUE;
    case DLL_PROCESS_DETACH:
	val_tsd_dtoa_ctx_fini();
	val_tsd_dec_ctx_fini();
	return TRUE;
    case DLL_THREAD_ATTACH: return 0;
    case DLL_THREAD_DETACH:
        w32_service_thread_detach(NULL);
        return TRUE;
    default: return TRUE;
    }
}

int
pthread_key_create(pthread_key_t *key, void (*dtor)(void *))
{
    tls_keys *key_defs, *new_key_defs;
    size_t i, k;
    int ret = ENOMEM;

    pthread_mutex_lock(&tls_key_defs_lock);
    if (tls_key_defs == NULL) {
        /* First key */
        new_key_defs = calloc(1, sizeof(*new_key_defs));
        if (new_key_defs == NULL) {
            pthread_mutex_unlock(&tls_key_defs_lock);
            return ENOMEM;
        }
        new_key_defs->keys_num = 8;
        new_key_defs->keys_dtors = calloc(new_key_defs->keys_num,
                                          sizeof(*new_key_defs->keys_dtors));
        if (new_key_defs->keys_dtors == NULL) {
            pthread_mutex_unlock(&tls_key_defs_lock);
            free(new_key_defs);
            return ENOMEM;
        }
        tls_key_defs = new_key_defs;
        new_key_defs->keys_dtors[0] = dtor;
        for (i = 1; i < new_key_defs->keys_num; i++)
            new_key_defs->keys_dtors[i] = NULL;
        pthread_mutex_unlock(&tls_key_defs_lock);
        return 0;
    }

    for (key_defs = tls_key_defs;
         key_defs != NULL;
         key_defs = key_defs->keys_next) {
        k = key_defs->keys_start_idx;
        for (i = 0; i < key_defs->keys_num; i++, k++) {
            if (key_defs->keys_dtors[i] == NULL) {
                /* Found free slot; use it */
                key_defs->keys_dtors[i] = dtor;
                *key = k;
                pthread_mutex_unlock(&tls_key_defs_lock);
                return 0;
            }
        }
        if (key_defs->keys_next != NULL)
            continue;

        /* Grow the registration array */
        /* XXX DRY */
        new_key_defs = calloc(1, sizeof(*new_key_defs));
        if (new_key_defs == NULL)
            break;

        new_key_defs->keys_dtors =
            calloc(key_defs->keys_num + key_defs->keys_num / 2,
                   sizeof(*new_key_defs->keys_dtors));
        if (new_key_defs->keys_dtors == NULL) {
            free(new_key_defs);
            break;
        }
        new_key_defs->keys_start_idx = key_defs->keys_start_idx +
            key_defs->keys_num;
        new_key_defs->keys_num = key_defs->keys_num + key_defs->keys_num / 2;
        new_key_defs->keys_dtors[i] = dtor;
        for (i = 1; i < new_key_defs->keys_num; i++)
            new_key_defs->keys_dtors[i] = NULL;
        key_defs->keys_next = new_key_defs;
        ret = 0;
        break;
    }
    pthread_mutex_unlock(&tls_key_defs_lock);
    return ret;
}

static void
key_lookup(pthread_key_t key, tls_keys **kd,
           size_t *dtor_idx, void (**dtor)(void *))
{
    tls_keys *key_defs;

    if (kd != NULL)
        *kd = NULL;
    if (dtor_idx != NULL)
        *dtor_idx = 0;
    if (dtor != NULL)
        *dtor = NULL;

    pthread_mutex_lock(&tls_key_defs_lock);
    key_defs = tls_key_defs;
    pthread_mutex_unlock(&tls_key_defs_lock);

    while (key_defs != NULL) {
        if (key >= key_defs->keys_start_idx &&
            key < key_defs->keys_start_idx + key_defs->keys_num) {
            if (kd != NULL)
                *kd = key_defs;
            if (dtor_idx != NULL)
                *dtor_idx = key - key_defs->keys_start_idx;
            if (dtor != NULL)
                *dtor = key_defs->keys_dtors[key - key_defs->keys_start_idx];
            return;
        }

        pthread_mutex_lock(&tls_key_defs_lock);
        key_defs = key_defs->keys_next;
        pthread_mutex_unlock(&tls_key_defs_lock);
        assert(key_defs != NULL);
        assert(key >= key_defs->keys_start_idx);
    }
}

int
pthread_setspecific(pthread_key_t key, void *value)
{
    void **new_values;
    size_t new_num;
    void (*dtor)(void *);
    size_t i;

    key_lookup(key, NULL, NULL, &dtor);
    if (dtor == NULL)
        return EINVAL;

    if (key >= values.values_num) {
        if (values.values_num == 0) {
            values.values = NULL;
            new_num = 8;
        } else {
            new_num = (values.values_num + values.values_num / 2);
        }
        new_values = realloc(values.values, sizeof(void *) * new_num);
        if (new_values == NULL)
            return ENOMEM;
        for (i = values.values_num; i < new_num; i++)
            new_values[i] = NULL;
        values.values = new_values;
        values.values_num = new_num;
    }

    assert(key < values.values_num);

    if (values.values[key] != NULL && dtor != NULL && dtor != DEAD_KEY)
        dtor(values.values[key]);

    values.values[key] = value;
    return 0;
}

void *
pthread_getspecific(pthread_key_t key)
{
    if (key >= values.values_num)
        return NULL;
    return values.values[key];
}
#else
#include <pthread.h>
#endif
#else
#include <pthread.h>
#endif

static pthread_key_t dec_ctx_key;
static pthread_once_t dec_ctx_once = PTHREAD_ONCE_INIT;

#define DEC_CONTEXT() tsd_dec_ctx_get(&dec_ctx_key)

// atexit finalizer to clean up the tsd dec contexts if main() exits
// without having called pthread_exit()
void val_tsd_dec_ctx_fini(void) {
  val_mem_free(pthread_getspecific(dec_ctx_key));
  pthread_setspecific(dec_ctx_key, NULL);
}

void val_tsd_dec_ctx_init(void) {
  if (pthread_key_create(&dec_ctx_key, val_mem_free) != 0) {
    fprintf(stderr, "error: cannot create thread specific key");
    abort();
  }
  atexit(val_tsd_dec_ctx_fini);
}

static decContext* tsd_dec_ctx_get(pthread_key_t *key) {
  pthread_once(&dec_ctx_once, val_tsd_dec_ctx_init); // cannot fail
  decContext *ctx = (decContext*)pthread_getspecific(*key);
  if (ctx) {
    return ctx;
  }

  ctx = malloc(sizeof(decContext));
  if (ctx) {
    if (key == &dec_ctx_key)
    {
      decContextDefault(ctx, DEC_INIT_BASE);
      // make sure (Int)D2U(rhs->exponent-lhs->exponent) does not overflow
      ctx->digits = MIN(DEC_MAX_DIGITS,
          INT32_MAX - (DECDPUN - 1) - (ctx->emax - ctx->emin - 1));
      ctx->traps = 0; /*no errors*/
    }
    if (pthread_setspecific(*key, ctx) != 0) {
      fprintf(stderr, "error: cannot store thread specific data");
      abort();
    }
  }
  return ctx;
}

typedef struct {
  val_refcnt refcnt;
  double num_double;
  char * literal_data;
  decNumber num_decimal; // must be the last field in the structure for memory management
} valp_literal_number;

typedef struct {
  decNumber number;
  decNumberUnit units[DEC_NUMBER_DOUBLE_EXTRA_UNITS];
} decNumberDoublePrecision;


static inline int valp_number_is_literal(val_t n) {
  assert(VALP_HAS_KIND(n, VAL_KIND_NUMBER));
  return VALP_HAS_FLAGS(n, VALP_FLAGS_NUMBER_LITERAL);
}

static valp_literal_number* valp_literal_number_ptr(val_t j) {
  assert(VALP_HAS_FLAGS(j, VALP_FLAGS_NUMBER_LITERAL));
  return (valp_literal_number*)j.u.ptr;
}

static decNumber* valp_dec_number_ptr(val_t j) {
  assert(VALP_HAS_FLAGS(j, VALP_FLAGS_NUMBER_LITERAL));
  return &(((valp_literal_number*)j.u.ptr)->num_decimal);
}

static valp_literal_number* valp_literal_number_alloc(unsigned literal_length) {
  /* The number of units needed is ceil(DECNUMDIGITS/DECDPUN)         */
  int units = ((literal_length+DECDPUN-1)/DECDPUN);

  valp_literal_number* n = val_mem_alloc(
    sizeof(valp_literal_number)
    + sizeof(decNumberUnit) * units
  );

  n->refcnt = VAL_REFCNT_INIT;
  n->num_double = NAN;
  n->literal_data = NULL;
  return n;
}

static val_t valp_literal_number_new(const char * literal) {
  size_t len = strlen(literal);
  if (len > DEC_MAX_DIGITS)
    return VAL_INVALID;
  valp_literal_number* n = valp_literal_number_alloc(len);

  decContext *ctx = DEC_CONTEXT();
  decContextClearStatus(ctx, DEC_Conversion_syntax);
  decNumberFromString(&n->num_decimal, literal, ctx);

  if (ctx->status & DEC_Conversion_syntax) {
    val_mem_free(n);
    return VAL_INVALID;
  }
  if (decNumberIsNaN(&n->num_decimal)) {
    // Reject NaN with payload.
    if (n->num_decimal.digits > 1 || *n->num_decimal.lsu != 0) {
      val_mem_free(n);
      return VAL_INVALID;
    }
    val_mem_free(n);
    return val_number(NAN);
  }

  val_t r = {VALP_FLAGS_NUMBER_LITERAL, 0, 0, 0, {&n->refcnt}};
  return r;
}

static double valp_literal_number_to_double(val_t j) {
  assert(VALP_HAS_FLAGS(j, VALP_FLAGS_NUMBER_LITERAL));
  decContext dblCtx;

  // init as decimal64 but change digits to allow conversion to binary64 (double)
  decContextDefault(&dblCtx, DEC_INIT_DECIMAL64);
  dblCtx.digits = DEC_NUMBER_DOUBLE_PRECISION;

  decNumber *p_dec_number = valp_dec_number_ptr(j);
  decNumberDoublePrecision dec_double;
  char literal[DEC_NUMBER_DOUBLE_PRECISION + DEC_NUMBER_STRING_GUARD + 1];

  // reduce the number to the shortest possible form
  // that fits into the 64 bit floating point representation
  decNumberReduce(&dec_double.number, p_dec_number, &dblCtx);

  decNumberToString(&dec_double.number, literal);

  char *end;
  return valp_strtod(tsd_dtoa_context_get(), literal, &end);
}

static const char* valp_literal_number_literal(val_t n) {
  assert(VALP_HAS_FLAGS(n, VALP_FLAGS_NUMBER_LITERAL));
  decNumber *pdec = valp_dec_number_ptr(n);
  valp_literal_number* plit = valp_literal_number_ptr(n);

  if (decNumberIsNaN(pdec)) {
    return "null";
  }

  if (decNumberIsInfinite(pdec)) {
    // We cannot preserve the literal data of numbers outside the limited
    // range of exponent. Since `decNumberToString` returns "Infinity"
    // (or "-Infinity"), and to reduce stack allocations as possible, we
    // normalize infinities in the callers instead of printing the maximum
    // (or minimum) double here.
    return NULL;
  }

  if (plit->literal_data == NULL) {
    int len = valp_dec_number_ptr(n)->digits + 15 /* 14 + NUL */;
    plit->literal_data = val_mem_alloc(len);

    // Preserve the actual precision as we have parsed it
    // don't do decNumberTrim(pdec);

    decNumberToString(pdec, plit->literal_data);
  }

  return plit->literal_data;
}

int val_number_has_literal(val_t n) {
  assert(VALP_HAS_KIND(n, VAL_KIND_NUMBER));
  return VALP_HAS_FLAGS(n, VALP_FLAGS_NUMBER_LITERAL);
}

const char* val_number_get_literal(val_t n) {
  assert(VALP_HAS_KIND(n, VAL_KIND_NUMBER));

  if (VALP_HAS_FLAGS(n, VALP_FLAGS_NUMBER_LITERAL)) {
    return valp_literal_number_literal(n);
  } else {
    return NULL;
  }
}

val_t val_number_with_literal(const char * literal) {
  return valp_literal_number_new(literal);
}
#endif /* USE_DECNUM */

val_t val_number(double x) {
  val_t j = {
#ifdef USE_DECNUM
    VALP_FLAGS_NUMBER_NATIVE,
#else
    VAL_KIND_NUMBER,
#endif
    0, 0, 0, {.number = x}
  };
  return j;
}

static void valp_number_free(val_t j) {
  assert(VALP_HAS_KIND(j, VAL_KIND_NUMBER));
#ifdef USE_DECNUM
  if (VALP_HAS_FLAGS(j, VALP_FLAGS_NUMBER_LITERAL) && valp_refcnt_dec(j.u.ptr)) {
    valp_literal_number* n = valp_literal_number_ptr(j);
    if (n->literal_data) {
      val_mem_free(n->literal_data);
    }
    val_mem_free(n);
  }
#endif
}

double val_number_value(val_t j) {
  assert(VALP_HAS_KIND(j, VAL_KIND_NUMBER));
#ifdef USE_DECNUM
  if (VALP_HAS_FLAGS(j, VALP_FLAGS_NUMBER_LITERAL)) {
    valp_literal_number* n = valp_literal_number_ptr(j);

    if (isnan(n->num_double)) {
      n->num_double = valp_literal_number_to_double(j);
    }

    return n->num_double;
  }
#endif
  return j.u.number;
}

int val_is_integer(val_t j){
  if (!VALP_HAS_KIND(j, VAL_KIND_NUMBER)){
    return 0;
  }

  double x = val_number_value(j);

  double ipart;
  double fpart = modf(x, &ipart);

  return fabs(fpart) < DBL_EPSILON;
}

int valp_number_is_nan(val_t n) {
  assert(VALP_HAS_KIND(n, VAL_KIND_NUMBER));

#ifdef USE_DECNUM
  if (VALP_HAS_FLAGS(n, VALP_FLAGS_NUMBER_LITERAL)) {
    decNumber *pdec = valp_dec_number_ptr(n);
    return decNumberIsNaN(pdec);
  }
#endif
  return isnan(n.u.number);
}

val_t val_number_abs(val_t n) {
  assert(VALP_HAS_KIND(n, VAL_KIND_NUMBER));

#ifdef USE_DECNUM
  if (VALP_HAS_FLAGS(n, VALP_FLAGS_NUMBER_LITERAL)) {
    valp_literal_number* m = valp_literal_number_alloc(valp_dec_number_ptr(n)->digits);

    decNumberAbs(&m->num_decimal, valp_dec_number_ptr(n), DEC_CONTEXT());
    val_t r = {VALP_FLAGS_NUMBER_LITERAL, 0, 0, 0, {&m->refcnt}};
    return r;
  }
#endif
  return val_number(fabs(val_number_value(n)));
}

val_t val_number_negate(val_t n) {
  assert(VALP_HAS_KIND(n, VAL_KIND_NUMBER));

#ifdef USE_DECNUM
  if (VALP_HAS_FLAGS(n, VALP_FLAGS_NUMBER_LITERAL)) {
    valp_literal_number* m = valp_literal_number_alloc(valp_dec_number_ptr(n)->digits);

    decNumberMinus(&m->num_decimal, valp_dec_number_ptr(n), DEC_CONTEXT());
    val_t r = {VALP_FLAGS_NUMBER_LITERAL, 0, 0, 0, {&m->refcnt}};
    return r;
  }
#endif
  return val_number(-val_number_value(n));
}

int valp_number_cmp(val_t a, val_t b) {
  assert(VALP_HAS_KIND(a, VAL_KIND_NUMBER));
  assert(VALP_HAS_KIND(b, VAL_KIND_NUMBER));

#ifdef USE_DECNUM
  if (VALP_HAS_FLAGS(a, VALP_FLAGS_NUMBER_LITERAL) && VALP_HAS_FLAGS(b, VALP_FLAGS_NUMBER_LITERAL)) {
    struct {
      decNumber number;
      decNumberUnit units[1];
    } res;

    decNumberCompare(&res.number,
                     valp_dec_number_ptr(a),
                     valp_dec_number_ptr(b),
                     DEC_CONTEXT()
                     );
    if (decNumberIsZero(&res.number)) {
      return 0;
    } else if (decNumberIsNegative(&res.number)) {
      return -1;
    } else {
      return 1;
    }
  }
#endif
  double da = val_number_value(a), db = val_number_value(b);
  if (da < db) {
    return -1;
  } else if (da == db) {
    return 0;
  } else {
    return 1;
  }
}

static int valp_number_equal(val_t a, val_t b) {
  return valp_number_cmp(a, b) == 0;
}

/*
 * Arrays (internal helpers)
 */

#define ARRAY_SIZE_ROUND_UP(n) (((n)*3)/2)
#define VALP_FLAGS_ARRAY   VALP_MAKE_FLAGS(VAL_KIND_ARRAY, VALP_PAYLOAD_ALLOCATED)

static int imax(int a, int b) {
  if (a>b) return a;
  else return b;
}

//FIXME signed vs unsigned
typedef struct {
  val_refcnt refcnt;
  int length, alloc_length;
  val_t elements[];
} valp_array;

static valp_array* valp_array_ptr(val_t a) {
  assert(VALP_HAS_KIND(a, VAL_KIND_ARRAY));
  return (valp_array*)a.u.ptr;
}

static valp_array* valp_array_alloc(unsigned size) {
  valp_array* a = val_mem_alloc(sizeof(valp_array) + sizeof(val_t) * size);
  a->refcnt.count = 1;
  a->length = 0;
  a->alloc_length = size;
  return a;
}

static val_t valp_array_new(unsigned size) {
  val_t r = {VALP_FLAGS_ARRAY, 0, 0, 0, {&valp_array_alloc(size)->refcnt}};
  return r;
}

static int valp_array_length(val_t a) {
  assert(VALP_HAS_KIND(a, VAL_KIND_ARRAY));
  return a.size;
}

static int valp_array_offset(val_t a) {
  assert(VALP_HAS_KIND(a, VAL_KIND_ARRAY));
  return a.offset;
}

static val_t* valp_array_read(val_t a, int i) {
  assert(VALP_HAS_KIND(a, VAL_KIND_ARRAY));
  if (i >= 0 && i < valp_array_length(a)) {
    valp_array* array = valp_array_ptr(a);
    assert(i + valp_array_offset(a) < array->length);
    return &array->elements[i + valp_array_offset(a)];
  } else {
    return 0;
  }
}

static val_t* valp_array_write(val_t* a, int i) {
  assert(i >= 0);
  valp_array* array = valp_array_ptr(*a);

  int pos = i + valp_array_offset(*a);
  if (pos < array->alloc_length && valp_refcnt_unshared(a->u.ptr)) {
    // use existing array space
    for (int j = array->length; j <= pos; j++) {
      array->elements[j] = VAL_NULL;
    }
    array->length = imax(pos + 1, array->length);
    a->size = imax(i + 1, a->size);
    return &array->elements[pos];
  } else {
    // allocate a new array
    int new_length = imax(i + 1, valp_array_length(*a));
    valp_array* new_array = valp_array_alloc(ARRAY_SIZE_ROUND_UP(new_length));
    int j;
    for (j = 0; j < valp_array_length(*a); j++) {
      new_array->elements[j] =
        val_copy(array->elements[j + valp_array_offset(*a)]);
    }
    for (; j < new_length; j++) {
      new_array->elements[j] = VAL_NULL;
    }
    new_array->length = new_length;
    val_free(*a);
    val_t new_jv = {VALP_FLAGS_ARRAY, 0, 0, new_length, {&new_array->refcnt}};
    *a = new_jv;
    return &new_array->elements[i];
  }
}

static int valp_equal(val_t a, val_t b, int depth);

static int valp_array_equal(val_t a, val_t b, int depth) {
  if (valp_array_length(a) != valp_array_length(b))
    return 0;
  if (valp_array_ptr(a) == valp_array_ptr(b) &&
      valp_array_offset(a) == valp_array_offset(b))
    return 1;
  for (int i=0; i<valp_array_length(a); i++) {
    int r = valp_equal(val_copy(*valp_array_read(a, i)),
                      val_copy(*valp_array_read(b, i)),
                      depth);
    if (r <= 0)
      return r;
  }
  return 1;
}

static void valp_clamp_slice_params(int len, int *pstart, int *pend)
{
  if (*pstart < 0) *pstart = len + *pstart;
  if (*pend < 0) *pend = len + *pend;

  if (*pstart < 0) *pstart = 0;
  if (*pstart > len) *pstart = len;
  if (*pend > len) *pend = len;
  if (*pend < *pstart) *pend = *pstart;
}


static int valp_contains(val_t a, val_t b, int depth);

static int valp_array_contains(val_t a, val_t b, int depth) {
  int r = 1;
  val_array_foreach(b, bi, belem) {
    int ri = 0;
    val_array_foreach(a, ai, aelem) {
      ri = valp_contains(aelem, val_copy(belem), depth);
      if (ri) break;
    }
    val_free(belem);
    if (ri <= 0) {
      r = ri;
      break;
    }
  }
  return r;
}


/*
 * Public
 */

static val_t valp_array_slice(val_t a, int start, int end) {
  assert(VALP_HAS_KIND(a, VAL_KIND_ARRAY));
  int len = valp_array_length(a);
  valp_clamp_slice_params(len, &start, &end);
  assert(0 <= start && start <= end && end <= len);

  // FIXME: maybe slice should reallocate if the slice is small enough
  if (start == end) {
    val_free(a);
    return val_array();
  }

  if (a.offset + start >= 1 << (sizeof(a.offset) * CHAR_BIT)) {
    val_t r = val_array_sized(end - start);
    for (int i = start; i < end; i++)
      r = val_array_append(r, val_array_get(val_copy(a), i));
    val_free(a);
    return r;
  } else {
    a.offset += start;
    a.size = end - start;
    return a;
  }
}

/*
 * Arrays (public interface)
 */

val_t val_array_sized(int n) {
  return valp_array_new(n);
}

val_t val_array(void) {
  return val_array_sized(16);
}

int val_array_length(val_t j) {
  assert(VALP_HAS_KIND(j, VAL_KIND_ARRAY));
  int len = valp_array_length(j);
  val_free(j);
  return len;
}

val_t val_array_get(val_t j, int idx) {
  assert(VALP_HAS_KIND(j, VAL_KIND_ARRAY));
  val_t* slot = valp_array_read(j, idx);
  val_t val;
  if (slot) {
    val = val_copy(*slot);
  } else {
    val = val_invalid();
  }
  val_free(j);
  return val;
}

val_t val_array_set(val_t j, int idx, val_t val) {
  assert(VALP_HAS_KIND(j, VAL_KIND_ARRAY));

  if (idx < 0)
    idx = valp_array_length(j) + idx;
  if (idx < 0) {
    val_free(j);
    val_free(val);
    return val_invalid_with_msg(val_string("Out of bounds negative array index"));
  }
  if (idx > (INT_MAX >> 2) - valp_array_offset(j)) {
    val_free(j);
    val_free(val);
    return val_invalid_with_msg(val_string("Array index too large"));
  }
  // copy/free of val,j coalesced
  val_t* slot = valp_array_write(&j, idx);
  val_free(*slot);
  *slot = val;
  return j;
}

val_t val_array_append(val_t j, val_t val) {
  // copy/free of val,j coalesced
  return val_array_set(j, val_array_length(val_copy(j)), val);
}

val_t val_array_concat(val_t a, val_t b) {
  assert(VALP_HAS_KIND(a, VAL_KIND_ARRAY));
  assert(VALP_HAS_KIND(b, VAL_KIND_ARRAY));

  // FIXME: could be faster
  val_array_foreach(b, i, elem) {
    a = val_array_append(a, elem);
    if (!val_is_valid(a)) break;
  }
  val_free(b);
  return a;
}

val_t val_array_slice(val_t a, int start, int end) {
  assert(VALP_HAS_KIND(a, VAL_KIND_ARRAY));
  // copy/free of a coalesced
  return valp_array_slice(a, start, end);
}

val_t val_array_indexes(val_t a, val_t b) {
  val_t res = val_array();
  int idx = -1;
  int alen = val_array_length(val_copy(a));
  for (int ai = 0; ai < alen; ++ai) {
    val_array_foreach(b, bi, belem) {
      int equal = val_equal(val_array_get(val_copy(a), ai + bi), belem);
      if (equal < 0) {
        val_free(res);
        val_free(a);
        val_free(b);
        return val_invalid_with_msg(val_string("Equality check too deep"));
      }
      if (!equal)
        idx = -1;
      else if (bi == 0 && idx == -1)
        idx = ai;
    }
    if (idx > -1)
      res = val_array_append(res, val_number(idx));
    idx = -1;
  }
  val_free(a);
  val_free(b);
  return res;
}

/*
 * Strings (internal helpers)
 */

#define VALP_FLAGS_STRING  VALP_MAKE_FLAGS(VAL_KIND_STRING, VALP_PAYLOAD_ALLOCATED)

typedef struct {
  val_refcnt refcnt;
  uint32_t hash;
  // high 31 bits are length, low bit is a flag
  // indicating whether hash has been computed.
  uint32_t length_hashed;
  uint32_t alloc_length;
  char data[];
} valp_string;

static valp_string* valp_string_ptr(val_t a) {
  assert(VALP_HAS_KIND(a, VAL_KIND_STRING));
  return (valp_string*)a.u.ptr;
}

static valp_string* valp_string_alloc(uint32_t size) {
  valp_string* s = val_mem_alloc(sizeof(valp_string) + size + 1);
  s->refcnt.count = 1;
  s->alloc_length = size;
  return s;
}

/* Copy a UTF8 string, replacing all badly encoded points with U+FFFD */
static val_t valp_string_copy_replace_bad(const char* data, uint32_t length) {
  const char* end = data + length;
  const char* i = data;

  // worst case: all bad bytes, each becomes a 3-byte U+FFFD
  uint64_t maxlength = (uint64_t)length * 3 + 1;
  if (maxlength >= INT_MAX) {
    return val_invalid_with_msg(val_string("String too long"));
  }

  valp_string* s = valp_string_alloc(maxlength);
  char* out = s->data;
  int c = 0;

  while ((i = valp_utf8_next(i, end, &c))) {
    if (c == -1) {
      continue;
    }
    out += valp_utf8_encode(c, out);
    assert(out < s->data + maxlength);
  }
  length = out - s->data;
  s->data[length] = 0;
  s->length_hashed = length << 1;
  val_t r = {VALP_FLAGS_STRING, 0, 0, 0, {&s->refcnt}};
  return r;
}

/* Assumes valid UTF8 */
static val_t valp_string_new(const char* data, uint32_t length) {
  valp_string* s = valp_string_alloc(length);
  s->length_hashed = length << 1;
  if (data != NULL)
    memcpy(s->data, data, length);
  s->data[length] = 0;
  val_t r = {VALP_FLAGS_STRING, 0, 0, 0, {&s->refcnt}};
  return r;
}

static val_t valp_string_empty_new(uint32_t length) {
  valp_string* s = valp_string_alloc(length);
  s->length_hashed = 0;
  memset(s->data, 0, length);
  s->data[length] = 0;
  val_t r = {VALP_FLAGS_STRING, 0, 0, 0, {&s->refcnt}};
  return r;
}


static void valp_string_free(val_t js) {
  valp_string* s = valp_string_ptr(js);
  if (valp_refcnt_dec(&s->refcnt)) {
    val_mem_free(s);
  }
}

static uint32_t valp_string_length(valp_string* s) {
  return s->length_hashed >> 1;
}

static uint32_t valp_string_remaining_space(valp_string* s) {
  assert(s->alloc_length >= valp_string_length(s));
  uint32_t r = s->alloc_length - valp_string_length(s);
  return r;
}

static val_t valp_string_append(val_t string, const char* data, uint32_t len) {
  valp_string* s = valp_string_ptr(string);
  uint32_t currlen = valp_string_length(s);
  if ((uint64_t)currlen + len >= INT_MAX - sizeof(valp_string) / 2) {
    val_free(string);
    return val_invalid_with_msg(val_string("String too long"));
  }

  if (valp_refcnt_unshared(string.u.ptr) &&
      valp_string_remaining_space(s) >= len) {
    // the next string fits at the end of a
    memcpy(s->data + currlen, data, len);
    s->data[currlen + len] = 0;
    s->length_hashed = (currlen + len) << 1;
    return string;
  } else {
    // allocate a bigger buffer and copy
    uint32_t allocsz = (currlen + len) * 2;
    if (allocsz < 32) allocsz = 32;
    valp_string* news = valp_string_alloc(allocsz);
    news->length_hashed = (currlen + len) << 1;
    memcpy(news->data, s->data, currlen);
    memcpy(news->data + currlen, data, len);
    news->data[currlen + len] = 0;
    valp_string_free(string);
    val_t r = {VALP_FLAGS_STRING, 0, 0, 0, {&news->refcnt}};
    return r;
  }
}

static uint32_t hash_seed;

static void valp_hash_seed_init(void) {
  uint32_t seed;
#if defined(HAVE_ARC4RANDOM)
  seed = arc4random();
#elif defined(HAVE_GETENTROPY)
  if (getentropy(&seed, sizeof(seed)) != 0)
    seed = (uint32_t)getpid() ^ (uint32_t)time(NULL);
#else
  int fd = open("/dev/urandom", O_RDONLY);
  if (fd >= 0) {
    if (read(fd, &seed, sizeof(seed)) != 4)
      seed = (uint32_t)getpid() ^ (uint32_t)time(NULL);
    close(fd);
  } else {
    seed = (uint32_t)getpid() ^ (uint32_t)time(NULL);
  }
#endif
  hash_seed = seed;
}

static uint32_t valp_hash_seed(void) {
  if (!hash_seed)
    valp_hash_seed_init();
  return hash_seed;
}

static uint32_t rotl32 (uint32_t x, int8_t r){
  return (x << r) | (x >> (32 - r));
}

static uint32_t valp_string_hash(val_t jstr) {
  valp_string* str = valp_string_ptr(jstr);
  if (str->length_hashed & 1)
    return str->hash;

  /* The following is based on MurmurHash3.
     MurmurHash3 was written by Austin Appleby, and is placed
     in the public domain. */

  const uint8_t* data = (const uint8_t*)str->data;
  int len = (int)valp_string_length(str);
  const int nblocks = len / 4;

  uint32_t h1 = valp_hash_seed();

  const uint32_t c1 = 0xcc9e2d51;
  const uint32_t c2 = 0x1b873593;
  const uint32_t* blocks = (const uint32_t *)(data + nblocks*4);

  for(int i = -nblocks; i; i++) {
    uint32_t k1 = blocks[i]; //FIXME: endianness/alignment

    k1 *= c1;
    k1 = rotl32(k1,15);
    k1 *= c2;

    h1 ^= k1;
    h1 = rotl32(h1,13);
    h1 = h1*5+0xe6546b64;
  }

  const uint8_t* tail = (const uint8_t*)(data + nblocks*4);

  uint32_t k1 = 0;

  switch(len & 3) {
  case 3: k1 ^= tail[2] << 16;
          QE_FALLTHROUGH;
  case 2: k1 ^= tail[1] << 8;
          QE_FALLTHROUGH;
  case 1: k1 ^= tail[0];
          k1 *= c1; k1 = rotl32(k1,15); k1 *= c2; h1 ^= k1;
  }

  h1 ^= len;

  h1 ^= h1 >> 16;
  h1 *= 0x85ebca6b;
  h1 ^= h1 >> 13;
  h1 *= 0xc2b2ae35;
  h1 ^= h1 >> 16;

  str->length_hashed |= 1;
  str->hash = h1;

  return h1;
}


static int valp_string_equal(val_t a, val_t b) {
  assert(VALP_HAS_KIND(a, VAL_KIND_STRING));
  assert(VALP_HAS_KIND(b, VAL_KIND_STRING));
  valp_string* stra = valp_string_ptr(a);
  valp_string* strb = valp_string_ptr(b);
  if (valp_string_length(stra) != valp_string_length(strb)) return 0;
  return memcmp(stra->data, strb->data, valp_string_length(stra)) == 0;
}

/*
 * Strings (public API)
 */

val_t val_string_sized(const char* str, int len) {
  return
    valp_utf8_is_valid(str, str+len) ?
    valp_string_new(str, len) :
    valp_string_copy_replace_bad(str, len);
}

val_t val_string_empty(int len) {
  return valp_string_empty_new(len);
}

val_t val_string(const char* str) {
  return val_string_sized(str, strlen(str));
}

int val_string_length_bytes(val_t j) {
  assert(VALP_HAS_KIND(j, VAL_KIND_STRING));
  int r = valp_string_length(valp_string_ptr(j));
  val_free(j);
  return r;
}

int val_string_length_codepoints(val_t j) {
  assert(VALP_HAS_KIND(j, VAL_KIND_STRING));
  const char* i = val_string_value(j);
  const char* end = i + val_string_length_bytes(val_copy(j));
  int c = 0, len = 0;
  while ((i = valp_utf8_next(i, end, &c))) len++;
  val_free(j);
  return len;
}


val_t val_string_indexes(val_t j, val_t k) {
  assert(VALP_HAS_KIND(j, VAL_KIND_STRING));
  assert(VALP_HAS_KIND(k, VAL_KIND_STRING));
  const char *jstr = val_string_value(j);
  const char *idxstr = val_string_value(k);
  const char *p, *lp;
  int jlen = val_string_length_bytes(val_copy(j));
  int idxlen = val_string_length_bytes(val_copy(k));
  val_t a = val_array();

  if (idxlen != 0) {
    int n = 0;
    p = lp = jstr;
    while ((p = _jq_memmem(p, (jstr + jlen) - p, idxstr, idxlen)) != NULL) {
      while (lp < p) {
        lp += valp_utf8_decode_length(*lp);
        n++;
      }

      a = val_array_append(a, val_number(n));
      if (!val_is_valid(a)) break;
      p++;
    }
  }
  val_free(j);
  val_free(k);
  return a;
}

val_t val_string_repeat(val_t j, int n) {
  assert(VALP_HAS_KIND(j, VAL_KIND_STRING));
  if (n < 0) {
    val_free(j);
    return val_null();
  }
  int len = val_string_length_bytes(val_copy(j));
  int64_t res_len = (int64_t)len * n;
  if ((uint64_t)res_len >= INT_MAX - sizeof(valp_string) / 2) {
    val_free(j);
    return val_invalid_with_msg(val_string("Repeat string result too long"));
  }
  if (res_len == 0) {
    val_free(j);
    return val_string("");
  }
  val_t res = val_string_empty(res_len);
  res = valp_string_append(res, val_string_value(j), len);
  for (int curr = len, grow; curr < res_len; curr += grow) {
    grow = MIN(res_len - curr, curr);
    res = valp_string_append(res, val_string_value(res), grow);
  }
  val_free(j);
  return res;
}

val_t val_string_split(val_t j, val_t sep) {
  assert(VALP_HAS_KIND(j, VAL_KIND_STRING));
  assert(VALP_HAS_KIND(sep, VAL_KIND_STRING));
  const char *jstr = val_string_value(j);
  const char *jend = jstr + val_string_length_bytes(val_copy(j));
  const char *sepstr = val_string_value(sep);
  const char *p, *s;
  int seplen = val_string_length_bytes(val_copy(sep));
  val_t a = val_array();

  assert(val_get_refcnt(a) == 1);

  if (seplen == 0) {
    int c;
    while ((jstr = valp_utf8_next(jstr, jend, &c))) {
      a = val_array_append(a, val_string_append_codepoint(val_string(""), c));
      if (!val_is_valid(a)) break;
    }
  } else {
    for (p = jstr; p < jend; p = s + seplen) {
      s = _jq_memmem(p, jend - p, sepstr, seplen);
      if (s == NULL)
        s = jend;
      a = val_array_append(a, val_string_sized(p, s - p));
      if (!val_is_valid(a)) break;
      // Add an empty string to denote that j ends on a sep
      if (s + seplen == jend && seplen != 0)
        a = val_array_append(a, val_string(""));
    }
  }
  val_free(j);
  val_free(sep);
  return a;
}

val_t val_string_explode(val_t j) {
  assert(VALP_HAS_KIND(j, VAL_KIND_STRING));
  const char* i = val_string_value(j);
  int len = val_string_length_bytes(val_copy(j));
  const char* end = i + len;
  val_t a = val_array_sized(len);
  int c;
  while ((i = valp_utf8_next(i, end, &c))) {
    a = val_array_append(a, val_number(c));
    if (!val_is_valid(a)) break;
  }
  val_free(j);
  return a;
}

val_t val_string_implode(val_t j) {
  assert(VALP_HAS_KIND(j, VAL_KIND_ARRAY));
  int len = val_array_length(val_copy(j));
  val_t s = val_string_empty(len);
  int i;

  assert(len >= 0);

  for (i = 0; i < len; i++) {
    val_t n = val_array_get(val_copy(j), i);
    assert(VALP_HAS_KIND(n, VAL_KIND_NUMBER));
    int nv = val_number_value(n);
    val_free(n);
    // outside codepoint range or in utf16 surrogate pair range
    if (nv < 0 || nv > 0x10FFFF || (nv >= 0xD800 && nv <= 0xDFFF))
      nv = 0xFFFD; // U+FFFD REPLACEMENT CHARACTER
    s = val_string_append_codepoint(s, nv);
    if (!val_is_valid(s)) break;
  }

  val_free(j);
  return s;
}

unsigned long val_string_hash(val_t j) {
  assert(VALP_HAS_KIND(j, VAL_KIND_STRING));
  uint32_t hash = valp_string_hash(j);
  val_free(j);
  return hash;
}

const char* val_string_value(val_t j) {
  assert(VALP_HAS_KIND(j, VAL_KIND_STRING));
  return valp_string_ptr(j)->data;
}

val_t val_string_slice(val_t j, int start, int end) {
  assert(VALP_HAS_KIND(j, VAL_KIND_STRING));
  const char *s = val_string_value(j);
  int len = val_string_length_bytes(val_copy(j));
  int i;
  const char *p, *e;
  int c;
  val_t res;

  valp_clamp_slice_params(len, &start, &end);
  assert(0 <= start && start <= end && end <= len);

  /* Look for byte offset corresponding to start codepoints */
  for (p = s, i = 0; i < start; i++) {
    p = valp_utf8_next(p, s + len, &c);
    if (p == NULL) {
      val_free(j);
      return val_string_empty(16);
    }
    if (c == -1) {
      val_free(j);
      return val_invalid_with_msg(val_string("Invalid UTF-8 string"));
    }
  }
  /* Look for byte offset corresponding to end codepoints */
  for (e = p; e != NULL && i < end; i++) {
    e = valp_utf8_next(e, s + len, &c);
    if (e == NULL) {
      e = s + len;
      break;
    }
    if (c == -1) {
      val_free(j);
      return val_invalid_with_msg(val_string("Invalid UTF-8 string"));
    }
  }

  /*
   * NOTE: Ideally we should do here what valp_array_slice() does instead
   * of allocating a new string as we do!  However, we assume NUL-
   * terminated strings all over, and in the val_t API, so for now we waste
   * memory like a drunken navy programmer.  There's probably nothing we
   * can do about it.
   */
  res = val_string_sized(p, e - p);
  val_free(j);
  return res;
}

val_t val_string_concat(val_t a, val_t b) {
  a = valp_string_append(a, val_string_value(b),
                        valp_string_length(valp_string_ptr(b)));
  val_free(b);
  return a;
}

val_t val_string_append_buf(val_t a, const char* buf, int len) {
  if (valp_utf8_is_valid(buf, buf+len)) {
    a = valp_string_append(a, buf, len);
  } else {
    val_t b = valp_string_copy_replace_bad(buf, len);
    a = val_string_concat(a, b);
  }
  return a;
}

val_t val_string_append_codepoint(val_t a, uint32_t c) {
  char buf[5];
  int len = valp_utf8_encode(c, buf);
  a = valp_string_append(a, buf, len);
  return a;
}

val_t val_string_append_str(val_t a, const char* str) {
  return val_string_append_buf(a, str, strlen(str));
}

val_t val_string_vfmt(const char* fmt, va_list ap) {
  int size = 1024;
  while (1) {
    char* buf = val_mem_alloc(size);
    va_list ap2;
    va_copy(ap2, ap);
    int n = vsnprintf(buf, size, fmt, ap2);
    va_end(ap2);
    /*
     * NOTE: here we support old vsnprintf()s that return -1 because the
     * buffer is too small.
     */
    if (n >= 0 && n < size) {
      val_t ret = val_string_sized(buf, n);
      val_mem_free(buf);
      return ret;
    } else {
      val_mem_free(buf);
      size = (n > 0) ? /* standard */ (n * 2) : /* not standard */ (size * 2);
    }
  }
}

val_t val_string_fmt(const char* fmt, ...) {
  va_list args;
  va_start(args, fmt);
  val_t res = val_string_vfmt(fmt, args);
  va_end(args);
  return res;
}

/*
 * Objects (internal helpers)
 */

#define VALP_FLAGS_OBJECT  VALP_MAKE_FLAGS(VAL_KIND_OBJECT, VALP_PAYLOAD_ALLOCATED)

struct object_slot {
  int next; /* next slot with same hash, for collisions */
  uint32_t hash;
  val_t string;
  val_t value;
};

typedef struct {
  val_refcnt refcnt;
  int next_free;
  struct object_slot elements[];
} valp_object;


/* warning: nontrivial justification of alignment */
static val_t valp_object_new(int size) {
  // Allocates an object of (size) slots and (size*2) hash buckets.

  // size must be a power of two
  assert(size > 0 && (size & (size - 1)) == 0);

  valp_object* obj = val_mem_alloc(sizeof(valp_object) +
                                 sizeof(struct object_slot) * size +
                                 sizeof(int) * (size * 2));
  obj->refcnt.count = 1;
  for (int i=0; i<size; i++) {
    obj->elements[i].next = i - 1;
    obj->elements[i].string = VAL_NULL;
    obj->elements[i].hash = 0;
    obj->elements[i].value = VAL_NULL;
  }
  obj->next_free = 0;
  int* hashbuckets = (int*)(&obj->elements[size]);
  for (int i=0; i<size*2; i++) {
    hashbuckets[i] = -1;
  }
  val_t r = {VALP_FLAGS_OBJECT, 0, 0, size, {&obj->refcnt}};
  return r;
}

static valp_object* valp_object_ptr(val_t o) {
  assert(VALP_HAS_KIND(o, VAL_KIND_OBJECT));
  return (valp_object*)o.u.ptr;
}

static uint32_t valp_object_mask(val_t o) {
  assert(VALP_HAS_KIND(o, VAL_KIND_OBJECT));
  return (o.size * 2) - 1;
}

static int valp_object_size(val_t o) {
  assert(VALP_HAS_KIND(o, VAL_KIND_OBJECT));
  return o.size;
}

static int* valp_object_buckets(val_t o) {
  return (int*)(&valp_object_ptr(o)->elements[o.size]);
}

static int* valp_object_find_bucket(val_t object, val_t key) {
  return valp_object_buckets(object) + (valp_object_mask(object) & valp_string_hash(key));
}

static struct object_slot* valp_object_get_slot(val_t object, int slot) {
  assert(slot == -1 || (slot >= 0 && slot < valp_object_size(object)));
  if (slot == -1) return 0;
  else return &valp_object_ptr(object)->elements[slot];
}

static struct object_slot* valp_object_next_slot(val_t object, struct object_slot* slot) {
  return valp_object_get_slot(object, slot->next);
}

static struct object_slot* valp_object_find_slot(val_t object, val_t keystr, int* bucket) {
  uint32_t hash = valp_string_hash(keystr);
  for (struct object_slot* curr = valp_object_get_slot(object, *bucket);
       curr;
       curr = valp_object_next_slot(object, curr)) {
    if (curr->hash == hash && valp_string_equal(keystr, curr->string)) {
      return curr;
    }
  }
  return 0;
}

static struct object_slot* valp_object_add_slot(val_t object, val_t key, int* bucket) {
  valp_object* o = valp_object_ptr(object);
  int newslot_idx = o->next_free;
  if (newslot_idx == valp_object_size(object)) return 0;
  struct object_slot* newslot = valp_object_get_slot(object, newslot_idx);
  o->next_free++;
  newslot->next = *bucket;
  *bucket = newslot_idx;
  newslot->hash = valp_string_hash(key);
  newslot->string = key;
  return newslot;
}

static val_t* valp_object_read(val_t object, val_t key) {
  assert(VALP_HAS_KIND(key, VAL_KIND_STRING));
  int* bucket = valp_object_find_bucket(object, key);
  struct object_slot* slot = valp_object_find_slot(object, key, bucket);
  if (slot == 0) return 0;
  else return &slot->value;
}

static int valp_object_rehash(val_t *objectp) {
  val_t object = *objectp;
  assert(VALP_HAS_KIND(object, VAL_KIND_OBJECT));
  assert(valp_refcnt_unshared(object.u.ptr));
  int size = valp_object_size(object);
  if (size > INT_MAX >> 2)
    return 0;
  val_t new_object = valp_object_new(size * 2);
  for (int i=0; i<size; i++) {
    struct object_slot* slot = valp_object_get_slot(object, i);
    if (val_get_kind(slot->string) == VAL_KIND_NULL) continue;
    int* new_bucket = valp_object_find_bucket(new_object, slot->string);
    assert(!valp_object_find_slot(new_object, slot->string, new_bucket));
    struct object_slot* new_slot = valp_object_add_slot(new_object, slot->string, new_bucket);
    assert(new_slot);
    new_slot->value = slot->value;
  }
  // references are transported, just drop the old table
  val_mem_free(valp_object_ptr(object));
  *objectp = new_object;
  return 1;
}

static val_t valp_object_unshare(val_t object) {
  assert(VALP_HAS_KIND(object, VAL_KIND_OBJECT));
  if (valp_refcnt_unshared(object.u.ptr))
    return object;

  val_t new_object = valp_object_new(valp_object_size(object));
  valp_object_ptr(new_object)->next_free = valp_object_ptr(object)->next_free;
  for (int i=0; i<valp_object_size(new_object); i++) {
    struct object_slot* old_slot = valp_object_get_slot(object, i);
    struct object_slot* new_slot = valp_object_get_slot(new_object, i);
    *new_slot = *old_slot;
    if (val_get_kind(old_slot->string) != VAL_KIND_NULL) {
      new_slot->string = val_copy(old_slot->string);
      new_slot->value = val_copy(old_slot->value);
    }
  }

  int* old_buckets = valp_object_buckets(object);
  int* new_buckets = valp_object_buckets(new_object);
  memcpy(new_buckets, old_buckets, sizeof(int) * valp_object_size(new_object)*2);

  val_free(object);
  assert(valp_refcnt_unshared(new_object.u.ptr));
  return new_object;
}

static int valp_object_write(val_t* object, val_t key, val_t **valpp) {
  *object = valp_object_unshare(*object);
  int* bucket = valp_object_find_bucket(*object, key);
  struct object_slot* slot = valp_object_find_slot(*object, key, bucket);
  if (slot) {
    // already has the key
    valp_string_free(key);
    *valpp = &slot->value;
    return 1;
  }
  slot = valp_object_add_slot(*object, key, bucket);
  if (slot) {
    slot->value = val_invalid();
  } else {
    if (!valp_object_rehash(object)) {
      valp_string_free(key);
      *valpp = NULL;
      return 0;
    }
    bucket = valp_object_find_bucket(*object, key);
    assert(!valp_object_find_slot(*object, key, bucket));
    slot = valp_object_add_slot(*object, key, bucket);
    assert(slot);
    slot->value = val_invalid();
  }
  *valpp = &slot->value;
  return 1;
}

static int valp_object_delete(val_t* object, val_t key) {
  assert(VALP_HAS_KIND(key, VAL_KIND_STRING));
  *object = valp_object_unshare(*object);
  int* bucket = valp_object_find_bucket(*object, key);
  int* prev_ptr = bucket;
  uint32_t hash = valp_string_hash(key);
  for (struct object_slot* curr = valp_object_get_slot(*object, *bucket);
       curr;
       curr = valp_object_next_slot(*object, curr)) {
    if (hash == curr->hash && valp_string_equal(key, curr->string)) {
      *prev_ptr = curr->next;
      valp_string_free(curr->string);
      curr->string = VAL_NULL;
      val_free(curr->value);
      return 1;
    }
    prev_ptr = &curr->next;
  }
  return 0;
}

static int valp_object_length(val_t object) {
  int n = 0;
  for (int i=0; i<valp_object_size(object); i++) {
    struct object_slot* slot = valp_object_get_slot(object, i);
    if (val_get_kind(slot->string) != VAL_KIND_NULL) n++;
  }
  return n;
}

static int valp_object_equal(val_t o1, val_t o2, int depth) {
  int len2 = valp_object_length(o2);
  int len1 = 0;
  for (int i=0; i<valp_object_size(o1); i++) {
    struct object_slot* slot = valp_object_get_slot(o1, i);
    if (val_get_kind(slot->string) == VAL_KIND_NULL) continue;
    val_t* slot2 = valp_object_read(o2, slot->string);
    if (!slot2) return 0;
    // FIXME: do less refcounting here
    int r = valp_equal(val_copy(slot->value), val_copy(*slot2), depth);
    if (r <= 0) return r;
    len1++;
  }
  return len1 == len2;
}

static int valp_object_contains(val_t a, val_t b, int depth) {
  assert(VALP_HAS_KIND(a, VAL_KIND_OBJECT));
  assert(VALP_HAS_KIND(b, VAL_KIND_OBJECT));
  int r = 1;

  val_object_foreach(b, key, b_val) {
    val_t a_val = val_object_get(val_copy(a), key);

    r = valp_contains(a_val, b_val, depth);

    if (r <= 0) break;
  }
  return r;
}

/*
 * Objects (public interface)
 */
#define DEFAULT_OBJECT_SIZE 8
val_t val_object(void) {
  return valp_object_new(8);
}

val_t val_object_get(val_t object, val_t key) {
  assert(VALP_HAS_KIND(object, VAL_KIND_OBJECT));
  assert(VALP_HAS_KIND(key, VAL_KIND_STRING));
  val_t* slot = valp_object_read(object, key);
  val_t val;
  if (slot) {
    val = val_copy(*slot);
  } else {
    val = val_invalid();
  }
  val_free(object);
  val_free(key);
  return val;
}

int val_object_has(val_t object, val_t key) {
  assert(VALP_HAS_KIND(object, VAL_KIND_OBJECT));
  assert(VALP_HAS_KIND(key, VAL_KIND_STRING));
  val_t* slot = valp_object_read(object, key);
  int res = slot ? 1 : 0;
  val_free(object);
  val_free(key);
  return res;
}

val_t val_object_set(val_t object, val_t key, val_t value) {
  assert(VALP_HAS_KIND(object, VAL_KIND_OBJECT));
  assert(VALP_HAS_KIND(key, VAL_KIND_STRING));
  // copy/free of object, key, value coalesced
  val_t* slot;
  if (!valp_object_write(&object, key, &slot)) {
    val_free(object);
    val_free(value);
    return val_invalid_with_msg(val_string("Object too big"));
  }
  val_free(*slot);
  *slot = value;
  return object;
}

val_t val_object_delete(val_t object, val_t key) {
  assert(VALP_HAS_KIND(object, VAL_KIND_OBJECT));
  assert(VALP_HAS_KIND(key, VAL_KIND_STRING));
  valp_object_delete(&object, key);
  val_free(key);
  return object;
}

int val_object_length(val_t object) {
  assert(VALP_HAS_KIND(object, VAL_KIND_OBJECT));
  int n = valp_object_length(object);
  val_free(object);
  return n;
}

val_t val_object_merge(val_t a, val_t b) {
  assert(VALP_HAS_KIND(a, VAL_KIND_OBJECT));
  val_object_foreach(b, k, v) {
    a = val_object_set(a, k, v);
    if (!val_is_valid(a)) break;
  }
  val_free(b);
  return a;
}

#ifndef MAX_OBJECT_MERGE_DEPTH
#define MAX_OBJECT_MERGE_DEPTH (10000)
#endif

static val_t valp_object_merge_recursive(val_t a, val_t b, int depth) {
  assert(VALP_HAS_KIND(a, VAL_KIND_OBJECT));
  assert(VALP_HAS_KIND(b, VAL_KIND_OBJECT));

  if (depth > MAX_OBJECT_MERGE_DEPTH) {
    val_free(a);
    val_free(b);
    return val_invalid_with_msg(val_string("Object merge too deep"));
  }

  val_object_foreach(b, k, v) {
    val_t elem = val_object_get(val_copy(a), val_copy(k));
    if (val_is_valid(elem) &&
        VALP_HAS_KIND(elem, VAL_KIND_OBJECT) &&
        VALP_HAS_KIND(v, VAL_KIND_OBJECT)) {
      val_t merged = valp_object_merge_recursive(elem, v, depth);
      if (!val_is_valid(merged)) {
        val_free(k);
        val_free(a);
        val_free(b);
        return merged;
      }
      a = val_object_set(a, k, merged);
    } else {
      val_free(elem);
      a = val_object_set(a, k, v);
    }
    if (!val_is_valid(a)) break;
  }
  val_free(b);
  return a;
}

val_t val_object_merge_recursive(val_t a, val_t b) {
  return valp_object_merge_recursive(a, b, 0);
}

/*
 * Object iteration (internal helpers)
 */

enum { ITER_FINISHED = -2 };

int val_object_iter_valid(val_t object, int i) {
  return i != ITER_FINISHED;
}

int val_object_iter(val_t object) {
  assert(VALP_HAS_KIND(object, VAL_KIND_OBJECT));
  return val_object_iter_next(object, -1);
}

int val_object_iter_next(val_t object, int iter) {
  assert(VALP_HAS_KIND(object, VAL_KIND_OBJECT));
  assert(iter != ITER_FINISHED);
  struct object_slot* slot;
  do {
    iter++;
    if (iter >= valp_object_size(object))
      return ITER_FINISHED;
    slot = valp_object_get_slot(object, iter);
  } while (val_get_kind(slot->string) == VAL_KIND_NULL);
  assert(val_get_kind(valp_object_get_slot(object,iter)->string)
         == VAL_KIND_STRING);
  return iter;
}

val_t val_object_iter_key(val_t object, int iter) {
  val_t s = valp_object_get_slot(object, iter)->string;
  assert(VALP_HAS_KIND(s, VAL_KIND_STRING));
  return val_copy(s);
}

val_t val_object_iter_value(val_t object, int iter) {
  return val_copy(valp_object_get_slot(object, iter)->value);
}

/*
 * Memory management
 */
val_t val_copy(val_t j) {
  if (VALP_IS_ALLOCATED(j)) {
    valp_refcnt_inc(j.u.ptr);
  }
  return j;
}

/*
 * Free children iteratively via a heap-allocated buffer to avoid
 * recursion through val_free, which would cause stack overflow on
 * deeply nested values.
 */
void val_free(val_t j) {
  val_t* pending = NULL;
  size_t len = 0, cap = 0;
  while (1) {
    switch (VALP_KIND(j)) {
      case VAL_KIND_ARRAY:
        if (valp_refcnt_dec(j.u.ptr)) {
          valp_array* arr = valp_array_ptr(j);
          if (len + arr->length > cap) {
            cap = (len + arr->length) * 2;
            pending = val_mem_realloc(pending, cap * sizeof(val_t));
          }
          for (int i = 0; i < arr->length; i++)
            pending[len++] = arr->elements[i];
          val_mem_free(arr);
        }
        break;
      case VAL_KIND_OBJECT:
        if (valp_refcnt_dec(j.u.ptr)) {
          int sz = valp_object_size(j);
          if (len + sz > cap) {
            cap = (len + sz) * 2;
            pending = val_mem_realloc(pending, cap * sizeof(val_t));
          }
          for (int i = 0; i < sz; i++) {
            struct object_slot* slot = valp_object_get_slot(j, i);
            if (val_get_kind(slot->string) != VAL_KIND_NULL) {
              valp_string_free(slot->string);
              pending[len++] = slot->value;
            }
          }
          val_mem_free(valp_object_ptr(j));
        }
        break;
      case VAL_KIND_INVALID:
        if (VALP_HAS_FLAGS(j, VALP_FLAGS_INVALID_MSG) && valp_refcnt_dec(j.u.ptr)) {
          if (len + 1 > cap) {
            cap = (len + 1) * 2;
            pending = val_mem_realloc(pending, cap * sizeof(val_t));
          }
          pending[len++] = ((valp_invalid*)j.u.ptr)->errmsg;
          val_mem_free(j.u.ptr);
        }
        break;
      case VAL_KIND_STRING:
        valp_string_free(j);
        break;
      case VAL_KIND_NUMBER:
        valp_number_free(j);
        break;
    }
    if (len == 0) break;
    j = pending[--len];
  }
  val_mem_free(pending);
}

int val_get_refcnt(val_t j) {
  if (VALP_IS_ALLOCATED(j)) {
    return j.u.ptr->count;
  } else {
    return 1;
  }
}

/*
 * Higher-level operations
 */

#ifndef MAX_EQUAL_DEPTH
#define MAX_EQUAL_DEPTH (10000)
#endif

static int valp_equal(val_t a, val_t b, int depth) {
  if (depth > MAX_EQUAL_DEPTH) {
    val_free(a);
    val_free(b);
    return -1;
  }
  int r;
  if (val_get_kind(a) != val_get_kind(b)) {
    r = 0;
  } else if (VALP_IS_ALLOCATED(a) &&
             VALP_IS_ALLOCATED(b) &&
             a.kind_flags == b.kind_flags &&
             a.size == b.size &&
             a.u.ptr == b.u.ptr) {
    r = 1;
  } else {
    switch (val_get_kind(a)) {
    case VAL_KIND_NUMBER:
      r = valp_number_equal(a, b);
      break;
    case VAL_KIND_ARRAY:
      r = valp_array_equal(a, b, depth + 1);
      break;
    case VAL_KIND_STRING:
      r = valp_string_equal(a, b);
      break;
    case VAL_KIND_OBJECT:
      r = valp_object_equal(a, b, depth + 1);
      break;
    default:
      r = 1;
      break;
    }
  }
  val_free(a);
  val_free(b);
  return r;
}

// Returns 1 if equal, 0 if not equal, or -1 if the comparison is too deep
int val_equal(val_t a, val_t b) {
  return valp_equal(a, b, 0);
}

int val_identical(val_t a, val_t b) {
  int r;
  if (a.kind_flags != b.kind_flags
      || a.offset != b.offset
      || a.size != b.size) {
    r = 0;
  } else {
    if (VALP_IS_ALLOCATED(a) /* b has the same flags */) {
      r = a.u.ptr == b.u.ptr;
    } else {
      r = memcmp(&a.u.ptr, &b.u.ptr, sizeof(a.u)) == 0;
    }
  }
  val_free(a);
  val_free(b);
  return r;
}

#ifndef MAX_CONTAINS_DEPTH
#define MAX_CONTAINS_DEPTH (10000)
#endif

static int valp_contains(val_t a, val_t b, int depth) {
  if (depth > MAX_CONTAINS_DEPTH) {
    val_free(a);
    val_free(b);
    return -1;
  }
  int r = 1;
  if (val_get_kind(a) != val_get_kind(b)) {
    r = 0;
  } else if (VALP_HAS_KIND(a, VAL_KIND_OBJECT)) {
    r = valp_object_contains(a, b, depth + 1);
  } else if (VALP_HAS_KIND(a, VAL_KIND_ARRAY)) {
    r = valp_array_contains(a, b, depth + 1);
  } else if (VALP_HAS_KIND(a, VAL_KIND_STRING)) {
    int b_len = val_string_length_bytes(val_copy(b));
    if (b_len != 0) {
      r = _jq_memmem(val_string_value(a), val_string_length_bytes(val_copy(a)),
                     val_string_value(b), b_len) != 0;
    } else {
      r = 1;
    }
  } else {
    r = val_equal(val_copy(a), val_copy(b));
  }
  val_free(a);
  val_free(b);
  return r;
}

// Returns 1 (contained), 0 (not contained), or -1 (too deep)
int val_contains(val_t a, val_t b) {
  return valp_contains(a, b, 0);
}
