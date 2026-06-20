# Beacon index

Every beacon Waypoint can raise. Custom Semgrep beacons are grouped by language × axis; off-the-shelf beacons come from the wired tools. See [the shared schema](README.md).

**176 custom beacons · 19 wired tools.**

## python
### abuse
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-py-decompression-bomb`](python/abuse/waypoint-py-decompression-bomb.md) | abuse | zlib/gzip/bz2/lzma/zipfile decompress of untrusted bytes with no size cap — decompression bomb? |
| [`waypoint-py-idor-lookup-by-id`](python/abuse/waypoint-py-idor-lookup-by-id.md) | security, abuse | lookup by user-supplied id — missing ownership/authorization check (IDOR)? |
| [`waypoint-py-infinite-loop`](python/abuse/waypoint-py-infinite-loop.md) | abuse | infinite loop — reachable bounded exit, or a dead loop / busy-spin compute sink? |
| [`waypoint-py-input-driven-alloc`](python/abuse/waypoint-py-input-driven-alloc.md) | abuse | [x]*N or range(N) where N may be user-controlled — allocation amplification / DoS? |
| [`waypoint-py-minidom-entity-expansion`](python/abuse/waypoint-py-minidom-entity-expansion.md) | abuse, security | minidom/expat parse of untrusted XML with no entity cap — billion-laughs expansion DoS? |
| [`waypoint-py-redos`](python/abuse/waypoint-py-redos.md) | abuse, security | regex with nested quantifiers on input — catastrophic backtracking (ReDoS)? |
| [`waypoint-py-unbounded-read`](python/abuse/waypoint-py-unbounded-read.md) | abuse | read() with no size limit on an input stream — unbounded memory allocation / DoS? |

### authz
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-py-authz-mass-assignment`](python/authz/waypoint-py-authz-mass-assignment.md) | security, abuse | untrusted request body **-splatted into a constructor — mass assignment / privilege escalation via unexpected fields? |
| [`waypoint-py-authz-privilege-from-request`](python/authz/waypoint-py-authz-privilege-from-request.md) | security, abuse | privilege field (is_admin/role/permissions/…) set from request input — privilege escalation? |
| [`waypoint-py-authz-route-no-auth`](python/authz/waypoint-py-authz-route-no-auth.md) | security, abuse | route handler has no auth decorator (@login_required/@jwt_required/…) — unauthenticated endpoint? |

### concurrency
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-py-async-shared-mutable`](python/concurrency/waypoint-py-async-shared-mutable.md) | concurrency, abuse | async mutation of shared state with no lock held — data race on a value-bearing structure? |
| [`waypoint-py-blocking-call-in-async`](python/concurrency/waypoint-py-blocking-call-in-async.md) | concurrency | blocking call (time.sleep / requests.*) inside async def — event loop stalled? |
| [`waypoint-py-concurrency-primitive`](python/concurrency/waypoint-py-concurrency-primitive.md) | concurrency | concurrency primitive present — unsynchronized shared-state access nearby? |
| [`waypoint-py-fire-and-forget-task`](python/concurrency/waypoint-py-fire-and-forget-task.md) | concurrency | create_task() result discarded — task GC'd early or exceptions lost? |
| [`waypoint-py-thread-shared-mutable-nolock`](python/concurrency/waypoint-py-thread-shared-mutable-nolock.md) | concurrency, abuse | module-level dict/list/counter mutated in a def with no lock — data race under threads? |

### edge-case
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-py-assert-validation`](python/edge-case/waypoint-py-assert-validation.md) | edge-case, security | assert as a validation gate — bypassed under -O, leaving the check unenforced? |
| [`waypoint-py-bare-except`](python/edge-case/waypoint-py-bare-except.md) | edge-case | bare except — which errors are silently caught (incl. KeyboardInterrupt)? |
| [`waypoint-py-mutable-default-arg`](python/edge-case/waypoint-py-mutable-default-arg.md) | edge-case | mutable default arg ([]/{}/dict()/list()/set()) — state leaking across calls if mutated? |
| [`waypoint-py-open-without-with`](python/edge-case/waypoint-py-open-without-with.md) | edge-case | open() outside a with-block — descriptor leak if close() is skipped on error? |
| [`waypoint-py-request-no-timeout`](python/edge-case/waypoint-py-request-no-timeout.md) | edge-case, abuse | requests.* without timeout= — indefinite hang / resource exhaustion on a slow peer? |
| [`waypoint-py-reraise-loses-context`](python/edge-case/waypoint-py-reraise-loses-context.md) | edge-case | except raises a different error with no `from` — original cause/traceback lost? |
| [`waypoint-py-swallowed-exception`](python/edge-case/waypoint-py-swallowed-exception.md) | edge-case | except…: pass — a dropped error that should be handled or logged? |
| [`waypoint-py-toctou-exists-open`](python/edge-case/waypoint-py-toctou-exists-open.md) | edge-case, security | os.path.exists/isfile($P) then open($P) — file swapped between check and use (TOCTOU)? |

