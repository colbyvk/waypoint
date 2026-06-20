# Regex with nested quantifiers on input (ReDoS)

- **Axes:** abuse, security
- **Languages:** Python, TypeScript
- **Generated rule(s):** `waypoint-py-redos`, `waypoint-ts-redos`
- **Agent hypothesis:** "regex with nested quantifiers on input — catastrophic backtracking (ReDoS)?"

## What it is
A regular expression contains a quantifier inside a group that is itself quantified —
shapes like `(a+)+`, `(\w+)+`, or `(.*)*`. On most inputs these behave fine, but a
single crafted string can make the regex engine try an astronomically large number
of ways to match, freezing the thread for seconds or minutes. That is a classic abuse
hazard: a tiny input forces enormous work (ReDoS). The flag marks regexes whose text
matches this nested-quantifier shape when they are run against input.

## Bad (flagged)
```python
# samples/monorepo/py_service/util.py
def validate(token):
    pattern = re.compile(r"(a+)+$")   # nested quantifier: (a+)+
    return pattern.match(token)
```
```ts
// samples/monorepo/ts_lib/src/parse.ts
export function isAllWords(input: string): boolean {
  const re = /(\w+)+$/;               // nested quantifier: (\w+)+
  return re.test(input);
}
```

## Acceptable (not a problem)
```python
# No WAYPOINT-OK control exists in the sample; minimal correct versions below.
# A flat quantifier with no nested repetition cannot backtrack catastrophically.
import re
def validate(token):
    return re.match(r"a+$", token)    # single quantifier — linear time
```
```ts
export function isAllWords(input: string): boolean {
  return /^\w+$/.test(input);        // single quantifier — linear time
}
```

## Notes for the agent
- **Confirms a real concern:** the regex is run against a value that can come from
  outside (request body, query param, uploaded text) AND the pattern really can
  backtrack (overlapping/nested `+`/`*`, often anchored with `$`).
- **Dismisses it:** the input is short and bounded, comes from a trusted source, the
  match runs with a timeout, or the pattern only *looks* nested but cannot actually
  blow up (e.g. the inner and outer parts cannot overlap).
- The fix is usually to rewrite the pattern without nesting (e.g. `\w+` instead of
  `(\w+)+`) — note that if recommending a change.
