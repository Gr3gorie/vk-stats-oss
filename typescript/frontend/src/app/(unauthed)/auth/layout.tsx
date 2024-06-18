import { ReactNode } from "react";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-w-screen relative min-h-[calc(100dvh-var(--header-height))] [--header-height:64px]">
      <div className="fixed left-0 top-0 z-50 h-[var(--header-height)] w-full" />
      <div className="mt-[var(--header-height)] flex min-h-[calc(100dvh-var(--header-height))] flex-col items-center">
        {children}
      </div>
    </div>
  );
}
