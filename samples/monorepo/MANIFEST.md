# Waypoint Plant Manifest

Intentionally insecure sample monorepo -- Waypoint test fixture. Do not deploy.

Every planted issue is listed below. The `line(approx)` column points at the
planted code (the `WAYPOINT-PLANT` marker comment sits on the line directly
above it). Clean controls (`WAYPOINT-OK`) are listed in a second table.

## Planted issues

| file | line(approx) | SHAPE_ID | axes | one-line description |
| --- | --- | --- | --- | --- |
| py_service/app.py | 12 | PY-EXEC-EVAL | security | `eval()` on `formula` derived from request args |
| py_service/app.py | 20 | PY-IDOR | security,abuse | item lookup by request `id` with no ownership check |
| py_service/db.py | 10 | PY-SQL-STRING | security,abuse | SQL built with `%`-formatting of `name` into `execute()` |
| py_service/db.py | 17 | PY-SQL-STRING | security,abuse | SQL built with f-string of `item_id` into `execute()` |
| py_service/util.py | 11 | PY-SUBPROCESS-SHELL | security | `subprocess.run(f"ping ... {host}", shell=True)` |
| py_service/util.py | 16 | PY-PATH-TRAVERSAL | security | `open(os.path.join(BASE_DIR, user_supplied))`, no normalization |
| py_service/util.py | 30 | PY-BARE-EXCEPT-PASS | edge-case | bare `except:` then `pass` swallows all errors |
| py_service/util.py | 36 | PY-REDOS | abuse,security | `re.compile(r"(a+)+$")` nested-quantifier regex on input |
| py_service/util.py | 44 | PY-INPUT-RECURSION | abuse | recursion driven by user int `n`, no depth bound |
| py_service/settings.py | 8 | HARDCODED-SECRET | security | hardcoded `AWS_SECRET_ACCESS_KEY` AKIA-style string |
| py_service/settings.py | 13 | PY-TLS-DISABLED | security | `requests.get(url, verify=False)` |
| py_service/settings.py | 18 | PY-TLS-DISABLED | security | `ssl._create_unverified_context()` |
| py_service/settings.py | 25 | PY-DROPPED-ERROR | edge-case | `except Exception: pass` drops the error |
| py_service/workers.py | 13 | PY-ASYNC-SHARED | concurrency,abuse | module dict `HITS` mutated in `async def`, no lock |
| py_service/workers.py | 31 | PY-THREAD-SHARED | concurrency | module `TOTAL` mutated from threads, no `Lock` |
| py_service/workers.py | 44 | PY-ASYNC-GATHER-WRITE | concurrency | `asyncio.gather` tasks append to shared `RESULTS` |
| rust_service/src/state.rs | 10 | RUST-UNSAFE-SEND-SYNC | concurrency,security | `unsafe impl Send` for struct holding raw pointer |
| rust_service/src/state.rs | 12 | RUST-UNSAFE-SEND-SYNC | concurrency,security | `unsafe impl Sync` for struct holding raw pointer |
| rust_service/src/state.rs | 15 | RUST-STATIC-MUT | concurrency,security | declaration of `static mut COUNTER` |
| rust_service/src/state.rs | 20 | RUST-STATIC-MUT | concurrency,security | `unsafe` read/write of `static mut COUNTER` |
| rust_service/src/state.rs | 31 | RUST-ARC-MUTEX | concurrency | `Arc<Mutex<_>>` moved into `thread::spawn` |
| rust_service/src/state.rs | 40 | RUST-UNWRAP | edge-case | `h.join().unwrap()` |
| rust_service/src/exec.rs | 6 | RUST-CMD-INJECT | security | `Command::new("sh").arg("-c").arg(user_input)` |
| rust_service/src/exec.rs | 10 | RUST-UNWRAP | edge-case | `.expect("command failed to start")` on Command output |
| rust_service/src/lib.rs | 11 | RUST-UNWRAP | edge-case | `s.parse::<u16>().unwrap()` |
| rust_service/src/main.rs | 10 | RUST-UNWRAP | edge-case | `std::env::var("APP_CONFIG").unwrap()` |
| rust_service/src/main.rs | 18 | RUST-UNWRAP | edge-case | `panic!` + `Option::unwrap()` on a `None` |
| react_app/src/UserProfile.tsx | 18 | TS-EFFECT-ASYNC-NOCLEANUP | concurrency,edge-case | `useEffect(() => { fetchData() }, [])`, async, no cleanup |
| react_app/src/UserProfile.tsx | 31 | TS-DANGEROUS-HTML | security | `dangerouslySetInnerHTML={{ __html: bio }}` (user-provided) |
| react_app/src/Dashboard.tsx | 16 | TS-SETSTATE-IN-ASYNC | concurrency,edge-case | `setStats`/`setCount` called after `await` in async cb |
| react_app/src/Dashboard.tsx | 21 | TS-EXHAUSTIVE-DEPS | concurrency,edge-case | `useEffect` deps `[]` omits `org` and `load` |
| ts_lib/src/index.ts | 10 | TS-NONNULL-DEREF | edge-case | `cfg.name!.toUpperCase()` on possibly-undefined |
| ts_lib/src/index.ts | 17 | TS-PROMISE-ALL-SHARED | concurrency | `Promise.all` tasks `push` to shared module `SEEN` |
| ts_lib/src/exec.ts | 6 | TS-EVAL | security | `eval(userStr)` |
| ts_lib/src/exec.ts | 11 | TS-EVAL | security | `new Function("x", userStr)` |
| ts_lib/src/exec.ts | 16 | TS-CHILD-PROCESS | security | `exec(\`git log ${userInput}\`)` |
| ts_lib/src/parse.ts | 5 | TS-REDOS | abuse,security | `RegExp /(\w+)+$/` nested quantifiers `.test(input)` |

Planted issue count: 37.

## Clean / false-positive controls (WAYPOINT-OK)

| file | line(approx) | description |
| --- | --- | --- |
| py_service/app.py | 29 | IDOR control: handler checks ownership before returning row |
| py_service/db.py | 24 | parametrized SQL with bound params (`?`, tuple) |
| py_service/db.py | 31 | parametrized SQL, no string interpolation |
| py_service/util.py | 22 | `with open(...)` context manager on a fixed path |
| py_service/workers.py | 23 | async handler guarded by `asyncio.Lock` |
| rust_service/src/lib.rs | 16 | returns `Result` instead of unwrapping |
| rust_service/src/state.rs | 33 | properly-locked `Arc<Mutex>` inside a clear scope |
| rust_service/src/exec.rs | 16 | fixed argv `ls -la`, no shell, no user interpolation |
| react_app/src/UserProfile.tsx | 22 | `useEffect` with cleanup `() => controller.abort()` |
| ts_lib/src/index.ts | 26 | guards `undefined` before use (no non-null assertion) |
| ts_lib/src/parse.ts | 10 | `JSON.parse` wrapped in `try/catch` with fallback |
