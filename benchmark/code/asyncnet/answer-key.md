# Answer key: asyncnet

This copy of Netlib was modified on purpose to contain deliberate defects, for use as a code-review benchmark. It must not be used in production or deployed in any form. It keeps the upstream license: see `LICENSE` in this directory, which applies unchanged to the modified files listed below.

Modified files:

- `seeded/netlib/http1connection.py`
- `seeded/netlib/httputil.py`
- `seeded/netlib/iostream.py`
- `seeded/netlib/simple_httpclient.py`

File paths in this key are relative to `pristine/` and `seeded/`. Line numbers refer to the seeded file.

## asyncnet-L1: logic, boundary

`netlib/iostream.py`, lines 926-926. Behaviour preserving: no.

```diff
--- pristine/netlib/iostream.py
+++ seeded/netlib/iostream.py
@@ -938,7 +938,7 @@
         return None
 
     def _check_max_bytes(self, delimiter: Union[bytes, Pattern], size: int) -> None:
-        if self._read_max_bytes is not None and size > self._read_max_bytes:
+        if self._read_max_bytes is not None and size >= self._read_max_bytes:
             raise UnsatisfiableReadError(
                 "delimiter %r not found within %d bytes"
                 % (delimiter, self._read_max_bytes)
```

**What is wrong.** _check_max_bytes rejects a read whose size is exactly max_bytes; the limit became exclusive.

**Why it matters.** read_until/read_until_regex promise to close only if MORE than max_bytes were read without the delimiter. A delimiter ending exactly at max_bytes, or a buffer of exactly max_bytes without it yet, now raises UnsatisfiableReadError and drops the connection; HTTP headers of exactly max_header_size are refused.

**How a reviewer could notice it.** Compare the operator with the docstring of read_until, which says 'more than max_bytes'.

**A note counts as a find if it states:** _check_max_bytes uses >= where it must be >, so a read of exactly max_bytes is wrongly treated as over the limit.

**Check.** py_compile exit 0 on a throwaway copy. Probe on a socketpair, read_until(b'\n', max_bytes=5) with b'abcd\n' available: pristine returns the 5 bytes; seeded closes the stream (StreamClosedError).

## asyncnet-L2: logic, semantic

`netlib/simple_httpclient.py`, lines 682-682. Behaviour preserving: no.

```diff
--- pristine/netlib/simple_httpclient.py
+++ seeded/netlib/simple_httpclient.py
@@ -679,7 +679,7 @@
             # always specified this POST-to-GET behavior, arguably
             # for *all* methods, but libcurl < 7.70 only does this
             # for POST, while libcurl >= 7.70 does it for other methods.
-            if (self.code == 303 and self.request.method != "HEAD") or (
+            if (self.code == 303 and self.request.method == "HEAD") or (
                 self.code in (301, 302) and self.request.method == "POST"
             ):
                 new_request.method = "GET"
```

**What is wrong.** The 303 branch of the redirect logic tests method == HEAD instead of != HEAD.

**Why it matters.** As the comment above says, a 303 means POST-to-GET for everything but HEAD. Now a POST followed through a 303 is re-sent as POST with its body, and a HEAD is turned into a GET.

**How a reviewer could notice it.** Read the condition against the comment just above it about 303 and HEAD.

**A note counts as a find if it states:** The 303 redirect condition is inverted (== HEAD instead of != HEAD): POST stays POST after a 303 and HEAD becomes GET.

**Check.** py_compile exit 0 on a throwaway copy. Probe of _HTTPConnection.finish on a 303 answering a POST with a stub client: pristine follows with ('GET', None); seeded follows with ('POST', b'x').

## asyncnet-S: suboptimization

`netlib/iostream.py`, lines 734-754. Behaviour preserving: yes.

