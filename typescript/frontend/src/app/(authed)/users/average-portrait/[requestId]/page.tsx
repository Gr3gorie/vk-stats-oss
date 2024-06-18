"use client";

import React, { Suspense, useEffect, useMemo, useState } from "react";

import { ResponsivePie as NivoResponsivePie, PieTooltipProps } from "@nivo/pie";
import { useSuspenseQuery } from "@tanstack/react-query";

import { isJobCompleted } from "@/api/job";
import {
  CharacteristicStats,
  viewAveragePortraitRequest,
} from "@/api/users/average-portrait/view";

import { JobProgress } from "@/components/jobs/progress";
import { RingsLoader } from "@/components/loaders/rings";

////////////////////////////////////////////////////////////////////////////////////////////////////

type PageParams = {
  requestId: string;
};

export default function Page({ params }: { params: PageParams }) {
  return (
    <div className="grid w-full grid-cols-[1fr_1024px_1fr] py-24 *:col-span-1 *:col-start-2 [&>.full-bleed]:col-span-3 [&>.full-bleed]:col-start-1">
      <h1 className="text-3xl font-bold">Средний портрет</h1>
      <div className="h-12" />
      <Suspense
        fallback={
          <RingsLoader size="160" className="mx-auto mt-12 text-slate-400" />
        }
      >
        <Content requestId={params.requestId} />
      </Suspense>
    </div>
  );
}

