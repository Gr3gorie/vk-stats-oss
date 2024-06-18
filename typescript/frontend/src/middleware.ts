import { MiddlewareConfig, NextResponse, type NextRequest } from "next/server";

import { match } from "ts-pattern";

import { AUTH_COOKIE_NAME, AuthCookieValue } from "./api/auth/cookies";
import { verifyAuthCookie } from "./auth/verify";

////////////////////////////////////////////////////////////////////////////////////////////////////

export const CURRENT_URL_HEADER_NAME = "x-vk-stats-url";
export const REDIRECT_AFTER_QUERY_PARAM_NAME = "redirect-after";

////////////////////////////////////////////////////////////////////////////////////////////////////

export const config: MiddlewareConfig = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};

export async function middleware(request: NextRequest): Promise<NextResponse> {
  ensureCurrentUrlHeader(request);

  const result = await authMiddleware(request);

  console.log("Auth result:", result);

  const response = await match(result)
    .returnType<NextResponse | Promise<NextResponse>>()
    .with({ kind: "unauthed" }, ({ reason: _ }) => {
      return handleUnauthed(request);
    })
    .with({ kind: "authed" }, () => {
      return handleAuthed(request);
    })
    .exhaustive();

  return response;
}

function handleUnauthed(request: NextRequest): NextResponse {
  if (request.nextUrl.pathname.startsWith("/auth")) {
    return NextResponse.next({ headers: request.headers });
  }

  return redirectToSignIn(request);
}

function handleAuthed(request: NextRequest): NextResponse {
  // TODO(TmLev): Handle "redirect-after" here or after auth redirect-callback?
  if (request.nextUrl.pathname.startsWith("/auth")) {
    const redirectAfter = request.nextUrl.searchParams.get(
      REDIRECT_AFTER_QUERY_PARAM_NAME,
    );
    const nextUrl = new URL(redirectAfter ?? "/", request.nextUrl.toString());
    return NextResponse.redirect(nextUrl, { headers: request.headers });
  }

  return NextResponse.next({ headers: request.headers });
}

////////////////////////////////////////////////////////////////////////////////////////////////////

type AuthResult =
  | {
      kind: "unauthed";
      reason: "missing-cookie" | "verification-failed" | "parse-failed";
    }
  | {
      kind: "authed";
    };

async function authMiddleware(request: NextRequest): Promise<AuthResult> {
  const encryptedAuthCookie = request.cookies.get(AUTH_COOKIE_NAME);
  if (!encryptedAuthCookie) {
    return { kind: "unauthed", reason: "missing-cookie" };
  }

  let decryptedAuthCookie;
  try {
    decryptedAuthCookie = await verifyAuthCookie(encryptedAuthCookie.value);
  } catch (error) {
    console.warn("Failed to decrypt auth cookie", error);
    return { kind: "unauthed", reason: "verification-failed" };
  }

  const parseResult = AuthCookieValue.safeParse(decryptedAuthCookie.payload);
  if (!parseResult.success) {
    return { kind: "unauthed", reason: "parse-failed" };
  }

  return { kind: "authed" };
}

////////////////////////////////////////////////////////////////////////////////////////////////////

function redirectToSignIn(request: NextRequest): NextResponse {
  const url = request.nextUrl;

  // Preserve the current URL so the user can be redirected back after signing in.
  // Except when the user is going to the sign-in page.
  const encodedRedirectAfter =
    url.pathname === "/auth/sign-in"
      ? null
      : encodeURIComponent(url.toString());

  const signInUrl = new URL("/auth/sign-in", url);
  if (encodedRedirectAfter) {
    signInUrl.searchParams.set(
      REDIRECT_AFTER_QUERY_PARAM_NAME,
      encodedRedirectAfter,
    );
  }

  const response = NextResponse.redirect(signInUrl, {
    headers: request.headers,
  });

  // Clear the auth cookie.
  response.headers.set(
    "Set-Cookie",
    `${AUTH_COOKIE_NAME}=; Path=/; HttpOnly; Max-Age=0`,
  );

  return response;
}

////////////////////////////////////////////////////////////////////////////////////////////////////

function ensureCurrentUrlHeader(mutRequest: NextRequest) {
  const urlAsString = mutRequest.nextUrl.toString();
  const fromHeader = mutRequest.headers.get(CURRENT_URL_HEADER_NAME);
  if (fromHeader !== urlAsString) {
    mutRequest.headers.set(CURRENT_URL_HEADER_NAME, urlAsString);
  }
}
