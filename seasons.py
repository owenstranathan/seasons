from datetime import datetime
from argparse import ArgumentParser
import urllib.request
import json
from pprint import pprint
import calendar
from collections import namedtuple

SeasonDay = namedtuple("SeasonDay", ["season", "day"])

nth = {
    0: "th",
    1: "st",
    2: "nd",
    3: "rd",
    4: "th",
    5: "th",
    6: "th",
    7: "th",
    8: "th",
    9: "th",
    11: "th",
    12: "th",
    13: "th",
}

def get_ordinal(number):
    if(number < 14 and number > -1):
        return nth[number]
    ones = number % 10
    return nth[abs(ones)]

def dict_to_datetime(d):
    return datetime(d["year"], d["month"], d["day"])

def get_year_seasons(year):
    try:
        URL = f"https://aa.usno.navy.mil/api/seasons?year={year}"
        data = urllib.request.urlopen(URL).read()

        payload = json.loads(data.decode())
    except:
        return {}

    seasons = payload["data"]
    equinoxes = [s for s in seasons if s["phenom"] == "Equinox"]
    solstices = [s for s in seasons if s["phenom"] == "Solstice"]

    return  {
        "year"             : year,
        "perihelion"       :[s for s in seasons if s["phenom"] == "Perihelion"][0],
        "aphelion"         :[s for s in seasons if s["phenom"] == "Aphelion"][0],
        "spring_equinox"   :[s for s in equinoxes if s["month"] == 3][0],
        "autumn_equinox"   :[s for s in equinoxes if s["month"] == 9][0],
        "summer_solstice"  :[s for s in solstices if s["month"] == 6][0],
        "winter_solstice"  :[s for s in solstices if s["month"] == 12][0],
    }

def get_season_day(d):
    this_year = get_year_seasons(d.year)
    last_year = get_year_seasons(d.year - 1)

    if((day := (d - dict_to_datetime(this_year["winter_solstice"])).days) > 0):
        return SeasonDay("Winter", day)
    elif((day := (d - dict_to_datetime(this_year["autumn_equinox"])).days) > 0):
        return SeasonDay("Autumn", day)
    elif((day := (d - dict_to_datetime(this_year["summer_solstice"])).days) > 0):
        return SeasonDay("Summer", day)
    elif((day := (d - dict_to_datetime(this_year["spring_equinox"])).days) > 0):
        return SeasonDay("Spring", day)
    elif((day := (d - dict_to_datetime(last_year["winter_solstice"])).days) > 0):
        return SeasonDay("Winter", day)
    else:
        raise Exception("Impossible Season!")


def string_to_datetime(string):
    return datetime.strptime(string, "%m/%d/%Y")

def main():
    parser = ArgumentParser(prog="seasons")
    parser.add_argument("datetime", type=string_to_datetime)
    args = parser.parse_args()
    season_day = get_season_day(args.datetime)
    today = datetime.now()
    verb = "is"
    if(args.datetime.year < today.year):
        verb = "was"
    print(f"{args.datetime.strftime('%m/%d/%Y')} {verb} the {season_day.day}{get_ordinal(season_day.day)} day of {season_day.season}")



def main_one():

    parser = ArgumentParser(prog = "seasons")

    parser.add_argument("year", type=int)
    parser.add_argument("range", type=int)
    args = parser.parse_args()

    years = [None] * args.range
    phtimes = [None] * args.range
    winters = [None] * args.range
    summers = [None] * args.range
    ahtimes = [None] * args.range
    springs = [None] * args.range
    autumns = [None] * args.range
    total_days = [None] * args.range
    leaps = [None] * args.range
    input_years = [args.year + i for i in range(args.range)]
    for i, year in enumerate(input_years):
        this_year = get_year_seasons(year)
        if not this_year:
            continue
        years[i] = this_year
        if i == 0:
            continue
        last_year = years[i-1]
        ph = dict_to_datetime(this_year["perihelion"])
        ah = dict_to_datetime(this_year["aphelion"])
        pws = dict_to_datetime(last_year["winter_solstice"])
        se = dict_to_datetime(this_year["spring_equinox"])
        ss = dict_to_datetime(this_year["summer_solstice"])
        ae = dict_to_datetime(this_year["autumn_equinox"])
        ws = dict_to_datetime(this_year["winter_solstice"])

        winter = (se - pws).days
        peritime = (ph - pws).days
        spring = (ss - se).days
        summer = (ae - ss).days
        aphitime = (ah - ss).days
        autumn = (ws - ae).days
        days = winter + spring + summer + autumn
        leaps[i] = calendar.isleap(year)
        winters[i] = winter
        phtimes[i] = peritime
        springs[i] = spring
        summers[i] = summer
        ahtimes[i] = aphitime
        autumns[i] = autumn
        total_days[i] = days
        years[i]["winter"] = winter
        years[i]["spring"] = spring
        years[i]["summer"] = summer
        years[i]["autumn"] = autumn
        years[i]["days"] = days
        # print(f"{year}:")
        # print(f"days: {days}")
        # print(f"winter: {winter}")
        # print(f"spring: {spring}")
        # print(f"summer: {summer}")
        # print(f"autumn: {autumn}")
        # pprint(this_year)
    print(f"  leaps: {['leap' if x else '----' for x in leaps]}")
    print(f"  years: {[f'{y}' for y in input_years]}")
    print(f"winters: {[f'{x:-4d}'if x is not None else '----' for x in winters ]}")
    print(f"phtimes: {[f'{x:-4d}'if x is not None else '----' for x in phtimes ]}")
    print(f"springs: {[f'{x:-4d}'if x is not None else '----' for x in springs ]}")
    print(f"summers: {[f'{x:-4d}'if x is not None else '----' for x in summers ]}")
    print(f"ahtimes: {[f'{x:-4d}'if x is not None else '----' for x in ahtimes ]}")
    print(f"autumns: {[f'{x:-4d}'if x is not None else '----' for x in autumns ]}")
    print(f"   days: {[f'{d:-4d}'if d is not None else '----' for d in total_days]}")

if __name__ == "__main__":
    main()
