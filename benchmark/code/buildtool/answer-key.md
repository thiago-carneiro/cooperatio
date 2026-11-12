# Answer key: buildtool

This copy of Forge was modified on purpose to contain deliberate defects, for use as a code-review benchmark. It must not be used in production or deployed in any form. It keeps the upstream license: see `COPYING` in this directory, which applies unchanged to the modified files listed below.

Modified files:

- `seeded/src/build.cc`
- `seeded/src/build_log.cc`
- `seeded/src/deps_log.cc`
- `seeded/src/disk_interface.cc`
- `seeded/src/graph.cc`
- `seeded/src/manifest_parser.cc`
- `seeded/src/state.cc`
- `seeded/src/subprocess-posix.cc`

File paths in this key are relative to `pristine/` and `seeded/`. Line numbers refer to the seeded file.

## buildtool-L1: logic, boundary

`src/deps_log.cc`, lines 308-308. Behaviour preserving: no.

```diff
--- pristine/src/deps_log.cc
+++ seeded/src/deps_log.cc
@@ -305,7 +305,7 @@
 DepsLog::Deps* DepsLog::GetDeps(Node* node) {
   // Abort if the node has no id (never referenced in the deps) or if
   // there's no deps recorded for the node.
-  if (node->id() < 0 || node->id() >= (int)deps_.size())
+  if (node->id() < 0 || node->id() > (int)deps_.size())
     return NULL;
   return deps_[node->id()];
 }
```

**What is wrong.** GetDeps accepts an id equal to deps_.size() and then reads deps_[size], one element past the end.

**Why it matters.** A node whose id is exactly the size of deps_ (for instance the last id assigned, with no deps record) causes an out-of-bounds read and returns garbage as a Deps pointer.

**How a reviewer could notice it.** Compare the bound with the index used on the next line.

**A note counts as a find if it states:** GetDeps uses > instead of >= for the upper bound, so id == deps_.size() reads one past the end of deps_.

**Check.** Scratch tree built with cmake and forge, g++ 13: exit 0, no compiler warning. ASan harness, RecordDeps(out, {in}) then GetDeps(in), whose id equals deps_.size(): pristine returns NULL; seeded heap-buffer-overflow in DepsLog::GetDeps (src/deps_log.cc:310).

## buildtool-L2: logic, semantic

`src/graph.cc`, lines 189-189. Behaviour preserving: no.

```diff
--- pristine/src/graph.cc
+++ seeded/src/graph.cc
@@ -186,7 +186,7 @@
         explanations_.Record(node, "%s is dirty", (*i)->path().c_str());
         dirty = true;
       } else {
-        if (!most_recent_input || (*i)->mtime() > most_recent_input->mtime()) {
+        if (!most_recent_input || (*i)->mtime() < most_recent_input->mtime()) {
           most_recent_input = *i;
         }
       }
```

**What is wrong.** RecomputeNodeDirty keeps the oldest input in most_recent_input: the comparison is reversed.

**Why it matters.** Output freshness is compared against the oldest input, so an output older than a newer input is considered clean and a stale artifact is not rebuilt. Compare the identical loop in Plan::CleanNode.

**How a reviewer could notice it.** The variable is called most_recent_input and the same selection in Plan::CleanNode uses >.

**A note counts as a find if it states:** The most_recent_input comparison uses < instead of >, selecting the oldest input, so stale outputs are not detected as dirty.

**Check.** Scratch tree built with cmake and forge, g++ 13: exit 0, no compiler warning. Build with two inputs, then only the newer one touched: pristine explains 'older than most recent input' and rebuilds; seeded 'no work to do'.

## buildtool-S: suboptimization

`src/build.cc`, lines 514-527. Behaviour preserving: yes.

```diff
--- pristine/src/build.cc
+++ seeded/src/build.cc
@@ -512,9 +512,9 @@
     //   which edges have already been visited.
     //
     void Visit(Edge* edge) {
-      auto insertion = visited_set_.emplace(edge);
-      if (!insertion.second)
+      if (std::find(visited_.begin(), visited_.end(), edge) != visited_.end())
         return;
+      visited_.push_back(edge);
 
       for (const Node* input : edge->inputs_) {
         Edge* producer = input->in_edge();
@@ -524,7 +524,7 @@
       sorted_edges_.push_back(edge);
     }
 
-    std::unordered_set<Edge*> visited_set_;
+    std::vector<Edge*> visited_;
     std::vector<Edge*> sorted_edges_;
   };
 
```

**What is wrong.** TopoSort::Visit searches a vector linearly to know whether an edge was already visited.

**Why it matters.** The membership test is called once per incoming edge of the graph, so the topological sort degrades to O(E^2); the comment above still says a simple set is used. The order and the result are unchanged.

