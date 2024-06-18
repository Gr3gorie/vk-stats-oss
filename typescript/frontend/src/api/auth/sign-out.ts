import { BACKEND_BASE_URL } from "../config";

export async function signOut() {
  const response = await fetch(`${BACKEND_BASE_URL}/auth/sign-out`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(`Failed to sign out: ${await response.text()}`);
  }
}
