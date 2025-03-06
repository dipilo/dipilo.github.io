import itertools
import random
import json
import os
import uuid
import shlex
from collections import defaultdict

######################################
# GLOBAL SETTINGS AND SAVED HYBRIDS STORAGE
######################################

SAVE_MODE = False  # Toggle for save mode
SAVED_FILE = "hybrids.json"
saved_hybrids = {}

def load_saved_hybrids():
    global saved_hybrids
    if os.path.exists(SAVED_FILE):
        try:
            with open(SAVED_FILE, "r") as f:
                loaded = json.load(f)
                saved_hybrids = {k.lower(): v for k, v in loaded.items()}
        except Exception as e:
            print("Error loading saved hybrids:", e)
            saved_hybrids = {}
    else:
        saved_hybrids = {}

def save_saved_hybrids():
    try:
        with open(SAVED_FILE, "w") as f:
            json.dump(saved_hybrids, f, indent=4)
    except Exception as e:
        print("Error saving hybrids:", e)

# Species-specific naming dictionaries based on fantasy tropes.
SPECIES_NAME_DICT = {
    "human": {"adjectives": ["Noble", "Valiant", "Wise", "Just", "Stalwart", "Gallant", "Resolute"],
              "nouns": ["Sovereign", "Knight", "Baron", "Emperor", "Scholar", "Champion", "Guardian"]},
    "centaur": {"adjectives": ["Wild", "Gallant", "Mighty", "Fierce"],
                "nouns": ["Stallion", "Archer", "Warrior", "Hunter"]},
    "mermaid": {"adjectives": ["Mystic", "Siren", "Oceanic", "Luminous"],
                "nouns": ["Maiden", "Siren", "Daughter", "Enchantress"]},
    "horse": {"adjectives": ["Swift", "Stalwart", "Majestic", "Noble"],
              "nouns": ["Steed", "Charger", "Mustang", "Galloper"]},
    "hippocampus": {"adjectives": ["Deep", "Blue", "Mystic", "Tidal"],
                    "nouns": ["Seahorse", "Triton", "Neptune", "Mariner"]},
    "fish": {"adjectives": ["Glimmering", "Silver", "Abyssal", "Sleek"],
             "nouns": ["Mariner", "Fin", "Scale", "Swimmer"]},
    "satyr/faun": {"adjectives": ["Wild", "Revelrous", "Mischievous", "Impish"],
                   "nouns": ["Satyr", "Faun", "Pan", "Bacchus"]},
    "naga": {"adjectives": ["Serpentine", "Venomous", "Sly", "Coiled"],
             "nouns": ["Cobra", "Viper", "Asp", "Python"]},
    "minotaur": {"adjectives": ["Fierce", "Rampaging", "Mighty", "Colossal"],
                 "nouns": ["Bull", "Behemoth", "Taurus", "Goliath"]},
    "harpy": {"adjectives": ["Screeching", "Winged", "Wild", "Tempestuous"],
              "nouns": ["Harpy", "Raptor", "Screamer", "Stormcaller"]},
    "griffin": {"adjectives": ["Majestic", "Golden", "Regal", "Imperial"],
                "nouns": ["Griffin", "Sky King", "Lion-Eagle", "Celestial"]},
    "chimera": {"adjectives": ["Hybrid", "Fused", "Nightmare", "Mutant"],
                "nouns": ["Abomination", "Mutant", "Beast", "Chimera"]},
    "cockatrice/basilisk": {"adjectives": ["Petrifying", "Cursed", "Venomous", "Sinister"],
                            "nouns": ["Cockatrice", "Basilisk", "Gorgon", "Medusa"]},
    "hippogriff": {"adjectives": ["Noble", "Skyborne", "Valiant", "Aerial"],
                   "nouns": ["Hippogriff", "Windrider", "Sky Knight", "Cloudstrider"]},
    "manticore": {"adjectives": ["Savage", "Dread", "Nightstalker", "Terrifying"],
                  "nouns": ["Manticore", "Scourge", "Beast", "Fury"]},
    "pegasus": {"adjectives": ["Celestial", "Winged", "Ethereal", "Radiant"],
                "nouns": ["Pegasus", "Cloudrider", "Skyborne", "Zephyr"]},
    "goat": {"adjectives": ["Stubborn", "Wild", "Rocky", "Spirited"],
             "nouns": ["Billy", "Capricorn", "Horned", "Mountain Goat"]},
    "snake": {"adjectives": ["Sinuous", "Venomous", "Slithering", "Creeping"],
              "nouns": ["Adder", "Viper", "Serpent", "Cobra"]},
    "bull": {"adjectives": ["Massive", "Raging", "Sturdy", "Titanic"],
             "nouns": ["Taurus", "Rampager", "Bovidae", "Goliath"]},
    "bird": {"adjectives": ["Feathered", "Swift", "Soaring", "Glorious"],
             "nouns": ["Avian", "Winged", "Skycaller", "Celestial"]},
    "lion": {"adjectives": ["Regal", "Mighty", "Savage", "Imperial"],
             "nouns": ["King", "Pride", "Roarer", "Majesty"]},
    "ipotane": {"adjectives": ["Hybrid", "Mystic", "Noble", "Enigmatic"],
                "nouns": ["Centaur", "Maned Steed", "Chimera", "Unity"]},
    "dragon": {"adjectives": ["Fiery", "Ancient", "Mighty", "Infernal", "Scaly", "Blazing"],
               "nouns": ["Wyrm", "Drake", "Serpent", "Flame", "Sovereign", "Ember", "Scourge"]},
    "tengu": {"adjectives": ["Mischievous", "Cunning", "Aerial", "Sleek", "Mystic", "Ethereal"],
              "nouns": ["Tengu", "Crow", "Harbinger", "Trickster", "Raven", "Shade"]}
}

