import { match } from "ts-pattern";
import { z } from "zod";

export const JobStatus = z.enum([
  "PENDING",
  "RUNNING",
  "CANCELLED",
  "SUCCEEDED",
  "FAILED",
]);

export function isJobCompleted(status: z.infer<typeof JobStatus>): boolean {
  return match(status)
    .with("PENDING", () => false)
    .with("RUNNING", () => false)
    .with("CANCELLED", () => true)
    .with("SUCCEEDED", () => true)
    .with("FAILED", () => true)
    .exhaustive();
}

export const PendingJobInfo = z.object({
  type: z.literal(JobStatus.Values.PENDING),
});

export const RunningJobInfo = z.object({
  type: z.literal(JobStatus.Values.RUNNING),
  progress: z
    .object({
      num_updated: z.number(),
      num_total: z.number(),
    })
    .nullable(),
});

export const CancelledJobInfo = z.object({
  type: z.literal(JobStatus.Values.CANCELLED),
});

export const SucceededJobInfo = z.object({
  type: z.literal(JobStatus.Values.SUCCEEDED),
  completed_at: z.string(),
});

export const FailedJobInfo = z.object({
  type: z.literal(JobStatus.Values.FAILED),
  // error: z.string(),
  completed_at: z.string(),
});

export type JobInfo = z.infer<typeof JobInfo>;
export const JobInfo = z.union([
  PendingJobInfo,
  RunningJobInfo,
  CancelledJobInfo,
  SucceededJobInfo,
  FailedJobInfo,
]);
