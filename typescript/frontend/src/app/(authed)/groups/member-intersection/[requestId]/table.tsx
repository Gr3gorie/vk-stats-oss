import {
  AlcoholEnum,
  LifeMainEnum,
  PeopleMainEnum,
  PoliticalEnum,
  RelationEnum,
  SexEnum,
  SmokingEnum,
  User,
} from "@/api/users/types";

import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

// export const USERS = z.array(User).parse(
//   JSON.parse(
//     `
//
// [{"id":4023,"first_name":"Антон","last_name":"Старовойтов","can_access_closed":true,"deactivated":null,"sex":2,"bdate":"1900-06-19T00:00:00","country":{"id":1,"title":"Россия"},"city":{"id":2,"title":"Санкт-Петербург"},"last_seen":{"platform":7,"time":"2024-05-20T12:24:48Z"},"relation":null,"personal":{"political":null,"langs":["Русский","English"],"people_main":null,"life_main":null,"smoking":2,"alcohol":null}},{"id":38445,"first_name":"Алина","last_name":"Бородина","can_access_closed":false,"deactivated":null,"sex":1,"bdate":"1989-02-22T00:00:00","country":{"id":1,"title":"Россия"},"city":{"id":2,"title":"Санкт-Петербург"},"last_seen":{"platform":2,"time":"2024-05-20T15:26:39Z"},"relation":null,"personal":null},{"id":143646,"first_name":"Александр","last_name":"Капитонов","can_access_closed":false,"deactivated":null,"sex":2,"bdate":"1988-04-19T00:00:00","country":{"id":1,"title":"Россия"},"city":{"id":2,"title":"Санкт-Петербург"},"last_seen":{"platform":4,"time":"2024-05-20T15:26:16Z"},"relation":null,"personal":null},{"id":181146,"first_name":"Алексей","last_name":"Сизов","can_access_closed":true,"deactivated":null,"sex":2,"bdate":"1900-10-01T00:00:00","country":{"id":1,"title":"Россия"},"city":{"id":2,"title":"Санкт-Петербург"},"last_seen":{"platform":4,"time":"2024-05-20T15:26:49Z"},"relation":null,"personal":null},{"id":235702,"first_name":"Натали","last_name":"Монахова","can_access_closed":true,"deactivated":null,"sex":1,"bdate":"1979-11-14T00:00:00","country":{"id":1,"title":"Россия"},"city":{"id":2,"title":"Санкт-Петербург"},"last_seen":{"platform":4,"time":"2024-05-20T14:19:32Z"},"relation":null,"personal":null},{"id":325300,"first_name":"Ольга","last_name":"Сергеева","can_access_closed":true,"deactivated":null,"sex":1,"bdate":null,"country":{"id":1,"title":"Россия"},"city":{"id":2,"title":"Санкт-Петербург"},"last_seen":{"platform":7,"time":"2024-05-20T15:02:06Z"},"relation":null,"personal":null},{"id":398813,"first_name":"Динара","last_name":"Алималлаева","can_access_closed":false,"deactivated":null,"sex":1,"bdate":"1900-01-16T00:00:00","country":{"id":1,"title":"Россия"},"city":{"id":2,"title":"Санкт-Петербург"},"last_seen":{"platform":4,"time":"2024-05-20T15:11:42Z"},"relation":null,"personal":null},{"id":439274,"first_name":"Анна","last_name":"Билятдинова","can_access_closed":true,"deactivated":null,"sex":1,"bdate":"1979-10-06T00:00:00","country":{"id":1,"title":"Россия"},"city":{"id":2,"title":"Санкт-Петербург"},"last_seen":{"platform":1,"time":"2024-05-17T13:48:19Z"},"relation":null,"personal":null},{"id":495798,"first_name":"Александра","last_name":"Кротова-Путинцева","can_access_closed":true,"deactivated":null,"sex":1,"bdate":"1900-12-08T00:00:00","country":{"id":1,"title":"Россия"},"city":{"id":2,"title":"Санкт-Петербург"},"last_seen":{"platform":1,"time":"2024-05-19T19:48:49Z"},"relation":null,"personal":null},{"id":561062,"first_name":"Екатерина","last_name":"Алейникова","can_access_closed":false,"deactivated":null,"sex":1,"bdate":"1900-12-22T00:00:00","country":{"id":1,"title":"Россия"},"city":{"id":2,"title":"Санкт-Петербург"},"last_seen":{"platform":2,"time":"2024-05-20T15:21:01Z"},"relation":null,"personal":null}]
//
// `,
//   ),
// );

