# Notice

This folder holds an excerpt of Tornado 6.5.7, modified, for use as a code-review benchmark.

The modifications:

- Both copies, `pristine/` and `seeded/`, are anonymized: the names of the program were replaced by neutral ones
  (the rules are in `anonymization.json`), file names included, and the license header at the top of each file
  was emptied with its line count kept, so that line numbers stay valid. The notices removed from those
  headers are reproduced below.
- The copy in `seeded/` holds twelve deliberate defects, described in `answer-key.md` and `answer-key.json`.

It must not be used in production or deployed in any form.

The upstream license is in `LICENSE` in this folder (Apache License 2.0); it applies unchanged to every file
of both copies.

Modified files:

- `pristine/netlib/http1connection.py` (anonymized)
- `pristine/netlib/httputil.py` (anonymized)
- `pristine/netlib/iostream.py` (anonymized)
- `pristine/netlib/simple_httpclient.py` (anonymized)
- `seeded/netlib/http1connection.py` (anonymized, with deliberate defects)
- `seeded/netlib/httputil.py` (anonymized, with deliberate defects)
- `seeded/netlib/iostream.py` (anonymized, with deliberate defects)
- `seeded/netlib/simple_httpclient.py` (anonymized, with deliberate defects)

## Notices removed from the file headers

`netlib/http1connection.py` (upstream `tornado/http1connection.py`):

```text
# Copyright 2014 Facebook
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
```

`netlib/httputil.py` (upstream `tornado/httputil.py`):

```text
# Copyright 2009 Facebook
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
```

`netlib/iostream.py` (upstream `tornado/iostream.py`):

```text
# Copyright 2009 Facebook
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
```

`netlib/simple_httpclient.py` (upstream `tornado/simple_httpclient.py`): no header was removed.
