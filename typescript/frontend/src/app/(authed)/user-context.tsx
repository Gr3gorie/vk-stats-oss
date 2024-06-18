"use client";

import { createContext, ReactNode, useContext } from "react";

import { AuthCookieValue } from "@/api/auth/cookies";

const USER_CONTEXT = createContext<AuthCookieValue | null>(null);

export function useUserContext() {
  const context = useContext(USER_CONTEXT);
  if (!context) {
    throw new Error("useUserContext must be used within a UserContextProvider");
  }
  return context;
}

export function UserContextProvider({
  value,
  children,
}: {
  value: AuthCookieValue;
  children: ReactNode;
}) {
  return (
    <USER_CONTEXT.Provider value={value}>{children}</USER_CONTEXT.Provider>
  );
}