### iac
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-py-cdk-db-no-encryption`](python/iac/waypoint-py-cdk-db-no-encryption.md) | security | RDS/Redshift built with no storage_encrypted=True — unencrypted DB at rest? |
| [`waypoint-py-cdk-db-public`](python/iac/waypoint-py-cdk-db-public.md) | security | DB construct with publicly_accessible=True — public database endpoint? |
| [`waypoint-py-cdk-destructive-removal-policy`](python/iac/waypoint-py-cdk-destructive-removal-policy.md) | security | removal_policy=RemovalPolicy.DESTROY on a data store — data lost on stack delete? |
| [`waypoint-py-cdk-iam-wildcard`](python/iac/waypoint-py-cdk-iam-wildcard.md) | security | IAM PolicyStatement with actions=['*'] / resources=['*'] — over-broad grant? |
| [`waypoint-py-cdk-log-retention-infinite`](python/iac/waypoint-py-cdk-log-retention-infinite.md) | security | LogGroup with no retention= — logs kept forever / no defined window? |
| [`waypoint-py-cdk-s3-no-encryption`](python/iac/waypoint-py-cdk-s3-no-encryption.md) | security | S3 bucket constructed with no encryption= — is data unencrypted at rest? |
| [`waypoint-py-cdk-s3-no-versioning`](python/iac/waypoint-py-cdk-s3-no-versioning.md) | security | S3 bucket with no versioned=True — object history lost, no rollback/audit trail? |
| [`waypoint-py-cdk-s3-public`](python/iac/waypoint-py-cdk-s3-public.md) | security | S3 bucket marked public_read_access / public BPA — intended public exposure? |
| [`waypoint-py-cdk-secret-literal-env`](python/iac/waypoint-py-cdk-secret-literal-env.md) | security | environment={...PASSWORD/SECRET/TOKEN...: '<literal>'} — hard-coded credential in IaC? |
| [`waypoint-py-cdk-sg-open-world`](python/iac/waypoint-py-cdk-sg-open-world.md) | security | security group ingress from Peer.any_ipv4/any_ipv6 — open to the world? |

### logic
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-py-logic-constant-condition`](python/logic/waypoint-py-logic-constant-condition.md) | logic | constant if-condition (if True / if False) — dead branch or a leftover debug toggle? |
| [`waypoint-py-logic-eq-none`](python/logic/waypoint-py-logic-eq-none.md) | logic | `== None` / `!= None` instead of `is None` — a custom __eq__ could make this check lie? |
| [`waypoint-py-logic-is-literal`](python/logic/waypoint-py-logic-is-literal.md) | logic | identity check against a literal ($X is <int/str>) — value comparison (==) almost certainly meant? |
| [`waypoint-py-logic-return-in-finally`](python/logic/waypoint-py-logic-return-in-finally.md) | logic | control flow (return/break/continue) inside finally — silently discards exceptions or the real return value? |
| [`waypoint-py-logic-self-comparison`](python/logic/waypoint-py-logic-self-comparison.md) | logic | self-comparison ($X == $X / $X != $X) is constant — likely a typo for a different operand? |

