"use client";

import { ReactNode, Suspense, useEffect, useMemo, useState } from "react";

import { ResponsiveBar } from "@nivo/bar";
import { useMutation, useSuspenseQuery } from "@tanstack/react-query";
import { download, generateCsv, mkConfig } from "export-to-csv";
import { Loader2Icon } from "lucide-react";
import { match } from "ts-pattern";

import { viewIntersectionRequest } from "@/api/groups/member-intersection/view";
import { isJobCompleted } from "@/api/job";
import { getUsers } from "@/api/users/get";
import { User } from "@/api/users/types";

import { JobProgress } from "@/components/jobs/progress";
import { RingsLoader } from "@/components/loaders/rings";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

import { userIntoRow, UserRow, UserTable } from "./table";

////////////////////////////////////////////////////////////////////////////////////////////////////

type PageParams = {
  requestId: string;
};

export default function Page({ params }: { params: PageParams }) {
  return (
    <div className="grid w-full grid-cols-[1fr_1024px_1fr] py-24 *:col-span-1 *:col-start-2 [&>.full-bleed]:col-span-3 [&>.full-bleed]:col-start-1">
      <h1 className="text-3xl font-bold">Пересечение сообществ</h1>
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
  const [refetchInterval, setRefetchInterval] = useState<number | false>(1_000);

  const requestQuery = useSuspenseQuery({
    queryKey: ["groups", "member-intersection", requestId],
    queryFn: async () => {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      return await viewIntersectionRequest({ request_id: requestId });
    },
    refetchInterval,
  });

  const hasIncompletedJobs = useMemo(() => {
    return (
      requestQuery.data.update_jobs.length > 0 &&
      requestQuery.data.update_jobs.some((j) => !isJobCompleted(j.status))
    );
  }, [requestQuery.data.update_jobs]);

  useEffect(() => {
    if (!hasIncompletedJobs) {
      setRefetchInterval(false);
    }
  }, [hasIncompletedJobs]);

  const barData = useMemo(() => {
    if (hasIncompletedJobs) {
      return [];
    }

    return requestQuery.data.groups.map((group) => {
      const intersection = requestQuery.data.intersection_member_ids.length;
      return {
        groupName: group.name,
        intersection,
        others: group.members_count - intersection,
      };
    });
  }, [hasIncompletedJobs, requestQuery.data]);

  const numTotalUsers = useMemo(() => {
    const sum = requestQuery.data.groups.reduce(
      (acc, group) => acc + group.members_count,
      0,
    );
    return sum - requestQuery.data.intersection_member_ids.length;
  }, [requestQuery.data]);

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
        <p>Было обработано {numTotalUsers} пользователей.</p>
        <p>
          В пересечение вошли {requestQuery.data.intersection_member_ids.length}{" "}
          пользователей.
        </p>
      </div>

      <div className="h-12" />

      <div className="full-bleed px-40">
        <GroupsWithMemberIntersectionBar
          className="h-80 w-full rounded-sm border border-solid border-slate-200"
          style={{
            // @ts-expect-error
            "--bar-container-padding": "0.5rem",
          }}
          data={barData}
        />
      </div>

      <div className="h-16" />

      <ViewUsers requestId={requestId} />
    </>
  );
}

