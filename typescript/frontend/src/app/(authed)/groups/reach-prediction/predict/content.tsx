"use client";

import { usePathname, useRouter } from "next/navigation";
import React, { startTransition, useMemo, useState } from "react";

import { AxisTick } from "@nivo/axes";
import { CustomLayerProps, ResponsiveLine } from "@nivo/line";
import { useSuspenseQuery } from "@tanstack/react-query";
import { DateRange } from "react-day-picker";
import { match } from "ts-pattern";

import {
  GroupsPredictReachRequest,
  predictReach,
} from "@/api/groups/reach-prediction/predict";

import { DatePicker } from "@/components/ui/date-picker";
import { DateRangePicker } from "@/components/ui/date-range-picker";
import { cn } from "@/lib/utils";

export function Content({ request }: { request: GroupsPredictReachRequest }) {
  const router = useRouter();
  const pathname = usePathname();

  const reachQuery = useSuspenseQuery({
    queryKey: ["groups", "reach-prediction", request],
    queryFn: async () => {
      return await predictReach(request);
    },
    refetchInterval: false,
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    retry: false,
    retryOnMount: false,
    refetchIntervalInBackground: false,
    refetchOnReconnect: false,
  });

  const lineData: Array<FakeDatum> = useMemo(() => {
    const existingData = reachQuery.data.existing.map((p) => ({
      x: p.date,
      y: p.reach,
    }));

    const predictionData = reachQuery.data.prediction.map((p) => ({
      x: p.date,
      y: p.reach,
    }));
    // Connect the last existing data point to the first prediction data point.
    predictionData.unshift({
      x: existingData[existingData.length - 1].x,
      y: existingData[existingData.length - 1].y,
    });

    return [
      {
        id: "Прошлый охват",
        color: "red",
        data: existingData,
      },
      {
        id: "Предсказание",
        color: "red",
        data: predictionData,
      },
    ];
  }, [reachQuery.data]);

  const [periodFrom, setPeriodFrom] = useState<Date | undefined>(
    () => new Date(request.period_from),
  );
  const [granularity, setGranularity] = useState<"DAY" | "WEEK" | "MONTH">(
    request.granularity,
  );

  return (
    <>
      <div className="text-md">
        <p suppressHydrationWarning>
          На основе данных сообщества {reachQuery.data.group_name}, начиная с{" "}
          {new Date(request.period_from).toLocaleDateString("ru")} и заканчивая
          сегодняшним днём.
        </p>

        <p>
          Предсказание построено для{" "}
          {match(granularity)
            .with("DAY", () => "ближайших 10 дней")
            .with("WEEK", () => "ближайших 6 недель")
            .with("MONTH", () => "ближайших 3 месяцев")
            .exhaustive()}
          .
        </p>
      </div>

      <div className="h-12" />

      <div className="flex w-full flex-row items-center justify-between">
        <DatePicker
          date={periodFrom}
          onDateChange={(d) => {
            if (!d) {
              return;
            }

            setPeriodFrom(d);
            startTransition(() => {
              const updatedRequest = {
                ...request,
                period_from: d.toISOString(),
              };
              const searchParams = new URLSearchParams(updatedRequest);
              router.push(
                `/groups/reach-prediction/predict?${searchParams.toString()}`,
              );
            });
          }}
        />

        <DataGranularitySwitcher
          granularity={granularity}
          setGranularity={(g) => {
            setGranularity(g);
            startTransition(() => {
              const updatedRequest = {
                ...request,
                granularity: g,
              };
              const searchParams = new URLSearchParams(updatedRequest);
              router.push(`${pathname}?${searchParams.toString()}`);
            });
          }}
          className="w-fit"
        />
      </div>
      <div className="full-bleed h-80 px-40">
        <MyResponsiveLine data={lineData} />
        {/* <GroupsWithMemberIntersectionBar */}
        {/*   className="h-80 w-full rounded-sm border border-solid border-slate-200" */}
        {/*   style={{ */}
        {/*     // @ts-expect-error */}
        {/*     "--bar-container-padding": "0.5rem", */}
        {/*   }} */}
        {/*   data={barData} */}
        {/* /> */}
      </div>

      <div className="h-16" />
    </>
  );
}

function DataGranularitySwitcher({
  granularity,
  setGranularity,
  className,
}: {
  granularity: "DAY" | "WEEK" | "MONTH";
  setGranularity: (granularity: "DAY" | "WEEK" | "MONTH") => void;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "grid grid-cols-3 items-center gap-1 rounded-md bg-slate-200 p-1 text-sm font-semibold",
        className,
      )}
    >
      <button
        onClick={() => setGranularity("DAY")}
        className={cn(
          "rounded-md px-2 py-1",
          granularity === "DAY" ? "bg-white" : "",
        )}
      >
        Дни
      </button>
      <button
        onClick={() => setGranularity("WEEK")}
        className={cn(
          "rounded-md px-2 py-1",
          granularity === "WEEK" ? "bg-white" : "",
        )}
      >
        Недели
      </button>
      <button
        onClick={() => setGranularity("MONTH")}
        className={cn(
          "rounded-md px-2 py-1",
          granularity === "MONTH" ? "bg-white" : "",
        )}
      >
        Месяцы
      </button>
    </div>
  );
}