function Content({ requestId }: { requestId: string }) {
  const [shouldRefetch, setShouldRefetch] = useState<false | undefined>(
    undefined,
  );
  const [refetchInterval, setRefetchInterval] = useState<number | false>(1_000);

  const requestQuery = useSuspenseQuery({
    queryKey: ["users", "average-portrait", requestId],
    queryFn: async () => {
      return await viewAveragePortraitRequest({ request_id: requestId });
    },
    refetchOnMount: shouldRefetch,
    refetchInterval: refetchInterval,
    refetchOnReconnect: shouldRefetch,
    refetchOnWindowFocus: shouldRefetch,
    refetchIntervalInBackground: shouldRefetch,
    retry: shouldRefetch,
    retryOnMount: shouldRefetch,
  });

  const hasPortrait = !!requestQuery.data?.average_portrait;
  useEffect(() => {
    if (hasPortrait) {
      setShouldRefetch(false);
      setRefetchInterval(false);
    }
  }, [hasPortrait]);

  const hasIncompletedJobs = useMemo(() => {
    return (
      requestQuery.data.update_jobs.length > 0 &&
      requestQuery.data.update_jobs.some((j) => !isJobCompleted(j.status))
    );
  }, [requestQuery.data.update_jobs]);

  if (hasIncompletedJobs) {
    return (
      <div>
        <div className="mb-6 text-lg font-[500]">
          Загружаем актуальные данные...
        </div>
        <div className="grid grid-cols-2 gap-x-8 gap-y-4">
          {requestQuery.data.update_jobs.map((j) => (
            <JobProgress
              key={j.group_id}
              job={j}
              group={requestQuery.data.groups.find((g) => g.id === j.group_id)!}
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="text-md">
        <p>
          Было обработано {requestQuery.data.num_total_users} пользователей.
        </p>
        <p>
          В выборку не вошли {requestQuery.data.average_portrait?.hidden_amount}{" "}
          скрытых и {requestQuery.data.average_portrait?.deleted_amount}{" "}
          замороженных/удалённых аккаунтов.
        </p>
      </div>

      <div className="h-12" />

      <h2 className="text-lg font-semibold">
        Среднестатистический пользователь
      </h2>
      <div className="h-4" />
      <div>
        <ul className="list-inside list-disc space-y-3">
          {requestQuery.data.average_portrait?.portrait.map((s) => (
            <li key={s.label}>
              {s.label}: {s.value}
            </li>
          ))}
        </ul>
      </div>

      <div className="h-24" />

      <div className="flex flex-col items-center">
        <SectionTitle>Основная информация</SectionTitle>
        <div className="h-8" />
      </div>
      <div className="full-bleed grid h-96 w-full grid-cols-4 gap-8 px-8">
        {requestQuery.data.average_portrait?.main_stats.map((s) => (
          <StatPie key={s.name} stats={s} />
        ))}
      </div>

      <div className="h-24" />

      <div className="flex flex-col items-center">
        <SectionTitle>Дополнительная информация</SectionTitle>
        <div className="h-8" />
      </div>

      <AdditionalStatsPieRow
        className="full-bleed grid h-96 w-full grid-cols-3 gap-8 px-8"
        stats={
          requestQuery.data.average_portrait?.additional_stats.slice(0, 3) ?? []
        }
      />
      <div className="h-8" />
      <AdditionalStatsPieRow
        className="full-bleed grid h-96 w-full grid-cols-3 gap-8 px-8"
        stats={
          requestQuery.data.average_portrait?.additional_stats.slice(3, 6) ?? []
        }
      />
    </>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-md rounded-md border border-solid border-slate-200 px-16 py-2 font-semibold">
      {children}
    </div>
  );
}

const AdditionalStatsPieRow = React.memo(function AdditionalStatsPieRow({
  stats,
  className,
}: {
  stats: Array<CharacteristicStats>;
  className?: string;
}) {
  return (
    <div className={className}>
      {stats.map((s) => (
        <StatPie key={s.name} stats={s} />
      ))}
    </div>
  );
});

const StatPie = React.memo(function StatPie({
  stats,
}: {
  stats: CharacteristicStats;
}) {
  const data = useMemo(
    () => stats.values.map((v) => ({ ...v, id: v.label })),
    [stats.values],
  );

  const subtitle = useMemo(() => stats.name, [stats.name]);

  return (
    <PieContainer>
      <ResponsivePie legend="known" data={data} />
      <PieSubtitle>{subtitle}</PieSubtitle>
    </PieContainer>
  );
});

////////////////////////////////////////////////////////////////////////////////////////////////////

type PieDatum = {
  label: string;
  value: number;

  color: string;
};

function ResponsivePie({
  data,
  legend,
}: {
  data: Array<PieDatum>;
  legend: "known" | "unknown";
}) {
  const marginRight = 135;
  const marginLeft = 15;

  return (
    <NivoResponsivePie
      data={data}
      //
      enableArcLinkLabels={false}
      sortByValue={false}
      //
      margin={{ right: marginRight, left: marginLeft, top: 20, bottom: 20 }}
      startAngle={0}
      innerRadius={0.5}
      padAngle={0.7}
      activeOuterRadiusOffset={8}
      colors={{ datum: "data.color" satisfies `data.${keyof PieDatum}` }}
      borderWidth={1}
      borderColor={{
        from: "color" satisfies keyof PieDatum,
        modifiers: [["brighter", 0.5]],
      }}
      // arcLabel={(e) => e.value}
      arcLabelsRadiusOffset={0.6}
      arcLabelsSkipAngle={10}
      arcLabelsTextColor={
        "white"
        //   {
        //   from: "color" satisfies keyof PieDatum,
        //   modifiers: [["brighter", 2]],
        // }
      }
      tooltip={(e) => <Tooltip datum={e.datum} />}
      legends={[
        {
          anchor: "right",
          direction: "column",
          justify: false,
          translateX: marginRight - 10,
          itemsSpacing: 10,
          itemWidth: legend === "known" ? 50 : 100,
          itemHeight: 18,
          itemTextColor: "#999",
          itemDirection: "right-to-left",
          itemOpacity: 1,
          symbolSize: 18,
          symbolShape: "circle",
          effects: [
            {
              on: "hover",
              style: {
                itemTextColor: "#000",
              },
            },
          ],
        },
      ]}
    />
  );
}

function Tooltip({ datum }: PieTooltipProps<PieDatum>) {
  return (
    <div className="rounded-sm border border-solid border-slate-200 bg-white p-2 text-sm shadow-lg">
      {datum.label}:{" "}
      <span className="font-semibold">{datum.formattedValue}</span>
    </div>
  );
}

function PieSubtitle({ children }: { children: React.ReactNode }) {
  return <div className="text-sm font-semibold text-slate-800">{children}</div>;
}

function PieContainer({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col items-center rounded-md border border-solid border-slate-100 pb-2">
      {children}
    </div>
  );
}