```diff
--- pristine/netlib/iostream.py
+++ seeded/netlib/iostream.py
@@ -740,7 +740,6 @@
             target_bytes = None
         else:
             target_bytes = 0
-        next_find_pos = 0
         while not self.closed():
             # Read from the socket until we get EWOULDBLOCK or equivalent.
             # SSL sockets do some internal buffering, and if the data is
@@ -758,14 +757,9 @@
                 break
 
             # Otherwise, we need to call the more expensive find_read_pos.
-            # It's inefficient to do this on every read, so instead
-            # do it on the first read and whenever the read buffer
-            # size has doubled.
-            if self._read_buffer_size >= next_find_pos:
-                pos = self._find_read_pos()
-                if pos is not None:
-                    return pos
-                next_find_pos = self._read_buffer_size * 2
+            pos = self._find_read_pos()
+            if pos is not None:
+                return pos
         return self._find_read_pos()
 
     def _handle_read(self) -> None:
```

**What is wrong.** _read_to_buffer_loop rescans the whole read buffer for the delimiter after every socket read instead of only when the buffer has doubled.

**Why it matters.** _find_read_pos is a linear search over the whole buffer. Called per chunk, a delimited read over n bytes costs O(n^2/chunk) instead of O(n): a large read_until without max_bytes burns CPU quadratically. Results are the same.

**How a reviewer could notice it.** Ask what _find_read_pos costs and how often the loop calls it; the buffer can hold many chunks.

**A note counts as a find if it states:** _read_to_buffer_loop calls the linear _find_read_pos on every read (doubling guard gone), making large delimited reads quadratic.

**Check.** py_compile exit 0 on a throwaway copy. Probe counting _find_read_pos during read_until over a socketpair: 4/16/64 MiB gave 9/11/19 calls on pristine and 66/258/1026 on seeded; the returned byte count is equal.

## asyncnet-R: repetition

`netlib/http1connection.py`, lines 467-482. Behaviour preserving: yes.

```diff
--- pristine/netlib/http1connection.py
+++ seeded/netlib/http1connection.py
@@ -465,7 +465,20 @@
             future = self._write_future = Future()
             data = b"\r\n".join(lines) + b"\r\n\r\n"
             if chunk:
-                data += self._format_chunk(chunk)
+                if self._expected_content_remaining is not None:
+                    self._expected_content_remaining -= len(chunk)
+                    if self._expected_content_remaining < 0:
+                        # Close the stream now to stop further framing errors.
+                        self.stream.close()
+                        raise httputil.HTTPOutputError(
+                            "Tried to write more data than Content-Length"
+                        )
+                if self._chunking_output and chunk:
+                    # Don't write out empty chunks because that means END-OF-STREAM
+                    # with chunked encoding
+                    data += utf8("%x" % len(chunk)) + b"\r\n" + chunk + b"\r\n"
+                else:
+                    data += chunk
             self._pending_write = self.stream.write(data)
             future_add_done_callback(self._pending_write, self._on_write_complete)
         return future
```

**What is wrong.** write_headers has an inline copy of the whole body of _format_chunk, while write() still calls the helper defined right below.

**Why it matters.** Two copies of the framing and Content-Length accounting logic must now be kept in sync; a fix applied to _format_chunk would not reach the first chunk sent with the headers.

**How a reviewer could notice it.** Compare the block in write_headers with _format_chunk a few lines below.

**A note counts as a find if it states:** write_headers duplicates the body of _format_chunk inline instead of calling the existing helper.

**Check.** py_compile exit 0 on a throwaway copy. write_headers output compared for fixed-length and chunked framing with a first chunk: byte-identical to pristine.

## asyncnet-C: clean-code break

`netlib/http1connection.py`, lines 641-654. Behaviour preserving: yes.

```diff
--- pristine/netlib/http1connection.py
+++ seeded/netlib/http1connection.py
@@ -625,19 +625,19 @@
         else:
             content_length = None
 
-        is_chunked = is_transfer_encoding_chunked(headers)
+        has_fixed_length = is_transfer_encoding_chunked(headers)
 
         if code == 204:
             # This response code is not allowed to have a non-empty body,
             # and has an implicit length of zero instead of read-until-close.
             # http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.3
-            if is_chunked or content_length not in (None, 0):
+            if has_fixed_length or content_length not in (None, 0):
                 raise httputil.HTTPInputError(
                     "Response with code %d should not have body" % code
                 )
             content_length = 0
 
-        if is_chunked:
+        if has_fixed_length:
             return self._read_chunked_body(delegate)
         if content_length is not None:
             return self._read_fixed_body(content_length, delegate)
```