def generate_unique_name(species=None):
    if species and species.lower() in SPECIES_NAME_DICT:
        name_dict = SPECIES_NAME_DICT[species.lower()]
        adjectives = name_dict.get("adjectives", [])
        nouns = name_dict.get("nouns", [])
    else:
        adjectives = ["Mystic", "Shadow", "Radiant", "Ancient", "Fierce"]
        nouns = ["Entity", "Being", "Spirit", "Wraith", "Force"]
    for _ in range(10):
        name = f"{random.choice(adjectives)} {random.choice(nouns)}"
        if name.lower() not in saved_hybrids:
            return name
    return f"{random.choice(adjectives)} {random.choice(nouns)} {random.randint(1,1000)}"

######################################
# 1. ALLELES, MUTATION RATES, AND BASE STATS
######################################

ALLELES = ["Hu", "Ho", "Fi", "Go", "Sn", "Bu", "Bi", "Li", "Dr"]  # "Dr" represents the dragon allele

mutation_rates = {
    "Hu": 1e-6,
    "Ho": 1e-6,
    "Fi": 1e-5,
    "Go": 1e-6,
    "Sn": 1e-5,
    "Bu": 1e-6,
    "Bi": 1e-6,
    "Li": 1e-6,
    "Dr": 1e-6
}

def allele_mutation_distribution(allele):
    dist = {}
    rate = mutation_rates[allele]
    dist[allele] = 1 - rate
    for alt in ALLELES:
        if alt != allele:
            dist[alt] = rate / (len(ALLELES) - 1)
    return dist

def random_inherited_allele(gene_tuple):
    base = random.choice(gene_tuple)
    dist = allele_mutation_distribution(base)
    choices, probs = zip(*dist.items())
    return random.choices(choices, weights=probs, k=1)[0]

######################################
# 2. SPECIES DEFINITIONS & DOMINANCE
######################################

known_species = {
    ("Hu", "Hu", "Hu"): "human",
    ("Hu", "Hu", "Ho"): "centaur",
    ("Hu", "Hu", "Fi"): "mermaid",
    ("Ho", "Ho", "Ho"): "horse",
    ("Ho", "Ho", "Fi"): "hippocampus",
    ("Fi", "Fi", "Fi"): "fish",
    ("Hu", "Hu", "Go"): "satyr/faun",
    ("Hu", "Hu", "Sn"): "naga",
    ("Bu", "Hu", "Bu"): "minotaur",
    ("Hu", "Bi", "Bi"): "harpy",
    ("Bi", "Bi", "Li"): "griffin",
    ("Li", "Go", "Sn"): "chimera",
    ("Bi", "Dr", "Sn"): "cockatrice/basilisk",
    ("Bi", "Bi", "Ho"): "hippogriff",
    ("Hu", "Li", "Dr"): "manticore",
    ("Ho", "Bi", "Ho"): "pegasus",
    ("Go", "Go", "Go"): "goat",
    ("Sn", "Sn", "Sn"): "snake",
    ("Bu", "Bu", "Bu"): "bull",
    ("Bi", "Bi", "Bi"): "bird",
    ("Li", "Li", "Li"): "lion",
    ("Ho", "Hu", "Hu"): "ipotane",
    ("Dr", "Dr", "Dr"): "dragon",
    ("Bi", "Bi", "Hu"): "tengu"
}

def count_alleles(gene_index):
    counts = defaultdict(int)
    for phenotype in known_species:
        counts[phenotype[gene_index]] += 1
    return counts

top_counts = count_alleles(0)
mid_counts = count_alleles(1)
bottom_counts = count_alleles(2)

def dominance_order(counts):
    return sorted(ALLELES, key=lambda a: (-counts.get(a, 0), a))

top_dominance_order    = dominance_order(top_counts)
mid_dominance_order    = dominance_order(mid_counts)
bottom_dominance_order = dominance_order(bottom_counts)

######################################
# 3. GENE EXPRESSION FUNCTIONS
######################################

def express_gene(genotype, dom_order):
    for allele in dom_order:
        if allele in genotype:
            return allele
    return None

def top_expression(genotype):
    return express_gene(genotype, top_dominance_order)

def mid_expression(genotype):
    return express_gene(genotype, mid_dominance_order)

def bottom_expression(genotype):
    return express_gene(genotype, bottom_dominance_order)

def overall_phenotype(top_geno, mid_geno, bottom_geno):
    t = top_expression(top_geno)
    m = mid_expression(mid_geno)
    b = bottom_expression(bottom_geno)
    return known_species.get((t, m, b), None)

######################################
# 4. FULL GENOTYPE ENUMERATION
######################################

def all_gene_genotypes():
    return [tuple(g) for g in itertools.combinations_with_replacement(ALLELES, 2)]

