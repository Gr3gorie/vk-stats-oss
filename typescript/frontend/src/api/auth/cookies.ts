import { z } from "zod";

export const AUTH_COOKIE_NAME = "sid";

export type AuthCookieValue = z.infer<typeof AuthCookieValue>;
export const AuthCookieValue = z.object({
  user_id: z.number(),
  user_first_name: z.string(),
  user_last_name: z.string(),
});
