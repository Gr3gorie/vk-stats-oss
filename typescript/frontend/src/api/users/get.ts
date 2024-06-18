import { z } from "zod";

import { BACKEND_BASE_URL } from "../config";
import { betterFetch } from "../fetch";
import { User } from "./types";

export type GetUsersRequest = {
  type: "FROM_GROUP_MEMBER_INTERSECTION";
  request_id: string;
};

export async function getUsers(request: GetUsersRequest): Promise<Array<User>> {
  const response = await betterFetch(`${BACKEND_BASE_URL}/users/`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Failed to get users: ${await response.text()}`);
  }

  return z.array(User).parse(await response.json());
}