### security
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-py-archive-extractall`](python/security/waypoint-py-archive-extractall.md) | security, abuse | zip/tar extractall on untrusted archive — path traversal (zip/tar slip)? |
| [`waypoint-py-cipher-ecb`](python/security/waypoint-py-cipher-ecb.md) | security | AES/DES MODE_ECB — pattern leakage on sensitive plaintext? |
| [`waypoint-py-django-csrf-exempt`](python/security/waypoint-py-django-csrf-exempt.md) | security, abuse | csrf_exempt on a state-changing view — cross-site request forgery? |
| [`waypoint-py-django-mark-safe`](python/security/waypoint-py-django-mark-safe.md) | security | mark_safe on a non-literal — XSS if the value is user-controlled? |
| [`waypoint-py-django-raw-sql`](python/security/waypoint-py-django-raw-sql.md) | security, abuse | Django .raw/.extra/RawSQL — unparametrized user input reaching the query (SQLi)? |
| [`waypoint-py-eval-exec`](python/security/waypoint-py-eval-exec.md) | security | eval/exec on a non-literal — attacker-controlled input reachable? |
| [`waypoint-py-flask-cors-wildcard`](python/security/waypoint-py-flask-cors-wildcard.md) | security, abuse | Flask-CORS origins="*" — any origin can call authenticated endpoints (CORS bypass)? |
| [`waypoint-py-flask-debug`](python/security/waypoint-py-flask-debug.md) | security | app.run(debug=True) — interactive debugger / RCE exposed in a reachable deploy? |
| [`waypoint-py-hardcoded-secret`](python/security/waypoint-py-hardcoded-secret.md) | security | secret-named variable assigned a string literal — hardcoded credential in source? |
| [`waypoint-py-insecure-random`](python/security/waypoint-py-insecure-random.md) | security | random.* output used as a token/secret/nonce — predictable, should be secrets/os.urandom? |
| [`waypoint-py-insecure-tempfile-mktemp`](python/security/waypoint-py-insecure-tempfile-mktemp.md) | security, edge-case | tempfile.mktemp() — predictable temp path with a create-time race (symlink/TOCTOU)? |
| [`waypoint-py-jinja-autoescape-off`](python/security/waypoint-py-jinja-autoescape-off.md) | security | jinja2 Environment(autoescape=False) — XSS on rendered user content? |
| [`waypoint-py-jwt-verify-disabled`](python/security/waypoint-py-jwt-verify-disabled.md) | security | jwt.decode with verify=False / verify_signature False — signature not enforced (auth bypass)? |
| [`waypoint-py-ldap-filter-fstring`](python/security/waypoint-py-ldap-filter-fstring.md) | security | LDAP search() filter built via f-string/format — LDAP injection from unescaped input? |
| [`waypoint-py-os-popen-system`](python/security/waypoint-py-os-popen-system.md) | security | os.popen/os.system on a built command — command injection if input is untrusted? |
| [`waypoint-py-path-traversal`](python/security/waypoint-py-path-traversal.md) | security | open(join(base, user)) with no containment check — path traversal? |
| [`waypoint-py-sql-string-build`](python/security/waypoint-py-sql-string-build.md) | security, abuse | string-built SQL into execute() — injection if input is untrusted? |
| [`waypoint-py-ssrf-nonliteral-url`](python/security/waypoint-py-ssrf-nonliteral-url.md) | security | HTTP client called with a non-literal URL — SSRF if destination is user-controlled? |
| [`waypoint-py-ssti-render-template-string`](python/security/waypoint-py-ssti-render-template-string.md) | security | render_template_string on a non-literal template — SSTI if input reaches the body? |
| [`waypoint-py-subprocess-shell`](python/security/waypoint-py-subprocess-shell.md) | security | shell=True / os.system — command injection if argument is untrusted? |
| [`waypoint-py-taint-code`](python/security/waypoint-py-taint-code.md) | security | tainted input reaches eval/exec — code injection along this dataflow? |
| [`waypoint-py-taint-command`](python/security/waypoint-py-taint-command.md) | security | tainted input reaches a command/shell sink — injection along this dataflow? |
| [`waypoint-py-taint-deserialize`](python/security/waypoint-py-taint-deserialize.md) | security | tainted input reaches pickle/yaml/marshal load — deserialization RCE along this dataflow? |
| [`waypoint-py-taint-path`](python/security/waypoint-py-taint-path.md) | security | tainted input reaches a file path sink — path traversal along this dataflow? |
| [`waypoint-py-taint-sql`](python/security/waypoint-py-taint-sql.md) | security, abuse | tainted input reaches a SQL query unsanitized — injection along this dataflow? |
| [`waypoint-py-taint-ssrf`](python/security/waypoint-py-taint-ssrf.md) | security | tainted input reaches an HTTP-client URL — SSRF along this dataflow? |
| [`waypoint-py-taint-ssti`](python/security/waypoint-py-taint-ssti.md) | security | tainted input reaches a template render — server-side template injection along this dataflow? |
| [`waypoint-py-tls-verify-disabled`](python/security/waypoint-py-tls-verify-disabled.md) | security | verify=False / unverified TLS context — MITM exposure? |
| [`waypoint-py-unsafe-deser`](python/security/waypoint-py-unsafe-deser.md) | security | pickle/marshal load of untrusted bytes — RCE on deserialization? |
| [`waypoint-py-weak-hash`](python/security/waypoint-py-weak-hash.md) | security | md5/sha1 — used in a security-sensitive context (collisions/preimage)? |
| [`waypoint-py-weak-tls-proto`](python/security/waypoint-py-weak-tls-proto.md) | security | PROTOCOL_TLSv1/SSLv3 — deprecated protocol enabling downgrade/MITM? |
| [`waypoint-py-xxe`](python/security/waypoint-py-xxe.md) | security, abuse | XML parse of untrusted input without entity hardening — XXE or entity-expansion DoS? |
| [`waypoint-py-yaml-unsafe-load`](python/security/waypoint-py-yaml-unsafe-load.md) | security | yaml.load without SafeLoader on untrusted input — object injection / RCE? |

## react
### abuse
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-react-heavy-work-in-render`](react/abuse/waypoint-react-heavy-work-in-render.md) | abuse | new RegExp / JSON.parse / .sort() in render path — per-render CPU amplification on large input? |
| [`waypoint-react-inline-prop-literal`](react/abuse/waypoint-react-inline-prop-literal.md) | abuse | inline arrow/object/array literal as a prop — new identity each render defeats memo and storms child re-renders? |

