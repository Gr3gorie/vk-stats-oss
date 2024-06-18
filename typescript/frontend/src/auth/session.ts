import "server-only";

import { cookies } from "next/headers";

import { AUTH_COOKIE_NAME, AuthCookieValue } from "@/api/auth/cookies";

import { verifyAuthCookie } from "./verify";

export async function extractSessionFromCookies() {
  const cookie = cookies().get(AUTH_COOKIE_NAME);

  try {
    const value = await verifyAuthCookie(cookie?.value ?? "");
    return AuthCookieValue.parse(value.payload);
  } catch (error) {
    return null;
  }
}