**How a reviewer could notice it.** The comment above Visit still speaks of a set, and the member is a vector searched with std::find.

**A note counts as a find if it states:** TopoSort uses a linear std::find over a vector as its visited set, making ComputeCriticalPath quadratic in the number of edges.

**Check.** Scratch tree built with cmake and forge, g++ 13: exit 0, no compiler warning. forge's own ComputeCriticalPath metric (-n -d stats, Debug build, independent edges) at 5000/10000/20000/40000 edges: 1.6/3.0/8.1/12.0 ms on pristine, 51.4/204.9/811.8/3269.6 ms on seeded, about 4x per doubling. Same [N/N] edge count reported by the dry run on 40000 edges.

## buildtool-R: repetition

`src/subprocess-posix.cc`, lines 179-187. Behaviour preserving: yes.

```diff
--- pristine/src/subprocess-posix.cc
+++ seeded/src/subprocess-posix.cc
@@ -177,8 +177,13 @@
 
 ExitStatus Subprocess::Finish() {
   if (pid_ != -1) {
-    TryFinish(0);
-    assert(pid_ == -1);
+    int status, ret;
+    while ((ret = waitpid(pid_, &status, 0)) < 0) {
+      if (errno != EINTR)
+        Fatal("waitpid(%d): %s", pid_, strerror(errno));
+    }
+    pid_ = -1;
+    exit_status_ = ParseExitStatus(status);
   }
   return exit_status_;
 }
```

**What is wrong.** Subprocess::Finish repeats the waitpid loop of TryFinish instead of calling it.

**Why it matters.** The reaping logic, including EINTR handling and the exit-status translation, now has two copies that can diverge.

**How a reviewer could notice it.** TryFinish is directly above Finish and contains the same loop.

**A note counts as a find if it states:** Subprocess::Finish duplicates the waitpid/EINTR loop of TryFinish instead of calling it.

**Check.** Scratch tree built with cmake and forge, g++ 13: exit 0, no compiler warning. A failing command (exit 3) and a console-pool job give output and exit status identical to pristine.

## buildtool-C: clean-code break

`src/state.cc`, lines 115-121. Behaviour preserving: yes.

```diff
--- pristine/src/state.cc
+++ seeded/src/state.cc
@@ -112,13 +112,13 @@
   const bool kAllowReplacements = true;
   const int kMaxValidEditDistance = 3;
 
-  int min_distance = kMaxValidEditDistance + 1;
+  int max_distance = kMaxValidEditDistance + 1;
   Node* result = NULL;
   for (Paths::iterator i = paths_.begin(); i != paths_.end(); ++i) {
     int distance = EditDistance(
         i->first, path, kAllowReplacements, kMaxValidEditDistance);
-    if (distance < min_distance && i->second) {
-      min_distance = distance;
+    if (distance < max_distance && i->second) {
+      max_distance = distance;
       result = i->second;
     }
   }
```

**What is wrong.** In SpellcheckNode the variable tracking the smallest distance seen is named max_distance.

**Why it matters.** The name states the opposite of the value it holds and reads as a maximum alongside kMaxValidEditDistance, misleading anyone tuning the suggestion threshold.

**How a reviewer could notice it.** The variable starts at the limit and only ever decreases.

**A note counts as a find if it states:** SpellcheckNode's max_distance actually tracks the minimum distance so far; the name says the opposite.

**Check.** Scratch tree built with cmake and forge, g++ 13: exit 0, no compiler warning. Rename of one local, reasoned. `forge -n target_on` gives the same 'did you mean' as pristine.

## buildtool-U: unintelligible code

`src/manifest_parser.cc`, lines 187-203. Behaviour preserving: yes.

```diff
--- pristine/src/manifest_parser.cc
+++ seeded/src/manifest_parser.cc
@@ -185,28 +185,21 @@
 }
 
 bool ManifestParser::ParseDefault(string* err) {
-  EvalString eval;
-  if (!lexer_.ReadPath(&eval, err))
-    return false;
-  if (eval.empty())
-    return lexer_.Error("expected target name", err);
-
-  do {
-    string path = eval.Evaluate(env_);
-    if (path.empty())
+  EvalString q;
+  string r, t;
+  uint64_t u;
+  for (int z = 0;; ++z)
+    if (!lexer_.ReadPath(&q, err) ||
+        (q.empty() && !z && (lexer_.Error("expected target name", err), 1)))
+      return false;
+    else if (q.empty())
+      return ExpectToken(Lexer::NEWLINE, err);
+    else if (r = q.Evaluate(env_), r.empty())
       return lexer_.Error("empty path", err);
-    uint64_t slash_bits;  // Unused because this only does lookup.
-    CanonicalizePath(&path, &slash_bits);
-    std::string default_err;
-    if (!state_->AddDefault(path, &default_err))
-      return lexer_.Error(default_err, err);
-
-    eval.Clear();
-    if (!lexer_.ReadPath(&eval, err))
-      return false;
-  } while (!eval.empty());
-
-  return ExpectToken(Lexer::NEWLINE, err);
+    else if (CanonicalizePath(&r, &u), !state_->AddDefault(r, &t))
+      return lexer_.Error(t, err);
+    else
+      q.Clear();
 }
 
 bool ManifestParser::ParseEdge(string* err) {
```

