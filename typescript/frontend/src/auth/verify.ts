import "server-only";

import { importSPKI, jwtVerify } from "jose";

////////////////////////////////////////////////////////////////////////////////////////////////////

const AUTH_PUBLIC_KEY = (() => {
  const key = process.env.AUTH_PUBLIC_KEY;
  if (!key) {
    throw new Error("AUTH_PUBLIC_KEY is not set");
  }
  return key;
})();

let publicKey = importSPKI(AUTH_PUBLIC_KEY, "RS256");

////////////////////////////////////////////////////////////////////////////////////////////////////

export async function verifyAuthCookie(encryptedValue: string) {
  const key = await publicKey;
  return await jwtVerify(encryptedValue, key);
}
