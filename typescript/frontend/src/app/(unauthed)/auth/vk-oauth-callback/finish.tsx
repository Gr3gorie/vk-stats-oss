"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";

import { useMutation } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";

import { finishSignIn } from "@/api/auth/sign-in";

import { Button, buttonVariants } from "@/components/ui/button";

export function FinishSignIn({
  code,
  authRedirectUri,
  onSuccessRedirectUrl,
}: {
  code: string;
  authRedirectUri: string;
  onSuccessRedirectUrl: string;
}) {
  const router = useRouter();

  const mutation = useMutation({
    mutationKey: ["finish-sign-in"],
    mutationFn: finishSignIn,
    onSuccess: async () => {
      console.log("Sign in finished, redirecting to", onSuccessRedirectUrl);

      router.push(onSuccessRedirectUrl);

      // Fake loading to let router push happen.
      await new Promise((resolve) => setTimeout(resolve, 1000));
    },
  });

  const fired = useRef(false);
  useEffect(() => {
    if (fired.current) {
      return;
    }
    fired.current = true;

    console.log("Finishing sign in with code", code);
    mutation.mutate({
      code,
      redirect_uri: authRedirectUri,
    });
  }, [authRedirectUri, code, mutation]);

  return (
    <Button
      className={buttonVariants({
        variant: "default",
        size: "lg",
        className: "gap-2",
      })}
      disabled
    >
      <Loader2 className="animate-spin" /> Авторизируемся...
    </Button>
  );
}
