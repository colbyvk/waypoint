// Authz fixtures — WAYPOINT-PLANT fires, WAYPOINT-OK must not.
declare const req: any;
declare const prisma: any;

class User {
  name = "";
  isAdmin = false;
  constructor(_data?: unknown) {}
}

export function massAssign(user: User) {
  // WAYPOINT-PLANT: waypoint-ts-authz-mass-assignment
  Object.assign(user, req.body);
  return user;
}

export function createFromBody() {
  // WAYPOINT-PLANT: waypoint-ts-authz-mass-assignment
  return new User(req.body);
}

export function prismaUpdate(id: string) {
  // WAYPOINT-PLANT: waypoint-ts-authz-mass-assignment
  return prisma.user.update({ where: { id }, data: req.body });
}

export function massAssignOk(user: User) {
  // WAYPOINT-OK: explicit, whitelisted field
  Object.assign(user, { name: req.body.name });
  return user;
}

export function setPriv(user: User) {
  // WAYPOINT-PLANT: waypoint-ts-authz-privilege-from-request
  user.isAdmin = req.body.isAdmin;
  return user;
}

export function setPrivOk(user: User) {
  // WAYPOINT-OK: privilege not from request
  user.isAdmin = false;
  return user;
}
