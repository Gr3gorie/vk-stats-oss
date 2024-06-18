import { z } from "zod";

import { BACKEND_BASE_URL } from "@/api/config";
import { betterFetch } from "@/api/fetch";

export type GroupsRequestMemberIntersectionRequest = {
  groups: Array<{
    url: string;
    freshness: "FRESH" | "STALE";
  }>;
};

export type InvalidGroupUrl = z.infer<typeof InvalidGroupUrl>;
export const InvalidGroupUrl = z.object({
  url: z.string(),
  index: z.number(),
  reason: z.enum(["NOT_VK", "MISSING_GROUP", "FAILED_TO_RESOLVE", "NOT_GROUP"]),
});

export const GroupsMemberIntersectionInvalidUrls = z.object({
  type: z.literal("INVALID_URLS"),
  invalid_urls: z.array(InvalidGroupUrl),
});

export const GroupsMemberIntersectionReachedLimits = z.object({
  type: z.literal("REACHED_LIMITS"),
  min_num_groups: z.number(),
  max_num_groups: z.number(),
});

export const GroupsMemberIntersectionDuplicateGroups = z.object({
  type: z.literal("DUPLICATE_GROUPS"),
});

export const GroupsMemberIntersectionInfo = z.object({
  type: z.literal("INFO"),
  request_id: z.string().uuid(),
});

export const UserMissingAccessToken = z.object({
  type: z.literal("MISSING_ACCESS_TOKEN"),
});

export type GroupsMemberIntersectionResult = z.infer<
  typeof GroupsMemberIntersectionResult
>;
export const GroupsMemberIntersectionResult = z.discriminatedUnion("type", [
  GroupsMemberIntersectionInvalidUrls,
  GroupsMemberIntersectionReachedLimits,
  GroupsMemberIntersectionDuplicateGroups,
  GroupsMemberIntersectionInfo,
  UserMissingAccessToken,
]);

export async function requestMemberIntersection(
  request: GroupsRequestMemberIntersectionRequest,
): Promise<GroupsMemberIntersectionResult> {
  const response = await betterFetch(
    `${BACKEND_BASE_URL}/groups/member-intersection`,
    {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to request member intersection: ${await response.text()}`,
    );
  }

  return GroupsMemberIntersectionResult.parse(await response.json());
}
