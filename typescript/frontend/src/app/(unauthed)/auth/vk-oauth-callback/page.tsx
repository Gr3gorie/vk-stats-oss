import Image from "next/image";

import { z } from "zod";

import LOGO from "@/app/logo.jpg";
import { REDIRECT_AFTER_QUERY_PARAM_NAME } from "@/middleware";

import { getCurrentUrlOrThrow } from "../current-url";
import { FinishSignIn } from "./finish";

export const dynamic = "force-dynamic";

const SearchParams = z.object({
  code: z.string(),
  state: z.string().transform((v) => {
    const decoded = decodeURIComponent(v);
    return new URLSearchParams(decoded);
  }),
});

export default async function Page({
  searchParams: rawSearchParams,
}: {
  searchParams: unknown;
}) {
  const currentUrl = getCurrentUrlOrThrow();
  const searchParams = SearchParams.parse(rawSearchParams);

  const redirectUri = new URL(currentUrl);
  redirectUri.search = "";
  redirectUri.hash = "";

  const redirectAfter = searchParams.state.get(REDIRECT_AFTER_QUERY_PARAM_NAME);
  const nextUrl = new URL(redirectAfter ?? "/", currentUrl);

  return (
    <main className="flex flex-col items-center px-24 py-16">
      {/* <Image src={LE_VK_STATS_ICON} alt="Ле ВК Статс" height={128} /> */}

      <div className="flex flex-row items-center gap-4">
        <Image src={LOGO} alt="vk-stats" width={128} height={128} />
        <h1 className="text-3xl font-bold text-slate-900">vk-stats</h1>
      </div>

      <div className="h-16" />

      <h2 className="text-xl text-slate-900">
        Сервис для анализа сообществ ВКонтакте
      </h2>

      <div className="h-12" />

      <FinishSignIn
        code={searchParams.code}
        authRedirectUri={redirectUri.toString()}
        onSuccessRedirectUrl={nextUrl.toString()}
      />
    </main>
  );
}