### authz
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-react-authz-clientside-guard`](react/authz/waypoint-react-authz-clientside-guard.md) | security, abuse | authorization decided client-side (isAdmin/role===admin) — is the same check enforced server-side, or is it bypassable? |

### concurrency
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-react-effect-async-no-cleanup`](react/concurrency/waypoint-react-effect-async-no-cleanup.md) | concurrency, edge-case | async effect without cleanup — unmount/stale-closure race? |
| [`waypoint-react-listener-in-effect-no-cleanup`](react/concurrency/waypoint-react-listener-in-effect-no-cleanup.md) | concurrency, edge-case | addEventListener/subscribe in useEffect with no removeEventListener/unsubscribe cleanup — leaked handler firing after unmount? |
| [`waypoint-react-setstate-in-async`](react/concurrency/waypoint-react-setstate-in-async.md) | concurrency, edge-case | setState inside async callback — stale-closure / out-of-order update race? |
| [`waypoint-react-timer-in-effect-no-cleanup`](react/concurrency/waypoint-react-timer-in-effect-no-cleanup.md) | concurrency, edge-case | setInterval/setTimeout in useEffect with no clearInterval/clearTimeout cleanup — fire-after-unmount / duplicate timers? |

### edge-case
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-react-array-index-key`](react/edge-case/waypoint-react-array-index-key.md) | edge-case | array index used as React key in a .map() — state/DOM corruption on reorder? |
| [`waypoint-react-direct-state-mutation`](react/edge-case/waypoint-react-direct-state-mutation.md) | edge-case | in-place mutation of suspected React state (push/splice/field=) — stale UI / skipped re-render? |
| [`waypoint-react-map-no-key`](react/edge-case/waypoint-react-map-no-key.md) | edge-case | JSX element returned from .map() without a key prop — broken reconciliation / remounts? |
| [`waypoint-react-nondeterministic-render`](react/edge-case/waypoint-react-nondeterministic-render.md) | edge-case | Math.random()/new Date()/Date.now() in render body — impure render, hydration mismatch, unstable ids? |
| [`waypoint-react-usestate-from-prop`](react/edge-case/waypoint-react-usestate-from-prop.md) | edge-case | useState(prop) — state frozen at mount, ignores later prop changes? |

### logic
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-react-logic-conditional-hook`](react/logic/waypoint-react-logic-conditional-hook.md) | logic | hook (use*) called inside an if-block — Rules of Hooks violation; state desync / runtime crash? |
| [`waypoint-react-logic-effect-no-deps`](react/logic/waypoint-react-logic-effect-no-deps.md) | logic | useEffect with no dependency array — runs every render; missing `[]` or explicit deps? |

### security
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-react-create-markup-helper`](react/security/waypoint-react-create-markup-helper.md) | security | createMarkup-style {__html} factory from a dynamic value — unsanitized HTML into dangerouslySetInnerHTML (XSS)? |
| [`waypoint-react-dangerous-html`](react/security/waypoint-react-dangerous-html.md) | security | dangerouslySetInnerHTML from non-constant — XSS? |
| [`waypoint-react-insecure-http-url`](react/security/waypoint-react-insecure-http-url.md) | security | plain http:// URL in fetch/href/src — cleartext transport (MITM / mixed content)? |
| [`waypoint-react-process-env-in-client`](react/security/waypoint-react-process-env-in-client.md) | security | process.env.X inside a client component — secret inlined into the JS bundle? |
| [`waypoint-react-target-blank-no-noopener`](react/security/waypoint-react-target-blank-no-noopener.md) | security | target=_blank link missing rel=noopener — reverse tabnabbing? |
| [`waypoint-react-token-in-webstorage`](react/security/waypoint-react-token-in-webstorage.md) | security | auth token/secret in localStorage/sessionStorage — exfiltratable by any XSS on the origin? |
| [`waypoint-react-unsafe-href`](react/security/waypoint-react-unsafe-href.md) | security | href/src bound to a dynamic value — javascript: URI, data: URI, or open redirect? |
| [`waypoint-react-untrusted-prop-spread`](react/security/waypoint-react-untrusted-prop-spread.md) | security, abuse | spread of an arbitrary object into JSX props — prop injection (dangerouslySetInnerHTML / href / handlers)? |

## rust
### abuse
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-rust-alloc-from-size`](rust/abuse/waypoint-rust-alloc-from-size.md) | abuse | Vec::with_capacity/reserve with a variable size — is the size attacker-controlled and unbounded? |
| [`waypoint-rust-infinite-loop`](rust/abuse/waypoint-rust-infinite-loop.md) | abuse | infinite loop (loop / while true) — bounded exit, or a dead loop / CPU busy-spin? |
| [`waypoint-rust-read-unbounded`](rust/abuse/waypoint-rust-read-unbounded.md) | abuse | read_to_end/read_to_string on input — is the source unbounded/attacker-controlled (memory DoS)? |
| [`waypoint-rust-unbounded-recursion`](rust/abuse/waypoint-rust-unbounded-recursion.md) | abuse | self-recursive fn with no visible depth bound — input-driven stack overflow (DoS)? |

