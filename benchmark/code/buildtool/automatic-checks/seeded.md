# Domain gates report: 8 files measured

## d-lint: 26 findings

src/build.cc:985:27: warning: 2 adjacent parameters of 'ExtractDeps' of similar type ('const string &') are easily swapped by mistake [bugprone-easily-swappable-parameters]
src/build_log.cc:167:17: warning: 2 adjacent parameters of 'ReadLine' of similar type ('char **') are easily swapped by mistake [bugprone-easily-swappable-parameters]
src/build_log.cc:19:9: warning: declaration uses identifier '__STDC_FORMAT_MACROS', which is a reserved identifier [bugprone-reserved-identifier]
src/build_log.cc:316:38: warning: repeated branch body in conditional chain [bugprone-branch-clone]
src/build_log.cc:66:57: warning: 4 adjacent parameters of 'LogEntry' of convertible types are easily swapped by mistake [bugprone-easily-swappable-parameters]
src/build_log.cc:90:42: warning: 3 adjacent parameters of 'RecordCommand' of convertible types are easily swapped by mistake [bugprone-easily-swappable-parameters]
src/deps_log.cc:206:15: warning: narrowing conversion from 'unsigned long' to signed type 'long' is implementation-defined [bugprone-narrowing-conversions]
src/deps_log.cc:219:24: warning: narrowing conversion from 'unsigned int' to signed type 'int' is implementation-defined [bugprone-narrowing-conversions]
src/deps_log.cc:240:23: warning: narrowing conversion from 'unsigned int' to signed type 'int' is implementation-defined [bugprone-narrowing-conversions]
src/deps_log.cc:262:25: warning: narrowing conversion from 'unsigned int' to signed type 'int' is implementation-defined [bugprone-narrowing-conversions]
src/disk_interface.cc:250:35: warning: 2 adjacent parameters of 'WriteFile' of similar type ('const string &') are easily swapped by mistake [bugprone-easily-swappable-parameters]
src/graph.cc:266:73: warning: parameter 'err' is unused [misc-unused-parameters]
src/graph.cc:319:14: warning: an assignment within an 'if' condition is bug-prone [bugprone-assignment-in-if-condition]
src/graph.cc:336:25: warning: an assignment within an 'if' condition is bug-prone [bugprone-assignment-in-if-condition]
src/graph.cc:392:8: warning: enum 'EscapeKind' uses a larger base type ('unsigned int', size: 4 bytes) than necessary for its value set, consider using 'std::uint8_t' (1 byte) as the base type to reduce its size [performance-enum-size]
src/graph.cc:482:35: warning: 2 adjacent parameters of 'MakePathList' of convertible types are easily swapped by mistake [bugprone-easily-swappable-parameters]
src/graph.cc:580:63: warning: parameter 'slash_bits' is unused [misc-unused-parameters]
src/graph.cc:648:3: warning: switch has 2 consecutive identical branches [bugprone-branch-clone]
src/graph.cc:707:69: warning: parameter 'err' is unused [misc-unused-parameters]
src/graph.cc:725:61: warning: parameter 'err' is unused [misc-unused-parameters]
src/graph.cc:748:27: warning: narrowing conversion from 'size_t' (aka 'unsigned long') to signed type 'int' is implementation-defined [bugprone-narrowing-conversions]
src/manifest_parser.cc:197:16: warning: an assignment within an 'if' condition is bug-prone [bugprone-assignment-in-if-condition]
src/manifest_parser.cc:217:7: warning: 'out' used after it was moved [bugprone-use-after-move]
src/subprocess-posix.cc:238:40: warning: parameter 'signo' is unused [misc-unused-parameters]
src/subprocess-posix.cc:238:58: warning: parameter 'info' is unused [misc-unused-parameters]
src/subprocess-posix.cc:238:70: warning: parameter 'context' is unused [misc-unused-parameters]

## d-security: 26 findings

