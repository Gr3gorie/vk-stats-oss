import { z } from "zod";

export enum SexEnum {
  WOMAN = 1,
  MAN,
}

export function displaySex(s: SexEnum) {
  return SEX_DISPLAY[s];
}

const SEX_DISPLAY: Record<SexEnum, string> = {
  [SexEnum.MAN]: "Мужчина",
  [SexEnum.WOMAN]: "Женщина",
};

export enum RelationEnum {
  SINGLE = 1,
  DATING,
  ENGAGED,
  MARRIED,
  COMPLICATED,
  ACTIVELY_SEARCHING,
  IN_LOVE,
  IN_A_CIVIL_UNION,
}

export enum PoliticalEnum {
  COMMUNIST = 1,
  SOCIALIST,
  MODERATE,
  LIBERAL,
  CONSERVATIVE,
  MONARCHIST,
  ULTRACONSERVATIVE,
  INDIFFERENT,
  LIBERTARIAN,
}

export enum PeopleMainEnum {
  INTELLIGENCE_AND_CREATIVITY = 1,
  KINDNESS_AND_HONESTY,
  BEAUTY_AND_HEALTH,
  POWER_AND_WEALTH,
  COURAGE_AND_PERSISTENCE,
  HUMOR_AND_LOVE_FOR_LIFE,
}

export enum LifeMainEnum {
  FAMILY_AND_CHILDREN = 1,
  CAREER_AND_MONEY,
  ENTERTAINMENT_AND_LEISURE,
  SCIENCE_AND_RESEARCH,
  IMPROVING_THE_WORLD,
  SELF_DEVELOPMENT,
  BEAUTY_AND_ART,
  FAME_AND_INFLUENCE,
}

export enum SmokingEnum {
  STRONGLY_NEGATIVE = 1,
  NEGATIVE,
  COMPROMISABLE,
  NEUTRAL,
  POSITIVE,
}

export enum AlcoholEnum {
  STRONGLY_NEGATIVE = 1,
  NEGATIVE,
  COMPROMISABLE,
  NEUTRAL,
  POSITIVE,
}

const Sex = z.nativeEnum(SexEnum);
const Relation = z.nativeEnum(RelationEnum);
const Political = z.nativeEnum(PoliticalEnum);
const PeopleMain = z.nativeEnum(PeopleMainEnum);
const LifeMain = z.nativeEnum(LifeMainEnum);
const Smoking = z.nativeEnum(SmokingEnum);
const Alcohol = z.nativeEnum(AlcoholEnum);

const Personal = z.object({
  political: Political.nullish(),
  langs: z.array(z.string()),
  people_main: PeopleMain.nullish(),
  life_main: LifeMain.nullish(),
  smoking: Smoking.nullish(),
  alcohol: Alcohol.nullish(),
});

const City = z.object({
  id: z.number(),
  title: z.string(),
});

const Country = z.object({
  id: z.number(),
  title: z.string(),
});

type User = z.infer<typeof User>;
const User = z.object({
  id: z.number(),
  first_name: z.string(),
  last_name: z.string(),
  sex: Sex.nullish(),
  bdate: z.string().nullish(),
  country: Country.nullish(),
  city: City.nullish(),
  relation: Relation.nullish(),
  personal: Personal.nullish(),
});

export {
  Sex,
  Relation,
  Political,
  PeopleMain,
  LifeMain,
  Smoking,
  Alcohol,
  Personal,
  City,
  Country,
  User,
};
