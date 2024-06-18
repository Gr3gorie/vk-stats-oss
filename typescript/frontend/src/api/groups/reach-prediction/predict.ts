import { z } from "zod";

import { BACKEND_BASE_URL } from "@/api/config";
import { betterFetch } from "@/api/fetch";

export type GroupsPredictReachRequest = z.infer<
  typeof GroupsPredictReachRequest
>;
export const GroupsPredictReachRequest = z.object({
  group_url: z.string(),
  period_from: z.string(),
  granularity: z.enum(["DAY", "WEEK", "MONTH"]),
});

export type Reach = z.infer<typeof Reach>;
export const Reach = z.object({
  date: z.string(),
  reach: z.number(),
});

export type GroupsPredictReachResponse = z.infer<
  typeof GroupsPredictReachResponse
>;
export const GroupsPredictReachResponse = z.object({
  group_name: z.string(),
  existing: z.array(Reach),
  prediction: z.array(Reach),
});

export async function predictReach(
  request: GroupsPredictReachRequest,
): Promise<GroupsPredictReachResponse> {
  console.log("Request", JSON.stringify(request, null, 2));

  const response = await betterFetch(
    `${BACKEND_BASE_URL}/groups/reach/predict`,
    {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to predict reach: ${await response.text()}`);
  }

  return GroupsPredictReachResponse.parse(await response.json());
}
