import Image from "next/image";
import Link from "next/link";

import {
  CardDescription,
  CardHeader,
  CardTitle,
  cardVariants,
} from "@/components/ui/card";

// import LE_VK_STATS_ICON from "../le-vk-stats.png";
import LOGO from "../logo.jpg";
import AVERAGE_PORTRAIT from "./_card-images/average-portrait.webp";
import GROUPS_INTERSECTION from "./_card-images/groups-intersection.webp";
import REACH_PREDICTION from "./_card-images/reach-prediction.webp";

export default function Home() {
  return (
    <main className="flex flex-col items-center px-24 py-16">
      {/* <Image src={LE_VK_STATS_ICON} alt="Ле ВК Статс" height={128} /> */}

      <div className="flex flex-row items-center gap-4">
        <Image src={LOGO} alt="vk-stats" width={128} height={128} />
        <h1 className="text-3xl font-bold text-slate-900">vk-stats</h1>
      </div>

      <div className="h-16" />

      <div className="grid grid-rows-2 gap-8">
        <GroupsIntersectionCard />
        <AveragePortraitCard />
        <ReachPredictionCard />
      </div>
    </main>
  );
}

function GroupsIntersectionCard() {
  return (
    <Link href="/groups/member-intersection" className={CARD_STYLES}>
      <CardHeader className="flex-row gap-x-8">
        <Image
          src={GROUPS_INTERSECTION}
          className="size-20 rounded-md"
          alt="Пересечение сообществ"
        />

        <div className="flex flex-col gap-y-1.5">
          <CardTitle>Пересечение сообществ</CardTitle>
          <CardDescription>
            Поиск пересекающейся аудитории в сообществах
          </CardDescription>
        </div>
      </CardHeader>
    </Link>
  );
}

function AveragePortraitCard() {
  return (
    <Link href="/users/average-portrait" className={CARD_STYLES}>
      <CardHeader className="flex-row gap-x-8">
        <Image
          src={AVERAGE_PORTRAIT}
          className="size-20 rounded-md"
          alt="Средний портрет"
        />

        <div className="flex flex-col gap-y-1.5">
          <CardTitle>Средний портрет</CardTitle>
          <CardDescription>
            Построение среднего портрета пользователя сообществ
          </CardDescription>
        </div>
      </CardHeader>
    </Link>
  );
}

function ReachPredictionCard() {
  return (
    <Link href="/groups/reach-prediction" className={CARD_STYLES}>
      <CardHeader className="flex-row gap-x-8">
        <Image
          src={REACH_PREDICTION}
          className="size-20 rounded-md"
          alt="Средний портрет"
        />

        <div className="flex flex-col gap-y-1.5">
          <CardTitle>Предсказание охвата</CardTitle>
          <CardDescription>
            Построение прогноза охвата сообществ для администраторов
          </CardDescription>
        </div>
      </CardHeader>
    </Link>
  );
}

const CARD_STYLES = cardVariants({ className: "hover:shadow-md transition" });