all_full_genotypes = []
phenotype_genotypes = defaultdict(list)
for top_geno in all_gene_genotypes():
    for mid_geno in all_gene_genotypes():
        for bottom_geno in all_gene_genotypes():
            sp = overall_phenotype(top_geno, mid_geno, bottom_geno)
            if sp is not None:
                genotype = {
                    "top": tuple(sorted(top_geno)),
                    "mid": tuple(sorted(mid_geno)),
                    "bottom": tuple(sorted(bottom_geno))
                }
                all_full_genotypes.append((genotype, sp))
                phenotype_genotypes[sp].append(genotype)

######################################
# 5. CROSS-BREEDING FUNCTIONS
######################################

def cross_gene(g1, g2):
    outcomes = defaultdict(float)
    for allele1 in g1:
        dist1 = allele_mutation_distribution(allele1)
        for allele2 in g2:
            dist2 = allele_mutation_distribution(allele2)
            for a1, p1 in dist1.items():
                for a2, p2 in dist2.items():
                    outcome = tuple(sorted((a1, a2)))
                    outcomes[outcome] += 0.25 * p1 * p2
    return outcomes

def cross_breed_random(sp1, sp2):
    if sp1 not in phenotype_genotypes or sp2 not in phenotype_genotypes:
        raise ValueError("Invalid parent species name.")
    parent1 = random.choice(phenotype_genotypes[sp1])
    parent2 = random.choice(phenotype_genotypes[sp2])
    top_allele1 = random_inherited_allele(parent1["top"])
    top_allele2 = random_inherited_allele(parent2["top"])
    mid_allele1 = random_inherited_allele(parent1["mid"])
    mid_allele2 = random_inherited_allele(parent2["mid"])
    bottom_allele1 = random_inherited_allele(parent1["bottom"])
    bottom_allele2 = random_inherited_allele(parent2["bottom"])
    offspring_top = tuple(sorted((top_allele1, top_allele2)))
    offspring_mid = tuple(sorted((mid_allele1, mid_allele2)))
    offspring_bottom = tuple(sorted((bottom_allele1, bottom_allele2)))
    species = overall_phenotype(offspring_top, offspring_mid, offspring_bottom)
    return {
        "offspring_top": offspring_top,
        "offspring_mid": offspring_mid,
        "offspring_bottom": offspring_bottom,
        "phenotype": species,
        "parent1_genotype": parent1,
        "parent2_genotype": parent2
    }

def cross_breed_from_genotype(geno1, geno2):
    top_allele1 = random.choice(geno1["top"])
    top_allele2 = random.choice(geno2["top"])
    mid_allele1 = random.choice(geno1["mid"])
    mid_allele2 = random.choice(geno2["mid"])
    bottom_allele1 = random.choice(geno1["bottom"])
    bottom_allele2 = random.choice(geno2["bottom"])
    offspring_top = tuple(sorted((top_allele1, top_allele2)))
    offspring_mid = tuple(sorted((mid_allele1, mid_allele2)))
    offspring_bottom = tuple(sorted((bottom_allele1, bottom_allele2)))
    species = overall_phenotype(offspring_top, offspring_mid, offspring_bottom)
    return {"top": offspring_top, "mid": offspring_mid, "bottom": offspring_bottom}, species

######################################
# 6. BASE STAT DICTIONARIES (Realistic Averages)
######################################

TOP_STATS = {
    "Hu": {"IQ": 100, "EQ": 90, "Dexterity": 85, "Strength": 60},
    "Ho": {"IQ": 50,  "EQ": 40, "Dexterity": 50, "Strength": 200},
    "Fi": {"IQ": 10,  "EQ": 10, "Dexterity": 20, "Strength": 5},
    "Go": {"IQ": 60,  "EQ": 55, "Dexterity": 75, "Strength": 70},
    "Sn": {"IQ": 25,  "EQ": 20, "Dexterity": 65, "Strength": 15},
    "Bu": {"IQ": 30,  "EQ": 25, "Dexterity": 40, "Strength": 250},
    "Bi": {"IQ": 40,  "EQ": 35, "Dexterity": 80, "Strength": 15},
    "Li": {"IQ": 70,  "EQ": 60, "Dexterity": 70, "Strength": 220},
    "Dr": {"IQ": 120,  "EQ": 115, "Dexterity": 85, "Strength": 300}
}

BOTTOM_STATS = {
    "Hu": {"Land Speed": 8.0,  "Swim Speed": 3.0, "Jump Height": 0.6},
    "Ho": {"Land Speed": 45.0, "Swim Speed": 8.0, "Jump Height": 1.2},
    "Fi": {"Land Speed": 0.5,  "Swim Speed": 20.0, "Jump Height": 0.3},
    "Go": {"Land Speed": 20.0, "Swim Speed": 3.0, "Jump Height": 1.0},
    "Sn": {"Land Speed": 1.0,  "Swim Speed": 2.0, "Jump Height": 0.1},
    "Bu": {"Land Speed": 25.0, "Swim Speed": 4.0, "Jump Height": 0.8},
    "Bi": {"Land Speed": 10.0, "Swim Speed": 8.0, "Jump Height": 0.5},
    "Li": {"Land Speed": 60.0, "Swim Speed": 12.0, "Jump Height": 2.0},
    "Dr": {"Land Speed": 50.0, "Swim Speed": 15.0, "Jump Height": 3.0}
}

