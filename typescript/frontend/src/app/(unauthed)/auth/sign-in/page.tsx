import Image from "next/image";

import { getSignInInfo } from "@/api/auth/sign-in";

import { buttonVariants } from "@/components/ui/button";

import LOGO from "../../../logo.jpg";
import { getCurrentUrlOrThrow } from "../current-url";

export const dynamic = "force-dynamic";

export default async function Page() {
  const currentUrl = getCurrentUrlOrThrow();

  const redirectUri = new URL(currentUrl);
  redirectUri.pathname = "/auth/vk-oauth-callback";
  redirectUri.search = "";
  redirectUri.hash = "";

  const signInInfo = await getSignInInfo({
    redirect_uri: redirectUri.toString(),
    state: encodeURIComponent(currentUrl.searchParams.toString()),
  });

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

      <a
        className={buttonVariants({ variant: "default", size: "lg" })}
        href={signInInfo.authorize_url}
      >
        Авторизоваться через ВКонтакте
      </a>
    </main>
  );
}
