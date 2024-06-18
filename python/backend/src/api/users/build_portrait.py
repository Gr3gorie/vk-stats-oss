from collections import Counter
from datetime import datetime

from pydantic import BaseModel
from vk.users import (
    Alcohol,
    LifeMain,
    PeopleMain,
    Political,
    Relation,
    Sex,
    Smoking,
    User,
)


class AveragePortrait(BaseModel):
    class PortraitStats(BaseModel):
        label: str
        value: str

    class CharacteristicStats(BaseModel):
        class StatPoint(BaseModel):
            label: str
            value: int
            color: str = "#AAAAAA"

        name: str
        values: list[StatPoint]

    hidden_amount: int = 0
    deleted_amount: int = 0

    portrait: list[PortraitStats]
    main_stats: list[CharacteristicStats]
    additional_stats: list[CharacteristicStats]


def sex_palette(num: int) -> str:
    match num:
        case 1:
            return "#F783AC"
        case 2:
            return "#1971C2"
        case _:
            return "AAAAAA"


def palette(num: int) -> str:
    match num:
        case 1:
            return "#598dfa"
        case 2:
            return "#7289da"
        case 3:
            return "#665191"
        case 4:
            return "#a05195"
        case 5:
            return "#d45087"
        case 6:
            return "#f95d6a"
        case 7:
            return "#ff7c43"
        case 8:
            return "#ffa600"
        case 9:
            return "#7fcdbb"
        case 10:
            return "#1d91c0"
        case _:
            return "AAAAAA"


def habit_palette(num: int) -> str:
    match num:
        case 1:
            return "#e51f1f"
        case 2:
            return "#f2a134"
        case 3:
            return "#f7e379"
        case 4:
            return "#bbdb44"
        case 5:
            return "#44ce1b"
        case _:
            return "AAAAAA"


def display_age(age: int) -> str:
    if 13 <= age < 18:
        return "13-18"
    elif 18 <= age < 23:
        return "18-23"
    elif 23 <= age < 28:
        return "23-28"
    elif 28 <= age < 33:
        return "28-33"
    elif 33 <= age < 38:
        return "33-38"
    elif 38 <= age < 43:
        return "38-43"
    elif 43 <= age < 48:
        return "43-48"
    elif 48 <= age < 53:
        return "48-53"
    elif 53 <= age < 58:
        return "53-58"
    else:
        return "58+"


def display_sex(s: Sex) -> str:
    match s:
        case Sex.MAN:
            return "мужской"
        case Sex.WOMAN:
            return "женский"


def display_relation(rel: Relation) -> str:
    match rel:
        case Relation.SINGLE:
            return "свободен"
        case Relation.DATING:
            return "есть партнер"
        case Relation.ENGAGED:
            return "помолвлен"
        case Relation.MARRIED:
            return "в браке"
        case Relation.COMPLICATED:
            return "всё сложно"
        case Relation.ACTIVELY_SEARCHING:
            return "в поиске"
        case Relation.IN_LOVE:
            return "влюблён"
        case Relation.IN_A_CIVIL_UNION:
            return "в гражданском браке"


def display_political(p: Political) -> str:
    match p:
        case Political.COMMUNIST:
            return "коммунистические"
        case Political.SOCIALIST:
            return "социалистические"
        case Political.MODERATE:
            return "умеренные"
        case Political.LIBERAL:
            return "либеральные"
        case Political.CONSERVATIVE:
            return "консервативные"
        case Political.MONARCHIST:
            return "монархические"
        case Political.ULTRACONSERVATIVE:
            return "ультраконсервативные"
        case Political.INDIFFERENT:
            return "индифферентные"
        case Political.LIBERTARIAN:
            return "либертарианские"


def display_peoplemain(p: PeopleMain) -> str:
    match p:
        case PeopleMain.INTELLIGENCE_AND_CREATIVITY:
            return "ум и креативность"
        case PeopleMain.KINDNESS_AND_HONESTY:
            return "доброта и честность"
        case PeopleMain.BEAUTY_AND_HEALTH:
            return "красота и здоровье"
        case PeopleMain.POWER_AND_WEALTH:
            return "власть и богатство"
        case PeopleMain.COURAGE_AND_PERSISTENCE:
            return "смелость и упорство"
        case PeopleMain.HUMOR_AND_LOVE_FOR_LIFE:
            return "юмор и жизнелюбие"