FLIGHT_STATS = {
    "Bi": 60.0,
    "Dr": 50.0
}

CLIMBING_STATS = {
    "Hu": {"Climbing": 2.0},
    "Ho": {"Climbing": 1.0},
    "Fi": {"Climbing": 0.1},
    "Go": {"Climbing": 15.0},
    "Sn": {"Climbing": 3.0},
    "Bu": {"Climbing": 1.0},
    "Bi": {"Climbing": 5.0},
    "Li": {"Climbing": 4.0},
    "Dr": {"Climbing": 6.0}
}

BITE_STATS = {
    "Hu": {"Bite": 200},
    "Ho": {"Bite": 350},
    "Fi": {"Bite": 50},
    "Go": {"Bite": 250},
    "Sn": {"Bite": 300},
    "Bu": {"Bite": 800},
    "Bi": {"Bite": 100},
    "Li": {"Bite": 700},
    "Dr": {"Bite": 900}
}

# New SIZE_STATS dictionary (in centimeters)
SIZE_STATS = {
    "Hu": 170,
    "Ho": 160,
    "Fi": 15,
    "Go": 120,
    "Sn": 250,
    "Bu": 200,
    "Bi": 50,
    "Li": 130,
    "Dr": 300
}

# Add a diet mapping for each allele.
DIET = {
    "Hu": "omnivore",
    "Ho": "herbivore",
    "Fi": "omnivore",
    "Go": "herbivore",
    "Sn": "carnivore",
    "Bu": "herbivore",
    "Bi": "omnivore",
    "Li": "carnivore",
    "Dr": "carnivore"
}

######################################
# 7. SPECIES STAT SOURCE RULES
######################################

DEFAULT_STAT_SOURCES = {
    "IQ": ["top"],
    "EQ": ["top"],
    "Dexterity": ["top"],
    "Strength": ["top"],
    "Land Speed": ["bottom"],
    "Swim Speed": ["bottom"],
    "Jump Height": ["bottom"],
    "Flight Speed": [],
    "Climbing": ["bottom"],
    "Bite": ["top"],
    "Venom": ["top"],
    "Fire Breathing": ["top"]
}

SPECIES_STAT_SOURCES = {
    "human": DEFAULT_STAT_SOURCES,
    "centaur": DEFAULT_STAT_SOURCES,
    "mermaid": DEFAULT_STAT_SOURCES,
    "horse": DEFAULT_STAT_SOURCES,
    "hippocampus": DEFAULT_STAT_SOURCES,
    "fish": DEFAULT_STAT_SOURCES,
    "satyr/faun": DEFAULT_STAT_SOURCES,
    "naga": {
        "IQ": ["top"],
        "EQ": ["top"],
        "Dexterity": ["top"],
        "Strength": ["top"],
        "Land Speed": ["bottom"],
        "Swim Speed": ["bottom"],
        "Jump Height": ["bottom"],
        "Flight Speed": ["top"],
        "Climbing": ["bottom"],
        "Bite": ["top"],
        "Venom": ["bottom"],
        "Fire Breathing": ["top"]
    },
    "minotaur": DEFAULT_STAT_SOURCES,
    "harpy": {
        "IQ": ["top"],
        "EQ": ["top"],
        "Dexterity": ["mid"],
        "Strength": ["top"],
        "Land Speed": ["top"],
        "Swim Speed": ["top"],
        "Jump Height": ["top"],
        "Flight Speed": ["mid"],
        "Climbing": ["bottom"],
        "Bite": ["top"],
        "Venom": ["top"],
        "Fire Breathing": ["top"]
    },
    "griffin": {
        "IQ": ["top"],
        "EQ": ["top"],
        "Dexterity": ["top"],
        "Strength": ["bottom"],
        "Land Speed": ["bottom"],
        "Swim Speed": ["bottom"],
        "Jump Height": ["bottom"],
        "Flight Speed": ["top"],
        "Climbing": ["bottom"],
        "Bite": ["top"],
        "Venom": ["top"],
        "Fire Breathing": ["top"]
    },
    "chimera": {
        "IQ": ["top", "mid", "bottom"],
        "EQ": ["top", "mid", "bottom"],
        "Dexterity": ["top"],
        "Strength": ["top"],
        "Land Speed": ["bottom"],
        "Swim Speed": ["bottom"],
        "Jump Height": ["bottom"],
        "Flight Speed": [],
        "Climbing": ["bottom"],
        "Bite": ["top"],
        "Venom": ["bottom"],
        "Fire Breathing": ["top"]
    },
    "cockatrice/basilisk": {
        "IQ": ["top"],
        "EQ": ["top"],
        "Dexterity": ["top"],
        "Strength": ["bottom"],
        "Land Speed": ["bottom"],
        "Swim Speed": ["bottom"],
        "Jump Height": ["bottom"],
        "Flight Speed": ["top"],
        "Climbing": ["bottom"],
        "Bite": ["top"],
        "Venom": ["bottom"],
        "Fire Breathing": ["top"]
    },
    "hippogriff": {
        "IQ": ["top"],
        "EQ": ["top"],
        "Dexterity": ["top"],
        "Strength": ["bottom"],
        "Land Speed": ["bottom"],
        "Swim Speed": ["bottom"],
        "Jump Height": ["bottom"],
        "Flight Speed": ["top"],
        "Climbing": ["bottom"],
        "Bite": ["top"],
        "Venom": ["top"],
        "Fire Breathing": ["top"]
    },
    "manticore": {
        "IQ": ["top"],
        "EQ": ["top"],
        "Dexterity": ["mid"],
        "Strength": ["mid"],
        "Land Speed": ["mid"],
        "Swim Speed": ["mid"],
        "Jump Height": ["mid"],
        "Flight Speed": [],
        "Climbing": ["bottom"],
        "Bite": ["top"],
        "Venom": ["bottom"],
        "Fire Breathing": ["top"]
    },
    "pegasus": {
        "IQ": ["top"],
        "EQ": ["top"],
        "Dexterity": ["top"],
        "Strength": ["top"],
        "Land Speed": ["bottom"],
        "Swim Speed": ["bottom"],
        "Jump Height": ["bottom"],
        "Flight Speed": ["mid"],
        "Climbing": ["bottom"],
        "Bite": ["top"],
        "Venom": ["top"],
        "Fire Breathing": ["top"]
    },
    "goat": DEFAULT_STAT_SOURCES,
    "snake": DEFAULT_STAT_SOURCES,
    "bull": DEFAULT_STAT_SOURCES,
    "bird": {
        "IQ": ["top"],
        "EQ": ["top"],
        "Dexterity": ["top"],
        "Strength": ["top"],
        "Land Speed": ["bottom"],
        "Swim Speed": ["bottom"],
        "Jump Height": ["bottom"],
        "Flight Speed": ["top"],
        "Climbing": ["bottom"],
        "Bite": ["top"],
        "Venom": ["top"],
        "Fire Breathing": ["top"]
    },
    "lion": DEFAULT_STAT_SOURCES,
    "ipotane": {
        "IQ": ["mid"],
        "EQ": ["mid"],
        "Dexterity": ["mid"],
        "Strength": ["mid"],
        "Land Speed": ["bottom"],
        "Swim Speed": ["bottom"],
        "Jump Height": ["bottom"],
        "Flight Speed": [],
        "Climbing": ["bottom"],
        "Bite": ["top"],
        "Venom": ["top"],
        "Fire Breathing": ["top"]
    },
    "dragon": DEFAULT_STAT_SOURCES,
    "tengu": {
        "IQ": ["bottom"],
        "EQ": ["bottom"],
        "Dexterity": ["bottom"],
        "Strength": ["bottom"],
        "Land Speed": ["bottom"],
        "Swim Speed": ["bottom"],
        "Jump Height": ["bottom"],
        "Flight Speed": ["mid"],
        "Climbing": ["bottom"],
        "Bite": ["top"],
        "Venom": ["top"],
        "Fire Breathing": ["top"]
    }
}

