import { headers as requestHeaders } from "next/headers";

import { CURRENT_URL_HEADER_NAME } from "@/middleware";

export function getCurrentUrlOrThrow() {
  const headers = requestHeaders();

  const urlFromHeader = headers.get(CURRENT_URL_HEADER_NAME);
  if (!urlFromHeader) {
    throw new Error("Missing current url header");
  }

  return new URL(urlFromHeader);
}