**What is wrong.** ParseDefault was rewritten as a single counted loop of if/else chains with comma operators, assignments in conditions and one-letter names.

**Why it matters.** The grammar it implements (at least one target, then more, then newline) is no longer visible; the error for the first empty path depends on a loop counter hidden in a comma expression.

**How a reviewer could notice it.** Try to write the grammar accepted by ParseDefault from the code.

**A note counts as a find if it states:** ParseDefault is rewritten as an unreadable counter loop with comma operators, assignments in conditions and one-letter names.

**Check.** Scratch tree built with cmake and forge, g++ 13: exit 0, no compiler warning. Manifests with valid `default a b` and with four malformed or edge forms (no target, unknown target, empty variable): output and exit status identical to pristine.

## buildtool-D: layering violation

`src/disk_interface.cc`, lines 34-44. Behaviour preserving: yes.

```diff
--- pristine/src/disk_interface.cc
+++ seeded/src/disk_interface.cc
@@ -31,6 +31,7 @@
 #include <unistd.h>
 #endif
 
+#include "graph.h"
 #include "metrics.h"
 #include "util.h"
 
@@ -38,7 +39,8 @@
 
 namespace {
 
-string DirName(const string& path) {
+string DirName(const string& raw_path) {
+  const string path = Node::PathDecanonicalized(raw_path, 0);
 #ifdef _WIN32
   static const char kPathSeparators[] = "\\/";
 #else
```

**What is wrong.** disk_interface.cc now includes graph.h and calls Node::PathDecanonicalized from DirName.

**Why it matters.** The disk abstraction is below the build graph (graph.cc includes disk_interface.h and calls DiskInterface). The lowest layer now depends on the graph layer for a call that, with slash_bits 0, is an identity.

**How a reviewer could notice it.** Look at the include list of the disk layer; graph.cc already includes disk_interface.h.

**A note counts as a find if it states:** disk_interface.cc includes graph.h and calls Node::PathDecanonicalized: the disk layer depends upward on the build graph.

**Check.** Scratch tree built with cmake and forge, g++ 13: exit 0, no compiler warning. Links with graph.o. Harness including disk_interface.cc dumped DirName for all 511 strings over {a,/} up to length 8: identical to pristine.

## buildtool-X: security

`src/deps_log.cc`, lines 202-202. Behaviour preserving: no.

```diff
--- pristine/src/deps_log.cc
+++ seeded/src/deps_log.cc
@@ -199,7 +199,7 @@
     bool is_deps = (size >> 31) != 0;
     size = size & 0x7FFFFFFF;
 
-    if (size > kMaxRecordSize || fread(buf, size, 1, f) < 1) {
+    if (fread(buf, size, 1, f) < 1) {
       read_failed = true;
       break;
     }
```

**What is wrong.** DepsLog::Load no longer checks the record size read from the file before fread into a fixed stack buffer.

**Why it matters.** buf is kMaxRecordSize + 1 bytes on the stack and size comes from the log file. A corrupted or crafted .forge_deps file overflows the stack buffer.

**How a reviewer could notice it.** buf has a fixed size and size is read from the file; look for the comparison between them.

**A note counts as a find if it states:** The size > kMaxRecordSize check was removed, so a record size from the file overflows the fixed stack buffer buf in fread.

**Check.** Scratch tree built with cmake and forge, g++ 13: exit 0, no compiler warning. A .forge_deps with a record header announcing 2 MiB, followed by 2 MiB: pristine 'premature end of file; recovering', exit 0; seeded SIGSEGV, exit 139.

## buildtool-K: concurrency or shared state

`src/subprocess-posix.cc`, lines 264-265. Behaviour preserving: no.

```diff
--- pristine/src/subprocess-posix.cc
+++ seeded/src/subprocess-posix.cc
@@ -257,7 +257,6 @@
   sigaddset(&set, SIGINT);
   sigaddset(&set, SIGTERM);
   sigaddset(&set, SIGHUP);
-  sigaddset(&set, SIGCHLD);
   if (sigprocmask(SIG_BLOCK, &set, &old_mask_) < 0)
     Fatal("sigprocmask: %s", strerror(errno));
 
```