src/build_log.cc:128:5: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/build_log.cc:147:3: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/build_log.cc:19:9: warning: declaration uses identifier '__STDC_FORMAT_MACROS', which is a reserved identifier [cert-dcl37-c,cert-dcl51-cpp]
src/build_log.cc:227:7: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/build_log.cc:239:9: warning: Opened stream never closed. Potential resource leak [clang-analyzer-unix.Stream]
src/build_log.cc:261:18: warning: 'atoi' used to convert a string to an integer value, but function will not report conversion errors; consider using 'strtol' instead [cert-err34-c]
src/build_log.cc:268:16: warning: 'atoi' used to convert a string to an integer value, but function will not report conversion errors; consider using 'strtol' instead [cert-err34-c]
src/build_log.cc:305:3: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/build_log.cc:353:5: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/build_log.cc:366:7: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/build_log.cc:374:3: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/build_log.cc:404:5: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/build_log.cc:418:9: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/build_log.cc:426:7: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/build_log.cc:431:3: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/deps_log.cc:150:5: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/deps_log.cc:170:7: warning: File position of the stream might be 'indeterminate' after a failed operation. Can cause undefined behavior [clang-analyzer-unix.Stream]
src/deps_log.cc:170:7: warning: Read function called when stream is in EOF state. Function has no effect [clang-analyzer-unix.Stream]
src/deps_log.cc:181:5: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/deps_log.cc:281:5: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/deps_log.cc:292:3: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/deps_log.cc:451:3: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/disk_interface.cc:268:5: warning: the value returned by this function should not be disregarded; neglecting it may lead to errors [cert-err33-c]
src/manifest_parser.cc:120:15: warning: 'atoi' used to convert a string to an integer value, but function will not report conversion errors; consider using 'strtol' instead [cert-err34-c]
src/state.cc:64:13: warning: initialization of 'kDefaultPool' with static storage duration may throw an exception that cannot be caught [cert-err58-cpp]
src/state.cc:65:13: warning: initialization of 'kConsolePool' with static storage duration may throw an exception that cannot be caught [cert-err58-cpp]

## d-complexity: 10 functions above cognitive 25

src/build.cc:271:12: warning: function 'CleanNode' has cognitive complexity of 40 (threshold 25) [readability-function-cognitive-complexity]
src/build.cc:703:21: warning: function 'Build' has cognitive complexity of 70 (threshold 25) [readability-function-cognitive-complexity]
src/build.cc:876:15: warning: function 'FinishCommand' has cognitive complexity of 55 (threshold 25) [readability-function-cognitive-complexity]
src/build_log.cc:208:22: warning: function 'Load' has cognitive complexity of 31 (threshold 25) [readability-function-cognitive-complexity]
src/deps_log.cc:154:21: warning: function 'Load' has cognitive complexity of 66 (threshold 25) [readability-function-cognitive-complexity]
src/deps_log.cc:68:15: warning: function 'RecordDeps' has cognitive complexity of 33 (threshold 25) [readability-function-cognitive-complexity]
src/graph.cc:278:22: warning: function 'RecomputeOutputDirty' has cognitive complexity of 26 (threshold 25) [readability-function-cognitive-complexity]
src/graph.cc:82:22: warning: function 'RecomputeNodeDirty' has cognitive complexity of 61 (threshold 25) [readability-function-cognitive-complexity]
src/manifest_parser.cc:205:22: warning: function 'ParseEdge' has cognitive complexity of 81 (threshold 25) [readability-function-cognitive-complexity]
src/manifest_parser.cc:38:22: warning: function 'Parse' has cognitive complexity of 27 (threshold 25) [readability-function-cognitive-complexity]

## d-duplicates: 5 repeated blocks of 6 lines

2x 6-line block at src/build_log.cc:345, src/build_log.cc:396: FILE* f = fopen(temp_path.c_str(), "wb");
2x 6-line block at src/subprocess-posix.cc:381, src/subprocess-posix.cc:433: (*i)->OnPipeReady();
2x 6-line block at src/subprocess-posix.cc:382, src/subprocess-posix.cc:434: if ((*i)->Done()) {
3x 6-line block at src/manifest_parser.cc:251, src/manifest_parser.cc:264, src/manifest_parser.cc:278: for (;;) {
3x 6-line block at src/manifest_parser.cc:253, src/manifest_parser.cc:265, src/manifest_parser.cc:279: EvalString in;
