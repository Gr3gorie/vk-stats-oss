"use client";

import { useRouter } from "next/navigation";

import { toast } from "sonner";
import { match } from "ts-pattern";

import { requestMemberIntersection } from "@/api/groups/member-intersection/request";

import { GroupUrlsForm } from "@/components/group-urls-form";

export default function Page() {
  const router = useRouter();

  return (
    <div className="w-full max-w-[1024px] p-24">
      <h1 className="text-3xl font-bold">Пересечение сообществ</h1>
      <div className="h-16" />

      <GroupUrlsForm
        minNumGroups={2}
        maxNumGroups={10}
        submitButtonText="Найти пересечение"
        onSubmit={async (form, values) => {
          try {
            const result = await requestMemberIntersection(values);
            match(result)
              .with({ type: "INVALID_URLS" }, () => {
                // TODO: Set form errors.
              })
              .with(
                { type: "REACHED_LIMITS" },
                ({ min_num_groups, max_num_groups }) => {
                  toast.error(
                    `Сообществ должно быть от ${min_num_groups} до ${max_num_groups}`,
                  );
                },
              )
              .with({ type: "DUPLICATE_GROUPS" }, () => {
                // TODO: Set form errors.
              })
              .with({ type: "MISSING_ACCESS_TOKEN" }, () => {
                // TODO: Toast with error (or require new sign-in).
              })
              .with({ type: "INFO" }, ({ request_id }) => {
                router.push(`/groups/member-intersection/${request_id}`);
              });
          } catch (error) {
            console.error("Failed to request member intersection", error);
          }
        }}
      />
    </div>
  );
}
