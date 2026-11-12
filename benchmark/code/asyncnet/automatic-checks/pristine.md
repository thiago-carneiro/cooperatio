# Domain gates report: 4 files measured

## d-lint: 112 findings

netlib/http1connection.py:71:17: RET501 [*] Do not explicitly `return None` in function if it is the only possible return value
netlib/http1connection.py:79:9: PLR0913 Too many arguments in function definition (7 > 5)
netlib/http1connection.py:79:9: PLR0917 Too many positional arguments (7 > 5)
netlib/http1connection.py:190:15: PLR0912 Too many branches (27 > 12)
netlib/http1connection.py:190:15: PLR0915 Too many statements (78 > 50)
netlib/http1connection.py:243:28: PLR2004 Magic value used in comparison, consider replacing `304` with a constant variable
netlib/http1connection.py:248:20: PLR2004 Magic value used in comparison, consider replacing `100` with a constant variable
netlib/http1connection.py:248:34: PLR2004 Magic value used in comparison, consider replacing `200` with a constant variable
netlib/http1connection.py:252:25: TRY301 Abstract `raise` to an inner function
netlib/http1connection.py:258:13: PLR5501 [*] Use `elif` instead of `else` then `if`, to reduce indentation
netlib/http1connection.py:386:9: PLR0912 Too many branches (13 > 12)
netlib/http1connection.py:422:40: PLR2004 Magic value used in comparison, consider replacing `100` with a constant variable
netlib/http1connection.py:422:66: PLR2004 Magic value used in comparison, consider replacing `200` with a constant variable
netlib/http1connection.py:442:69: PLR2004 Magic value used in comparison, consider replacing `304` with a constant variable
netlib/http1connection.py:479:23: TRY003 Avoid specifying long messages outside the exception class
netlib/http1connection.py:486:9: RET505 [*] Unnecessary `else` after `return` statement
netlib/http1connection.py:519:9: SIM102 Use a single `if` statement instead of nested `if` statements
netlib/http1connection.py:562:9: RET505 [*] Unnecessary `elif` after `return` statement
netlib/http1connection.py:572:31: ARG002 Unused method argument: `future`
netlib/http1connection.py:618:17: B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
netlib/http1connection.py:624:23: TRY003 Avoid specifying long messages outside the exception class
netlib/http1connection.py:630:20: PLR2004 Magic value used in comparison, consider replacing `204` with a constant variable
netlib/http1connection.py:670:17: B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
netlib/http1connection.py:670:23: TRY003 Avoid specifying long messages outside the exception class
netlib/http1connection.py:674:27: TRY003 Avoid specifying long messages outside the exception class
netlib/http1connection.py:680:23: TRY003 Avoid specifying long messages outside the exception class
netlib/http1connection.py:746:31: TRY003 Avoid specifying long messages outside the exception class
netlib/http1connection.py:752:27: TRY003 Avoid specifying long messages outside the exception class
netlib/http1connection.py:770:23: TRY003 Avoid specifying long messages outside the exception class
netlib/http1connection.py:810:9: SIM105 Use `contextlib.suppress(Exception)` instead of `try`-`except`-`pass`
netlib/http1connection.py:891:15: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:43:1: B018 Found useless expression. Either assign it to a variable or remove it.
netlib/httputil.py:45:1: E402 Module level import not at top of file
netlib/httputil.py:46:1: E402 Module level import not at top of file
netlib/httputil.py:219:9: PLR5501 [*] Use `elif` instead of `else` then `if`, to reduce indentation
netlib/httputil.py:277:23: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:282:13: PLR5501 [*] Use `elif` instead of `else` then `if`, to reduce indentation
netlib/httputil.py:291:17: B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
netlib/httputil.py:291:23: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:491:9: PLR0913 Too many arguments in function definition (10 > 5)
netlib/httputil.py:491:9: PLR0917 Too many positional arguments (10 > 5)
netlib/httputil.py:524:17: B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
netlib/httputil.py:524:23: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:572:25: SIM105 Use `contextlib.suppress(Exception)` instead of `try`-`except`-`pass`
netlib/httputil.py:589:9: RET505 [*] Unnecessary `else` after `return` statement
netlib/httputil.py:806:10: SIM101 Multiple `isinstance` calls for `args`, merge into a single call
netlib/httputil.py:825:12: RET504 Unnecessary assignment to `url` before `return` statement
netlib/httputil.py:989:12: PLW0603 Using the global statement to update `_DEFAULT_PARSE_BODY_CONFIG` is discouraged
netlib/httputil.py:993:5: PLR0913 Too many arguments in function definition (6 > 5)
netlib/httputil.py:993:5: PLR0912 Too many branches (13 > 12)
netlib/httputil.py:1034:17: TRY301 Abstract `raise` to an inner function
netlib/httputil.py:1034:23: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:1043:17: TRY301 Abstract `raise` to an inner function
netlib/httputil.py:1043:23: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:1048:5: PLR0912 Too many branches (13 > 12)
netlib/httputil.py:1070:15: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:1080:15: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:1083:15: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:1089:19: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:1091:19: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:1096:19: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:1099:19: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:1154:15: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:1180:15: TRY003 Avoid specifying long messages outside the exception class
netlib/httputil.py:1253:26: PLR2004 Magic value used in comparison, consider replacing `2` with a constant variable
netlib/httputil.py:1297:5: PLC0415 `import` should be at the top-level of a file
netlib/httputil.py:1338:5: RET505 [*] Unnecessary `else` after `return` statement
netlib/httputil.py:1351:30: PLR2004 Magic value used in comparison, consider replacing `2` with a constant variable
netlib/iostream.py:175:9: RET505 [*] Unnecessary `else` after `return` statement
netlib/iostream.py:532:23: TRY003 Avoid specifying long messages outside the exception class
netlib/iostream.py:624:13: SIM105 Use `contextlib.suppress(asyncio.CancelledError)` instead of `try`-`except`-`pass`
netlib/iostream.py:677:9: PLR0912 Too many branches (14 > 12)
netlib/iostream.py:875:13: RET505 [*] Unnecessary `elif` after `return` statement
netlib/iostream.py:888:19: TRY003 Avoid specifying long messages outside the exception class
netlib/iostream.py:913:20: RET504 Unnecessary assignment to `num_bytes` before `return` statement
netlib/iostream.py:914:9: RET505 [*] Unnecessary `elif` after `return` statement
netlib/iostream.py:1007:9: SIM102 Use a single `if` statement instead of nested `if` statements
netlib/iostream.py:1128:44: ARG002 Unused method argument: `server_hostname`
netlib/iostream.py:1242:19: TRY003 Avoid specifying long messages outside the exception class
netlib/iostream.py:1244:13: SIM108 Use ternary operator `ssl_options = _server_ssl_defaults if server_side else _client_ssl_defaults` instead of `if`-`else`-block
netlib/iostream.py:1367:17: RET502 [*] Do not implicitly `return None` in function able to return non-`None` value
netlib/iostream.py:1368:13: RET505 [*] Unnecessary `elif` after `return` statement
netlib/iostream.py:1370:17: RET502 [*] Do not implicitly `return None` in function able to return non-`None` value
netlib/iostream.py:1500:19: TRY003 Avoid specifying long messages outside the exception class
netlib/iostream.py:1548:17: RET505 [*] Unnecessary `else` after `return` statement
netlib/iostream.py:1581:19: TRY003 Avoid specifying long messages outside the exception class
netlib/iostream.py:1608:13: RET505 [*] Unnecessary `else` after `return` statement
netlib/iostream.py:1615:5: PLC0415 `import` should be at the top-level of a file
netlib/simple_httpclient.py:118:9: PLR0913 Too many arguments in function definition (7 > 5)
netlib/simple_httpclient.py:118:9: PLR0917 Too many positional arguments (7 > 5)
netlib/simple_httpclient.py:255:9: PLR0913 Too many arguments in function definition (8 > 5)
netlib/simple_httpclient.py:255:9: PLR0917 Too many positional arguments (8 > 5)
netlib/simple_httpclient.py:288:15: PLR0912 Too many branches (40 > 12)
netlib/simple_httpclient.py:288:15: PLR0915 Too many statements (93 > 50)
netlib/simple_httpclient.py:292:17: TRY301 Abstract `raise` to an inner function
netlib/simple_httpclient.py:318:21: TRY301 Abstract `raise` to an inner function
netlib/simple_httpclient.py:365:17: TRY301 Abstract `raise` to an inner function
netlib/simple_httpclient.py:374:21: TRY301 Abstract `raise` to an inner function
netlib/simple_httpclient.py:393:21: TRY301 Abstract `raise` to an inner function
netlib/simple_httpclient.py:393:27: TRY003 Avoid specifying long messages outside the exception class
netlib/simple_httpclient.py:415:21: TRY301 Abstract `raise` to an inner function
netlib/simple_httpclient.py:512:16: RET504 Unnecessary assignment to `connection` before `return` statement
netlib/simple_httpclient.py:544:9: ARG002 Unused method argument: `typ`
netlib/simple_httpclient.py:546:9: ARG002 Unused method argument: `tb`
netlib/simple_httpclient.py:571:9: RET505 [*] Unnecessary `else` after `return` statement
netlib/simple_httpclient.py:584:17: TRY301 Abstract `raise` to an inner function
netlib/simple_httpclient.py:594:68: PLR2004 Magic value used in comparison, consider replacing `100` with a constant variable
netlib/simple_httpclient.py:622:9: PLR0915 Too many statements (52 > 50)
netlib/simple_httpclient.py:666:21: SIM105 Use `contextlib.suppress(KeyError)` instead of `try`-`except`-`pass`
netlib/simple_httpclient.py:682:30: PLR2004 Magic value used in comparison, consider replacing `303` with a constant variable
netlib/simple_httpclient.py:693:21: SIM105 Use `contextlib.suppress(KeyError)` instead of `try`-`except`-`pass`
netlib/simple_httpclient.py:706:9: SIM108 Use ternary operator `buffer = BytesIO() if self.request.streaming_callback else BytesIO(data)` instead of `if`-`else`-block