def display_lifemain(li: LifeMain) -> str:
    match li:
        case LifeMain.FAMILY_AND_CHILDREN:
            return "семья и дети"
        case LifeMain.CAREER_AND_MONEY:
            return "карьера и деньги"
        case LifeMain.ENTERTAINMENT_AND_LEISURE:
            return "развлечения и отдых"
        case LifeMain.SCIENCE_AND_RESEARCH:
            return "наука и исследования"
        case LifeMain.IMPROVING_THE_WORLD:
            return "совершенствование мира"
        case LifeMain.SELF_DEVELOPMENT:
            return "саморазвитие"
        case LifeMain.BEAUTY_AND_ART:
            return "красота и искусство"
        case LifeMain.FAME_AND_INFLUENCE:
            return "слава и влияние"


def display_smoking(s: Smoking) -> str:
    match s:
        case Smoking.STRONGLY_NEGATIVE:
            return "резко негативное"
        case Smoking.NEGATIVE:
            return "негативное"
        case Smoking.COMPROMISABLE:
            return "компромиссное"
        case Smoking.NEUTRAL:
            return "нейтральное"
        case Smoking.POSITIVE:
            return "положительное"


def display_alcohol(a: Alcohol) -> str:
    match a:
        case Alcohol.STRONGLY_NEGATIVE:
            return "резко негативное"
        case Alcohol.NEGATIVE:
            return "негативное"
        case Alcohol.COMPROMISABLE:
            return "компромиссное"
        case Alcohol.NEUTRAL:
            return "нейтральное"
        case Alcohol.POSITIVE:
            return "положительное"


