import { z } from "zod";

import { BACKEND_BASE_URL } from "../config";

////////////////////////////////////////////////////////////////////////////////////////////////////

export type GetSignInInfoRequest = {
  redirect_uri: string;
  state?: string;
};

export type SignInInfo = z.infer<typeof SignInInfo>;
export const SignInInfo = z.object({
  authorize_url: z.string(),
});

export async function getSignInInfo(request: GetSignInInfoRequest) {
  const queryParams = new URLSearchParams(request);
  const url = new URL(
    `${BACKEND_BASE_URL}/auth/sign-in/info?${queryParams.toString()}`,
  );

  const response = await fetch(url, {
    credentials: "include",
  });
  if (!response.ok) {
    throw new Error(`Failed to get sign-in info: ${await response.text()}`);
  }

  return SignInInfo.parse(await response.json());
}

////////////////////////////////////////////////////////////////////////////////////////////////////

export type FinishSignInRequest = {
  code: string;
  redirect_uri: string;
};

export async function finishSignIn(request: FinishSignInRequest) {
  const response = await fetch(`${BACKEND_BASE_URL}/auth/sign-in/finish`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Failed to finish sign-in: ${await response.text()}`);
  }
}
