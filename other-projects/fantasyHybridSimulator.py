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

######################################
# STAT UNITS DICTIONARY
######################################
STAT_UNITS = {
    "IQ": "",
    "EQ": "",
    "Dexterity": "",
    "Strength": "kg",
    "Land Speed": "km/h",
    "Swim Speed": "km/h",
    "Jump Height": "m",
    "Flight Speed": "km/h",
    "Climbing": "m/min",
    "Bite": "psi",
    "Size": "cm",
    "Venom": "",
    "Fire Breathing": "",
    "Gestation Period": "days",
    "Litter Size": "offspring",
    "Maturation Age": "years",
    "Lifespan": "years",
    "Growth Rate": "cm/year",
    "Lion Head IQ": "",
    "Goat Head IQ": "",
    "Snake Head IQ": "",
    "Lion Head EQ": "",
    "Goat Head EQ": "",
    "Snake Head EQ": "",
    "Lion Head Diet": "",
    "Goat Head Diet": "",
    "Snake Head Diet": "",
    "Visual Field": "degrees",
    "Visual Acuity": "cpd, 20/x",
    "Smell Strength": "ppb",
    "Smell Acuity": "ouE/m³",
    "Smell Distance": "m",
    "Hearing Range": "Hz",
    "Hearing Distance": "m",
    "Thaumagen Production Rate": "BCU/hour",
    "Thaumacyst Max Capacity": "BCU",
    "Thaucyst Current Capacity": "BCU"
}

######################################
# NEW: SPECIES-LEVEL STAT DICTIONARIES
######################################
# These base values are drawn from a consensus of fantasy role-playing sources.
MATURATION_AGE_SPECIES = {
    "human": 18,
    "centaur": 15,
    "mermaid": 20,
    "horse": 4,
    "hippocampus": 2,
    "fish": 1,
    "satyr/faun": 12,
    "naga": 20,
    "minotaur": 12,
    "harpy": 10,
    "griffin": 8,
    "chimera": 5,
    "cockatrice/basilisk": 4,
    "hippogriff": 6,
    "manticore": 8,
    "pegasus": 4,
    "goat": 2,
    "snake": 2,
    "bull": 3,
    "bird": 1,
    "lion": 3,
    "ipotane": 16,
    "dragon": 100,
    "tengu": 15
}

LIFESPAN_SPECIES = {
    "human": 80,
    "centaur": 100,
    "mermaid": 200,
    "horse": 25,
    "hippocampus": 30,
    "fish": 5,
    "satyr/faun": 100,
    "naga": 200,
    "minotaur": 50,
    "harpy": 40,
    "griffin": 80,
    "chimera": 20,
    "cockatrice/basilisk": 30,
    "hippogriff": 60,
    "manticore": 40,
    "pegasus": 30,
    "goat": 15,
    "snake": 20,
    "bull": 20,
    "bird": 5,
    "lion": 15,
    "ipotane": 80,
    "dragon": 1000,
    "tengu": 200
}
# Growth Rate will be computed as: Growth Rate = Size / Maturation Age

