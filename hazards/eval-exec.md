# eval/exec (or eval/new Function) on dynamic input

- **Axes:** security
- **Languages:** Python, TypeScript
- **Generated rule(s):** `waypoint-py-eval-exec`, `waypoint-ts-eval`
- **Agent hypothesis (Python):** "eval/exec on a non-literal — attacker-controlled input reachable?"
- **Agent hypothesis (TypeScript):** "eval/new Function on dynamic input — code injection?"

## What it is
The code runs a string as live program code: Python's `eval()` / `exec()`, or
JavaScript's `eval()` / `new Function(...)`. If any part of that string can come from
outside, the caller is no longer giving you *data* — they are giving you *code to run*,
which means arbitrary code execution. This is one of the highest-severity shapes Waypoint
looks for. The rules deliberately ignore `eval`/`exec` of a plain hard-coded literal
(rarely interesting) and flag the rest so the agent can trace where the string came from.

## Bad (flagged)
```python
# samples/monorepo/py_service/app.py
@app.route("/calc")
def calc():
    formula = request.args.get("formula", "1+1")
    result = eval(formula)            # request value executed as code
    return jsonify({"result": result})
```
```ts
// samples/monorepo/ts_lib/src/exec.ts
export function evalExpr(userStr: string): unknown {
  return eval(userStr);              // caller's string executed as code
}
export function makeFn(userStr: string): Function {
  return new Function("x", userStr); // caller's string compiled into a function
}
```

## Acceptable (not a problem)
```python
# No WAYPOINT-OK control exists in the sample; minimal correct versions below.
# Parse the value as data with a safe, non-code evaluator instead of eval().
import ast
def calc(formula: str):
    return ast.literal_eval(formula)  # only literals; cannot execute code
```
```ts
// Use JSON.parse (data, not code) instead of eval/new Function.
export function parseConfig(userStr: string): unknown {
  return JSON.parse(userStr);         // parses data; no code execution
}
```

## Notes for the agent
- **Confirms a real concern:** the string passed to eval/exec/new Function can be
  traced back to any external source (request, header, file, env var, message).
- **Dismisses it:** the argument is a fixed literal or built only from trusted
  constants, or the work can be (and should be) done with a data parser like
  `ast.literal_eval` / `JSON.parse`.
- There is almost never a good reason to keep `eval`/`exec`/`new Function` on
  external input — if confirmed, recommend replacing it, not sanitizing around it.
