import { z } from "zod";

import { BACKEND_BASE_URL } from "@/api/config";
import { betterFetch } from "@/api/fetch";
import { JobInfo, JobStatus } from "@/api/job";

export type UsersAveragePortraitRequest = {
  request_id: string;
};

export const UsersAveragePortraitRequestViewGroup = z.object({
  id: z.number(),
  name: z.string(),
  screen_name: z.string(),
  members_count: z.number(),
  photo_url: z.string().nullable(),
});

export const UsersAveragePortraitRequestViewGroupUpdateJob = z.object({
  group_id: z.number(),
  status: JobStatus,
  info: JobInfo,
});

export type PortraitStats = z.infer<typeof PortraitStats>;
export const PortraitStats = z.object({
  label: z.string(),
  value: z.string(),
});

export type StatPoint = z.infer<typeof StatPoint>;
export const StatPoint = z.object({
  label: z.string(),
  value: z.number(),
  color: z.string(),
});

export type CharacteristicStats = z.infer<typeof CharacteristicStats>;
export const CharacteristicStats = z.object({
  name: z.string(),
  values: z.array(StatPoint),
});

export type AveragePortrait = z.infer<typeof AveragePortrait>;
export const AveragePortrait = z.object({
  portrait: z.array(PortraitStats),
  main_stats: z.array(CharacteristicStats),
  additional_stats: z.array(CharacteristicStats),
  hidden_amount: z.number(),
  deleted_amount: z.number(),
});

export const UsersAveragePortraitRequestView = z.object({
  groups: z.array(UsersAveragePortraitRequestViewGroup),
  update_jobs: z.array(UsersAveragePortraitRequestViewGroupUpdateJob),
  num_total_users: z.number(),
  average_portrait: AveragePortrait.nullable(),
});

export async function viewAveragePortraitRequest(
  request: UsersAveragePortraitRequest,
) {
  const response = await betterFetch(
    `${BACKEND_BASE_URL}/users/average-portrait/${request.request_id}`,
    {
      method: "GET",
      headers: {
        "content-type": "application/json",
      },
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to view average portrait request: ${await response.text()}`,
    );
  }

  return UsersAveragePortraitRequestView.parse(await response.json());
}
