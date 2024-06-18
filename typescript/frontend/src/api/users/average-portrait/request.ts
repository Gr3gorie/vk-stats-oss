import { z } from "zod";

import { BACKEND_BASE_URL } from "@/api/config";
import { betterFetch } from "@/api/fetch";

export type UsersAveragePortraitRequest = {
  groups: Array<{
    url: string;
    freshness: "FRESH" | "STALE";
  }>;
};

export const UsersAveragePortraitErrorReachedLimits = z.object({
  type: z.literal("REACHED_LIMITS"),
  min_num_groups: z.number(),
  max_num_groups: z.number(),
});

export const UsersAveragePortraitErrorUserMissingAccessToken = z.object({
  type: z.literal("MISSING_ACCESS_TOKEN"),
});

export const UsersAveragePortraitErrorInvalidGroupUrls = z.object({
  type: z.literal("INVALID_GROUP_URLS"),
  urls: z.array(
    z.object({
      url: z.string(),
      index: z.number(),
    }),
  ),
});

export const UsersAveragePortraitInfo = z.object({
  type: z.literal("INFO"),
  request_id: z.string().uuid(),
});

export type UsersAveragePortraitResult = z.infer<
  typeof UsersAveragePortraitResult
>;
export const UsersAveragePortraitResult = z.union([
  UsersAveragePortraitErrorReachedLimits,
  UsersAveragePortraitErrorUserMissingAccessToken,
  UsersAveragePortraitErrorInvalidGroupUrls,
  UsersAveragePortraitInfo,
]);

export async function requestAveragePortrait(
  request: UsersAveragePortraitRequest,
): Promise<UsersAveragePortraitResult> {
  const response = await betterFetch(
    `${BACKEND_BASE_URL}/users/average-portrait`,
    {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to request average portrait: ${await response.text()}`,
    );
  }

  return UsersAveragePortraitResult.parse(await response.json());
}
