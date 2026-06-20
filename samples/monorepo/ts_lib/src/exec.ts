// Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.
import { exec } from "child_process";

export function evalExpr(userStr: string): unknown {
  // WAYPOINT-PLANT: TS-EVAL [axes: security]
  return eval(userStr);
}

export function makeFn(userStr: string): Function {
  // WAYPOINT-PLANT: TS-EVAL [axes: security]
  return new Function("x", userStr);
}

export function runCmd(userInput: string): void {
  // WAYPOINT-PLANT: TS-CHILD-PROCESS [axes: security]
  exec(`git log ${userInput}`, (err, stdout) => {
    if (err) return;
    console.log(stdout);
  });
}