**What is wrong.** In _read_body the flag holding the result of is_transfer_encoding_chunked is named has_fixed_length, the opposite of what it means.

**Why it matters.** The next reader takes `if has_fixed_length: read chunked` for an inverted branch, and may 'fix' it into a framing bug; the name states the contrary of the semantics.

**How a reviewer could notice it.** Look at the value assigned to the flag and at the branch that follows it.

**A note counts as a find if it states:** has_fixed_length in _read_body actually holds 'is chunked', so the name says the opposite of the value.

**Check.** py_compile exit 0 on a throwaway copy. Rename of a local confined to its three occurrences in _read_body (grep on pristine: 3 occurrences in the file). No behavioural probe; reasoned as a pure rename.

## asyncnet-U: unintelligible code

`netlib/iostream.py`, lines 183-195. Behaviour preserving: yes.

```diff
--- pristine/netlib/iostream.py
+++ seeded/netlib/iostream.py
@@ -181,27 +181,18 @@
         """
         assert 0 < size <= self._size
         self._size -= size
-        pos = self._first_pos
-
-        buffers = self._buffers
-        while buffers and size > 0:
-            is_large, b = buffers[0]
-            b_remain = len(b) - size - pos
-            if b_remain <= 0:
-                buffers.popleft()
-                size -= len(b) - pos
-                pos = 0
-            elif is_large:
-                pos += size
-                size = 0
-            else:
-                pos += size
-                del typing.cast(bytearray, b)[:pos]
-                pos = 0
-                size = 0
+        q, z = self._buffers, self._first_pos
+        while q and size > 0:
+            f, w = q[0]
+            r = len(w) - z
+            size, z = (
+                (q.popleft() and 0 or size - r, 0)
+                if size >= r
+                else (0, z + size if f else w.__delitem__(slice(z + size)) or 0)
+            )
 
         assert size == 0
-        self._first_pos = pos
+        self._first_pos = z
 
 
 class BaseIOStream:
```

**What is wrong.** _StreamBuffer.advance was compressed into one opaque expression: single-letter names, and-or tricks and __delitem__(slice(...)) with side effects hidden inside a tuple.

**Why it matters.** The method is the core of the write-buffer bookkeeping and now cannot be understood or safely changed; the three distinct cases (buffer exhausted, large view advance, small bytearray compaction) are no longer visible.

**How a reviewer could notice it.** Try to state in words what each branch of the expression in advance does.

**A note counts as a find if it states:** _StreamBuffer.advance is rewritten as an unreadable and-or/__delitem__ expression with one-letter names, hiding its three cases.

**Check.** py_compile exit 0 on a throwaway copy. Random-operation fuzz of _StreamBuffer against a bytearray model, 200000 operations: no mismatch on pristine or seeded.

## asyncnet-D: layering violation

`netlib/httputil.py`, lines 1178-1183. Behaviour preserving: yes.

```diff
--- pristine/netlib/httputil.py
+++ seeded/netlib/httputil.py
@@ -1175,10 +1175,12 @@
     >>> parse_response_start_line("HTTP/1.1 200 OK")
     ResponseStartLine(version='HTTP/1.1', code=200, reason='OK')
     """
+    from netlib.http1connection import parse_int
+
     match = _ABNF.status_line.fullmatch(line)
     if not match:
         raise HTTPInputError("Error parsing response start line")
-    r = ResponseStartLine(match.group(1), int(match.group(2)), match.group(3))
+    r = ResponseStartLine(match.group(1), parse_int(match.group(2)), match.group(3))
     if not r.version.startswith("HTTP/1"):
         # HTTP/2 and above doesn't use parse_response_start_line.
         raise HTTPInputError("Unexpected HTTP version %r" % r.version)
```