######################################
# 8. STAT CALCULATION FUNCTIONS (Including Stat Mutation and Size)
######################################

STAT_MUTATION_RATE = 0.0001  # 0.01% chance per stat

def get_stat_base(stat, section, allele):
    if stat in ["IQ", "EQ", "Dexterity", "Strength"]:
        return TOP_STATS[allele][stat]
    elif stat in ["Land Speed", "Swim Speed", "Jump Height"]:
        return BOTTOM_STATS[allele][stat]
    elif stat == "Flight Speed":
        return FLIGHT_STATS.get(allele, 0)
    elif stat == "Climbing":
        return CLIMBING_STATS[allele]["Climbing"]
    elif stat == "Bite":
        return BITE_STATS[allele]["Bite"]
    elif stat == "Venom":
        return 1 if allele in ["Sn", "Dr"] else 0
    elif stat == "Fire Breathing":
        return 1 if allele == "Dr" else 0
    else:
        return 0

def apply_random_variation(value):
    factor = random.uniform(0.9, 1.1)
    return round(value * factor, 3)

def maybe_mutate_stat(value, stat):
    if random.random() < STAT_MUTATION_RATE:
        if stat in ["Venom", "Fire Breathing"]:
            mutated_value = not value
            message = f"{stat} mutated from {value} to {mutated_value}"
            return mutated_value, message
        else:
            factor = random.uniform(0.5, 1.5)
            mutated_value = round(value * factor, 3)
            message = f"{stat} mutated: multiplied by {round(factor,3)} (from {value} to {mutated_value})"
            return mutated_value, message
    return value, None