######################################
# SPECIES-SPECIFIC NAMING DICTIONARIES
######################################
SPECIES_NAME_DICT = {
    "human": {
        "adjectives": ["Noble", "Valiant", "Wise", "Just", "Stalwart", "Gallant", "Resolute", "Dignified", "Honorable"],
        "nouns": ["Sovereign", "Knight", "Baron", "Emperor", "Scholar", "Champion", "Guardian", "Regent", "Patriarch"]
    },
    "centaur": {
        "adjectives": ["Wild", "Gallant", "Mighty", "Fierce"],
        "nouns": ["Stallion", "Archer", "Warrior", "Hunter"]
    },
    "mermaid": {
        "adjectives": ["Mystic", "Siren", "Oceanic", "Luminous"],
        "nouns": ["Maiden", "Siren", "Daughter", "Enchantress"]
    },
    "horse": {
        "adjectives": ["Swift", "Stalwart", "Majestic", "Noble"],
        "nouns": ["Steed", "Charger", "Mustang", "Galloper"]
    },
    "hippocampus": {
        "adjectives": ["Deep", "Blue", "Mystic", "Tidal"],
        "nouns": ["Seahorse", "Triton", "Neptune", "Mariner"]
    },
    "fish": {
        "adjectives": ["Glimmering", "Silver", "Abyssal", "Sleek"],
        "nouns": ["Mariner", "Fin", "Scale", "Swimmer"]
    },
    "satyr/faun": {
        "adjectives": ["Wild", "Revelrous", "Mischievous", "Impish"],
        "nouns": ["Satyr", "Faun", "Pan", "Bacchus"]
    },
    "naga": {
        "adjectives": ["Serpentine", "Venomous", "Sly", "Coiled"],
        "nouns": ["Cobra", "Viper", "Asp", "Python"]
    },
    "minotaur": {
        "adjectives": ["Fierce", "Rampaging", "Mighty", "Colossal"],
        "nouns": ["Bull", "Behemoth", "Taurus", "Goliath"]
    },
    "harpy": {
        "adjectives": ["Screeching", "Winged", "Wild", "Tempestuous"],
        "nouns": ["Harpy", "Raptor", "Screamer", "Stormcaller"]
    },
    "griffin": {
        "adjectives": ["Majestic", "Golden", "Regal", "Imperial"],
        "nouns": ["Griffin", "Sky King", "Lion-Eagle", "Celestial"]
    },
    "chimera": {
        "adjectives": ["Hybrid", "Fused", "Nightmare", "Mutant"],
        "nouns": ["Abomination", "Mutant", "Beast", "Chimera"]
    },
    "cockatrice/basilisk": {
        "adjectives": ["Petrifying", "Cursed", "Venomous", "Sinister"],
        "nouns": ["Cockatrice", "Basilisk", "Gorgon", "Medusa"]
    },
    "hippogriff": {
        "adjectives": ["Noble", "Skyborne", "Valiant", "Aerial"],
        "nouns": ["Hippogriff", "Windrider", "Sky Knight", "Cloudstrider"]
    },
    "manticore": {
        "adjectives": ["Savage", "Dread", "Nightstalker", "Terrifying"],
        "nouns": ["Manticore", "Scourge", "Beast", "Fury"]
    },
    "pegasus": {
        "adjectives": ["Celestial", "Winged", "Ethereal", "Radiant"],
        "nouns": ["Pegasus", "Cloudrider", "Skyborne", "Zephyr"]
    },
    "goat": {
        "adjectives": ["Stubborn", "Wild", "Rocky", "Spirited"],
        "nouns": ["Billy", "Capricorn", "Horned", "Mountain Goat"]
    },
    "snake": {
        "adjectives": ["Sinuous", "Venomous", "Slithering", "Creeping"],
        "nouns": ["Adder", "Viper", "Serpent", "Cobra"]
    },
    "bull": {
        "adjectives": ["Massive", "Raging", "Sturdy", "Titanic"],
        "nouns": ["Taurus", "Rampager", "Bovidae", "Goliath"]
    },
    "bird": {
        "adjectives": ["Feathered", "Swift", "Soaring", "Glorious"],
        "nouns": ["Avian", "Winged", "Skycaller", "Celestial"]
    },
    "lion": {
        "adjectives": ["Regal", "Mighty", "Savage", "Imperial"],
        "nouns": ["King", "Pride", "Roarer", "Majesty"]
    },
    "ipotane": {
        "adjectives": ["Hybrid", "Mystic", "Noble", "Enigmatic"],
        "nouns": ["Centaur", "Maned Steed", "Chimera", "Unity"]
    },
    "dragon": {
        "adjectives": ["Fiery", "Ancient", "Mighty", "Infernal", "Scaly", "Blazing"],
        "nouns": ["Wyrm", "Drake", "Serpent", "Flame", "Sovereign", "Ember", "Scourge"]
    },
    "tengu": {
        "adjectives": ["Mischievous", "Cunning", "Aerial", "Sleek", "Mystic", "Ethereal"],
        "nouns": ["Tengu", "Crow", "Harbinger", "Trickster", "Raven", "Shade"]
    }
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
    "Dr": {"IQ": 90,  "EQ": 80, "Dexterity": 60, "Strength": 300}
}

BOTTOM_STATS = {
    "Hu": {"Land Speed": 8.0,  "Swim Speed": 3.0, "Jump Height": 0.6},
    "Ho": {"Land Speed": 45.0, "Swim Speed": 8.0, "Jump Height": 1.2},
    "Fi": {"Land Speed": 0.5,  "Swim Speed": 40.0, "Jump Height": 0.3},
    "Go": {"Land Speed": 20.0, "Swim Speed": 3.0, "Jump Height": 1.0},
    "Sn": {"Land Speed": 1.0,  "Swim Speed": 2.0, "Jump Height": 0.1},
    "Bu": {"Land Speed": 25.0, "Swim Speed": 4.0, "Jump Height": 0.8},
    "Bi": {"Land Speed": 10.0, "Swim Speed": 8.0, "Jump Height": 0.5},
    "Li": {"Land Speed": 60.0, "Swim Speed": 12.0, "Jump Height": 2.0},
    "Dr": {"Land Speed": 80.0, "Swim Speed": 6.0, "Jump Height": 3.0}
}