def build_portrait(users: list[User]) -> AveragePortrait:
    sex_counts = Counter(user.sex for user in users if user.sex is not None)
    most_common_sex = AveragePortrait.PortraitStats(
        label="Пол",
        value=display_sex(sex_counts.most_common(1)[0][0]) if sex_counts else "-",
    )
    sex_stats = AveragePortrait.CharacteristicStats(
        name="Пол",
        values=[
            AveragePortrait.CharacteristicStats.StatPoint(
                label=display_sex(sex), value=count, color=sex_palette(sex.value)
            )
            for sex, count in sorted(sex_counts.items(), key=lambda t: t[0].value)
        ],
    )

    age_counts = Counter()
    for user in users:
        years_passed = datetime.now().year - (user.bdate.year if user.bdate else 1904)
        if user.bdate is not None and years_passed <= 100:
            age = (datetime.now() - user.bdate).days // 365
            category = display_age(age)
            age_counts[category] += 1
    most_common_age = AveragePortrait.PortraitStats(
        label="Возраст",
        value=f"{age_counts.most_common(1)[0][0] if age_counts else '-'}",
    )
    age_stats = AveragePortrait.CharacteristicStats(
        name="Возраст",
        values=[
            AveragePortrait.CharacteristicStats.StatPoint(
                label=str(age), value=count, color=palette(i + 1)
            )
            for i, (age, count) in enumerate(sorted(age_counts.items()))
        ],
    )

    city_counts = Counter(user.city.title for user in users if user.city is not None)
    most_common_city = AveragePortrait.PortraitStats(
        label="Живёт в",
        value=city_counts.most_common(1)[0][0] if city_counts else "-",
    )
    city_stats = AveragePortrait.CharacteristicStats(
        name="Город",
        values=[
            AveragePortrait.CharacteristicStats.StatPoint(
                label=str(city), value=count, color=palette(i + 1)
            )
            for i, (city, count) in enumerate(city_counts.most_common(10))
        ],
    )

    relation_counts = Counter(
        user.relation for user in users if user.relation is not None
    )
    most_common_relation = AveragePortrait.PortraitStats(
        label="Семейное положение",
        value=display_relation(relation_counts.most_common(1)[0][0])
        if relation_counts
        else "-",
    )
    relation_stats = AveragePortrait.CharacteristicStats(
        name="Семейное положение",
        values=[
            AveragePortrait.CharacteristicStats.StatPoint(
                label=display_relation(rel), value=count, color=palette(rel.value)
            )
            for rel, count in sorted(relation_counts.items(), key=lambda t: t[0].value)
        ],
    )

    main_stats = [sex_stats, age_stats, city_stats, relation_stats]

    political_counts = Counter(
        user.personal.political
        for user in users
        if user.personal is not None and user.personal.political is not None
    )
    most_common_political = AveragePortrait.PortraitStats(
        label="Политические предпочтения",
        value=display_political(political_counts.most_common(1)[0][0])
        if political_counts
        else "-",
    )
    political_stats = AveragePortrait.CharacteristicStats(
        name="Политические предпочтения",
        values=[
            AveragePortrait.CharacteristicStats.StatPoint(
                label=display_political(pol), value=count, color=palette(pol.value)
            )
            for pol, count in sorted(political_counts.items(), key=lambda t: t[0].value)
        ],
    )

    langs_counts = Counter()
    for user in users:
        if user.personal is not None and user.personal.langs:
            langs_counts.update(user.personal.langs)
    most_common_lang = AveragePortrait.PortraitStats(
        label="Знает языки",
        value=", ".join([lang for lang, _count in langs_counts.most_common(2)])
        if langs_counts
        else "-",
    )
    langs_stats = AveragePortrait.CharacteristicStats(
        name="Языки",
        values=[
            AveragePortrait.CharacteristicStats.StatPoint(
                label=str(lang), value=count, color=palette(i + 1)
            )
            for i, (lang, count) in enumerate(langs_counts.most_common(10))
        ],
    )

    people_main_counts = Counter(
        user.personal.people_main
        for user in users
        if user.personal is not None and user.personal.people_main is not None
    )
    most_common_people_main = AveragePortrait.PortraitStats(
        label="Главное в людях",
        value=display_peoplemain(people_main_counts.most_common(1)[0][0])
        if people_main_counts
        else "-",
    )
    people_main_stats = AveragePortrait.CharacteristicStats(
        name="Главное в людях",
        values=[
            AveragePortrait.CharacteristicStats.StatPoint(
                label=display_peoplemain(main), value=count, color=palette(main.value)
            )
            for main, count in sorted(
                people_main_counts.items(), key=lambda t: t[0].value
            )
        ],
    )

    life_main_counts = Counter(
        user.personal.life_main
        for user in users
        if user.personal is not None and user.personal.life_main is not None
    )
    most_common_life_main = AveragePortrait.PortraitStats(
        label="Главное в жизни",
        value=display_lifemain(life_main_counts.most_common(1)[0][0])
        if life_main_counts
        else "-",
    )
    life_main_stats = AveragePortrait.CharacteristicStats(
        name="Главное в жизни",
        values=[
            AveragePortrait.CharacteristicStats.StatPoint(
                label=display_lifemain(main), value=count, color=palette(main.value)
            )
            for main, count in sorted(
                life_main_counts.items(), key=lambda t: t[0].value
            )
        ],
    )

    smoking_counts = Counter(
        user.personal.smoking
        for user in users
        if user.personal is not None and user.personal.smoking is not None
    )
    most_common_smoking = AveragePortrait.PortraitStats(
        label="Отношение к курению",
        value=display_smoking(smoking_counts.most_common(1)[0][0])
        if smoking_counts
        else "-",
    )
    smoking_stats = AveragePortrait.CharacteristicStats(
        name="Отношение к курению",
        values=[
            AveragePortrait.CharacteristicStats.StatPoint(
                label=display_smoking(smoking),
                value=count,
                color=habit_palette(smoking.value),
            )
            for smoking, count in sorted(
                smoking_counts.items(), key=lambda t: t[0].value
            )
        ],
    )

    alcohol_counts = Counter(
        user.personal.alcohol
        for user in users
        if user.personal is not None and user.personal.alcohol is not None
    )
    most_common_alcohol = AveragePortrait.PortraitStats(
        label="Отношение к алкоголю",
        value=display_alcohol(alcohol_counts.most_common(1)[0][0])
        if alcohol_counts
        else "-",
    )
    alcohol_stats = AveragePortrait.CharacteristicStats(
        name="Отношение к алкоголю",
        values=[
            AveragePortrait.CharacteristicStats.StatPoint(
                label=display_alcohol(alcohol),
                value=count,
                color=habit_palette(alcohol.value),
            )
            for alcohol, count in sorted(
                alcohol_counts.items(), key=lambda t: t[0].value
            )
        ],
    )

    additional_stats = [
        political_stats,
        langs_stats,
        people_main_stats,
        life_main_stats,
        smoking_stats,
        alcohol_stats,
    ]
    portrait = [
        most_common_sex,
        most_common_age,
        most_common_city,
        most_common_relation,
        most_common_political,
        most_common_lang,
        most_common_people_main,
        most_common_life_main,
        most_common_smoking,
        most_common_alcohol,
    ]

    hidden_amount = sum(1 for user in users if not user.can_access_closed)
    deleted_amount = sum(1 for user in users if user.deactivated)

    return AveragePortrait(
        hidden_amount=hidden_amount,
        deleted_amount=deleted_amount,
        portrait=portrait,
        main_stats=main_stats,
        additional_stats=additional_stats,
    )
