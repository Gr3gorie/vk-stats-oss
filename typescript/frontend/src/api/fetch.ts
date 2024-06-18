export function betterFetch(
  input: string | URL | globalThis.Request,
  init?: RequestInit,
): Promise<Response> {
  // TOOD(TmLev): Merge headers and "cookie" header in particular.
  return fetch(input, {
    ...init,
    credentials: "include",
    ...(typeof window === "undefined"
      ? { headers: { Cookie: getCookies() } }
      : {}),
  });
}

function getCookies() {
  try {
    // Dynamically import next/headers to avoid breaking the build.
    const { cookies } = require("next/headers");
    return cookies().toString();
  } catch (e) {
    return null;
  }
}