FLIGHT_STATS = {
    "Bi": 80.0,
    "Dr": 120.0
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

# New SIZE_STATS dictionary (in centimeters) – base expected sizes.
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

######################################
# NEW: GESTATION, LITTER, MATURATION, LIFESPAN, AND GROWTH RATE STATS
######################################
GESTATION_STATS = {
    "Hu": 280,
    "Ho": 340,
    "Fi": 1,
    "Go": 150,
    "Sn": 60,
    "Bu": 300,
    "Bi": 30,
    "Li": 110,
    "Dr": 400
}

LITTER_STATS = {
    "Hu": 1,
    "Ho": 1,
    "Fi": 1000,
    "Go": 2,
    "Sn": 20,
    "Bu": 1,
    "Bi": 3,
    "Li": 3,
    "Dr": 5
}

# NEW: Per-allele Senses Stats
# Units: Vision in cycles/degree (e.g. human ~30 cpd); Smell in parts-per-billion (ppb) detection threshold (lower values are more sensitive, so here higher numbers indicate better sensitivity);
# Hearing in Hz (upper limit of audible range).
SENSE_DETAIL_STATS_PER_ALLELE = {
    "Hu": {
        "Visual Field": 180, 
        "Visual Acuity": {"cpd": 30, "Snellen": 20},  # 30 cpd; 20/20 vision
        "Smell Strength": 10, 
        "Smell Acuity": 100,         # in OUₑ/m³
        "Smell Distance": 5,
        "Hearing Lower": 20, 
        "Hearing Upper": 20000, 
        "Hearing Distance": 100
    },
    "Ho": {
        "Visual Field": 200, 
        "Visual Acuity": {"cpd": 20, "Snellen": 25},
        "Smell Strength": 8,  
        "Smell Acuity": 120,        
        "Smell Distance": 10,
        "Hearing Lower": 14, 
        "Hearing Upper": 25000, 
        "Hearing Distance": 150
    },
    "Fi": {
        "Visual Field": 90,  
        "Visual Acuity": {"cpd": 10, "Snellen": 40},
        "Smell Strength": 5,  
        "Smell Acuity": 50,  
        "Smell Distance": 2,
        "Hearing Lower": 50, 
        "Hearing Upper": 5000,  
        "Hearing Distance": 30
    },
    "Go": {
        "Visual Field": 160, 
        "Visual Acuity": {"cpd": 25, "Snellen": 22},
        "Smell Strength": 5,  
        "Smell Acuity": 150, 
        "Smell Distance": 15,
        "Hearing Lower": 20, 
        "Hearing Upper": 20000, 
        "Hearing Distance": 80
    },
    "Sn": {
        "Visual Field": 120, 
        "Visual Acuity": {"cpd": 8, "Snellen": 50},
        "Smell Strength": 3,  
        "Smell Acuity": 200, 
        "Smell Distance": 20,
        "Hearing Lower": 10, 
        "Hearing Upper": 10000, 
        "Hearing Distance": 50
    },
    "Bu": {
        "Visual Field": 140, 
        "Visual Acuity": {"cpd": 12, "Snellen": 45},
        "Smell Strength": 7,  
        "Smell Acuity": 110, 
        "Smell Distance": 8,
        "Hearing Lower": 25, 
        "Hearing Upper": 18000, 
        "Hearing Distance": 70
    },
    "Bi": {
        "Visual Field": 320, 
        "Visual Acuity": {"cpd": 40, "Snellen": 15},
        "Smell Strength": 2,  
        "Smell Acuity": 180, 
        "Smell Distance": 30,
        "Hearing Lower": 30, 
        "Hearing Upper": 22000, 
        "Hearing Distance": 250
    },
    "Li": {
        "Visual Field": 180, 
        "Visual Acuity": {"cpd": 28, "Snellen": 20},
        "Smell Strength": 6,  
        "Smell Acuity": 140, 
        "Smell Distance": 10,
        "Hearing Lower": 20, 
        "Hearing Upper": 20000, 
        "Hearing Distance": 100
    },
    "Dr": {
        "Visual Field": 240, 
        "Visual Acuity": {"cpd": 35, "Snellen": 18},
        "Smell Strength": 3,  
        "Smell Acuity": 200, 
        "Smell Distance": 50,
        "Hearing Lower": 15, 
        "Hearing Upper": 30000, 
        "Hearing Distance": 300
    }
}

# NEW: Detailed Per-allele Magic Stats for Beam Energy.
# Units:
# • Thaumagen Production Rate: Joules/hour;
# • Thaumacyst Capacity: Joules.
MAGIC_STATS_PER_ALLELE = {
    "Hu": {"Thaumagen": 10, "Thaumacyst": 100},
    "Ho": {"Thaumagen": 12, "Thaumacyst": 110},
    "Fi": {"Thaumagen": 2,  "Thaumacyst": 20},
    "Go": {"Thaumagen": 8,  "Thaumacyst": 90},
    "Sn": {"Thaumagen": 5,  "Thaumacyst": 60},
    "Bu": {"Thaumagen": 9,  "Thaumacyst": 105},
    "Bi": {"Thaumagen": 15, "Thaumacyst": 140},
    "Li": {"Thaumagen": 12, "Thaumacyst": 130},
    "Dr": {"Thaumagen": 25, "Thaumacyst": 300}
}

MATURATION_AGE_SPECIES = {
    "human": 18,
    "centaur": 15,
    "mermaid": 20,
    "horse": 4,
    "hippocampus": 2,
    "fish": 1,
    "satyr/faun": 12,
    "naga": 20,
    "minotaur": 12,
    "harpy": 10,
    "griffin": 8,
    "chimera": 5,
    "cockatrice/basilisk": 4,
    "hippogriff": 6,
    "manticore": 8,
    "pegasus": 4,
    "goat": 2,
    "snake": 2,
    "bull": 3,
    "bird": 1,
    "lion": 3,
    "ipotane": 16,
    "dragon": 100,
    "tengu": 15
}

LIFESPAN_SPECIES = {
    "human": 80,
    "centaur": 100,
    "mermaid": 200,
    "horse": 25,
    "hippocampus": 30,
    "fish": 5,
    "satyr/faun": 100,
    "naga": 200,
    "minotaur": 50,
    "harpy": 40,
    "griffin": 80,
    "chimera": 20,
    "cockatrice/basilisk": 30,
    "hippogriff": 60,
    "manticore": 40,
    "pegasus": 30,
    "goat": 15,
    "snake": 20,
    "bull": 20,
    "bird": 5,
    "lion": 15,
    "ipotane": 80,
    "dragon": 1000,
    "tengu": 200
}
# Growth Rate will be computed as: Growth Rate = Size / Maturation Age

######################################
# ADD DIET MAPPING FOR EACH ALLELE
######################################
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
    "Fire Breathing": ["top"],
    "Gestation Period": ["bottom"],
    "Litter Size": ["bottom"],
    "Maturation Age": ["bottom"],
    "Lifespan": ["bottom"],
    "Growth Rate": ["bottom"]
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
        "Fire Breathing": ["top"],
        "Gestation Period": ["bottom"],
        "Litter Size": ["bottom"],
        "Maturation Age": ["bottom"],
        "Lifespan": ["bottom"],
        "Growth Rate": ["bottom"]
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
        "Fire Breathing": ["top"],
        "Gestation Period": ["bottom"],
        "Litter Size": ["bottom"],
        "Maturation Age": ["bottom"],
        "Lifespan": ["bottom"],
        "Growth Rate": ["bottom"]
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
        "Fire Breathing": ["top"],
        "Gestation Period": ["bottom"],
        "Litter Size": ["bottom"],
        "Maturation Age": ["bottom"],
        "Lifespan": ["bottom"],
        "Growth Rate": ["bottom"]
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
        "Fire Breathing": ["top"],
        "Gestation Period": ["bottom"],
        "Litter Size": ["bottom"],
        "Maturation Age": ["bottom"],
        "Lifespan": ["bottom"],
        "Growth Rate": ["bottom"]
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
        "Fire Breathing": ["top"],
        "Gestation Period": ["bottom"],
        "Litter Size": ["bottom"],
        "Maturation Age": ["bottom"],
        "Lifespan": ["bottom"],
        "Growth Rate": ["bottom"]
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
        "Fire Breathing": ["top"],
        "Gestation Period": ["bottom"],
        "Litter Size": ["bottom"],
        "Maturation Age": ["bottom"],
        "Lifespan": ["bottom"],
        "Growth Rate": ["bottom"]
    },
    "manticore": {
        "IQ": ["top"],
        "EQ": ["top"],
        "Dexterity": ["mid"],
        "Strength": ["mid"],
        "Land Speed": ["mid"],
        "Swim Speed": ["mid"],
        "Jump Height": ["mid"],
        "Flight Speed": ["bottom"],
        "Climbing": ["bottom"],
        "Bite": ["top"],
        "Venom": ["bottom"],
        "Fire Breathing": ["top"],
        "Gestation Period": ["bottom"],
        "Litter Size": ["bottom"],
        "Maturation Age": ["bottom"],
        "Lifespan": ["bottom"],
        "Growth Rate": ["bottom"]
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
        "Fire Breathing": ["top"],
        "Gestation Period": ["bottom"],
        "Litter Size": ["bottom"],
        "Maturation Age": ["bottom"],
        "Lifespan": ["bottom"],
        "Growth Rate": ["bottom"]
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
        "Fire Breathing": ["top"],
        "Gestation Period": ["bottom"],
        "Litter Size": ["bottom"],
        "Maturation Age": ["bottom"],
        "Lifespan": ["bottom"],
        "Growth Rate": ["bottom"]
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
        "Fire Breathing": ["top"],
        "Gestation Period": ["bottom"],
        "Litter Size": ["bottom"],
        "Maturation Age": ["bottom"],
        "Lifespan": ["bottom"],
        "Growth Rate": ["bottom"]
    },
    "dragon": {
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
        "Fire Breathing": ["top"],
        "Gestation Period": ["bottom"],
        "Litter Size": ["bottom"],
        "Maturation Age": ["bottom"],
        "Lifespan": ["bottom"],
        "Growth Rate": ["bottom"]
    },
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
        "Fire Breathing": ["top"],
        "Gestation Period": ["bottom"],
        "Litter Size": ["bottom"],
        "Maturation Age": ["bottom"],
        "Lifespan": ["bottom"],
        "Growth Rate": ["bottom"]
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
        # Existing chimera-specific calculations for IQ and EQ
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
        # Calculate detailed sense stats for each head separately.
        for head, allele in zip(["Lion Head", "Goat Head", "Snake Head"], [top_expr, mid_expr, bottom_expr]):
            # Visual Field (in degrees)
            vf = apply_random_variation(SENSE_DETAIL_STATS_PER_ALLELE[allele]["Visual Field"])
            vf, vf_mut = maybe_mutate_stat(vf, "Visual Field")
            stats[f"{head} Visual Field"] = vf
            if vf_mut:
                mutations[f"{head} Visual Field"] = vf_mut

            # Visual Acuity: compute separately from 'cpd' and 'Snellen', then format as "X cpd, 20/Y"
            va = SENSE_DETAIL_STATS_PER_ALLELE[allele]["Visual Acuity"]
            cpd_val = apply_random_variation(va["cpd"])
            cpd_val, cpd_mut = maybe_mutate_stat(cpd_val, "Visual Acuity")
            snellen_val = va["Snellen"]  # assumed relatively fixed per allele
            stats[f"{head} Visual Acuity"] = f"{round(cpd_val,1)} cpd, 20/{round(snellen_val)}"
            if cpd_mut:
                mutations[f"{head} Visual Acuity"] = cpd_mut

            # Smell Strength
            ss = apply_random_variation(SENSE_DETAIL_STATS_PER_ALLELE[allele]["Smell Strength"])
            ss, ss_mut = maybe_mutate_stat(ss, "Smell Strength")
            stats[f"{head} Smell Strength"] = ss
            if ss_mut:
                mutations[f"{head} Smell Strength"] = ss_mut

            # Smell Acuity (in OUₑ/m³)
            sa = apply_random_variation(SENSE_DETAIL_STATS_PER_ALLELE[allele]["Smell Acuity"])
            sa, sa_mut = maybe_mutate_stat(sa, "Smell Acuity")
            stats[f"{head} Smell Acuity"] = sa
            if sa_mut:
                mutations[f"{head} Smell Acuity"] = sa_mut

            # Smell Distance (in meters)
            sd = apply_random_variation(SENSE_DETAIL_STATS_PER_ALLELE[allele]["Smell Distance"])
            sd, sd_mut = maybe_mutate_stat(sd, "Smell Distance")
            stats[f"{head} Smell Distance"] = sd
            if sd_mut:
                mutations[f"{head} Smell Distance"] = sd_mut

            # Hearing: Calculate lower and upper limits, then combine into a Hearing Range.
            hl = apply_random_variation(SENSE_DETAIL_STATS_PER_ALLELE[allele]["Hearing Lower"])
            hl, hl_mut = maybe_mutate_stat(hl, "Hearing Lower")
            hu = apply_random_variation(SENSE_DETAIL_STATS_PER_ALLELE[allele]["Hearing Upper"])
            hu, hu_mut = maybe_mutate_stat(hu, "Hearing Upper")
            stats[f"{head} Hearing Range"] = f"{round(hl,1)}-{round(hu,1)} Hz"
            if hl_mut:
                mutations[f"{head} Hearing Lower"] = hl_mut
            if hu_mut:
                mutations[f"{head} Hearing Upper"] = hu_mut

            # Hearing Distance (in meters)
            hd = apply_random_variation(SENSE_DETAIL_STATS_PER_ALLELE[allele]["Hearing Distance"])
            hd, hd_mut = maybe_mutate_stat(hd, "Hearing Distance")
            stats[f"{head} Hearing Distance"] = f"{round(hd,1)} m"
            if hd_mut:
                mutations[f"{head} Hearing Distance"] = hd_mut

        for stat in ["Dexterity", "Strength", "Land Speed", "Swim Speed", "Jump Height",
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
        if mut_iq_top: mutations["Lion Head IQ"] = mut_iq_top
        if mut_iq_mid: mutations["Goat Head IQ"] = mut_iq_mid
        if mut_iq_bottom: mutations["Snake Head IQ"] = mut_iq_bottom
        if mut_eq_top: mutations["Lion Head EQ"] = mut_eq_top
        if mut_eq_mid: mutations["Goat Head EQ"] = mut_eq_mid
        if mut_eq_bottom: mutations["Snake Head EQ"] = mut_eq_bottom
    else:
        # For non-chimera species, average the detailed sense stats from the three alleles.
        # For hearing, compute average lower and upper then combine into a range.
        for sense in ["Visual Field", "Smell Strength", "Smell Acuity", "Smell Distance"]:
            alleles = [top_expr, mid_expr, bottom_expr]
            vals = [SENSE_DETAIL_STATS_PER_ALLELE[allele][sense] for allele in alleles]
            avg_val = sum(vals) / 3
            avg_val = apply_random_variation(avg_val)
            avg_val, msg = maybe_mutate_stat(avg_val, sense)
            stats[sense] = avg_val
            if msg:
                mutations[sense] = msg

        # For Visual Acuity, average the 'cpd' and 'Snellen' separately:
        va_vals = [SENSE_DETAIL_STATS_PER_ALLELE[allele]["Visual Acuity"] for allele in [top_expr, mid_expr, bottom_expr]]
        avg_cpd = sum([v["cpd"] for v in va_vals]) / 3
        avg_snellen = sum([v["Snellen"] for v in va_vals]) / 3
        avg_cpd = apply_random_variation(avg_cpd)
        avg_cpd, msg = maybe_mutate_stat(avg_cpd, "Visual Acuity")
        if msg:
            mutations["Visual Acuity"] = msg
        stats["Visual Acuity"] = f"{round(avg_cpd,1)} cpd, 20/{round(avg_snellen)}"

        # For Hearing Range, average the lower and upper limits, then display as a range.
        lower_vals = [SENSE_DETAIL_STATS_PER_ALLELE[allele]["Hearing Lower"] for allele in [top_expr, mid_expr, bottom_expr]]
        upper_vals = [SENSE_DETAIL_STATS_PER_ALLELE[allele]["Hearing Upper"] for allele in [top_expr, mid_expr, bottom_expr]]
        avg_lower = apply_random_variation(sum(lower_vals) / 3)
        avg_upper = apply_random_variation(sum(upper_vals) / 3)
        stats["Hearing Range"] = f"{round(avg_lower,1)}-{round(avg_upper,1)} Hz"

        # Also average Hearing Distance:
        hearing_distance_vals = [SENSE_DETAIL_STATS_PER_ALLELE[allele]["Hearing Distance"] for allele in [top_expr, mid_expr, bottom_expr]]
        avg_hearing_distance = apply_random_variation(sum(hearing_distance_vals) / 3)
        avg_hearing_distance, msg = maybe_mutate_stat(avg_hearing_distance, "Hearing Distance")
        stats["Hearing Distance"] = f"{round(avg_hearing_distance,1)} m"
        if msg:
            mutations["Hearing Distance"] = msg
        # Continue with other physical stats:
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
        stats["Visual Acuity"] = f"{round(avg_cpd,1)} cpd, 20/{round(avg_snellen)}"


    # Compute Size, Maturation Age, Lifespan, and Growth Rate (existing code)
    base_size = (SIZE_STATS.get(top_expr, 170) + SIZE_STATS.get(mid_expr, 170) + SIZE_STATS.get(bottom_expr, 170)) / 3.0
    size_val = apply_random_variation(base_size)
    size_val, size_mut = maybe_mutate_stat(size_val, "Size")
    stats["Size"] = size_val
    if size_mut:
        mutations["Size"] = size_mut

    if species in MATURATION_AGE_SPECIES:
        base_mat_age = MATURATION_AGE_SPECIES[species]
        mat_age_value = apply_random_variation(base_mat_age)
        mat_age_value, mat_mut = maybe_mutate_stat(mat_age_value, "Maturation Age")
        stats["Maturation Age"] = mat_age_value
        if mat_mut:
            mutations["Maturation Age"] = mat_mut
    if species in LIFESPAN_SPECIES:
        base_life = LIFESPAN_SPECIES[species]
        life_value = apply_random_variation(base_life)
        life_value, life_mut = maybe_mutate_stat(life_value, "Lifespan")
        stats["Lifespan"] = life_value
        if life_mut:
            mutations["Lifespan"] = life_mut

    if "Maturation Age" in stats and stats["Maturation Age"]:
        growth_rate = round(stats["Size"] / stats["Maturation Age"], 3)
        growth_rate, gr_mut = maybe_mutate_stat(growth_rate, "Growth Rate")
        stats["Growth Rate"] = growth_rate
        if gr_mut:
            mutations["Growth Rate"] = gr_mut

    for new_stat, stat_dict in [("Gestation Period", GESTATION_STATS), ("Litter Size", LITTER_STATS)]:
        base_val = 0.15 * stat_dict.get(top_expr, 0) + 0.15 * stat_dict.get(mid_expr, 0) + 0.7 * stat_dict.get(bottom_expr, 0)
        value = apply_random_variation(base_val)
        final_value, msg = maybe_mutate_stat(value, new_stat)
        stats[new_stat] = final_value
        if msg:
            mutations[new_stat] = msg

    # --- NEW: Calculate Magic Stats (Thaumagen and Thaumacyst displayed as a fraction) ---
    magic_vals = {"Thaumagen": [], "Thaumacyst": []}
    for allele in [top_expr, mid_expr, bottom_expr]:
        for key in magic_vals:
            magic_vals[key].append(MAGIC_STATS_PER_ALLELE[allele][key])
    avg_thaumagen = sum(magic_vals["Thaumagen"]) / 3
    avg_thaumacyst = sum(magic_vals["Thaumacyst"]) / 3
    production_rate = apply_random_variation(avg_thaumagen)
    production_rate, msg = maybe_mutate_stat(production_rate, "Thaumagen Production Rate")
    stats["Thaumagen Production Rate"] = production_rate
    if msg:
        mutations["Thaumagen Production Rate"] = msg

    scaled_thaumacyst = avg_thaumacyst * (stats["Size"] / 170)
    scaled_thaumacyst = apply_random_variation(scaled_thaumacyst)
    scaled_thaumacyst, msg = maybe_mutate_stat(scaled_thaumacyst, "Thaumacyst Max Capacity")
    # Display as a fraction "current/max"
    age_fraction = random.uniform(0, 1)
    current_capacity = age_fraction * scaled_thaumacyst
    current_capacity = apply_random_variation(current_capacity)
    current_capacity, msg2 = maybe_mutate_stat(current_capacity, "Thaumacyst Current Capacity")
    stats["Thaumacyst Capacity"] = f"{current_capacity:.1f}/{scaled_thaumacyst:.1f}"
    if msg:
        mutations["Thaumacyst Capacity"] = msg
    if msg2:
        mutations["Thaumacyst Capacity"] = msg2

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
    # Variant logic:
    #   - Any species can become Giant if its computed Size is at least 3.0× its base size.
    #     In that case, we prefix with "Giant " and multiply its Lifespan by 3.0.
    #   - Only species with a human allele (top allele "Hu") and not manticore can become Dwarven.
    #     If the computed Size is ≤0.8× base and Strength is ≥1.2× the base top strength, prefix with "Dwarven " and multiply Lifespan by 4.0.
    off_top = top_expression(offspring_geno["top"])
    off_mid = mid_expression(offspring_geno["mid"])
    off_bottom = bottom_expression(offspring_geno["bottom"])
    base_size = (SIZE_STATS.get(off_top, 170) + SIZE_STATS.get(off_mid, 170) + SIZE_STATS.get(off_bottom, 170)) / 3.0
    base_strength = TOP_STATS.get(off_top, {}).get("Strength", 60)
    variant_prefix = ""
    if sim_stats["Size"] >= 2.5 * base_size:
        variant_prefix = "Giant "
        sim_stats["Lifespan"] = round(sim_stats["Lifespan"] * 3.0, 3)
    elif off_top == "Hu" and species != "manticore" and sim_stats["Size"] <= 0.8 * base_size and sim_stats["Strength"] >= 1.2 * base_strength:
        variant_prefix = "Dwarven "
        sim_stats["Lifespan"] = round(sim_stats["Lifespan"] * 4.0, 3)
    species_variant = variant_prefix + species

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
        "name": generate_unique_name(species_variant),
        "genotype": offspring_geno,
        "species": species_variant,
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
    output = "\n--- RANDOM SIMULATION RESULTS ---\n"
    for sp, count in frequency.items():
        output += f"{sp}: {count} times\n"
    return output

######################################
# COMMAND-DRIVEN INTERFACE ADAPTATION
######################################
class HybridCLI:
    def __init__(self):
        self.SAVE_MODE = False
        self.SAVED_FILE = "hybrids.json"
        self.saved_hybrids = {}
        self.load_saved_hybrids()

    def load_saved_hybrids(self):
        if os.path.exists(self.SAVED_FILE):
            try:
                with open(self.SAVED_FILE, "r") as f:
                    loaded = json.load(f)
                    self.saved_hybrids = {k.lower(): v for k, v in loaded.items()}
            except Exception as e:
                self.saved_hybrids = {}
        else:
            self.saved_hybrids = {}

    def save_saved_hybrids(self):
        try:
            with open(self.SAVED_FILE, "w") as f:
                json.dump(self.saved_hybrids, f, indent=4)
        except Exception as e:
            pass

    def process_command(self, command_line: str) -> str:
        output = ""
        parts = shlex.split(command_line)
        if not parts:
            return ""
        cmd = parts[0].lower()

        if cmd == "help":
            output += (
                "Commands:\n"
                "  toggle                    - Toggle save mode ON/OFF\n"
                "  list                      - List available known species and saved hybrids\n"
                "  breed [arg1] [arg2]       - Breed two species or saved hybrids\n"
                "                             e.g., breed naga pegasus or breed \"Silver Griffin\" \"Mystic Stag\"\n"
                "  random                    - Generate a random species (with a unique name if save mode is ON)\n"
                "  simulate [n]              - Run random generation n times and list frequency of species produced\n"
                "  help                      - Show this help message\n"
                "  quit                      - Exit the simulator\n"
            )
        elif cmd == "toggle":
            self.SAVE_MODE = not self.SAVE_MODE
            mode_status = "ON" if self.SAVE_MODE else "OFF"
            output += f"Save mode toggled {mode_status}.\n"
        elif cmd == "list":
            output += "Available species (from known definitions):\n"
            for sp in sorted(phenotype_genotypes.keys()):
                output += f"  {sp}\n"
            if self.SAVE_MODE:
                output += "\nSaved hybrids:\n"
                for name in sorted(self.saved_hybrids.keys()):
                    record = self.saved_hybrids[name]
                    output += f"  {record['name']} (Species: {record['species']}, Genotype: {record.get('genotype','N/A')})\n"
        elif cmd == "breed":
            if len(parts) != 3:
                output += "Usage: breed [species_or_saved_name1] [species_or_saved_name2]\n"
            else:
                arg1, arg2 = parts[1].lower(), parts[2].lower()
                if self.SAVE_MODE and (arg1 in self.saved_hybrids and arg2 in self.saved_hybrids):
                    offspring_data = breed_from_saved(arg1, arg2)
                    if offspring_data is None:
                        return output
                    offspring, mutations = offspring_data
                    output += "\n--- BREEDING RESULT (from saved hybrids) ---\n"
                    output += f"Parent 1: {self.saved_hybrids[arg1]['name']} (Species: {self.saved_hybrids[arg1]['species']}, Genotype: {self.saved_hybrids[arg1].get('genotype','N/A')})\n"
                    output += f"Parent 2: {self.saved_hybrids[arg2]['name']} (Species: {self.saved_hybrids[arg2]['species']}, Genotype: {self.saved_hybrids[arg2].get('genotype','N/A')})\n"
                    output += f"Offspring name: {offspring['name']}\n"
                    output += f"Inherited species: {offspring['species']}\n"
                    output += "Offspring genotype:\n"
                    output += f"  Top   : {offspring['genotype']['top']}\n"
                    output += f"  Mid   : {offspring['genotype']['mid']}\n"
                    output += f"  Bottom: {offspring['genotype']['bottom']}\n"
                    output += "Inherited stats:\n"
                    for stat, value in offspring["stats"].items():
                        unit = STAT_UNITS.get(stat, "")
                        output += f"  {stat:15s}: {value} {unit}".rstrip() + "\n"
                        if stat in mutations:
                            output += f"                <-- {mutations[stat]}\n"
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
                            output += "Miscarriage: Offspring species could not be determined after several attempts.\n"
                            return output
                    except ValueError as e:
                        output += f"Error: {e}\n"
                        return output
                    off_top = top_expression(result["offspring_top"])
                    off_mid = mid_expression(result["offspring_mid"])
                    off_bottom = bottom_expression(result["offspring_bottom"])
                    stats, mutations = generate_individual_stats(result["phenotype"], off_top, off_mid, off_bottom)
                    base_size = (SIZE_STATS.get(off_top, 170) + SIZE_STATS.get(off_mid, 170) + SIZE_STATS.get(off_bottom, 170)) / 3.0
                    base_strength = TOP_STATS.get(off_top, {}).get("Strength", 60)
                    variant_prefix = ""
                    if stats["Size"] >= 3.0 * base_size:
                        variant_prefix = "Giant "
                        stats["Lifespan"] = round(stats["Lifespan"] * 3.0, 3)
                    elif off_top == "Hu" and result["phenotype"] != "manticore" and stats["Size"] <= 0.8 * base_size and stats["Strength"] >= 1.2 * base_strength:
                        variant_prefix = "Dwarven "
                        stats["Lifespan"] = round(stats["Lifespan"] * 4.0, 3)
                    result["phenotype"] = variant_prefix + result["phenotype"]
                    output += "\n--- BREEDING RESULT (from known species simulation) ---\n"
                    output += f"Parent 1 ({arg1}) - Genotype: {result['parent1_genotype']}\n"
                    output += f"Parent 2 ({arg2}) - Genotype: {result['parent2_genotype']}\n"
                    output += "\nOffspring genotype:\n"
                    output += f"  Top   : {result['offspring_top']}\n"
                    output += f"  Mid   : {result['offspring_mid']}\n"
                    output += f"  Bottom: {result['offspring_bottom']}\n"
                    output += f"Offspring species: {result['phenotype']}\n"
                    output += "\nOffspring stats (sources per stat are defined by species):\n"
                    for stat, value in stats.items():
                        unit = STAT_UNITS.get(stat, "")
                        output += f"  {stat:15s}: {value} {unit}".rstrip() + "\n"
                        if stat in mutations:
                            output += f"                <-- {mutations[stat]}\n"
        elif cmd == "random":
            genotype, sp = random.choice(all_full_genotypes)
            output += "--- RANDOM SPECIES GENERATED ---\n"
            output += "Genotype:\n"
            output += f"  Top   : {genotype['top']}\n"
            output += f"  Mid   : {genotype['mid']}\n"
            output += f"  Bottom: {genotype['bottom']}\n"
            output += f"Species: {sp}\n"
            expr_top = top_expression(genotype["top"])
            expr_mid = mid_expression(genotype["mid"])
            expr_bottom = bottom_expression(genotype["bottom"])
            stats, mutations = generate_individual_stats(sp, expr_top, expr_mid, expr_bottom)
            base_size = (SIZE_STATS.get(expr_top, 170) + SIZE_STATS.get(expr_mid, 170) + SIZE_STATS.get(expr_bottom, 170)) / 3.0
            base_strength = TOP_STATS.get(expr_top, {}).get("Strength", 60)
            variant_prefix = ""
            if stats["Size"] >= 3.0 * base_size:
                variant_prefix = "Giant "
                stats["Lifespan"] = round(stats["Lifespan"] * 3.0, 3)
            elif expr_top == "Hu" and sp != "manticore" and stats["Size"] <= 0.8 * base_size and stats["Strength"] >= 1.2 * base_strength:
                variant_prefix = "Dwarven "
                stats["Lifespan"] = round(stats["Lifespan"] * 4.0, 3)
            sp = variant_prefix + sp
            output += f"Species (with variant): {sp}\n"
            if self.SAVE_MODE:
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
                self.saved_hybrids[new_name.lower()] = record
                self.save_saved_hybrids()
                output += f"Assigned unique name: {new_name}\n"
            output += "\nStats:\n"
            for stat, value in stats.items():
                unit = STAT_UNITS.get(stat, "")
                output += f"  {stat:15s}: {value} {unit}".rstrip() + "\n"
                if stat in mutations:
                    output += f"                <-- {mutations[stat]}\n"
        elif cmd == "simulate":
            if len(parts) < 2:
                output += "Usage: simulate [number of iterations]\n"
            else:
                try:
                    n = int(parts[1])
                    output += simulate_random(n)
                except ValueError:
                    output += "Please enter a valid integer for number of iterations.\n"
        elif cmd == "quit":
            output += "Exit command received. (Please close the browser tab.)\n"
        else:
            output += f"Unknown command: {cmd}\n"
        return output

# Create a global CLI instance
cli = HybridCLI()

def run_command(command_line: str) -> str:
    return cli.process_command(command_line)

######################################
# MAIN LOOP (for local testing)
######################################
if __name__ == '__main__':
    load_saved_hybrids()
    print("Welcome to the Expanded Hybrid Breeding Simulator!")
    print(
        "Commands:\n"
        "  toggle                    - Toggle save mode ON/OFF\n"
        "  list                      - List available known species and saved hybrids\n"
        "  breed [arg1] [arg2]       - Breed two species or saved hybrids (enclose names with spaces in quotes)\n"
        "  random                    - Generate a random species (with a unique name if save mode is ON)\n"
        "  simulate [n]              - Run random generation n times and list frequency of species produced\n"
        "  help                      - Show this help message\n"
        "  quit                      - Exit the simulator\n"
    )
    while True:
        command = input("\nEnter command: ").strip()
        if not command:
            continue
        output = run_command(command)
        print(output)
        if command.lower().startswith("quit"):
            break