## d-security: 33 findings

netlib/http1connection.py:68: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/http1connection.py:236: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/http1connection.py:395: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/http1connection.py:406: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/http1connection.py:407: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/http1connection.py:408: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/http1connection.py:694: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/http1connection.py:809: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/http1connection.py:812: B110 LOW Try, Except, Pass detected.
netlib/http1connection.py:820: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/httputil.py:568: B110 LOW Try, Except, Pass detected.
netlib/httputil.py:574: B110 LOW Try, Except, Pass detected.
netlib/iostream.py:166: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/iostream.py:182: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/iostream.py:203: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/iostream.py:418: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/iostream.py:717: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/iostream.py:804: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/iostream.py:952: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/iostream.py:989: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/iostream.py:1406: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/iostream.py:1463: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/simple_httpclient.py:167: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/simple_httpclient.py:168: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/simple_httpclient.py:391: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/simple_httpclient.py:593: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/simple_httpclient.py:613: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/simple_httpclient.py:623: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/simple_httpclient.py:628: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/simple_httpclient.py:629: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/simple_httpclient.py:661: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/simple_httpclient.py:670: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
netlib/simple_httpclient.py:701: B101 LOW Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.

## d-complexity: 2 functions above 15

netlib/http1connection.py:190:15: C901 `_read_message` is too complex (23 > 15)
netlib/simple_httpclient.py:288:15: C901 `run` is too complex (36 > 15)