**What is wrong.** httputil.parse_response_start_line imports and calls parse_int from http1connection, a function-level import made to dodge the import cycle.

**Why it matters.** http1connection is built on top of httputil (it imports httputil at module level). The shared HTTP utility layer now depends on one of its protocol implementations; the deferred import is what hides the cycle.

**How a reviewer could notice it.** A function-level import inside a low-level module usually hides a cycle; check who imports whom.

**A note counts as a find if it states:** httputil now depends upward on http1connection (function-level import of parse_int), inverting the module layering and hiding an import cycle.

**Check.** py_compile exit 0 on a throwaway copy. parse_response_start_line output identical to pristine in a fresh process; the deferred import resolves.

## asyncnet-X: security

`netlib/http1connection.py`, lines 41-41. Behaviour preserving: no.

```diff
--- pristine/netlib/http1connection.py
+++ seeded/netlib/http1connection.py
@@ -38,7 +38,7 @@
 
 from typing import cast, Optional, Type, Awaitable, Callable, Union, Tuple
 
-CR_OR_LF_RE = re.compile(b"\r|\n")
+CR_OR_LF_RE = re.compile(b"\r\n")
 
 
 class _QuietException(Exception):
```

**What is wrong.** The header sanity check regex only matches the two-byte sequence CRLF, not a lone CR or a lone LF.

**Why it matters.** write_headers relies on this to reject header injection. HTTPHeaders.__setitem__ does no validation, and this same package accepts bare LF as a line terminator on input (parse_line), so a header value containing a bare \n coming from application or user data now reaches the wire: response splitting / header injection.

**How a reviewer could notice it.** Compare the regex with its name and with the error message raised at its use site.

**A note counts as a find if it states:** CR_OR_LF_RE matches only the sequence CRLF, so a header value with a bare CR or LF passes the check (header injection).

**Check.** py_compile exit 0 on a throwaway copy. Probe of write_headers with a header value holding a bare LF, set through __setitem__: pristine raises ValueError; seeded writes the injected Set-Cookie line to the stream.

## asyncnet-K: concurrency or shared state

`netlib/simple_httpclient.py`, lines 118-137. Behaviour preserving: no.

```diff
--- pristine/netlib/simple_httpclient.py
+++ seeded/netlib/simple_httpclient.py
@@ -115,6 +115,10 @@
         Added the ``max_body_size`` argument.
     """
 
+    active = (
+        {}
+    )  # type: Dict[object, Tuple[HTTPRequest, Callable[[HTTPResponse], None]]]
+
     def initialize(  # type: ignore
         self,
         max_clients: int = 10,
@@ -130,9 +134,6 @@
         self.queue = (
             collections.deque()
         )  # type: Deque[Tuple[object, HTTPRequest, Callable[[HTTPResponse], None]]]
-        self.active = (
-            {}
-        )  # type: Dict[object, Tuple[HTTPRequest, Callable[[HTTPResponse], None]]]
         self.waiting = (
             {}
         )  # type: Dict[object, Tuple[HTTPRequest, Callable[[HTTPResponse], None], object]]
```

**What is wrong.** The active-requests dictionary became a class attribute shared by every SimpleAsyncHTTPClient instance instead of per-instance state.

**Why it matters.** max_clients is documented per client, and clients exist per IOLoop or with force_instance=True. Requests of one client now count against all others (including across threads/IOLoops, unsynchronised), and a release on one client does not wake the queue of the other: requests stall until they time out.

**How a reviewer could notice it.** Note that active is declared in the class body while queue and waiting are set per instance.

**A note counts as a find if it states:** active is now class-level mutable state shared across client instances, so max_clients and queue release leak between clients/IOLoops.

**Check.** py_compile exit 0 on a throwaway copy. Probe: two SimpleAsyncHTTPClient(force_instance=True), `a.active is b.active`: False on pristine, True on seeded.