def generate_individual_stats(species, top_expr, mid_expr, bottom_expr):
    if species != "chimera":
        overall_diet = DIET.get(top_expr, "omnivore")
    stats = {}
    mutations = {}
    if species == "chimera":
        iq_top = apply_random_variation(TOP_STATS[top_expr]["IQ"])
        iq_top, mut_iq_top = maybe_mutate_stat(iq_top, "IQ")
        iq_mid = apply_random_variation(TOP_STATS[mid_expr]["IQ"])
        iq_mid, mut_iq_mid = maybe_mutate_stat(iq_mid, "IQ")
        iq_bottom = apply_random_variation(TOP_STATS[bottom_expr]["IQ"])
        iq_bottom, mut_iq_bottom = maybe_mutate_stat(iq_bottom, "IQ")
        eq_top = apply_random_variation(TOP_STATS[top_expr]["EQ"])
        eq_top, mut_eq_top = maybe_mutate_stat(eq_top, "EQ")
        eq_mid = apply_random_variation(TOP_STATS[mid_expr]["EQ"])
        eq_mid, mut_eq_mid = maybe_mutate_stat(eq_mid, "EQ")
        eq_bottom = apply_random_variation(TOP_STATS[bottom_expr]["EQ"])
        eq_bottom, mut_eq_bottom = maybe_mutate_stat(eq_bottom, "EQ")
        stats["Lion Head IQ"] = iq_top
        stats["Goat Head IQ"] = iq_mid
        stats["Snake Head IQ"] = iq_bottom
        stats["Lion Head EQ"] = eq_top
        stats["Goat Head EQ"] = eq_mid
        stats["Snake Head EQ"] = eq_bottom
        stats["Lion Head Diet"] = DIET.get(top_expr, "omnivore")
        stats["Goat Head Diet"] = DIET.get(mid_expr, "omnivore")
        stats["Snake Head Diet"] = DIET.get(bottom_expr, "omnivore")
        for stat in ["Dexterity", "Strength", "Land Speed", "Swim Speed", "Jump Height", "Flight Speed", "Climbing", "Bite", "Venom", "Fire Breathing"]:
            sources = SPECIES_STAT_SOURCES.get(species, DEFAULT_STAT_SOURCES).get(stat, [])
            if not sources:
                base = 0
            else:
                values = []
                for sec in sources:
                    allele = {"top": top_expr, "mid": mid_expr, "bottom": bottom_expr}.get(sec)
                    values.append(get_stat_base(stat, sec, allele))
                base = sum(values) / len(values)
            if stat in ["Venom", "Fire Breathing"]:
                value = True if base >= 0.5 else False
                final_value, msg = maybe_mutate_stat(value, stat)
            else:
                value = apply_random_variation(base)
                final_value, msg = maybe_mutate_stat(value, stat)
            stats[stat] = final_value
            if msg:
                mutations[stat] = msg
        if mut_iq_top: mutations["Lion Head IQ"] = mut_iq_top
        if mut_iq_mid: mutations["Goat Head IQ"] = mut_iq_mid
        if mut_iq_bottom: mutations["Snake Head IQ"] = mut_iq_bottom
        if mut_eq_top: mutations["Lion Head EQ"] = mut_eq_top
        if mut_eq_mid: mutations["Goat Head EQ"] = mut_eq_mid
        if mut_eq_bottom: mutations["Snake Head EQ"] = mut_eq_bottom
    else:
        for stat in ["IQ", "EQ", "Dexterity", "Strength",
                     "Land Speed", "Swim Speed", "Jump Height",
                     "Flight Speed", "Climbing", "Bite", "Venom", "Fire Breathing"]:
            sources = SPECIES_STAT_SOURCES.get(species, DEFAULT_STAT_SOURCES).get(stat, [])
            if not sources:
                base = 0
            else:
                values = []
                for sec in sources:
                    allele = {"top": top_expr, "mid": mid_expr, "bottom": bottom_expr}.get(sec)
                    values.append(get_stat_base(stat, sec, allele))
                base = sum(values) / len(values)
            if stat in ["Venom", "Fire Breathing"]:
                value = True if base >= 0.5 else False
                final_value, msg = maybe_mutate_stat(value, stat)
            else:
                value = apply_random_variation(base)
                final_value, msg = maybe_mutate_stat(value, stat)
            stats[stat] = final_value
            if msg:
                mutations[stat] = msg
        stats["diet"] = DIET.get(top_expr, "omnivore")
        if species == "naga":
            stats["Strength"] = round(stats["Strength"] * 1.5, 3)
            stats["Dexterity"] = round(stats["Dexterity"] * 1.5, 3)
            stats["Climbing"] = round(stats["Climbing"] * 1.5, 3)
    size_val = (SIZE_STATS.get(top_expr, 170) + SIZE_STATS.get(mid_expr, 170) + SIZE_STATS.get(bottom_expr, 170)) / 3.0
    size_val = apply_random_variation(size_val)
    size_val, size_mut = maybe_mutate_stat(size_val, "Size")
    stats["Size"] = size_val
    if size_mut:
        mutations["Size"] = size_mut
    return stats, mutations

######################################
# 9. OFFSPRING BREEDING FROM SAVED HYBRIDS
######################################

def cross_breed_from_genotype(geno1, geno2):
    top_allele1 = random.choice(geno1["top"])
    top_allele2 = random.choice(geno2["top"])
    mid_allele1 = random.choice(geno1["mid"])
    mid_allele2 = random.choice(geno2["mid"])
    bottom_allele1 = random.choice(geno1["bottom"])
    bottom_allele2 = random.choice(geno2["bottom"])
    offspring_top = tuple(sorted((top_allele1, top_allele2)))
    offspring_mid = tuple(sorted((mid_allele1, mid_allele2)))
    offspring_bottom = tuple(sorted((bottom_allele1, bottom_allele2)))
    species = overall_phenotype(offspring_top, offspring_mid, offspring_bottom)
    return {"top": offspring_top, "mid": offspring_mid, "bottom": offspring_bottom}, species

