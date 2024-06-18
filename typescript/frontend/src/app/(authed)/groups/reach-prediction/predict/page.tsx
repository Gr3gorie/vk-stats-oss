import { redirect } from "next/navigation";
import React, { Suspense } from "react";

import { GroupsPredictReachRequest } from "@/api/groups/reach-prediction/predict";

import { RingsLoader } from "@/components/loaders/rings";

import { Content } from "./content";

export default function Page({
  searchParams: rawSearchParams,
}: {
  searchParams: unknown;
}) {
  const searchParams = GroupsPredictReachRequest.safeParse(rawSearchParams);
  if (!searchParams.success) {
    redirect("/groups/reach-prediction");
  }

  return (
    <div className="grid w-full grid-cols-[1fr_1024px_1fr] py-24 *:col-span-1 *:col-start-2 [&>.full-bleed]:col-span-3 [&>.full-bleed]:col-start-1">
      <h1 className="text-3xl font-bold">Предсказание охвата</h1>
      <div className="h-12" />
      <Suspense
        key={JSON.stringify(searchParams.data)}
        fallback={
          <RingsLoader size="160" className="mx-auto mt-12 text-slate-400" />
        }
      >
        <Content request={searchParams.data} />
      </Suspense>
    </div>
  );
}
