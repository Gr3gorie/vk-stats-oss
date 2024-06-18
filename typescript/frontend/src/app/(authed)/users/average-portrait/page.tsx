"use client";

import { useRouter } from "next/navigation";

import { match } from "ts-pattern";

import { requestAveragePortrait } from "@/api/users/average-portrait/request";

import { GroupUrlsForm } from "@/components/group-urls-form";

export default function Page() {
  const router = useRouter();

  return (
    <div className="w-full max-w-[1024px] p-24">
      <h1 className="text-3xl font-bold">Средний портрет</h1>
      <div className="h-16" />
      <GroupUrlsForm
        minNumGroups={1}
        maxNumGroups={10}
        submitButtonText="Построить портрет"
        onSubmit={async (form, values) => {
          try {
            const result = await requestAveragePortrait(values);
            match(result).with({ type: "INFO" }, ({ request_id }) => {
              router.push(`/users/average-portrait/${request_id}`);
            });
            // TODO: Match other result variants.
          } catch (error) {
            console.error("Failed to request average portrait", error);
          }
        }}
      />
    </div>
  );
}
