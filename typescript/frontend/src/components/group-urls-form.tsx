import { Fragment } from "react";

import { zodResolver } from "@hookform/resolvers/zod";
import { skipToken, useQuery } from "@tanstack/react-query";
import { XIcon } from "lucide-react";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";

import { getLastUpdated } from "@/api/groups/last-updated/get";

import { cn } from "@/lib/utils";

import { Button } from "./ui/button";
import {
  ArrayFieldError,
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "./ui/form";
import { Input } from "./ui/input";

type GroupUrl = z.infer<typeof GroupUrlSchema>;
const GroupUrlSchema = z.object({
  freshness: z.enum(["FRESH", "STALE"]).default("STALE"),
  url: z
    .string()
    .url("Невалидный URL")
    .refine(
      (value) => {
        const startsWithVkCom =
          value.startsWith("https://vk.com/") ||
          value.startsWith("http://vk.com/");
        return startsWithVkCom;
      },
      { message: 'Ссылка должна начинаться с "https://vk.com/"' },
    ),
});

type Freshness = z.infer<typeof GroupUrlSchema>["freshness"];

type FormSchema = z.infer<ReturnType<typeof buildFormSchema>>;
function buildFormSchema(
  minNumGroups: number,
  maxNumGroups: number,
  message: string,
) {
  const FormSchema = z.object({
    groups: z
      .array(GroupUrlSchema)
      .min(minNumGroups, message)
      .max(maxNumGroups, message),
  });

  return FormSchema;
}

function useGroupUrlsForm({
  minNumGroups,
  maxNumGroups,
}: {
  minNumGroups: number;
  maxNumGroups: number;
}) {
  return useForm<FormSchema>({
    resolver: zodResolver(
      buildFormSchema(minNumGroups, maxNumGroups, "Неверное количество"),
    ),
    mode: "onSubmit",
    defaultValues: {
      groups: Array.from(
        { length: minNumGroups },
        () => ({ url: "", freshness: "STALE" }) satisfies GroupUrl,
      ),
    },
  });
}

export function GroupUrlsForm({
  minNumGroups,
  maxNumGroups,
  submitButtonText,
  onSubmit: propOnSubmit,
}: {
  minNumGroups: number;
  maxNumGroups: number;
  submitButtonText: string;
  onSubmit: (
    form: ReturnType<typeof useGroupUrlsForm>,
    values: FormSchema,
  ) => void;
}) {
  const form = useGroupUrlsForm({ minNumGroups, maxNumGroups });
  const { fields: groupUrlsFields } = useFieldArray({
    control: form.control,
    name: "groups",
  });

  function onSubmit(values: FormSchema) {
    console.log("Group URLs form submitted", values);
    propOnSubmit(form, values);
  }

  const numGroups = form.watch("groups").length;

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <div className="grid grid-cols-[auto_1fr_auto] items-center gap-x-4">
          {groupUrlsFields.map((field, index) => (
            <Fragment key={field.id}>
              {index > 0 && <div className="col-span-3 h-6" />}

              <FormField
                control={form.control}
                name={`groups.${index}.url` as const}
                render={({ field }) => (
                  <FormItem className="contents space-y-0">
                    <FormLabel className="justify-self-end">
                      Ссылка на сообщество:
                    </FormLabel>

                    <div className="group relative">
                      <FormControl>
                        <Input
                          placeholder="https://vk.com/..."
                          {...form.register(`groups.${index}.url` as const)}
                        />
                      </FormControl>
                      <Button
                        variant="secondary"
                        size="icon"
                        className={cn(
                          "absolute right-2 top-1/2 h-fit w-fit -translate-y-1/2 transform rounded-sm bg-destructive-foreground",
                          numGroups <= minNumGroups
                            ? "invisible"
                            : "invisible group-hover:visible",
                        )}
                        type="button"
                        onClick={() => {
                          const groups = form.getValues("groups");
                          if (groups.length <= minNumGroups) {
                            // TODO(TmLev): Toast.
                            return;
                          }
                          form.setValue(
                            "groups",
                            groups.filter((_, i) => i !== index),
                          );
                        }}
                      >
                        <XIcon
                          width={16}
                          height={16}
                          className="text-slate-700"
                        />
                      </Button>
                    </div>

                    <DataFreshnessSwitcher
                      groupUrl={form.watch().groups[index].url}
                      freshness={form.watch().groups[index].freshness}
                      setFreshness={(value) => {
                        form.setValue(
                          `groups.${index}.freshness` as const,
                          value,
                        );
                      }}
                    />

                    <FormMessage<z.infer<typeof GroupUrlSchema>>
                      arrayFields={{
                        isError: (error): error is ArrayFieldError => {
                          return "message" in error && "type" in error;
                        },
                        displayError: (error) => error.message ?? "",
                      }}
                      className="col-span-2 col-start-2 pt-2"
                    />
                  </FormItem>
                )}
              />
            </Fragment>
          ))}

          {form.formState.errors.groups?.message && (
            <p className="col-span-2 text-destructive">
              {form.formState.errors.groups.message}
            </p>
          )}

          {numGroups < maxNumGroups && (
            <Button
              type="button"
              variant="outline"
              className="col-start-2 mt-6 justify-start"
              onClick={() => {
                const groups = form.getValues("groups");
                if (groups.length >= maxNumGroups) {
                  // TODO(TmLev): Toast.
                  return;
                }

                form.setValue("groups", [
                  ...groups,
                  { url: "", freshness: "STALE" },
                ]);
              }}
            >
              + Добавить ещё одно сообщество
            </Button>
          )}
        </div>

        <div className="h-12" />

        <div className="flex flex-col items-center">
          <Button
            type="submit"
            className="min-w-64"
            onClick={() => {
              console.log("submitting");
            }}
          >
            {submitButtonText}
          </Button>
        </div>
      </form>
    </Form>
  );
}

// TODO(TmLev): Extract to a separate file.
export function DataFreshnessSwitcher({
  groupUrl,
  freshness,
  setFreshness,
  className,
}: {
  groupUrl: string;
  freshness: Freshness;
  setFreshness: (value: Freshness) => void;
  className?: string;
}) {
  const lastUpdatedQuery = useQuery({
    queryKey: ["groups", "last-updated", groupUrl],
    queryFn: groupUrl
      ? async () => {
          return await getLastUpdated({ group_url: groupUrl });
        }
      : skipToken,
  });

  return (
    <div className={className}>
      <div className="font grid grid-cols-2 items-center gap-1 rounded-md bg-slate-200 p-1 text-xs">
        <button
          type="button"
          onClick={() => setFreshness("STALE")}
          className={cn(
            "rounded-md px-2 py-1",
            freshness === "STALE" ? "bg-white" : "",
          )}
        >
          Приблизительно, <br /> но быстро
          <br />
          {lastUpdatedQuery.data?.last_updated_at && (
            <>данные от {formatDate(lastUpdatedQuery.data.last_updated_at)}</>
          )}
        </button>
        <button
          type="button"
          onClick={() => setFreshness("FRESH")}
          className={cn(
            "rounded-md px-2 py-1",
            freshness === "FRESH" ? "bg-white" : "",
          )}
        >
          Точно, <br /> но медленно
        </button>
      </div>
    </div>
  );
}

// Format dates as DD.MM.YYYY
function formatDate(d: Date): string {
  const formatter = new Intl.DateTimeFormat("ru", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });

  return formatter.format(d);
}
