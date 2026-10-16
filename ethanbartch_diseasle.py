# Diseasle - a Wordle game for infectious diseases
# Uses the WHO Global Health Observatory API (no key needed)
# pip install requests matplotlib

import random
import requests
import matplotlib.pyplot as plt

# disease name: [WHO code, pathogen, how it spreads, vaccine?]
diseases = {
    "measles": ["WHS3_62", "virus", "air", "yes"],
    "whooping cough": ["WHS3_43", "bacteria", "air", "yes"],
    "tuberculosis": ["TB_e_inc_num", "bacteria", "air", "yes"],
    "malaria": ["MALARIA_EST_CASES", "parasite", "mosquito", "yes"],
    "hiv": ["HIV_0000000026", "virus", "sex/blood", "no"],
    "syphilis": ["STI_SYPHILIS_CASES_NUM", "bacteria", "sex/blood", "no"],
    "gonorrhea": ["STI_GONORRHEA_CASES_NUM", "bacteria", "sex/blood", "no"],
    "chlamydia": ["STI_CHLAMYDIA_CASES_NUM", "bacteria", "sex/blood", "no"],
    "sleeping sickness": ["NTD_4", "parasite", "tsetse fly", "no"],
    "leishmaniasis": ["NTD_LEISHVNUM", "parasite", "sandfly", "no"],
    "leprosy": ["WHS3_45", "bacteria", "close contact", "no"],
}


def get_data(name):
    # download the data for one disease from the WHO
    code = diseases[name][0]
    url = "https://ghoapi.azureedge.net/api/" + code
    response = requests.get(url)
    rows = response.json()["value"]

    # add up the cases for each year (countries only)
    cases_by_year = {}
    countries_by_year = {}
    for row in rows:
        if row["SpatialDimType"] != "COUNTRY" or row["NumericValue"] is None:
            continue
        year = row["TimeDim"]
        country = row["SpatialDim"]
        cases = row["NumericValue"]
        cases_by_year[year] = cases_by_year.get(year, 0) + cases
        if year not in countries_by_year:
            countries_by_year[year] = {}
        countries_by_year[year][country] = countries_by_year[year].get(country, 0) + cases

    if len(cases_by_year) == 0:
        return None

    # use the most recent year that has lots of countries reporting
    most = max(len(c) for c in countries_by_year.values())
    good_years = [y for y in countries_by_year if len(countries_by_year[y]) >= most / 2]
    year = max(good_years)

    # find the country with the most cases that year
    hotspot = max(countries_by_year[year], key=countries_by_year[year].get)

    return {"year": year,
            "total": int(cases_by_year[year]),
            "hotspot": hotspot,
            "by_year": cases_by_year}


def check_guess(guess, answer, data):
    g = diseases[guess]
    a = diseases[answer]
    labels = ["Pathogen", "Spread", "Vaccine"]

    print()
    for i in range(3):
        if g[i + 1] == a[i + 1]:
            print(labels[i] + ": " + g[i + 1] + " ✅")
        else:
            print(labels[i] + ": " + g[i + 1] + " ❌")

    if data[guess]["total"] < data[answer]["total"]:
        print("Cases: " + format(data[guess]["total"], ",") + " ⬆ (answer has more)")
    elif data[guess]["total"] > data[answer]["total"]:
        print("Cases: " + format(data[guess]["total"], ",") + " ⬇ (answer has fewer)")
    else:
        print("Cases: " + format(data[guess]["total"], ",") + " ✅")

    if data[guess]["hotspot"] == data[answer]["hotspot"]:
        print("Hotspot: " + data[guess]["hotspot"] + " ✅")
    else:
        print("Hotspot: " + data[guess]["hotspot"] + " ❌")
    print()


def make_graph(answer, data):
    years = sorted(data[answer]["by_year"])
    cases = [data[answer]["by_year"][y] for y in years]
    plt.plot(years, cases, marker="o")
    plt.title(answer.title() + " cases per year (WHO data)")
    plt.xlabel("Year")
    plt.ylabel("Cases")
    plt.show()


# ---- main game ----
print("Welcome to DISEASLE!")
print("Loading data from the WHO...")

data = {}
for name in list(diseases):
    result = get_data(name)
    if result is None:
        del diseases[name]  # skip diseases with no data
    else:
        data[name] = result

print("Diseases you can guess:", ", ".join(diseases))
answer = random.choice(list(diseases))

won = False
for turn in range(1, 7):
    guess = input("Guess " + str(turn) + "/6: ").lower().strip()
    while guess not in diseases:
        guess = input("Not on the list, try again: ").lower().strip()

    if guess == answer:
        won = True
        break
    check_guess(guess, answer, data)

if won:
    print("You got it! It was " + answer + "!")
else:
    print("Out of guesses! It was " + answer + ".")

info = data[answer]
print("In " + str(info["year"]) + " there were " + format(info["total"], ",")
      + " cases, and the most were in " + info["hotspot"] + ".")
make_graph(answer, data)