### concurrency
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-rust-arc-refcell`](rust/concurrency/waypoint-rust-arc-refcell.md) | concurrency | Arc<RefCell<...>> — non-thread-safe interior mutability shared across threads (data race / panic)? |
| [`waypoint-rust-concurrency-primitive`](rust/concurrency/waypoint-rust-concurrency-primitive.md) | concurrency | spawn/Arc present — unsynchronized shared-state access nearby? |
| [`waypoint-rust-lock-across-await`](rust/concurrency/waypoint-rust-lock-across-await.md) | concurrency | lock().unwrap()/lock().await inside async fn with awaits — is a guard held across an await point (deadlock)? |
| [`waypoint-rust-rc-near-spawn`](rust/concurrency/waypoint-rust-rc-near-spawn.md) | concurrency | Rc::new near thread::spawn — is a non-Send Rc moved across a thread boundary? |
| [`waypoint-rust-static-mut`](rust/concurrency/waypoint-rust-static-mut.md) | concurrency, security | static mut accessed — any concurrent reader/writer (data race)? |
| [`waypoint-rust-unbounded-channel-near-spawn`](rust/concurrency/waypoint-rust-unbounded-channel-near-spawn.md) | concurrency, abuse | unbounded mpsc::channel near spawn — no backpressure, queue grows unbounded? |
| [`waypoint-rust-unsafe-send-sync`](rust/concurrency/waypoint-rust-unsafe-send-sync.md) | concurrency, security | hand-written unsafe Send/Sync — is the cross-thread invariant actually sound? |

### edge-case
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-rust-env-var-unwrap`](rust/edge-case/waypoint-rust-env-var-unwrap.md) | edge-case | env::var(...).unwrap()/expect — missing env var panics the process at startup? |
| [`waypoint-rust-lock-expect-panic`](rust/edge-case/waypoint-rust-lock-expect-panic.md) | edge-case, concurrency | lock().expect()/unwrap() — poisoned lock turns one panic into a cascading crash? |
| [`waypoint-rust-lossy-cast`](rust/edge-case/waypoint-rust-lossy-cast.md) | edge-case | as u8/u16/u32/i32 narrowing cast — can the value overflow the target type and corrupt logic? |
| [`waypoint-rust-panic-family`](rust/edge-case/waypoint-rust-panic-family.md) | edge-case | expect/unreachable/todo/unimplemented/panic — reachable on a real input (DoS)? |
| [`waypoint-rust-panicking-index`](rust/edge-case/waypoint-rust-panicking-index.md) | edge-case | slice/Vec index access — can the index be out of bounds on a real input (panic)? |
| [`waypoint-rust-unwrap-panic`](rust/edge-case/waypoint-rust-unwrap-panic.md) | edge-case | unwrap/expect/panic — reachable panic on a real input (DoS)? |