## asyncnet-E: swallowed failure

`netlib/httputil.py`, lines 1095-1096. Behaviour preserving: no.

```diff
--- pristine/netlib/httputil.py
+++ seeded/netlib/httputil.py
@@ -1093,7 +1093,7 @@
         disp_header = headers.get("Content-Disposition", "")
         disposition, disp_params = _parse_header(disp_header)
         if disposition != "form-data" or not part.endswith(b"\r\n"):
-            raise HTTPInputError("Invalid multipart/form-data")
+            continue
         value = part[eoh + 4 : -2]
         if not disp_params.get("name"):
             raise HTTPInputError("multipart/form-data missing name")
```

**What is wrong.** parse_multipart_form_data silently drops a malformed part instead of raising HTTPInputError.

**Why it matters.** Every other malformed case in the function raises. A truncated or malformed part now yields a successfully parsed form with fields or files simply missing, which handlers treat as valid input.

**How a reviewer could notice it.** Every other malformed case in the loop raises; this one continues.

**A note counts as a find if it states:** A malformed multipart part (bad disposition or no trailing CRLF) is skipped with continue instead of raising, so the error becomes a form with missing fields.

**Check.** py_compile exit 0 on a throwaway copy. Probe with one valid part and one part whose disposition is 'attachment': pristine raises HTTPInputError; seeded returns arguments ['a'] with no error.

## asyncnet-A: broken contract

`netlib/httputil.py`, lines 1130-1130. Behaviour preserving: no.

```diff
--- pristine/netlib/httputil.py
+++ seeded/netlib/httputil.py
@@ -1127,7 +1127,7 @@
     elif isinstance(ts, (tuple, time.struct_time)):
         time_num = calendar.timegm(ts)
     elif isinstance(ts, datetime.datetime):
-        time_num = calendar.timegm(ts.utctimetuple())
+        time_num = calendar.timegm(ts.timetuple())
     else:
         raise TypeError("unknown timestamp type: %r" % ts)
     return email.utils.formatdate(time_num, usegmt=True)
```

**What is wrong.** format_timestamp uses ts.timetuple() for datetimes, ignoring the UTC offset of aware datetimes.

**Why it matters.** The docstring promises that aware objects are converted to UTC before formatting. Any aware non-UTC datetime is now emitted shifted by its offset, with a GMT label: wrong Date/Expires/Last-Modified headers.

**How a reviewer could notice it.** Read the docstring sentence on aware datetimes, then the datetime branch.

**A note counts as a find if it states:** format_timestamp no longer converts aware datetimes to UTC (timetuple instead of utctimetuple), contradicting its docstring.

**Check.** py_compile exit 0 on a throwaway copy. format_timestamp(2020-01-01 12:00 +03:00): pristine 'Wed, 01 Jan 2020 09:00:00 GMT'; seeded '... 12:00:00 GMT'.

## asyncnet-M: resource lifecycle

`netlib/simple_httpclient.py`, lines 349-350. Behaviour preserving: no.

```diff
--- pristine/netlib/simple_httpclient.py
+++ seeded/netlib/simple_httpclient.py
@@ -346,7 +346,6 @@
 
             if self.final_callback is None:
                 # final_callback is cleared if we've hit our timeout.
-                stream.close()
                 return
             self.stream = stream
             self.stream.set_close_callback(self.on_connection_close)
```

**What is wrong.** When the connect timeout has already fired, run() returns with the freshly connected stream still open.

**Why it matters.** self.stream has not been assigned at this point, so nothing else can ever close that stream: one socket leaks per request that times out while connecting.

**How a reviewer could notice it.** Follow the local stream on the early return: self.stream is only assigned after it.

**A note counts as a find if it states:** On the timed-out-while-connecting path run() returns without closing the just-connected stream, leaking the socket.

**Check.** py_compile exit 0 on a throwaway copy. Probe of run() with a stub TCP client and final_callback already cleared: the connected stream is closed on pristine and left open on seeded.
