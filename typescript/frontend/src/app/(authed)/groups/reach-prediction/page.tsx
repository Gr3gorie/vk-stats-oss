"use client";

import { useRouter } from "next/navigation";

import { GroupsPredictReachRequest } from "@/api/groups/reach-prediction/predict";

import { GroupUrlsForm } from "@/components/group-urls-form";

export default function Page() {
  const router = useRouter();

  return (
    <div className="w-full max-w-[1024px] p-24">
      <h1 className="text-3xl font-bold">Предсказание охвата</h1>
      <div className="h-16" />

      <GroupUrlsForm
        minNumGroups={1}
        maxNumGroups={1}
        submitButtonText="Предсказать охват"
        onSubmit={(form, values) => {
          const periodFrom = new Date();
          periodFrom.setMonth(periodFrom.getMonth() - 3);

          const searchParams = new URLSearchParams({
            group_url: values.groups[0].url,
            period_from: periodFrom.toISOString(),
            granularity: "DAY",
          } satisfies GroupsPredictReachRequest);

          router.push(
            `/groups/reach-prediction/predict?${searchParams.toString()}`,
          );
        }}
      />
    </div>
  );
}