function ViewUsers({ requestId }: { requestId: string }) {
  const [users, setUsers] = useState<Array<User> | null>(null);
  const userRows = useMemo(() => {
    if (users == null) {
      return [];
    }

    return users.map(userIntoRow);
  }, [users]);

  const getUsersMutation = useMutation({
    mutationKey: ["users", "group-member-intersection", requestId],
    mutationFn: async () => {
      return await getUsers({
        type: "FROM_GROUP_MEMBER_INTERSECTION",
        request_id: requestId,
      });
    },
    onSuccess: (users) => {
      setUsers(users);
    },
  });

  if (users == null) {
    return (
      <Button
        variant="secondary"
        size="lg"
        className="gap-4 data-[is-pending=true]:cursor-wait"
        data-is-pending={getUsersMutation.isPending}
        disabled={getUsersMutation.isPending}
        onClick={() => {
          if (getUsersMutation.isPending) {
            return;
          }
          getUsersMutation.mutate();
        }}
      >
        {getUsersMutation.isPending ? (
          <>
            <Loader2Icon className="animate-spin" />
            Загрузка...
          </>
        ) : (
          "Показать пользователей"
        )}
      </Button>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      <Button
        variant="secondary"
        size="sm"
        className="self-end"
        onClick={() => {
          const csv = generateCsv(csvConfig)(userRows);
          download(csvConfig)(csv);
        }}
      >
        Экспорт в .csv
      </Button>
      <UserTable users={userRows} />
    </div>
  );
}

// mkConfig merges your options with the defaults
// and returns WithDefaults<ConfigOptions>
const csvConfig = mkConfig({
  useKeysAsHeaders: false,
  columnHeaders: [
    {
      key: "id" satisfies keyof UserRow,
      displayLabel: "ID",
    },
    {
      key: "first_name" satisfies keyof UserRow,
      displayLabel: "Имя",
    },
    {
      key: "last_name" satisfies keyof UserRow,
      displayLabel: "Фамилия",
    },
    {
      key: "sex" satisfies keyof UserRow,
      displayLabel: "Пол",
    },
    {
      key: "bdate" satisfies keyof UserRow,
      displayLabel: "Дата рождения",
    },
    {
      key: "country" satisfies keyof UserRow,
      displayLabel: "Страна",
    },
    {
      key: "city" satisfies keyof UserRow,
      displayLabel: "Город",
    },
    {
      key: "relation" satisfies keyof UserRow,
      displayLabel: "Семейное положение",
    },
    {
      key: "political" satisfies keyof UserRow,
      displayLabel: "Политические предпочтения",
    },
    {
      key: "langs" satisfies keyof UserRow,
      displayLabel: "Языки",
    },
    {
      key: "people_main" satisfies keyof UserRow,
      displayLabel: "Главное в людях",
    },
    {
      key: "life_main" satisfies keyof UserRow,
      displayLabel: "Главное в жизни",
    },
    {
      key: "smoking" satisfies keyof UserRow,
      displayLabel: "Отношение к курению",
    },
    {
      key: "alcohol" satisfies keyof UserRow,
      displayLabel: "Отношение к алкоголю",
    },
  ],
});

function GroupsWithMemberIntersectionBar({
  data,
  style,
  className,
}: {
  data: Array<{
    groupName: string;
    intersection: number;
    others: number;
  }>;
  style?: React.CSSProperties;
  className?: string;
}) {
  const [mode, setMode] = useState<"absolute" | "relative">("relative");

  const barData = useMemo(() => {
    if (mode === "absolute") {
      return data;
    }

    return data.map((group) => {
      const total = group.intersection + group.others;
      const intersection = (group.intersection / total) * 100;
      const others = 100 - intersection;
      return { ...group, intersection, others };
    });
  }, [data, mode]);

  return (
    <div className={cn("relative", className)} style={style}>
      <div className="absolute right-[var(--bar-container-padding)] top-[var(--bar-container-padding)] z-10">
        <ModeSwitcher mode={mode} setMode={setMode} />
      </div>

      <ResponsiveBar
        //
        data={barData}
        keys={["intersection", "others"]}
        indexBy="groupName"
        //
        enableTotals={mode !== "relative"}
        enableGridY={false}
        //
        layout="horizontal"
        padding={0.3} // Copy-pasta.
        margin={{ top: 50, right: 130, bottom: 50, left: 300 }} // Copy-pasta.
        //
        //
        labelSkipWidth={60}
        label={(e) => {
          const value = e.value ?? 0;
          return match(mode)
            .with("relative", () => formatPercent(value))
            .with("absolute", () => value.toString())
            .exhaustive();
        }}
        //
        tooltip={(e) => {
          const value = e.value ?? 0;

          return (
            <Tooltip
              id={e.id}
              value={match(mode)
                .with("relative", () => formatPercent(value))
                .with("absolute", () => value)
                .exhaustive()}
              color={e.color}
            />
          );
        }}
        //
        colors={(d) => {
          return match(d.id)
            .with("intersection", () => "#5CC1B6")
            .with("others", () => "#D6C6EC")
            .otherwise(() => {
              throw new Error(`Unknown data id: ${d.id}`);
            });
        }}
        //
        valueScale={{ type: "linear" }} // Copy-pasta.
      />
    </div>
  );
}

function ModeSwitcher({
  mode,
  setMode,
}: {
  mode: "absolute" | "relative";
  setMode: (mode: "absolute" | "relative") => void;
}) {
  return (
    <div className="grid grid-cols-2 items-center gap-1 rounded-md bg-slate-200 p-1 text-sm font-semibold">
      <button
        onClick={() => setMode("absolute")}
        className={cn(
          "rounded-md px-2 py-1",
          mode === "absolute" ? "bg-white" : "",
        )}
      >
        Числа
      </button>
      <button
        onClick={() => setMode("relative")}
        className={cn(
          "rounded-md px-2 py-1",
          mode === "relative" ? "bg-white" : "",
        )}
      >
        Проценты
      </button>
    </div>
  );
}

function Tooltip({
  id,
  value,
  color,
}: {
  id: string | number;
  value: ReactNode;
  color: string;
}) {
  const label = match(id)
    .returnType<string>()
    .with("intersection", () => "Пересечение")
    .with("others", () => "Остальные")
    .otherwise((id) => {
      throw new Error(`Unknown data/tooltip id: ${id}`);
    });
  return (
    <div className="flex flex-row items-center rounded-sm border border-solid border-slate-200 bg-white p-2 text-sm shadow-lg">
      <div
        className="mr-2 size-[12px] rounded-sm"
        style={{ backgroundColor: color }}
      />
      {label}:&nbsp;<div className="font-semibold">{value}</div>
    </div>
  );
}

function formatPercent(value: number) {
  const precision = value < 10 ? 2 : 1;
  return value.toFixed(precision) + "%";
}
