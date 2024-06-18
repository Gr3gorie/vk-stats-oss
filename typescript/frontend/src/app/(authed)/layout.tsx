import { redirect } from "next/navigation";
import { ReactNode } from "react";

import { extractSessionFromCookies } from "@/auth/session";

import { Header } from "./header";
import { UserContextProvider } from "./user-context";

export default async function Layout({ children }: { children: ReactNode }) {
  const user = await extractSessionFromCookies();
  if (!user) {
    redirect("/auth/sign-in");
  }

  return (
    <UserContextProvider value={user}>
      <div className="min-w-screen relative min-h-[calc(100dvh-var(--header-height))] [--header-height:64px]">
        <Header className="fixed left-0 top-0 z-50 h-[var(--header-height)] w-full" />
        <div className="mt-[var(--header-height)] flex min-h-[calc(100dvh-var(--header-height))] flex-col items-center">
          {children}
        </div>
      </div>
    </UserContextProvider>
  );
}
