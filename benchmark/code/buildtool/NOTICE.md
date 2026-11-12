# Notice

This folder holds an excerpt of Ninja 1.13.2, modified, for use as a code-review benchmark.

The modifications:

- Both copies, `pristine/` and `seeded/`, are anonymized: the names of the program were replaced by neutral ones
  (the rules are in `anonymization.json`), file names included, and the license header at the top of each file
  was emptied with its line count kept, so that line numbers stay valid. The notices removed from those
  headers are reproduced below.
- The copy in `seeded/` holds twelve deliberate defects, described in `answer-key.md` and `answer-key.json`.

It must not be used in production or deployed in any form.

The upstream license is in `COPYING` in this folder (Apache License 2.0); it applies unchanged to every file
of both copies.

Modified files:

- `pristine/src/build.cc` (anonymized)
- `pristine/src/build_log.cc` (anonymized)
- `pristine/src/deps_log.cc` (anonymized)
- `pristine/src/disk_interface.cc` (anonymized)
- `pristine/src/graph.cc` (anonymized)
- `pristine/src/manifest_parser.cc` (anonymized)
- `pristine/src/state.cc` (anonymized)
- `pristine/src/subprocess-posix.cc` (anonymized)
- `seeded/src/build.cc` (anonymized, with deliberate defects)
- `seeded/src/build_log.cc` (anonymized, with deliberate defects)
- `seeded/src/deps_log.cc` (anonymized, with deliberate defects)
- `seeded/src/disk_interface.cc` (anonymized, with deliberate defects)
- `seeded/src/graph.cc` (anonymized, with deliberate defects)
- `seeded/src/manifest_parser.cc` (anonymized, with deliberate defects)
- `seeded/src/state.cc` (anonymized, with deliberate defects)
- `seeded/src/subprocess-posix.cc` (anonymized, with deliberate defects)

## Notices removed from the file headers

`src/build.cc` (upstream `src/build.cc`):

```text
// Copyright 2011 Google Inc. All Rights Reserved.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//     http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
```

`src/build_log.cc` (upstream `src/build_log.cc`):

```text
// Copyright 2011 Google Inc. All Rights Reserved.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//     http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// On AIX, inttypes.h gets indirectly included by build_log.h.
// It's easiest just to ask for the printf format macros right away.
```

`src/deps_log.cc` (upstream `src/deps_log.cc`):

```text
// Copyright 2012 Google Inc. All Rights Reserved.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//     http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
```

`src/disk_interface.cc` (upstream `src/disk_interface.cc`):

```text
// Copyright 2011 Google Inc. All Rights Reserved.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//     http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
```

`src/graph.cc` (upstream `src/graph.cc`):

```text
// Copyright 2011 Google Inc. All Rights Reserved.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//     http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
```

`src/manifest_parser.cc` (upstream `src/manifest_parser.cc`):

```text
// Copyright 2011 Google Inc. All Rights Reserved.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//     http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
```

`src/state.cc` (upstream `src/state.cc`):

```text
// Copyright 2011 Google Inc. All Rights Reserved.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//     http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
```

`src/subprocess-posix.cc` (upstream `src/subprocess-posix.cc`):

```text
// Copyright 2012 Google Inc. All Rights Reserved.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//     http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
```