### logic
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-rust-logic-bool-literal-compare`](rust/logic/waypoint-rust-logic-bool-literal-compare.md) | logic | bool compared to a literal (== true / == false) — redundant; check the condition isn't inverted. |
| [`waypoint-rust-logic-self-comparison`](rust/logic/waypoint-rust-logic-self-comparison.md) | logic | self-comparison ($X == $X / != $X) is constant — likely a typo for a different operand? |

### security
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-rust-command-dynamic-program`](rust/security/waypoint-rust-command-dynamic-program.md) | security, abuse | Command::new(variable) — is the executed program name attacker-controlled? |
| [`waypoint-rust-command-shell`](rust/security/waypoint-rust-command-shell.md) | security | Command::new("sh"/"bash") — interpolated arg leading to command injection? |
| [`waypoint-rust-hardcoded-secret`](rust/security/waypoint-rust-hardcoded-secret.md) | security | credential-named binding = string literal — is it a hardcoded secret? |
| [`waypoint-rust-mem-transmute`](rust/security/waypoint-rust-mem-transmute.md) | security | mem::transmute — could it produce an invalid value or break layout assumptions? |
| [`waypoint-rust-sql-format`](rust/security/waypoint-rust-sql-format.md) | security | query/execute(format!(...)) — does an interpolated value reach the SQL string (injection)? |
| [`waypoint-rust-ssrf-nonliteral-url`](rust/security/waypoint-rust-ssrf-nonliteral-url.md) | security | reqwest::get / Client send with a non-literal URL — SSRF if destination is user-controlled? |
| [`waypoint-rust-taint-command`](rust/security/waypoint-rust-taint-command.md) | security | tainted env/args reaches a Command argument — command injection along this dataflow? |
| [`waypoint-rust-taint-sql`](rust/security/waypoint-rust-taint-sql.md) | security, abuse | tainted env/args reaches a SQL query — injection along this dataflow? |
| [`waypoint-rust-tempfile-predictable`](rust/security/waypoint-rust-tempfile-predictable.md) | security, edge-case | predictable temp path (temp_dir().join(const) / fixed /tmp path) — symlink/TOCTOU race? |
| [`waypoint-rust-tls-verify-disabled`](rust/security/waypoint-rust-tls-verify-disabled.md) | security | danger_accept_invalid_certs(true) / SslVerifyMode::NONE — TLS verification off (MITM)? |
| [`waypoint-rust-unchecked-access`](rust/security/waypoint-rust-unchecked-access.md) | security, edge-case | unchecked get/from_utf8 — can an out-of-bounds index or invalid UTF-8 reach this (UB)? |
| [`waypoint-rust-unsafe-block`](rust/security/waypoint-rust-unsafe-block.md) | security, concurrency | raw unsafe block — is any memory/thread-safety invariant violable on a real input? |

## typescript
### abuse
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-ts-redos`](typescript/abuse/waypoint-ts-redos.md) | abuse, security | RegExp with nested quantifiers on input — catastrophic backtracking (ReDoS)? |
| [`waypoint-ts-unbounded-allocation`](typescript/abuse/waypoint-ts-unbounded-allocation.md) | abuse | new Array(n) with non-literal n — attacker-controlled size forces giant allocation? |
| [`waypoint-ts-unbounded-findmany`](typescript/abuse/waypoint-ts-unbounded-findmany.md) | abuse | findMany() with no take/limit — unbounded result set (missing pagination, memory DoS)? |
| [`waypoint-ts-unbounded-loop`](typescript/abuse/waypoint-ts-unbounded-loop.md) | abuse | while(true)/for(;;) — can input prevent the break and hang the loop (DoS)? |

### authz
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-ts-authz-mass-assignment`](typescript/authz/waypoint-ts-authz-mass-assignment.md) | security, abuse | untrusted req.body bulk-assigned into a model/ORM write — mass assignment / privilege escalation? |
| [`waypoint-ts-authz-privilege-from-request`](typescript/authz/waypoint-ts-authz-privilege-from-request.md) | security, abuse | privilege field (isAdmin/role/permissions/…) set from req input — privilege escalation? |

### concurrency
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-ts-promise-all-race`](typescript/concurrency/waypoint-ts-promise-all-race.md) | concurrency | Promise.all/race over concurrent ops — shared-state write race? |
| [`waypoint-ts-promise-executor-no-reject`](typescript/concurrency/waypoint-ts-promise-executor-no-reject.md) | concurrency, edge-case | new Promise executor with resolve but no reject — error path leaves promise hung? |
| [`waypoint-ts-shared-counter-multi-async`](typescript/concurrency/waypoint-ts-shared-counter-multi-async.md) | concurrency | module-level counter ++/-- inside async fn — lost-update race across concurrent invocations? |
| [`waypoint-ts-shared-mutable-async`](typescript/concurrency/waypoint-ts-shared-mutable-async.md) | concurrency | shared module-level state mutated in async fn — interleaving race across awaits? |
| [`waypoint-ts-timer-leak`](typescript/concurrency/waypoint-ts-timer-leak.md) | concurrency | setInterval / self-rescheduling setTimeout — handle never cleared or ticks overlap? |

### edge-case
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-ts-empty-catch`](typescript/edge-case/waypoint-ts-empty-catch.md) | edge-case | empty catch — a dropped error that should be handled? |
| [`waypoint-ts-json-parse-no-try`](typescript/edge-case/waypoint-ts-json-parse-no-try.md) | edge-case | JSON.parse with no surrounding try/catch — unhandled SyntaxError on bad input? |
| [`waypoint-ts-loose-equality`](typescript/edge-case/waypoint-ts-loose-equality.md) | edge-case | loose == / != — coercion produces a wrong comparison result? |
| [`waypoint-ts-non-null-assertion`](typescript/edge-case/waypoint-ts-non-null-assertion.md) | edge-case | non-null assertion (!) — can the value be null/undefined here? |
| [`waypoint-ts-unguarded-computed-index`](typescript/edge-case/waypoint-ts-unguarded-computed-index.md) | edge-case | arr[computedIndex].prop — index out of range yields undefined, property read throws? |
| [`waypoint-ts-unhandled-promise`](typescript/edge-case/waypoint-ts-unhandled-promise.md) | edge-case | .then() with no .catch and not awaited — unhandled rejection on the error path? |