export function userIntoRow(user: User): UserRow {
  return {
    id: user.id,
    first_name: user.first_name,
    last_name: user.last_name,
    sex: user.sex ? SEX_DISPLAY[user.sex] : null,
    bdate: user.bdate ? displayBdate(user.bdate) : null,
    country: user.country?.title ?? null,
    city: user.city?.title ?? null,
    relation: user.relation ? RELATION_DISPLAY[user.relation] : null,
    political: user.personal?.political
      ? POLITICAL_DISPLAY[user.personal.political]
      : null,
    langs: user.personal?.langs ? user.personal.langs.join(", ") : null,
    people_main: user.personal?.people_main
      ? PEOPLE_MAIN_DISPLAY[user.personal.people_main]
      : null,
    life_main: user.personal?.life_main
      ? LIFE_MAIN_DISPLAY[user.personal.life_main]
      : null,
    smoking: user.personal?.smoking
      ? SMOKING_DISPLAY[user.personal.smoking]
      : null,
    alcohol: user.personal?.alcohol
      ? ALCOHOL_DISPLAY[user.personal.alcohol]
      : null,
  };
}

export type UserRow = {
  id: number;
  first_name: string;
  last_name: string;
  sex: string | null;
  bdate: string | null;
  country: string | null;
  city: string | null;
  relation: string | null;
  political: string | null;
  langs: string | null;
  people_main: string | null;
  life_main: string | null;
  smoking: string | null;
  alcohol: string | null;
};