def breed_from_saved(parent1_name, parent2_name):
    if parent1_name not in saved_hybrids or parent2_name not in saved_hybrids:
        print("One or both parent names not found in saved hybrids.")
        return None
    parent1 = saved_hybrids[parent1_name]
    parent2 = saved_hybrids[parent2_name]
    geno1 = parent1.get("genotype", None)
    geno2 = parent2.get("genotype", None)
    if geno1 is None or geno2 is None:
        print("Saved parents do not have genotype info. Cannot breed using genotype simulation.")
        return None
    MAX_ATTEMPTS = 10
    attempt = 0
    offspring_geno, species = None, None
    while attempt < MAX_ATTEMPTS:
        offspring_geno, species = cross_breed_from_genotype(geno1, geno2)
        if species is not None:
            break
        attempt += 1
    if species is None:
        print("Miscarriage: Offspring species could not be determined after several attempts.")
        return None
    sim_stats, sim_mutations = generate_individual_stats(
        species,
        top_expression(offspring_geno["top"]),
        mid_expression(offspring_geno["mid"]),
        bottom_expression(offspring_geno["bottom"])
    )
    parents_avg = {}
    for stat in ["IQ", "EQ", "Dexterity", "Strength",
                 "Land Speed", "Swim Speed", "Jump Height",
                 "Flight Speed", "Climbing", "Bite"]:
        parents_avg[stat] = round((parent1["stats"][stat] + parent2["stats"][stat]) / 2, 3)
    venom_avg = ((1 if parent1["stats"]["Venom"] else 0) + (1 if parent2["stats"]["Venom"] else 0)) / 2
    weight_genotype = 0.7
    weight_parents = 0.3
    final_stats = {}
    combined_mutations = {}
    for stat in ["IQ", "EQ", "Dexterity", "Strength",
                 "Land Speed", "Swim Speed", "Jump Height",
                 "Flight Speed", "Climbing", "Bite"]:
        final_val = round(weight_genotype * sim_stats[stat] + weight_parents * parents_avg[stat], 3)
        final_stats[stat] = final_val
        if stat in sim_mutations:
            combined_mutations[stat] = sim_mutations[stat]
    sim_venom = 1 if sim_stats["Venom"] else 0
    final_venom_num = weight_genotype * sim_venom + weight_parents * venom_avg
    final_stats["Venom"] = True if final_venom_num >= 0.5 else False
    if "Venom" in sim_mutations:
        combined_mutations["Venom"] = sim_mutations["Venom"]
    offspring = {
        "name": generate_unique_name(species),
        "genotype": offspring_geno,
        "species": species,
        "stats": final_stats,
        "mode": "saved_breed",
        "parents": [parent1_name, parent2_name]
    }
    saved_hybrids[offspring["name"].lower()] = offspring
    save_saved_hybrids()
    return offspring, combined_mutations

######################################
# NEW: RANDOM SIMULATION COMMAND
######################################

def simulate_random(n):
    frequency = defaultdict(int)
    for _ in range(n):
        _, species = random.choice(all_full_genotypes)
        frequency[species] += 1
    print("\n--- RANDOM SIMULATION RESULTS ---")
    for sp, count in frequency.items():
        print(f"{sp}: {count} times")

######################################
# 10. INTERACTIVE COMMAND-LINE INTERFACE
######################################

def list_species():
    print("Available species (from known definitions):")
    for sp in sorted(phenotype_genotypes.keys()):
        print("  " + sp)
    if SAVE_MODE:
        print("\nSaved hybrids:")
        for name in sorted(saved_hybrids.keys()):
            record = saved_hybrids[name]
            print(f"  {record['name']} (Species: {record['species']}, Genotype: {record.get('genotype','N/A')})")

