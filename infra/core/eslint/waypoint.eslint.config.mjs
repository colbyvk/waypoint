// Waypoint's own ESLint flat config.
//
// detectors/run_all.sh runs ESLint with `--no-config-lookup --config <this file>`
// so a SCANNED project's own eslint.config.* and its plugins are NEVER loaded.
// That matters for security: ESLint imports (executes) the project's config module
// and every plugin it lists, so reading an untrusted project's config would run
// attacker-controlled code. We also run Waypoint's OWN eslint binary (not the
// target's), so no code from the scanned tree is executed.
//
// Core rules need no plugins and always run. typescript-eslint (for parsing .ts),
// eslint-plugin-security and eslint-plugin-react-hooks are added only if they
// resolve from Waypoint's install — best-effort, so this is safe with nothing else
// present. (Waypoint's Semgrep rules already cover most of this surface.)

async function tryImport(name) {
  try { const m = await import(name); return m.default ?? m; } catch { return null; }
}

const tseslint   = await tryImport("typescript-eslint");
const security   = await tryImport("eslint-plugin-security");
const reactHooks = await tryImport("eslint-plugin-react-hooks");

// Core ESLint rules that map to Waypoint axes (no plugin required).
const coreRules = {
  "no-eval": "error",
  "no-implied-eval": "error",
  "no-new-func": "error",
  "no-script-url": "error",
  "no-cond-assign": ["error", "always"],
  "no-return-assign": ["error", "always"],
  "no-constant-condition": "error",
  "no-self-compare": "error",
  "use-isnan": "error",
  "valid-typeof": "error",
  "no-dupe-keys": "error",
  "no-unsafe-negation": "error",
  "no-unreachable": "error",
  "no-fallthrough": "error",
};

const config = [];

// TypeScript needs a real parser — only lint .ts/.tsx if one resolves.
if (tseslint && tseslint.parser) {
  config.push({
    files: ["**/*.ts", "**/*.tsx", "**/*.mts", "**/*.cts"],
    languageOptions: { parser: tseslint.parser },
    rules: coreRules,
  });
}
config.push({ files: ["**/*.js", "**/*.jsx", "**/*.mjs", "**/*.cjs"], rules: coreRules });

if (security) {
  config.push({
    plugins: { security },
    rules: {
      "security/detect-eval-with-expression": "error",
      "security/detect-child-process": "warn",
      "security/detect-non-literal-require": "warn",
      "security/detect-unsafe-regex": "warn",
    },
  });
}

if (reactHooks) {
  config.push({
    files: ["**/*.jsx", "**/*.tsx"],
    plugins: { "react-hooks": reactHooks },
    rules: { "react-hooks/rules-of-hooks": "error", "react-hooks/exhaustive-deps": "warn" },
  });
}

export default config;
