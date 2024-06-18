import { match } from "ts-pattern";

import { JobInfo } from "@/api/job";

import { Progress } from "@/components/ui/progress";

export function JobProgress({
  group,
  job,
}: {
  group: {
    name: string;
    photo_url: string | null;
  };
  job: {
    info: JobInfo;
  };
}) {
  const progressValue = match(job.info)
    .with({ type: "PENDING" }, () => 0)
    .with({ type: "RUNNING" }, ({ progress }) =>
      progress ? progress.num_updated / progress.num_total : 0,
    )
    .with({ type: "CANCELLED" }, () => 0)
    .with({ type: "FAILED" }, () => 0)
    .with({ type: "SUCCEEDED" }, () => 1)
    .exhaustive();

  const progressValuePercent = Math.round(progressValue * 100);

  return (
    <div className="flex w-full flex-col gap-2">
      <div className="flex flex-row items-center gap-2">
        {group.photo_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={group.photo_url}
            className="h-8 w-8 rounded-full"
            alt="Group photo"
          />
        ) : (
          <div className="h-8 w-8 rounded-full bg-slate-200" />
        )}
        <div className="text-md">{group.name}</div>
      </div>

      <Progress value={progressValuePercent} max={100} className="w-full" />
    </div>
  );
}