**What is wrong.** SIGCHLD is no longer blocked outside ppoll/pselect.

**Why it matters.** The comment says handlers are only enabled during ppoll/pselect. A child exiting while the signal is unblocked runs the handler, then DoWork resets s_sigchld_received to 0 and enters ppoll: the wakeup is lost and a console subprocess, which has no pipe, is never reaped, so the build hangs.

**How a reviewer could notice it.** Compare the signals handled below with the set blocked above, and with the comment on blocking.

**A note counts as a find if it states:** SIGCHLD is left unblocked outside ppoll, so an early child exit is lost when DoWork clears s_sigchld_received: signal race and possible hang for console jobs.

**Check.** Scratch tree built with cmake and forge, g++ 13: exit 0, no compiler warning. Harness: Add a console 'true', sleep 300 ms so the child exits before DoWork, then loop on DoWork: pristine reaps it, exit 0; seeded never reaps it and was killed by the 5 s timeout (137).

## buildtool-E: swallowed failure

`src/disk_interface.cc`, lines 227-228. Behaviour preserving: no.

```diff
--- pristine/src/disk_interface.cc
+++ seeded/src/disk_interface.cc
@@ -222,7 +222,7 @@
   struct stat st;
   if (stat(path.c_str(), &st) < 0) {
 #endif
-    if (errno == ENOENT || errno == ENOTDIR)
+    if (errno == ENOENT || errno == ENOTDIR || errno == EACCES)
       return 0;
     *err = "stat(" + path + "): " + strerror(errno);
     return -1;
```

**What is wrong.** RealDiskInterface::Stat treats a permission error as 'file does not exist'.

**Why it matters.** Stat's return of 0 means missing. An unreadable directory now produces a plausible 'missing' answer instead of an error, so forge reports a missing input or rebuilds and overwrites outputs instead of stopping.

**How a reviewer could notice it.** Stat returning 0 means missing; ask whether a permission error means that.

**A note counts as a find if it states:** Stat maps EACCES to 0 (missing) instead of reporting the error, converting a permission failure into a false 'file does not exist'.

**Check.** Scratch tree built with cmake and forge, g++ 13: exit 0, no compiler warning. Input inside a directory with mode 000, run as non-root: pristine 'stat(sub/in): Permission denied'; seeded "'sub/in', needed by 'out', missing and no known rule to make it".

## buildtool-A: broken contract

`src/graph.cc`, lines 650-651. Behaviour preserving: no.

```diff
--- pristine/src/graph.cc
+++ seeded/src/graph.cc
@@ -648,7 +648,6 @@
   case DiskInterface::Okay:
     break;
   case DiskInterface::NotFound:
-    err->clear();
     break;
   case DiskInterface::OtherError:
     *err = "loading '" + path + "': " + *err;
```

**What is wrong.** LoadDepFile keeps the not-found message in *err instead of clearing it.

**Why it matters.** The comments promise 'Treat a missing depfile as empty' and 'On a missing depfile: return false and empty *err'. RecomputeNodeDirty aborts when *err is non-empty, so a missing depfile now fails the build instead of forcing a rebuild.

**How a reviewer could notice it.** The comments state the contract twice; the identical switch in Builder::ExtractDeps clears err.

**A note counts as a find if it states:** LoadDepFile no longer clears *err for NotFound, breaking its documented 'missing depfile returns false with empty *err' behaviour.

**Check.** Scratch tree built with cmake and forge, g++ 13: exit 0, no compiler warning. Rule with a depfile that the command does not write: pristine builds, exit 0; seeded 'forge: error: No such file or directory', exit 1.

## buildtool-M: resource lifecycle

`src/build_log.cc`, lines 238-239. Behaviour preserving: no.

```diff
--- pristine/src/build_log.cc
+++ seeded/src/build_log.cc
@@ -236,7 +236,6 @@
         *err = "build log version is too new; starting over";
       }
       if (invalid_log_version) {
-        fclose(file);
         platformAwareUnlink(path.c_str());
         // Don't report this as a failure. A missing build log will cause
         // us to rebuild the outputs anyway.
```

**What is wrong.** BuildLog::Load returns on the invalid-version path without closing the file it opened.

**Why it matters.** Every other exit from Load closes file; here the FILE and its descriptor leak, and on Windows the unlink of the still-open file fails.

**How a reviewer could notice it.** List the exits of Load; this is the only one without fclose.

**A note counts as a find if it states:** The invalid-log-version branch of BuildLog::Load returns without fclose(file), leaking the FILE.

**Check.** Scratch tree built with cmake and forge, g++ 13: exit 0, no compiler warning. Harness calling BuildLog::Load on a '# forge log v1' file, counting /proc/self/fd: delta 0 on pristine, 1 on seeded.
