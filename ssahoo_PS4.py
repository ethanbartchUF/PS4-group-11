#!/usr/bin/env python
#if running through Jupyter or similar environment, I've separated blocks of code with "# ---" in between

import requests
import matplotlib.pyplot as plt

BASE_URL = "https://pokeapi.co/api/v2/"

def get_json(url):
    """Get data from PokéAPI and return it as a Python dictionary."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

# -------------------------------------------------------------------

generation_list = get_json(BASE_URL + "generation?limit=100")

generations = []

for item in generation_list["results"]:
    data = get_json(item["url"])

    if data["main_region"] is not None:
        region = data["main_region"]["name"]
    else:
        region = "unknown"

    generations.append({
        "id": data["id"],
        "name": data["name"],
        "region": region,
        "species": data["pokemon_species"]
    })

# Put generations in numerical order
generations.sort(key=lambda x: x["id"])

print("Pokémon introduced by generation:\n")

for generation in generations:
    print(
        f"Generation {generation['id']} "
        f"({generation['region'].title()}): "
        f"{len(generation['species'])} Pokémon"
    )

# -------------------------------------------------------------------

labels = []
counts = []

for generation in generations:
    labels.append(
        f"Gen {generation['id']}\n{generation['region'].title()}"
    )
    counts.append(len(generation["species"]))

plt.figure(figsize=(10, 6))
plt.bar(labels, counts)

plt.title("Pokémon Introduced by Generation")
plt.xlabel("Generation")
plt.ylabel("Number of Pokémon")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# -------------------------------------------------------------------

generation_results = []

for generation in generations:

    print(
        f"Analyzing Generation {generation['id']} "
        f"({generation['region'].title()})..."
    )

    type_counts = {}
    single_type = 0
    dual_type = 0
    type_pokemon = {}

    for species in generation["species"]:

        # Get the Pokémon's numerical ID from its species URL
        pokemon_id = species["url"].strip("/").split("/")[-1]

        pokemon = get_json(BASE_URL + "pokemon/" + pokemon_id)

        pokemon_types = []

        for type_info in pokemon["types"]:
            pokemon_types.append(type_info["type"]["name"])

        # Count each type
        # A Pokémon with two types is counted once in each type category.
        # For example, a Fire/Flying Pokémon adds 1 to Fire and 1 to Flying.
        # Because of this, the type counts will add up to more than the total
        # number of Pokémon in a generation.
        for pokemon_type in pokemon_types:

            if pokemon_type in type_counts:
                type_counts[pokemon_type] += 1
            else:
                type_counts[pokemon_type] = 1
                
            # Also save the names of Pokémon belonging to each type
            if pokemon_type not in type_pokemon:
                type_pokemon[pokemon_type] = []

            type_pokemon[pokemon_type].append(species["name"])

        # Count single-type vs dual-type Pokémon
        if len(pokemon_types) == 1:
            single_type += 1

        elif len(pokemon_types) == 2:
            dual_type += 1

    generation_results.append({
        "id": generation["id"],
        "region": generation["region"],
        "total": len(generation["species"]),
        "types": type_counts,
        "type_pokemon": type_pokemon,
        "single": single_type,
        "dual": dual_type
    })
print("Done analyzing all generations!")

# ------------------------------------------------------------
# Interactive generation and type lookup

print("\nInteractive Pokémon Type Lookup")

generation_choice = input(
    "Enter a generation number (1-9): "
)

if generation_choice.isdigit():
    generation_choice = int(generation_choice)

    selected_generation = None

    for generation in generation_results:
        if generation["id"] == generation_choice:
            selected_generation = generation
            break

    if selected_generation is not None:

        print(
            f"\nGeneration {selected_generation['id']} "
            f"({selected_generation['region'].title()})"
        )

        print(
            f"Total Pokémon introduced: "
            f"{selected_generation['total']}"
        )

        print(
            f"Single-type Pokémon: "
            f"{selected_generation['single']}"
        )

        print(
            f"Dual-type Pokémon: "
            f"{selected_generation['dual']}"
        )

        type_choice = input(
            "\nEnter a Pokémon type to look up "
            "(for example Fire, Water, or Grass): "
        ).lower()

        type_count = selected_generation["types"].get(type_choice, 0)
        pokemon_list = selected_generation["type_pokemon"].get(type_choice, [])

        print(
            f"\nGeneration {generation_choice} introduced "
            f"{type_count} {type_choice.title()}-type Pokémon."
)

        if pokemon_list:
            print("\nThose Pokémon are:")

        for pokemon_name in pokemon_list:
            formatted_name = pokemon_name.replace("-", " ").title()
            print(f"- {formatted_name}")
else:
    print("No Pokémon of that type were introduced in this generation.")

# -------------------------------------------------------------------

for generation in generation_results:

    print()
    print(
        f"Generation {generation['id']} "
        f"({generation['region'].title()})"
    )

    sorted_types = sorted(
        generation["types"].items(),
        key=lambda x: x[1],
        reverse=True
    )

    for pokemon_type, count in sorted_types:
        print(f"{pokemon_type.title()}: {count}")

    most_common = sorted_types[0]

    print(
        f"Most common type: "
        f"{most_common[0].title()} ({most_common[1]})"
    )

    print(f"Single-type Pokémon: {generation['single']}")
    print(f"Dual-type Pokémon: {generation['dual']}")

# -------------------------------------------------------------------

all_types = set()

for generation in generation_results:
    for pokemon_type in generation["types"]:
        all_types.add(pokemon_type)

all_types = sorted(all_types)

type_matrix = []

for pokemon_type in all_types:
    row = []

    for generation in generation_results:
        count = generation["types"].get(pokemon_type, 0)
        row.append(count)

    type_matrix.append(row)


plt.figure(figsize=(11, 8))

# "plasma" changes the heatmap to a purple/orange/yellow color scheme
image = plt.imshow(type_matrix, aspect="auto", cmap="coolwarm")

plt.colorbar(image, label="Number of Pokémon")

plt.yticks(
    range(len(all_types)),
    [pokemon_type.title() for pokemon_type in all_types]
)

plt.xticks(
    range(len(generation_results)),
    [f"Gen {generation['id']}" for generation in generation_results]
)

plt.title("Pokémon Types by Generation")
plt.xlabel("Generation")
plt.ylabel("Type")

plt.tight_layout()
plt.show()

# -------------------------------------------------------------------

# These bars show type assignments, not unique Pokémon.
# A dual-type Pokémon contributes to both of its types, so the total
# height of a bar can be greater than the number of Pokémon introduced
# in that generation.

generation_labels = []

for generation in generation_results:
    generation_labels.append(f"Gen {generation['id']}")

# Keeps track of how high the previous type bars have already stacked
bottom = [0] * len(generation_results)

plt.figure(figsize=(12, 7))

for pokemon_type in all_types:

    counts = []

    for generation in generation_results:
        counts.append(
            generation["types"].get(pokemon_type, 0)
        )

    plt.bar(
        generation_labels,
        counts,
        bottom=bottom,
        label=pokemon_type.title()
    )

    # Move the starting point upward for the next type
    for i in range(len(bottom)):
        bottom[i] += counts[i]


plt.title("Type Representation by Pokémon Generation")
plt.xlabel("Generation")
plt.ylabel("Number of Type Assignments")

plt.legend(
    title="Type",
    bbox_to_anchor=(1.05, 1),
    loc="upper left"
)

plt.tight_layout()
plt.show()

# -------------------------------------------------------------------

chain_list = get_json(BASE_URL + "evolution-chain?limit=1000")

one_stage = 0
two_stage = 0
three_stage = 0

# These counts represent evolution families, not individual Pokémon.
# Because multiple Pokémon can belong to the same evolution family,
# the total number of evolution lines will be smaller than the total
# number of Pokémon species.

print("Analyzing evolution chains...")

# Each family is classified by the deepest evolution stage it reaches,
# meaning, rather than looking at how many evolutions a Pokémon has, like
# Eevee which has multiple evolution forms, it's simply looking at how many
# times the Pokémon evolves.

for item in chain_list["results"]:

    data = get_json(item["url"])
    chain = data["chain"]

    # No evolves_to means this Pokémon does not evolve
    if len(chain["evolves_to"]) == 0:
        one_stage += 1

    else:
        has_third_stage = False

        for second_stage in chain["evolves_to"]:

            if len(second_stage["evolves_to"]) > 0:
                has_third_stage = True

        if has_third_stage:
            three_stage += 1
        else:
            two_stage += 1


print()
print("Evolution family summary:")
print("1-stage / no evolution:", one_stage)
print("2-stage evolution lines:", two_stage)
print("3-stage evolution lines:", three_stage)

# -------------------------------------------------------------------

categories = [
    "No Evolution",
    "2 Stages",
    "3 Stages"
]

values = [
    one_stage,
    two_stage,
    three_stage
]

plt.figure(figsize=(8, 5))
plt.bar(categories, values)

plt.title("Pokémon Evolution Families")
plt.xlabel("Evolution Line Length")
plt.ylabel("Number of Evolution Families")

plt.tight_layout()
plt.show()