### iac
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-ts-cdk-db-no-encryption`](typescript/iac/waypoint-ts-cdk-db-no-encryption.md) | security | RDS/Redshift built with no storageEncrypted:true — unencrypted DB at rest? |
| [`waypoint-ts-cdk-db-public`](typescript/iac/waypoint-ts-cdk-db-public.md) | security | DB construct with publiclyAccessible:true — public database endpoint? |
| [`waypoint-ts-cdk-destructive-removal-policy`](typescript/iac/waypoint-ts-cdk-destructive-removal-policy.md) | security | removalPolicy: RemovalPolicy.DESTROY on a data store — data lost on stack delete? |
| [`waypoint-ts-cdk-iam-wildcard`](typescript/iac/waypoint-ts-cdk-iam-wildcard.md) | security | IAM PolicyStatement with actions:['*'] / resources:['*'] — over-broad grant? |
| [`waypoint-ts-cdk-log-retention-infinite`](typescript/iac/waypoint-ts-cdk-log-retention-infinite.md) | security | LogGroup with no retention: prop — logs kept forever / no defined window? |
| [`waypoint-ts-cdk-s3-no-encryption`](typescript/iac/waypoint-ts-cdk-s3-no-encryption.md) | security | S3 bucket constructed with no encryption: prop — is data unencrypted at rest? |
| [`waypoint-ts-cdk-s3-no-versioning`](typescript/iac/waypoint-ts-cdk-s3-no-versioning.md) | security | S3 bucket with no versioned:true — object history lost, no rollback/audit trail? |
| [`waypoint-ts-cdk-s3-public`](typescript/iac/waypoint-ts-cdk-s3-public.md) | security | S3 bucket with publicReadAccess:true / disabled BPA — intended public exposure? |
| [`waypoint-ts-cdk-secret-literal-env`](typescript/iac/waypoint-ts-cdk-secret-literal-env.md) | security | environment={ ...PASSWORD/SECRET/TOKEN...: '<literal>' } — hard-coded credential in IaC? |
| [`waypoint-ts-cdk-sg-open-world`](typescript/iac/waypoint-ts-cdk-sg-open-world.md) | security | security group ingress from Peer.anyIpv4/anyIpv6 — open to the world? |

### logic
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-ts-logic-assignment-in-condition`](typescript/logic/waypoint-ts-logic-assignment-in-condition.md) | logic | assignment (=) used in an if/while condition — meant === comparison? |
| [`waypoint-ts-logic-constant-condition`](typescript/logic/waypoint-ts-logic-constant-condition.md) | logic | constant if-condition (if (true) / if (false)) — dead branch or leftover toggle? |
| [`waypoint-ts-logic-nan-comparison`](typescript/logic/waypoint-ts-logic-nan-comparison.md) | logic | comparison against NaN (=== NaN / != NaN) is always false/true — must use Number.isNaN(). |
| [`waypoint-ts-logic-self-comparison`](typescript/logic/waypoint-ts-logic-self-comparison.md) | logic | self-comparison ($X === $X / !==) is constant — likely a typo for a different operand? |
| [`waypoint-ts-logic-sort-no-comparator`](typescript/logic/waypoint-ts-logic-sort-no-comparator.md) | logic | Array.sort() with no comparator — lexicographic order is wrong for numbers; confirm element type. |

