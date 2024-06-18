"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { useMutation } from "@tanstack/react-query";
import { cva } from "class-variance-authority";

import { signOut } from "@/api/auth/sign-out";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

import LOGO from "../logo.jpg";
import { useUserContext } from "./user-context";

export function Header({ className }: { className?: string }) {
  const pathname = usePathname();

  return (
    <div
      className={cn(
        "flex flex-row items-center gap-8 border-b border-solid border-slate-200 bg-white px-12 text-slate-800",
        className,
      )}
    >
      <Link
        href="/"
        className={linkVariants({
          active: false,
          className: "flex flex-row items-center gap-1",
        })}
      >
        <Image src={LOGO} alt="Ле ВК Статс" width={32} height={32} /> vk-stats
      </Link>

      <Link
        href="/groups/member-intersection"
        className={linkVariants({
          active: pathname.startsWith("/groups/member-intersection"),
        })}
      >
        Пересечение сообществ
      </Link>

      <Link
        href="/users/average-portrait"
        className={linkVariants({
          active: pathname.startsWith("/users/average-portrait"),
        })}
      >
        Средний портрет
      </Link>

      <Link
        href="/groups/reach-prediction"
        className={linkVariants({
          active: pathname.startsWith("/groups/reach-prediction"),
        })}
      >
        Предсказание охвата
      </Link>

      <UserButton className="ml-auto" />
    </div>
  );
}

function UserButton({ className }: { className?: string }) {
  const router = useRouter();

  const signOutMutation = useMutation({
    mutationKey: ["sign-out"],
    mutationFn: signOut,
  });

  const user = useUserContext();
  const userInitials = `${user.user_first_name[0]}${user.user_last_name[0]}`;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          className={cn("size-[32px] rounded-full bg-slate-200", className)}
        >
          {userInitials}
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Аккаунт</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <a
            href={`https://vk.com/id${user.user_id}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            Профиль
          </a>
        </DropdownMenuItem>
        <DropdownMenuItem>Настройки</DropdownMenuItem>
        {/* <DropdownMenuItem>Мои анализы</DropdownMenuItem> */}
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onSelect={async () => {
            await signOutMutation.mutateAsync();
            router.push("/auth/sign-in");
          }}
        >
          Выйти
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

const linkVariants = cva("border-b border-solid tracking-tight text-sm", {
  variants: {
    active: {
      true: "border-slate-800",
      false: "border-transparent hover:border-slate-400",
    },
  },
});