export function UserTable({ users }: { users: Array<UserRow> }) {
  // console.log(JSON.stringify(users, null, 2));

  return (
    <Table>
      <TableCaption className="text-left">
        Список из {users.length} пользователей, попавших в пересечение
      </TableCaption>

      <TableHeader>
        <TableRow>
          <TableHead className="w-[100px]">ID</TableHead>
          <TableHead>Имя</TableHead>
          <TableHead>Фамилия</TableHead>
          <TableHead>Пол</TableHead>
          <TableHead className="w-max text-nowrap">Дата рождения</TableHead>
          <TableHead className="w-max text-nowrap">Страна</TableHead>
          <TableHead className="w-max text-nowrap">Город</TableHead>
          <TableHead className="w-max text-nowrap">
            Семейное положение
          </TableHead>
          <TableHead className="w-max text-nowrap">
            Политические взгляды
          </TableHead>
          <TableHead className="w-max text-nowrap">Языки</TableHead>
          <TableHead className="w-max text-nowrap">Главное в людях</TableHead>
          <TableHead className="w-max text-nowrap">Главное в жизни</TableHead>
          <TableHead className="w-max text-nowrap">
            Отношение к курению
          </TableHead>
          <TableHead className="w-max text-nowrap">
            Отношение к алкоголю
          </TableHead>
        </TableRow>
      </TableHeader>

      <TableBody>
        {users.map((user) => (
          <TableRow key={user.id}>
            <TableCell className="font-medium">
              <a
                href={`https://vk.com/id${user.id}`}
                className="hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                {user.id}
              </a>
            </TableCell>
            <TableCell>{user.first_name}</TableCell>
            <TableCell className="w-max text-nowrap">
              {user.last_name}
            </TableCell>
            <TableCell>{user.sex ?? "-"}</TableCell>
            <TableCell>{user.bdate ?? "-"}</TableCell>
            <TableCell>{user.country ?? "-"}</TableCell>
            <TableCell className="w-max text-nowrap">
              {user.city ?? "-"}
            </TableCell>
            <TableCell>{user.relation ?? "-"}</TableCell>
            <TableCell>{user.political ?? "-"}</TableCell>
            <TableCell className="w-max text-nowrap">
              {user.langs ?? "-"}
            </TableCell>
            <TableCell>{user.people_main ?? "-"}</TableCell>
            <TableCell>{user.life_main ?? "-"}</TableCell>
            <TableCell>{user.smoking ?? "-"}</TableCell>
            <TableCell>{user.alcohol ?? "-"}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function displayBdate(bdate: string): string {
  const date = new Date(bdate);

  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = date.getFullYear();

  const now = new Date();
  const yearDiff = now.getFullYear() - year;

  return [day, month, yearDiff > 100 ? undefined : year]
    .filter(Boolean)
    .join(".");
}

const SEX_DISPLAY: Record<SexEnum, string> = {
  [SexEnum.MAN]: "Мужской",
  [SexEnum.WOMAN]: "Женский",
};

const RELATION_DISPLAY: Record<RelationEnum, string> = {
  [RelationEnum.SINGLE]: "Свободен",
  [RelationEnum.DATING]: "В отношениях",
  [RelationEnum.ENGAGED]: "Помолвлен(а)",
  [RelationEnum.MARRIED]: "Женат/Замужем",
  [RelationEnum.COMPLICATED]: "Всё сложно",
  [RelationEnum.ACTIVELY_SEARCHING]: "В активном поиске",
  [RelationEnum.IN_LOVE]: "Влюблён(а)",
  [RelationEnum.IN_A_CIVIL_UNION]: "В гражданском браке",
};

const POLITICAL_DISPLAY: Record<PoliticalEnum, string> = {
  [PoliticalEnum.COMMUNIST]: "Коммунистические",
  [PoliticalEnum.SOCIALIST]: "Социалистические",
  [PoliticalEnum.MODERATE]: "Центристские",
  [PoliticalEnum.LIBERAL]: "Либеральные",
  [PoliticalEnum.CONSERVATIVE]: "Консервативные",
  [PoliticalEnum.MONARCHIST]: "Монархические",
  [PoliticalEnum.ULTRACONSERVATIVE]: "Ультраконсервативные",
  [PoliticalEnum.INDIFFERENT]: "Индифферентные",
  [PoliticalEnum.LIBERTARIAN]: "Либертарианские",
};

const PEOPLE_MAIN_DISPLAY: Record<PeopleMainEnum, string> = {
  [PeopleMainEnum.INTELLIGENCE_AND_CREATIVITY]: "Ум и креативность",
  [PeopleMainEnum.KINDNESS_AND_HONESTY]: "Доброта и честность",
  [PeopleMainEnum.BEAUTY_AND_HEALTH]: "Красота и здоровье",
  [PeopleMainEnum.POWER_AND_WEALTH]: "Власть и богатство",
  [PeopleMainEnum.COURAGE_AND_PERSISTENCE]: "Смелость и упорство",
  [PeopleMainEnum.HUMOR_AND_LOVE_FOR_LIFE]: "Юмор и жизнелюбие",
};

const LIFE_MAIN_DISPLAY: Record<LifeMainEnum, string> = {
  [LifeMainEnum.FAMILY_AND_CHILDREN]: "Семья и дети",
  [LifeMainEnum.CAREER_AND_MONEY]: "Карьера и деньги",
  [LifeMainEnum.ENTERTAINMENT_AND_LEISURE]: "Развлечения и отдых",
  [LifeMainEnum.SCIENCE_AND_RESEARCH]: "Наука и исследования",
  [LifeMainEnum.IMPROVING_THE_WORLD]: "Совершенствование мира",
  [LifeMainEnum.SELF_DEVELOPMENT]: "Саморазвитие",
  [LifeMainEnum.BEAUTY_AND_ART]: "Красота и искусство",
  [LifeMainEnum.FAME_AND_INFLUENCE]: "Слава и влияние",
};

const SMOKING_DISPLAY: Record<SmokingEnum, string> = {
  [SmokingEnum.STRONGLY_NEGATIVE]: "Резко негативное",
  [SmokingEnum.NEGATIVE]: "Негативное",
  [SmokingEnum.COMPROMISABLE]: "Компромиссное",
  [SmokingEnum.NEUTRAL]: "Нейтральное",
  [SmokingEnum.POSITIVE]: "Положительное",
};

const ALCOHOL_DISPLAY: Record<AlcoholEnum, string> = {
  [AlcoholEnum.STRONGLY_NEGATIVE]: "Резко негативное",
  [AlcoholEnum.NEGATIVE]: "Негативное",
  [AlcoholEnum.COMPROMISABLE]: "Компромиссное",
  [AlcoholEnum.NEUTRAL]: "Нейтральное",
  [AlcoholEnum.POSITIVE]: "Положительное",
};