type FakeDatum = {
  id: string;
  color: string;
  data: Array<{
    x: string;
    y: number | null;
  }>;
};

function buildFakeData(): FakeDatum {
  const today = new Date();

  const formatter = new Intl.DateTimeFormat("ru", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });

  const data = Array.from({ length: 37 }, (_, i) => {
    const date = new Date(today);
    date.setDate(today.getDate() - 30 + i);

    return {
      x: formatter.format(date),
      y: i < 30 ? Math.floor(Math.random() * 100) : null,
    };
  });

  // data[data.length - 1].y = 0;

  return {
    id: "current",
    color: "red",
    data,
  };
}

function buildFakePredictedData(): FakeDatum {
  const today = new Date();

  const formatter = new Intl.DateTimeFormat("ru", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });

  const data = Array.from({ length: 37 }, (_, i) => {
    const date = new Date(today);
    date.setDate(today.getDate() - 30 + i);

    return {
      x: formatter.format(date),
      y: i + 1 < 30 ? null : Math.floor(Math.random() * 100),
    };
  });

  return {
    id: "predicted",
    color: "red",
    data,
  };
}

// make sure parent container have a defined height when using
// responsive component, otherwise height will be 0 and
// no chart will be rendered.
// website examples showcase many properties,
// you'll often use just a few of them.
const MyResponsiveLine = React.memo(function MyResponsiveLine({
  data,
}: {
  data: Array<FakeDatum>;
}) {
  const numPoints = data.reduce((acc, d) => acc + d.data.length, 0);

  return (
    <ResponsiveLine
      data={data}
      layers={[
        "grid",
        "markers",
        "areas",
        DashedLine,
        "slices",
        "points",
        "axes",
        "legends",
        "mesh",
        "crosshair",
      ]}
      margin={{ top: 50, right: 150, bottom: 30, left: 100 }}
      xScale={{ type: "point" }}
      yScale={{
        type: "linear",
        min: "auto",
        max: "auto",
        reverse: false,
      }}
      // yFormat=" >-.0f"
      axisTop={null}
      axisRight={null}
      axisBottom={{
        renderTick: (tick) => {
          const everyNthTick =
            numPoints < 10 ? 5 : numPoints < 20 ? 8 : numPoints < 40 ? 10 : 30;
          if (tick.tickIndex % everyNthTick !== 0) {
            return <div />;
          }
          return <AxisTick {...tick} />;
        },
        tickSize: 5,
        tickPadding: 5,
        tickRotation: 0,
        // legend: "transportation",
        // legendOffset: 36,
        // legendPosition: "middle",
        // truncateTickAt: 0,
      }}
      axisLeft={{
        tickSize: 5,
        tickPadding: 5,
        tickRotation: 0,
        legend: "Охват",
        legendOffset: -80,
        legendPosition: "middle",
        truncateTickAt: 0,
      }}
      pointSize={10}
      pointColor={{ theme: "background" }}
      pointBorderWidth={2}
      pointBorderColor={{ from: "serieColor" }}
      pointLabel="data.yFormatted"
      pointLabelYOffset={-12}
      enableArea={true}
      //
      crosshairType="cross"
      enableCrosshair={true}
      enableTouchCrosshair={true}
      useMesh={true}
      isInteractive={true}
      //
      legends={[
        {
          anchor: "bottom-right",
          direction: "column",
          justify: false,
          translateX: 100,
          translateY: 0,
          itemsSpacing: 0,
          itemDirection: "left-to-right",
          itemWidth: 80,
          itemHeight: 20,
          itemOpacity: 0.75,
          symbolSize: 12,
          symbolShape: "circle",
          symbolBorderColor: "rgba(0, 0, 0, .5)",
          effects: [
            {
              on: "hover",
              style: {
                itemBackground: "rgba(0, 0, 0, .03)",
                itemOpacity: 1,
              },
            },
          ],
        },
      ]}
    />
  );
});

const DashedLine = ({
  series,
  lineGenerator,
  xScale,
  yScale,
}: CustomLayerProps) => {
  return series.map(({ id, data, color }) => {
    return (
      <path
        key={id}
        d={
          lineGenerator(
            data
              .filter((d) => d.data.y != null)
              .map((d) => ({
                // @ts-expect-error
                x: xScale(d.data.x),
                // @ts-expect-error
                y: yScale(d.data.y),
              })),
          ) ?? undefined
        }
        fill="none"
        stroke={color}
        style={
          // @ts-expect-error
          styleById[id] ?? styleById.default
        }
      />
    );
  });
};

const styleById = {
  predicted: {
    strokeDasharray: "12, 6",
    strokeWidth: 2,
  },
  // current: {
  //   strokeDasharray: "1, 16",
  //   strokeWidth: 8,
  //   strokeLinejoin: "round",
  //   strokeLinecap: "round",
  // },
  // rhum: {
  //     strokeDasharray: '6, 6',
  //     strokeWidth: 4,
  // },
  default: {
    strokeWidth: 2,
  },
} as const;
