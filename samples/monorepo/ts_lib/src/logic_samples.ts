// Logic-smell fixtures — WAYPOINT-PLANT should fire, WAYPOINT-OK must not.

export function assignCond(x: number, y: number): number {
  // WAYPOINT-PLANT: waypoint-ts-logic-assignment-in-condition
  if (x = y) {
    return 1;
  }
  // WAYPOINT-OK: a comparison, not an assignment
  if (x === y) {
    return 2;
  }
  return 0;
}

export function sortNums(nums: number[]): number[] {
  // WAYPOINT-PLANT: waypoint-ts-logic-sort-no-comparator
  return nums.sort();
}

export function sortOk(nums: number[]): number[] {
  // WAYPOINT-OK: explicit numeric comparator
  return nums.sort((a, b) => a - b);
}

export function selfCmp(a: number, b: number): boolean {
  // WAYPOINT-PLANT: waypoint-ts-logic-self-comparison
  if (a === a) {
    return true;
  }
  // WAYPOINT-OK: distinct operands
  return a === b;
}

export function constCond(x: boolean): number {
  // WAYPOINT-PLANT: waypoint-ts-logic-constant-condition
  if (true) {
    return 1;
  }
  // WAYPOINT-OK: a real condition
  if (x) {
    return 2;
  }
  return 0;
}

export function nanCmp(x: number): boolean {
  // WAYPOINT-PLANT: waypoint-ts-logic-nan-comparison
  if (x === NaN) {
    return true;
  }
  // WAYPOINT-OK: the correct NaN test
  return Number.isNaN(x);
}
