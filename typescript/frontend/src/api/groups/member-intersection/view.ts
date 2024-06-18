import { z } from "zod";

import { BACKEND_BASE_URL } from "@/api/config";
import { betterFetch } from "@/api/fetch";
import { JobInfo, JobStatus } from "@/api/job";

export type GroupsViewMemberIntersectionRequest = {
  request_id: string;
};

export type GroupsMemberIntersectionRequestGroup = z.infer<
  typeof GroupsMemberIntersectionRequestGroup
>;
export const GroupsMemberIntersectionRequestGroup = z.object({
  id: z.number(),
  name: z.string(),
  screen_name: z.string(),
  members_count: z.number(),
  photo_url: z.string().nullable(),
});

export type GroupsMemberIntersectionRequestGroupUpdateJob = z.infer<
  typeof GroupsMemberIntersectionRequestGroupUpdateJob
>;
export const GroupsMemberIntersectionRequestGroupUpdateJob = z.object({
  group_id: z.number(),
  status: JobStatus,
  info: JobInfo,
});

export const GroupsMemberIntersectionRequest = z.object({
  groups: z.array(GroupsMemberIntersectionRequestGroup),
  update_jobs: z.array(GroupsMemberIntersectionRequestGroupUpdateJob),
  intersection_member_ids: z.array(z.number()),
});

export async function viewIntersectionRequest(
  request: GroupsViewMemberIntersectionRequest,
) {
  const response = await betterFetch(
    `${BACKEND_BASE_URL}/groups/member-intersection/${request.request_id}`,
    {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to view intersection request: ${await response.text()}`,
    );
  }

  return GroupsMemberIntersectionRequest.parse(await response.json());
}