## d-duplicates: 11 repeated blocks of 6 lines

2x 6-line block at netlib/iostream.py:338, netlib/iostream.py:376: .. versionchanged:: 4.0
2x 6-line block at netlib/iostream.py:339, netlib/iostream.py:377: Added the ``max_bytes`` argument. The ``callback`` argument 
2x 6-line block at netlib/iostream.py:350, netlib/iostream.py:387: self._read_max_bytes = max_bytes
2x 6-line block at netlib/iostream.py:351, netlib/iostream.py:388: try:
2x 6-line block at netlib/iostream.py:352, netlib/iostream.py:389: self._try_inline_read()
2x 6-line block at netlib/iostream.py:353, netlib/iostream.py:390: except UnsatisfiableReadError as e:
2x 6-line block at netlib/iostream.py:355, netlib/iostream.py:392: gen_log.info("Unsatisfiable read, closing connection: %s" % 
2x 6-line block at netlib/iostream.py:356, netlib/iostream.py:393: self.close(exc_info=e)
2x 6-line block at netlib/iostream.py:420, netlib/iostream.py:464: self._read_partial = partial
2x 6-line block at netlib/simple_httpclient.py:47, netlib/simple_httpclient.py:66: For historical reasons, this is a subclass of `.HTTPClientEr
3x 6-line block at netlib/iostream.py:421, netlib/iostream.py:466, netlib/iostream.py:496: try:
