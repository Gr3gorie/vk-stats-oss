import { z } from "zod";

import { BACKEND_BASE_URL } from "@/api/config";
import { betterFetch } from "@/api/fetch";

export type GroupsGetLastUpdatedRequest = {
  group_url: string;
};

export const GroupsLastUpdated = z.object({
  last_updated_at: z
    .string()
    .transform((value) => new Date(value))
    .nullable(),
});

export async function getLastUpdated(request: GroupsGetLastUpdatedRequest) {
  const searchParams = new URLSearchParams(request);
  const url = `${BACKEND_BASE_URL}/groups/last-updated?${searchParams.toString()}`;

  const response = await betterFetch(url, { method: "GET" });
  if (!response.ok) {
    throw new Error(`Failed to get last updated: ${await response.text()}`);
  }

  const parseResult = GroupsLastUpdated.safeParse(await response.json());
  if (!parseResult.success) {
    throw new Error(
      `Failed to parse last updated: ${parseResult.error.errors}`,
    );
  }

  return parseResult.data;
}