def breed_species(cmd_args):
    if len(cmd_args) != 2:
        print("Usage: breed [species_or_saved_name1] [species_or_saved_name2]")
        return
    arg1, arg2 = cmd_args[0].lower(), cmd_args[1].lower()
    if SAVE_MODE and (arg1 in saved_hybrids and arg2 in saved_hybrids):
        offspring_data = breed_from_saved(arg1, arg2)
        if offspring_data is None:
            return
        offspring, mutations = offspring_data
        print("\n--- BREEDING RESULT (from saved hybrids) ---")
        print("Parent 1:", saved_hybrids[arg1]["name"], f"(Species: {saved_hybrids[arg1]['species']}, Genotype: {saved_hybrids[arg1].get('genotype','N/A')})")
        print("Parent 2:", saved_hybrids[arg2]["name"], f"(Species: {saved_hybrids[arg2]['species']}, Genotype: {saved_hybrids[arg2].get('genotype','N/A')})")
        print("Offspring name:", offspring["name"])
        print("Inherited species:", offspring["species"])
        print("Offspring genotype:")
        print("  Top   :", offspring["genotype"]["top"])
        print("  Mid   :", offspring["genotype"]["mid"])
        print("  Bottom:", offspring["genotype"]["bottom"])
        print("Inherited stats:")
        for stat, value in offspring["stats"].items():
            print(f"  {stat:15s}: {value}", end="")
            if stat in mutations:
                print(f"  <-- {mutations[stat]}")
            else:
                print("")
    else:
        try:
            MAX_ATTEMPTS = 10
            attempt = 0
            result = None
            while attempt < MAX_ATTEMPTS:
                result = cross_breed_random(arg1, arg2)
                if result["phenotype"] is not None:
                    break
                attempt += 1
            if result is None or result["phenotype"] is None:
                print("Miscarriage: Offspring species could not be determined after several attempts.")
                return
        except ValueError as e:
            print("Error:", e)
            return
        print("\n--- BREEDING RESULT (from known species simulation) ---")
        print(f"Parent 1 ({arg1}) - Genotype: {result['parent1_genotype']}")
        print(f"Parent 2 ({arg2}) - Genotype: {result['parent2_genotype']}")
        print("\nOffspring genotype:")
        print("  Top   :", result["offspring_top"])
        print("  Mid   :", result["offspring_mid"])
        print("  Bottom:", result["offspring_bottom"])
        print("Offspring species:", result["phenotype"])
        if result["phenotype"] is not None:
            off_top = top_expression(result["offspring_top"])
            off_mid = mid_expression(result["offspring_mid"])
            off_bottom = bottom_expression(result["offspring_bottom"])
            stats, mutations = generate_individual_stats(result["phenotype"], off_top, off_mid, off_bottom)
            if SAVE_MODE:
                new_name = generate_unique_name(result["phenotype"])
                record = {
                    "name": new_name,
                    "genotype": {
                        "top": list(result["offspring_top"]),
                        "mid": list(result["offspring_mid"]),
                        "bottom": list(result["offspring_bottom"])
                    },
                    "species": result["phenotype"],
                    "stats": stats,
                    "mode": "generated",
                    "parents": []
                }
                saved_hybrids[new_name.lower()] = record
                save_saved_hybrids()
                print(f"\nAssigned unique name: {new_name}")
            print("\nOffspring stats (sources per stat are defined by species):")
            for stat, value in stats.items():
                print(f"  {stat:15s}: {value}", end="")
                if stat in mutations:
                    print(f"  <-- {mutations[stat]}")
                else:
                    print("")
        else:
            print("The offspring species is unknown.")

def generate_random_species():
    genotype, sp = random.choice(all_full_genotypes)
    print("\n--- RANDOM SPECIES GENERATED ---")
    print("Genotype:")
    print("  Top   :", genotype["top"])
    print("  Mid   :", genotype["mid"])
    print("  Bottom:", genotype["bottom"])
    print("Species:", sp)
    expr_top = top_expression(genotype["top"])
    expr_mid = mid_expression(genotype["mid"])
    expr_bottom = bottom_expression(genotype["bottom"])
    stats, mutations = generate_individual_stats(sp, expr_top, expr_mid, expr_bottom)
    if SAVE_MODE:
        new_name = generate_unique_name(sp)
        record = {
            "name": new_name,
            "genotype": {
                "top": list(genotype["top"]),
                "mid": list(genotype["mid"]),
                "bottom": list(genotype["bottom"])
            },
            "species": sp,
            "stats": stats,
            "mode": "generated",
            "parents": []
        }
        saved_hybrids[new_name.lower()] = record
        save_saved_hybrids()
        print("Assigned unique name:", new_name)
    print("\nStats:")
    for stat, value in stats.items():
        print(f"  {stat:15s}: {value}", end="")
        if stat in mutations:
            print(f"  <-- {mutations[stat]}")
        else:
            print("")

def simulate_random(n):
    frequency = defaultdict(int)
    for _ in range(n):
        _, species = random.choice(all_full_genotypes)
        frequency[species] += 1
    print("\n--- RANDOM SIMULATION RESULTS ---")
    for sp, count in frequency.items():
        print(f"{sp}: {count} times")

def toggle_save_mode():
    global SAVE_MODE
    SAVE_MODE = not SAVE_MODE
    mode_status = "ON" if SAVE_MODE else "OFF"
    print(f"Save mode toggled {mode_status}.")

def print_help():
    help_text = """
Commands:
  toggle                    - Toggle save mode ON/OFF
  list                      - List available known species and saved hybrids
  breed [arg1] [arg2]       - Breed two species or saved hybrids (if names exist in saved list)
                              e.g., breed naga pegasus or breed "Silver Griffin" "Mystic Stag"
  random                    - Generate a random species (with a unique name if save mode is ON)
  simulate [n]              - Run the random generation n times and list frequency of species produced
  help                      - Show this help message
  quit                      - Exit the simulator

Note: Enclose hybrid names containing spaces in quotes.
"""
    print(help_text)

def main():
    load_saved_hybrids()
    print("Welcome to the Expanded Hybrid Breeding Simulator!")
    print_help()
    while True:
        command = input("\nEnter command: ").strip()
        if not command:
            continue
        parts = shlex.split(command)
        if not parts:
            continue
        cmd = parts[0].lower()
        if cmd == "quit":
            print("Exiting the simulator. Goodbye!")
            break
        elif cmd == "help":
            print_help()
        elif cmd == "toggle":
            toggle_save_mode()
        elif cmd == "list":
            list_species()
        elif cmd == "breed":
            breed_species(parts[1:])
        elif cmd == "random":
            generate_random_species()
        elif cmd == "simulate":
            if len(parts) < 2:
                print("Usage: simulate [number of iterations]")
            else:
                try:
                    n = int(parts[1])
                    simulate_random(n)
                except ValueError:
                    print("Please enter a valid integer for number of iterations.")
        else:
            print("Unknown command. Type 'help' to see available commands.")

if __name__ == '__main__':
    main()
