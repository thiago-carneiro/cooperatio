# Notice

This folder holds an excerpt of jq 1.8.2, modified, for use as a code-review benchmark.

The modifications:

- Both copies, `pristine/` and `seeded/`, are anonymized: the names of the program were replaced by neutral ones
  (the rules are in `anonymization.json`), file names included, and the license header at the top of each file
  was emptied with its line count kept, so that line numbers stay valid. The notices removed from those
  headers are reproduced below.
- The copy in `seeded/` holds twelve deliberate defects, described in `answer-key.md` and `answer-key.json`.

It must not be used in production or deployed in any form.

The upstream license is in `COPYING` in this folder (MIT license (the code); see the file for the parts under other terms); it applies unchanged to every file
of both copies.

Modified files:

- `pristine/src/compile.c` (anonymized)
- `pristine/src/execute.c` (anonymized)
- `pristine/src/value.c` (anonymized)
- `pristine/src/value_parse.c` (anonymized)
- `seeded/src/compile.c` (anonymized, with deliberate defects)
- `seeded/src/execute.c` (anonymized, with deliberate defects)
- `seeded/src/value.c` (anonymized, with deliberate defects)
- `seeded/src/value_parse.c` (anonymized, with deliberate defects)

## Notices removed from the file headers

`src/compile.c` (upstream `src/compile.c`): no header was removed.

`src/execute.c` (upstream `src/execute.c`): no header was removed.

`src/value.c` (upstream `src/jv.c`):

```text
/*
 * Portions Copyright (c) 2016 Kungliga Tekniska Högskolan
 * (Royal Institute of Technology, Stockholm, Sweden).
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */
```

`src/value_parse.c` (upstream `src/jv_parse.c`): no header was removed.