### security
| beacon | axes | hypothesis |
|---|---|---|
| [`waypoint-ts-child-process`](typescript/security/waypoint-ts-child-process.md) | security | child_process exec with interpolation — command injection? |
| [`waypoint-ts-child-process-shell`](typescript/security/waypoint-ts-child-process-shell.md) | security | spawn/execFile with shell:true — command injection via shell metacharacters? |
| [`waypoint-ts-cors-wildcard`](typescript/security/waypoint-ts-cors-wildcard.md) | security, abuse | cors({origin:"*"}) or origin:true — any origin can call authenticated endpoints? |
| [`waypoint-ts-dom-xss-sink`](typescript/security/waypoint-ts-dom-xss-sink.md) | security | non-literal HTML sink — does untrusted input reach it unescaped (DOM XSS)? |
| [`waypoint-ts-eval`](typescript/security/waypoint-ts-eval.md) | security | eval/new Function on dynamic input — code injection? |
| [`waypoint-ts-fs-path-traversal`](typescript/security/waypoint-ts-fs-path-traversal.md) | security | non-literal fs path — path traversal from user-controlled path? |
| [`waypoint-ts-hardcoded-secret`](typescript/security/waypoint-ts-hardcoded-secret.md) | security | credential-named var assigned a string literal — hardcoded secret? |
| [`waypoint-ts-insecure-cookie`](typescript/security/waypoint-ts-insecure-cookie.md) | security, abuse | res.cookie / cookie.serialize without httpOnly+secure+sameSite — session/auth cookie exposed? |
| [`waypoint-ts-open-redirect`](typescript/security/waypoint-ts-open-redirect.md) | security | non-literal redirect/location target — open redirect from user input? |
| [`waypoint-ts-postmessage-origin`](typescript/security/waypoint-ts-postmessage-origin.md) | security | postMessage('*') / message listener — origin unchecked (data injection)? |
| [`waypoint-ts-proto-pollution-merge`](typescript/security/waypoint-ts-proto-pollution-merge.md) | security | Object.assign over JSON.parse — prototype pollution via __proto__ key? |
| [`waypoint-ts-sql-template-injection`](typescript/security/waypoint-ts-sql-template-injection.md) | security | interpolated SQL template — is an interpolated value untrusted (SQL injection)? |
| [`waypoint-ts-ssrf-nonliteral-url`](typescript/security/waypoint-ts-ssrf-nonliteral-url.md) | security | axios/fetch/http.get with a non-literal URL — SSRF if destination is user-controlled? |
| [`waypoint-ts-taint-command`](typescript/security/waypoint-ts-taint-command.md) | security | tainted input reaches a child_process sink — command injection along this dataflow? |
| [`waypoint-ts-taint-redirect`](typescript/security/waypoint-ts-taint-redirect.md) | security | tainted input reaches a redirect/location target — open redirect along this dataflow? |
| [`waypoint-ts-taint-sql`](typescript/security/waypoint-ts-taint-sql.md) | security, abuse | tainted input reaches a SQL query string — injection along this dataflow? |
| [`waypoint-ts-taint-ssrf`](typescript/security/waypoint-ts-taint-ssrf.md) | security | tainted input reaches an HTTP-client URL — SSRF along this dataflow? |
| [`waypoint-ts-taint-xss`](typescript/security/waypoint-ts-taint-xss.md) | security | tainted input reaches an HTML sink unescaped — DOM XSS along this dataflow? |
| [`waypoint-ts-vm-runincontext`](typescript/security/waypoint-ts-vm-runincontext.md) | security | vm.runIn*Context on a non-literal — code injection / RCE (vm is not a sandbox)? |
| [`waypoint-ts-weak-jwt`](typescript/security/waypoint-ts-weak-jwt.md) | security | JWT alg none or decode-as-verify — signature not enforced (auth bypass)? |

## Off-the-shelf detectors
| tool | default axes | doc |
|---|---|---|
| bandit | security | [off-the-shelf/bandit.md](off-the-shelf/bandit.md) |
| cargo-audit | security | [off-the-shelf/cargo-audit.md](off-the-shelf/cargo-audit.md) |
| cargo-geiger | concurrency, security | [off-the-shelf/cargo-geiger.md](off-the-shelf/cargo-geiger.md) |
| cargo-mutants | logic | [off-the-shelf/cargo-mutants.md](off-the-shelf/cargo-mutants.md) |
| clippy | edge-case | [off-the-shelf/clippy.md](off-the-shelf/clippy.md) |
| codeql | security | [off-the-shelf/codeql.md](off-the-shelf/codeql.md) |
| eslint | edge-case | [off-the-shelf/eslint.md](off-the-shelf/eslint.md) |
| fast-check | logic, edge-case | [off-the-shelf/fast-check.md](off-the-shelf/fast-check.md) |
| fuzz | logic, edge-case | [off-the-shelf/fuzz.md](off-the-shelf/fuzz.md) |
| gitleaks | security | [off-the-shelf/gitleaks.md](off-the-shelf/gitleaks.md) |
| hypothesis | logic, edge-case | [off-the-shelf/hypothesis.md](off-the-shelf/hypothesis.md) |
| mypy | edge-case | [off-the-shelf/mypy.md](off-the-shelf/mypy.md) |
| npm-audit | security | [off-the-shelf/npm-audit.md](off-the-shelf/npm-audit.md) |
| osv-scanner | security | [off-the-shelf/osv-scanner.md](off-the-shelf/osv-scanner.md) |
| pip-audit | security | [off-the-shelf/pip-audit.md](off-the-shelf/pip-audit.md) |
| proptest | logic, edge-case | [off-the-shelf/proptest.md](off-the-shelf/proptest.md) |
| race-detector | logic, concurrency | [off-the-shelf/race-detector.md](off-the-shelf/race-detector.md) |
| ruff | edge-case | [off-the-shelf/ruff.md](off-the-shelf/ruff.md) |
| trivy | security | [off-the-shelf/trivy.md](off-the-shelf/trivy.md) |
