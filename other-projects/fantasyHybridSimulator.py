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
    "Petrification": "",
    "Charm": "",
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
    "Visual Acuity": "",
    "Smell Strength": "ppb",
    "Smell Acuity": "ouE/m³",
    "Smell Distance": "m",
    "Hearing Range": "",
    "Hearing Distance": "",
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
    "lamia": 20,
    "gorgon": 20,
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
    "tengu": 15,
    "unicorn": 3,
    "sphinx": 10
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
    "lamia": 200,
    "gorgon": 200,
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
    "tengu": 200,
    "unicorn": 1000,
    "sphinx": 200
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
    "lamia": {
        "adjectives": ["Enchanting", "Sinuous", "Velvet", "Moonlit"],
        "nouns": ["Lamia", "Enchantress", "Temptress", "Sable"]
    },
    "gorgon": {
        "adjectives": ["Stonegaze", "Cursed", "Serpentine", "Dire"],
        "nouns": ["Gorgon", "Medusa", "Petrifier", "Stare"]
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
    },
    "sphinx": {
        "adjectives": ["Riddling", "Enigmatic", "Majestic", "Oracle", "Solemn", "Ancient"],
        "nouns": ["Sphinx", "Riddler", "Keeper", "Oracle", "Sentinel", "Seer"]
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
    ("Hu", "Sn", "Sn"): "lamia",
    ("Hu", "Bi", "Sn"): "gorgon",
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
    ("Bi", "Bi", "Hu"): "tengu",
    ("Go", "Ho", "Li"): "unicorn",
    ("Hu", "Bi", "Li"): "sphinx"
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

# NEW: Toggle for showing detailed elemental magic affinities in stat blocks
MAGIC_AFFINITY_MODE = False

# NEW: Base elemental affinity weights per allele (0.0–1.0)
# These represent natural inclination toward each element. Final values
# are blended across alleles, influenced by Beam (raw power), and then
# normalized to 0–100 with competitive dampening across elements.
AFFINITY_BASE_PER_ALLELE = {
    # Human: broadly capable generalists
    "Hu": {"Fire": 0.50, "Water": 0.50, "Earth": 0.50, "Air": 0.50, "Beam": 0.50},
    # Horse: grounded, earthy
    "Ho": {"Fire": 0.30, "Water": 0.30, "Earth": 0.80, "Air": 0.20, "Beam": 0.40},
    # Fish: water-aligned
    "Fi": {"Fire": 0.20, "Water": 0.90, "Earth": 0.30, "Air": 0.40, "Beam": 0.45},
    # Goat: sure-footed, earth-heavy
    "Go": {"Fire": 0.30, "Water": 0.30, "Earth": 0.80, "Air": 0.30, "Beam": 0.45},
    # Snake: earthy and a touch aquatic
    "Sn": {"Fire": 0.20, "Water": 0.50, "Earth": 0.60, "Air": 0.10, "Beam": 0.40},
    # Bull: very earthy
    "Bu": {"Fire": 0.30, "Water": 0.30, "Earth": 0.80, "Air": 0.20, "Beam": 0.45},
    # Bird: strongly air-aligned
    "Bi": {"Fire": 0.30, "Water": 0.30, "Earth": 0.30, "Air": 0.90, "Beam": 0.55},
    # Lion: fiery and a bit earthy
    "Li": {"Fire": 0.80, "Water": 0.20, "Earth": 0.50, "Air": 0.20, "Beam": 0.60},
    # Dragon: very strong fire and solid air/earth; beam power boosted separately
    "Dr": {"Fire": 0.90, "Water": 0.40, "Earth": 0.60, "Air": 0.60, "Beam": 0.90}
}

def compute_magic_affinities(top_expr: str, mid_expr: str, bottom_expr: str, stats: dict) -> dict:
    """
    Compute elemental magic affinities with two constraints:
    1) Reciprocal sparsity: probability of gaining additional active affinities
       decreases as 1/(1+n) with each already-accepted affinity (ordered by value).
    2) Hyperbolic competition: higher values in some elements dampen others via
       a factor 1/(1 + K * sum(other_values)).

    Returns numeric affinity values (0–100) for Fire/Water/Earth/Air/Beam and an
    "Active Affinities" summary string listing elements that were accepted by the
    reciprocal process. Beam is derived from raw magical power (Thaumagen/Thaumacyst)
    and slightly biased by the presence of Dragon alleles.
    """
    elements = ["Fire", "Water", "Earth", "Air", "Beam"]

    def _avg_base(element: str) -> float:
        vals = [
            AFFINITY_BASE_PER_ALLELE.get(allele, {}).get(element, 0.5)
            for allele in (top_expr, mid_expr, bottom_expr)
        ]
        return sum(vals) / len(vals)

    # Base potentials in 0..100, blended from alleles
    base = {e: _avg_base(e) for e in elements}
    # Mana (thaumagen/thaumacyst) is not Beam, but it should increase chances/values
    max_thaumagen = max(v["Thaumagen"] for v in MAGIC_STATS_PER_ALLELE.values()) or 1.0
    max_thaumacyst = max(v["Thaumacyst"] for v in MAGIC_STATS_PER_ALLELE.values()) or 1.0
    prod = float(stats.get("Thaumagen Production Rate", 0.0))
    cap_max = 0.0
    cap_field = stats.get("Thaumacyst Capacity")
    if isinstance(cap_field, str) and "/" in cap_field:
        try:
            cap_max = float(cap_field.split("/")[1])
        except Exception:
            cap_max = 0.0
    elif isinstance(cap_field, (int, float)):
        cap_max = float(cap_field)
    mana_score = 0.6 * min(prod / max_thaumagen, 1.0) + 0.4 * min(cap_max / max_thaumacyst, 1.0)

    # Initial potentials: allele-driven plus small noise (no direct mana or beam coupling here)
    potentials = {}
    for e in elements:
        allele_base = base[e] * 100.0
        raw = allele_base + random.uniform(-5.0, 5.0)
        # Slight extra for Beam if Dragon allele(s) present
        if e == "Beam":
            dragon_bias = sum(1 for a in (top_expr, mid_expr, bottom_expr) if a == "Dr") / 3.0
            raw *= (1.0 + 0.2 * dragon_bias)
        potentials[e] = max(0.0, min(100.0, raw))

    # Hyperbolic competition should reduce the probability of high values, not deterministically shrink them.
    # We sample final values using a Beta(a,b) on [0,1], scaled by each element's potential.
    # High competition -> larger b (skews toward lower samples); high mana -> larger a (skews higher) and reduces effective competition.
    K = 0.8  # base competition strength; higher -> stronger trade-offs
    # Very high mana reduces competition, allowing rare "all-high" outcomes
    K_eff = K * (1.0 - 0.9 * (mana_score ** 2))
    values = {}
    for e in elements:
        total_comp = sum(v for k, v in potentials.items() if k != e) / 100.0
        # Shape parameters: a grows with mana and the element's own potential; b grows with competition
        a = 1.0 + 2.0 * mana_score * (potentials[e] / 100.0)
        b = 1.0 + max(0.0, K_eff) * total_comp * 5.0
        # Sample final fraction in [0,1]
        frac = random.betavariate(max(a, 1e-3), max(b, 1e-3))
        val = potentials[e] * frac
        values[e] = max(0.0, min(100.0, val))

    # Reciprocal acceptance for "active" affinities; sort by adjusted strength
    order = sorted(elements, key=lambda x: values[x], reverse=True)
    accepted = []
    count = 0
    for e in order:
        p_accept = 1.0 / (1.0 + count)
        # favor acceptance for strong values; very low values less likely
        p_accept *= min(1.0, values[e] / 50.0)
        # mana increases chance to add more affinities
        p_accept *= (1.0 + 0.75 * mana_score)
        if random.random() < min(1.0, p_accept):
            accepted.append(e)
            count += 1

    result = {}
    for e in elements:
        result[f"Affinity {e}"] = round(values[e], 2)
    result["Active Affinities"] = ", ".join(accepted) if accepted else "None"
    return result

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
    "Litter Size": ["bottom"]
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
        "Litter Size": ["bottom"]
    },
    "lamia": {
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
        "Litter Size": ["bottom"]
    },
    "gorgon": {
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
        "Litter Size": ["bottom"]
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
        "Litter Size": ["bottom"]
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
        "Litter Size": ["bottom"]
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
        "Litter Size": ["bottom"]
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
        "Litter Size": ["bottom"]
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
        "Litter Size": ["bottom"]
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
        "Litter Size": ["bottom"]
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
        "Litter Size": ["bottom"]
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
        "Litter Size": ["bottom"]
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
        "Litter Size": ["bottom"]
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
        "Litter Size": ["bottom"]
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
        "Litter Size": ["bottom"]
    },
    "unicorn": {
        "IQ": ["top"],
        "EQ": ["top"],
        "Dexterity": ["mid"],
        "Strength": ["mid"],
        "Land Speed": ["mid"],
        "Swim Speed": ["mid"],
        "Jump Height": ["mid"],
        "Flight Speed": [],
        "Climbing": ["mid"],
        "Bite": ["top"],
        "Venom": ["top"],
        "Fire Breathing": ["top"],
        "Gestation Period": ["mid"],
        "Litter Size": ["mid"]
    },
    "sphinx": {
        "IQ": ["top"],
        "EQ": ["top"],
        "Dexterity": ["top"],
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
        "Litter Size": ["bottom"]
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
        if stat in ["Venom", "Fire Breathing", "Petrification", "Charm"]:
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
        # Species-specific tweaks:
        # Naga: minor dexterity bonus to reflect four arms; Lamia and Gorgon do not receive this.
        if species == "naga" and "Dexterity" in stats:
            boosted = round(stats["Dexterity"] * 1.5, 3)
            stats["Dexterity"] = boosted
        # Gorgon: Petrification ability
        petr_val = (species == "gorgon")
        petr_val, msg = maybe_mutate_stat(petr_val, "Petrification")
        stats["Petrification"] = petr_val
        if msg:
            mutations["Petrification"] = msg
        # Charm: present for lamia and sphinx, otherwise false (still subject to mutation)
        charm_val = (species in ["lamia"])
        charm_val, msg = maybe_mutate_stat(charm_val, "Charm")
        stats["Charm"] = charm_val
        if msg:
            mutations["Charm"] = msg
        stats["diet"] = DIET.get(top_expr, "omnivore")

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

    # Optionally add detailed elemental magic affinities
    if MAGIC_AFFINITY_MODE:
        try:
            affinities = compute_magic_affinities(top_expr, mid_expr, bottom_expr, stats)
            stats.update(affinities)
        except Exception:
            # Fail-closed: do not break simulation if affinity calc misfires
            pass

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

def breed_from_saved(parent1_name, parent2_name, silent: bool = False):
    if parent1_name not in saved_hybrids or parent2_name not in saved_hybrids:
        if not silent:
            print("One or both parent names not found in saved hybrids.")
        return None
    parent1 = saved_hybrids[parent1_name]
    parent2 = saved_hybrids[parent2_name]
    geno1 = parent1.get("genotype")
    geno2 = parent2.get("genotype")
    if geno1 is None or geno2 is None:
        print("Saved parents do not have genotype info. Cannot breed using genotype simulation.")
        return None

    # 1. Generate offspring genotype + species
    MAX_ATTEMPTS = 10
    attempt = 0
    offspring_geno, species = None, None
    while attempt < MAX_ATTEMPTS:
        offspring_geno, species = cross_breed_from_genotype(geno1, geno2)
        if species is not None:
            break
        attempt += 1
    if species is None:
        if not silent:
            print("Miscarriage: Offspring species could not be determined after several attempts.")
        return None

    # 2. Simulate full stats for that species (includes senses, diet, magic, size, etc.)
    top_expr    = top_expression(offspring_geno["top"])
    mid_expr    = mid_expression(offspring_geno["mid"])
    bottom_expr = bottom_expression(offspring_geno["bottom"])
    sim_stats, sim_mutations = generate_individual_stats(species, top_expr, mid_expr, bottom_expr)

    # 3. Compute base size/strength for variant thresholds
    base_size = (
        SIZE_STATS.get(top_expr, 170) +
        SIZE_STATS.get(mid_expr, 170) +
        SIZE_STATS.get(bottom_expr, 170)
    ) / 3.0
    base_strength = TOP_STATS.get(top_expr, {}).get("Strength", 60)

    # 4. Compute average raw magic across the three alleles
    avg_thaumagen = (
        MAGIC_STATS_PER_ALLELE[top_expr]["Thaumagen"] +
        MAGIC_STATS_PER_ALLELE[mid_expr]["Thaumagen"] +
        MAGIC_STATS_PER_ALLELE[bottom_expr]["Thaumagen"]
    ) / 3
    avg_thaumacyst = (
        MAGIC_STATS_PER_ALLELE[top_expr]["Thaumacyst"] +
        MAGIC_STATS_PER_ALLELE[mid_expr]["Thaumacyst"] +
        MAGIC_STATS_PER_ALLELE[bottom_expr]["Thaumacyst"]
    ) / 3

    # 5. Determine if this sim_stats are "high magic"
    #    sim_stats["Thaumagen Production Rate"] is numeric,
    #    sim_stats["Thaumacyst Capacity"] is "current/max"
    cur_max = sim_stats["Thaumacyst Capacity"].split("/")
    current, maximum = float(cur_max[0]), float(cur_max[1])

    # require at least 20% above the “pure average” baseline
    MAGIC_THRESHOLD_MULTIPLIER = 1.2

    has_high_magic = (
        sim_stats["Thaumagen Production Rate"] > avg_thaumagen * MAGIC_THRESHOLD_MULTIPLIER
        or
        maximum > avg_thaumacyst * MAGIC_THRESHOLD_MULTIPLIER
    )

    # 6. Helpers for variant checks
    is_human_allele = (top_expr == "Hu")
    is_horse_head = (top_expr == "Ho")
    is_unicorn = (species == "unicorn")
    is_not_unicorn = (species != "unicorn")
    is_not_manticore = (species != "manticore")
    is_not_sphinx = (species != "sphinx")
    is_giant = (sim_stats["Size"] >= 2.5 * base_size)
    is_small = (sim_stats["Size"] <= 0.5 * base_size)

    # 7. Apply variants in priority order
    variant_prefix = ""

    if is_giant:
        variant_prefix = "Giant "
        sim_stats["Lifespan"] = round(sim_stats["Lifespan"] * 3.0, 3)

    elif is_giant and has_high_magic:
        variant_prefix = "Cyclopse "
        sim_stats["Lifespan"] = round(sim_stats["Lifespan"] * 3.0, 3)

    elif is_human_allele and is_not_manticore and is_not_sphinx and is_small and has_high_magic:
        variant_prefix = "Fairy "
        sim_stats["Lifespan"] = round(sim_stats["Lifespan"] * 4.5, 3)

    elif is_human_allele and is_not_manticore and is_not_sphinx and has_high_magic \
         and sim_stats["Size"] >= 1.2 * base_size:
        variant_prefix = "Elven "
        sim_stats["Lifespan"] = round(sim_stats["Lifespan"] * 7.5, 3)

    elif is_human_allele and is_not_manticore and is_not_sphinx\
         and sim_stats["Size"] <= 0.8 * base_size \
         and sim_stats["Strength"] >= 1.2 * base_strength:
        variant_prefix = "Dwarven "
        sim_stats["Lifespan"] = round(sim_stats["Lifespan"] * 4.0, 3)

    elif is_unicorn:
        sim_stats["Thaumagen Production Rate"] = round(
            sim_stats["Thaumagen Production Rate"] * 3, 3
        )
        # Scale both current and max in capacity string if present
        cap = sim_stats.get("Thaumacyst Capacity")
        if isinstance(cap, str) and "/" in cap:
            try:
                cur_s, max_s = cap.split("/")
                cur_v = float(cur_s.strip()) * 2
                max_v = float(max_s.strip()) * 2
                sim_stats["Thaumacyst Capacity"] = f"{cur_v:.1f}/{max_v:.1f}"
            except Exception:
                pass
        elif isinstance(cap, (int, float)):
            sim_stats["Thaumacyst Capacity"] = round(cap * 2, 3)

    elif is_horse_head and has_high_magic and is_not_unicorn:
        variant_prefix = "Unicorn "
        sim_stats["Lifespan"] = round(sim_stats["Lifespan"] * 40.0, 3)

    species_variant = variant_prefix + species

    # 8. Blend with parents’ stats as before
    def _get_core_stat(sdict: dict, sname: str):
        if sname in sdict:
            return sdict[sname]
        if sname == "IQ":
            vals = [sdict.get(k) for k in ["Lion Head IQ", "Goat Head IQ", "Snake Head IQ"] if k in sdict]
            if vals:
                return round(sum(vals)/len(vals), 3)
        if sname == "EQ":
            vals = [sdict.get(k) for k in ["Lion Head EQ", "Goat Head EQ", "Snake Head EQ"] if k in sdict]
            if vals:
                return round(sum(vals)/len(vals), 3)
        return None
    parents_avg = {}
    for stat in ["IQ","EQ","Dexterity","Strength",
                 "Land Speed","Swim Speed","Jump Height",
                 "Flight Speed","Climbing","Bite"]:
        v1 = _get_core_stat(parent1["stats"], stat)
        v2 = _get_core_stat(parent2["stats"], stat)
        if v1 is None:
            v1 = 0
        if v2 is None:
            v2 = 0
        parents_avg[stat] = round((v1 + v2) / 2, 3)
    venom_avg = ((1 if parent1["stats"].get("Venom", False) else 0) +
                 (1 if parent2["stats"].get("Venom", False) else 0)) / 2
    weight_geno, weight_par = 0.7, 0.3

    final_stats = {}
    combined_mutations = {}
    for stat in parents_avg:
        sim_val = _get_core_stat(sim_stats, stat)
        if sim_val is None:
            sim_val = 0
        val = round(weight_geno * sim_val + weight_par * parents_avg[stat], 3)
        final_stats[stat] = val
        if stat in sim_mutations:
            combined_mutations[stat] = sim_mutations[stat]
    sim_ven = 1 if sim_stats["Venom"] else 0
    final_stats["Venom"] = (
        True if (weight_geno * sim_ven + weight_par * venom_avg) >= 0.5 else False
    )
    if "Venom" in sim_mutations:
        combined_mutations["Venom"] = sim_mutations["Venom"]

    for key, value in sim_stats.items():
        if key not in final_stats:
            final_stats[key] = value
            # carry over any mutation note
            if key in sim_mutations:
                combined_mutations[key] = sim_mutations[key]

    # If magic affinities mode is active, blend elemental affinities from parents
    if MAGIC_AFFINITY_MODE:
        def ensure_affinities(record):
            # If record has Affinity stats, keep; otherwise compute from genotype
            have = any(k.startswith("Affinity ") for k in record.get("stats", {}))
            if not have and "genotype" in record:
                geno = record["genotype"]
                t = top_expression(geno["top"])
                m = mid_expression(geno["mid"])
                b = bottom_expression(geno["bottom"])
                aff = compute_magic_affinities(t, m, b, record.get("stats", {}))
                record.setdefault("stats", {}).update(aff)

        # Make sure parents have affinities computed (for older saves)
        try:
            p1 = saved_hybrids.get(parent1_name, parent1)
            p2 = saved_hybrids.get(parent2_name, parent2)
        except Exception:
            p1, p2 = parent1, parent2
        ensure_affinities(p1)
        ensure_affinities(p2)

        # Ensure offspring sim has affinities (in case global mode was OFF earlier)
        if not any(k.startswith("Affinity ") for k in sim_stats.keys()):
            aff = compute_magic_affinities(top_expr, mid_expr, bottom_expr, sim_stats)
            sim_stats.update(aff)
            for k, v in aff.items():
                if k not in final_stats:
                    final_stats[k] = v

        # Blend numeric affinity values; skip the Active Affinities label for blending
        for elem in ("Fire", "Water", "Earth", "Air", "Beam"):
            key = f"Affinity {elem}"
            sim_val = float(sim_stats.get(key, 0.0))
            p1_val = float(p1.get("stats", {}).get(key, 0.0))
            p2_val = float(p2.get("stats", {}).get(key, 0.0))
            parents_avg_val = (p1_val + p2_val) / 2.0
            final_stats[key] = round(weight_geno * sim_val + weight_par * parents_avg_val, 2)
        # Recompute Active Affinities from the blended values via simple ordering + reciprocal
        # Reuse the acceptance rule on the blended numbers for display only
        ordered = sorted([("Fire", final_stats.get("Affinity Fire", 0.0)),
                          ("Water", final_stats.get("Affinity Water", 0.0)),
                          ("Earth", final_stats.get("Affinity Earth", 0.0)),
                          ("Air", final_stats.get("Affinity Air", 0.0)),
                          ("Beam", final_stats.get("Affinity Beam", 0.0))], key=lambda x: x[1], reverse=True)
        accepted = []
        count = 0
        for name, val in ordered:
            p_acc = (1.0 / (1.0 + count)) * min(1.0, val / 50.0)
            if random.random() < min(1.0, p_acc):
                accepted.append(name)
                count += 1
        final_stats["Active Affinities"] = ", ".join(accepted) if accepted else "None"

    # 9. Build & save the offspring record with the truly complete statblock
    offspring = {
        "name": generate_unique_name(species_variant),
        "genotype": offspring_geno,
        "species": species_variant,
        "stats": final_stats,     # now contains both core and detailed stats
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
        self.saved_hybrids = {}
        # Session state for chunked optimize to avoid UI freezes
        self._opt_session = None  # dict or None
        # Litter mode controls
        self.LITTER_MODE = False
        self.LITTER_CAP = 10

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
        global saved_hybrids
        global MAGIC_AFFINITY_MODE
        output = ""
        parts = shlex.split(command_line)
        if not parts:
            return ""
        cmd = parts[0].lower()

        if cmd == "help":
            output += (
                "Commands:\n"
                "  toggle                    - Toggle save mode ON/OFF\n"
                "  magic [on|off|status]     - Toggle or set elemental magic affinity display\n"
                "  litter [on|off|status|cap=N] - Toggle litter reproduction and/or set a safety cap per pairing\n"
                "  optimize start <gens> <stats> [species ...] [chunk=N] - Start a chunked evolution session (non-blocking)\n"
                "  optimize step|continue [chunk=N|auto] - Run N generations or 'auto' (all remaining) in the active session\n"
                "  optimize run <gens> <stats> [species ...] [chunk=N] - Start, then auto-continue until completion\n"
                "  optimize until <condition> [<gens>] <stats> [species ...] [chunk=N] - Run until goal or until gens done\n"
                "     Conditions: variant=<Name> | species=<name> | stat:Size>=340 (use STAT names; case-insensitive)\n"
                "     Notes: species can be positional (no 'species=' needed); last bare integer sets chunk size.\n"
                "  optimize check <condition> - Return whether the goal condition is currently satisfied (true/false)\n"
                "  optimize finalize         - Print result summary and end the active session (if any)\n"
                "  optimize status            - Show current optimize session progress and best candidate\n"
                "  optimize stop              - Stop the active session\n"
                "    Tips: stats can include Affinity Fire/Water/Earth/Air/Beam (or just fire, water, etc.)\n"
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
            if self.SAVE_MODE:
                self.saved_hybrids.clear()
            mode_status = "ON" if self.SAVE_MODE else "OFF"
            output += f"Save mode is now {mode_status}.\n"
        elif cmd == "list":
            output += "Available species (from known definitions):\n"
            for sp in sorted(phenotype_genotypes.keys()):
                output += f"  {sp}\n"
            if self.SAVE_MODE and self.saved_hybrids:
                output += "\nSaved hybrids:\n"
                for name in sorted(self.saved_hybrids.keys()):
                    record = self.saved_hybrids[name]
                    output += f"  {record['name']} (Species: {record['species']}, Genotype: {record.get('genotype','N/A')})\n"
        elif cmd == "litter":
            # Usage: litter -> toggle; litter on/off; litter status; litter cap=N
            if len(parts) == 1:
                self.LITTER_MODE = not self.LITTER_MODE
                state = "ON" if self.LITTER_MODE else "OFF"
                output += f"Litter mode toggled {state}. (Cap={self.LITTER_CAP})\n"
            else:
                sub = parts[1].lower()
                if sub in ("on", "enable", "enabled"):
                    self.LITTER_MODE = True
                    output += f"Litter mode: ON (Cap={self.LITTER_CAP})\n"
                elif sub in ("off", "disable", "disabled"):
                    self.LITTER_MODE = False
                    output += "Litter mode: OFF\n"
                elif sub.startswith("cap="):
                    try:
                        cap = int(sub.split("=", 1)[1])
                        self.LITTER_CAP = max(1, cap)
                        output += f"Litter cap set to {self.LITTER_CAP}.\n"
                    except Exception:
                        output += "Invalid cap value. Use litter cap=N\n"
                elif sub in ("status", "state"):
                    state = "ON" if self.LITTER_MODE else "OFF"
                    output += f"Litter mode is {state}. Cap={self.LITTER_CAP}.\n"
                else:
                    output += "Usage: litter [on|off|status|cap=N]\n"
        elif cmd == "breed":
            if len(parts) != 3:
                output += "Usage: breed [species_or_saved_name1] [species_or_saved_name2]\n"
            else:
                arg1, arg2 = parts[1].lower(), parts[2].lower()

                # — Saved-hybrid branch —
                if self.SAVE_MODE and arg1 in self.saved_hybrids and arg2 in self.saved_hybrids:
                    # Make breed_from_saved use our in-memory store
                    saved_hybrids = self.saved_hybrids

                    def _num(v):
                        try:
                            return float(v)
                        except Exception:
                            try:
                                # Extract number from string
                                s = str(v)
                                if '/' in s:
                                    return float(s.split('/')[1])
                                return float(''.join(ch for ch in s if (ch.isdigit() or ch in '.-')))
                            except Exception:
                                return 0.0
                    # Estimate litter count from parents' stats
                    lit1 = _num(self.saved_hybrids[arg1]["stats"].get("Litter Size", 1))
                    lit2 = _num(self.saved_hybrids[arg2]["stats"].get("Litter Size", 1))
                    litter_count = 1
                    if self.LITTER_MODE:
                        avg = (lit1 + lit2) / 2.0 if (lit1 and lit2) else max(lit1, lit2, 1)
                        litter_count = max(1, min(self.LITTER_CAP, int(round(avg))))

                    output += "\n--- BREEDING RESULT (from saved hybrids) ---\n"
                    output += f"Parent 1: {self.saved_hybrids[arg1]['name']} (Species: {self.saved_hybrids[arg1]['species']})\n"
                    output += f"Parent 2: {self.saved_hybrids[arg2]['name']} (Species: {self.saved_hybrids[arg2]['species']})\n"
                    for i in range(litter_count):
                        result = breed_from_saved(arg1, arg2)
                        if result is None:
                            output += "Miscarriage: could not determine offspring species after 10 attempts.\n"
                            continue
                        offspring, mutations = result
                        # Store back into session memory
                        self.saved_hybrids[offspring["name"].lower()] = offspring
                        prefix = f"Offspring {i+1}/{litter_count}: " if litter_count > 1 else "Offspring: "
                        output += prefix + f"{offspring['name']}\n"
                        output += f"Species: {offspring['species']}\n"
                        output += "(Saved into session memory)\n"
                        output += "Genotype:\n"
                        output += f"  Top   : {offspring['genotype']['top']}\n"
                        output += f"  Mid   : {offspring['genotype']['mid']}\n"
                        output += f"  Bottom: {offspring['genotype']['bottom']}\n"
                        output += "Stats:\n"
                        for stat, val in offspring["stats"].items():
                            unit = STAT_UNITS.get(stat, "")
                            output += f"  {stat:15s}: {val} {unit}".rstrip() + "\n"
                            if stat in mutations:
                                output += f"                <-- {mutations[stat]}\n"

                # — Known-species branch remains unchanged —
                else:
                    # … your existing cross_breed_random + stats + variant logic …
                    try:
                        MAX_ATTEMPTS = 10
                        for _ in range(MAX_ATTEMPTS):
                            result = cross_breed_random(arg1, arg2)
                            if result["phenotype"] is not None:
                                break
                        else:
                            output += "Miscarriage: Offspring species could not be determined after several attempts.\n"
                            return output
                    except ValueError as e:
                        output += f"Error: {e}\n"
                        return output

                    # Estimate litter count for species parents by sampling their genotypes' statblocks
                    def _num(v):
                        try:
                            return float(v)
                        except Exception:
                            try:
                                s = str(v)
                                if '/' in s:
                                    return float(s.split('/')[1])
                                return float(''.join(ch for ch in s if (ch.isdigit() or ch in '.-')))
                            except Exception:
                                return 0.0
                    litter_count = 1
                    if self.LITTER_MODE:
                        p1_t = top_expression(result["parent1_genotype"]["top"])
                        p1_m = mid_expression(result["parent1_genotype"]["mid"])
                        p1_b = bottom_expression(result["parent1_genotype"]["bottom"])
                        p1_stats, _ = generate_individual_stats(arg1, p1_t, p1_m, p1_b)
                        p2_t = top_expression(result["parent2_genotype"]["top"])
                        p2_m = mid_expression(result["parent2_genotype"]["mid"])
                        p2_b = bottom_expression(result["parent2_genotype"]["bottom"])
                        p2_stats, _ = generate_individual_stats(arg2, p2_t, p2_m, p2_b)
                        avg = (_num(p1_stats.get("Litter Size", 1)) + _num(p2_stats.get("Litter Size", 1))) / 2.0
                        litter_count = max(1, min(self.LITTER_CAP, int(round(avg))))

                    output += "\n--- BREEDING RESULT (from species simulation) ---\n"
                    output += f"Parent 1 ({arg1})  Genotype: {result['parent1_genotype']}\n"
                    output += f"Parent 2 ({arg2})  Genotype: {result['parent2_genotype']}\n"
                    for i in range(litter_count):
                        # compute stats & variant prefix (same as before)…
                        off_top = top_expression(result["offspring_top"])
                        off_mid = mid_expression(result["offspring_mid"])
                        off_bot = bottom_expression(result["offspring_bottom"])
                        stats, mutations = generate_individual_stats(
                            result["phenotype"], off_top, off_mid, off_bot
                        )
                        species_name = generate_unique_name(result["phenotype"])
                        offspring = {
                            "name": species_name,
                            "genotype": {
                                "top": result["offspring_top"],
                                "mid": result["offspring_mid"],
                                "bottom": result["offspring_bottom"]
                            },
                            "species": result["phenotype"],
                            "stats": stats
                        }
                        if self.SAVE_MODE:
                            self.saved_hybrids[offspring["name"].lower()] = offspring
                            output += f"(Saved in session as “{offspring['name']}”)\n"
                        output += "\nGenotype:\n"
                        output += f"  Top   : {result['offspring_top']}\n"
                        output += f"  Mid   : {result['offspring_mid']}\n"
                        output += f"  Bottom: {result['offspring_bottom']}\n"
                        output += f"Species: {offspring['species']}\n"
                        output += "\nStats:\n"
                        for stat, val in stats.items():
                            unit = STAT_UNITS.get(stat, "")
                            output += f"  {stat:15s}: {val} {unit}".rstrip() + "\n"
                            if stat in mutations:
                                output += f"                <-- {mutations[stat]}\n"
        elif cmd == "magic":
            # Toggle or set the elemental magic affinity display mode
            # Usage: magic            -> toggle
            #        magic on|off     -> set explicitly
            #        magic status     -> report current state
            if len(parts) == 1:
                MAGIC_AFFINITY_MODE = not MAGIC_AFFINITY_MODE
                state = "ON" if MAGIC_AFFINITY_MODE else "OFF"
                output += f"Magic affinities display toggled {state}.\n"
            else:
                sub = parts[1].lower()
                if sub in ("on", "enable", "enabled"):
                    MAGIC_AFFINITY_MODE = True
                    output += "Magic affinities display: ON\n"
                elif sub in ("off", "disable", "disabled"):
                    MAGIC_AFFINITY_MODE = False
                    output += "Magic affinities display: OFF\n"
                elif sub in ("status", "state"):
                    state = "ON" if MAGIC_AFFINITY_MODE else "OFF"
                    output += f"Magic affinities display is {state}.\n"
                else:
                    output += "Usage: magic [on|off|status]\n"
        elif cmd == "optimize":
            # Chunked session controls to avoid long blocking runs in UI contexts
            if len(parts) > 1 and parts[1].lower() in ("start", "step", "continue", "status", "stop", "run", "until", "check", "finalize"):
                sub = parts[1].lower()
                # Helper reused by 'until' and 'check'
                def _check_condition(cond: str) -> bool:
                    cl = cond.lower()
                    if cl.startswith("variant="):
                        want = cl.split("=", 1)[1].strip()
                        for rec in self.saved_hybrids.values():
                            sp = rec.get("species", "").lower()
                            if sp.startswith(want + " "):
                                return True
                        return False
                    if cl.startswith("species="):
                        want = cl.split("=", 1)[1].strip()
                        for rec in self.saved_hybrids.values():
                            if rec.get("species", "").lower() == want:
                                return True
                        return False
                    if cl.startswith("stat:"):
                        # Format: stat:Name>=value | <= | == | > | <
                        expr = cl[5:]
                        op = None
                        for candidate in (">=","<=","==",">","<"):
                            if candidate in expr:
                                op = candidate
                                break
                        if not op:
                            return False
                        left, right = expr.split(op, 1)
                        stat_name = left.strip()
                        try:
                            threshold = float(right.strip())
                        except Exception:
                            return False
                        # Canonicalize stat name to exact key
                        canon = None
                        for k in STAT_UNITS.keys():
                            if k.lower() == stat_name:
                                canon = k
                                break
                        if canon is None:
                            canon = stat_name
                        def _num(v):
                            if isinstance(v, (int, float)):
                                return float(v)
                            if isinstance(v, bool):
                                return 1.0 if v else 0.0
                            if isinstance(v, str):
                                if '/' in v:
                                    try:
                                        return float(v.split('/')[-1])
                                    except Exception:
                                        pass
                                buf = ''.join(ch for ch in v if (ch.isdigit() or ch in '.-'))
                                try:
                                    return float(buf) if buf else 0.0
                                except Exception:
                                    return 0.0
                            return 0.0
                        for rec in self.saved_hybrids.values():
                            val = _num(rec.get("stats", {}).get(canon, 0))
                            if ((op == ">=" and val >= threshold) or
                                (op == ">"  and val >  threshold) or
                                (op == "<=" and val <= threshold) or
                                (op == "<"  and val <  threshold) or
                                (op == "==" and abs(val-threshold) < 1e-9)):
                                return True
                        return False
                    return False

                if sub == "check":
                    if len(parts) < 3:
                        return "Usage: optimize check <condition>\n"
                    cond = parts[2]
                    ok = _check_condition(cond)
                    return ("GOAL: true\n" if ok else "GOAL: false\n")

                if sub == "finalize":
                    if not self._opt_session:
                        return "No active optimize session to finalize.\n"
                    parsed_stats = self._opt_session["parsed_stats"]
                    target_species = self._opt_session.get("target_species")
                    baseline_stats = self._opt_session.get("baseline_stats", {})
                    baseline_N = self._opt_session.get("baseline_N", 100)
                    all_final = list(self.saved_hybrids.values())
                    def _score_of_local(record):
                        return _score_of(parsed_stats, record)
                    all_final.sort(key=_score_of_local, reverse=True)
                    best_overall = all_final[0] if all_final else None
                    best_species = None
                    if target_species:
                        species_final = [rec for rec in all_final if rec["species"].lower() == target_species]
                        if species_final:
                            best_species = species_final[0]
                    else:
                        best_species = best_overall
                    out = "\n--- OPTIMIZATION RESULT ---\n"
                    if target_species and baseline_stats:
                        out += f"Random {target_species} baseline (N={baseline_N}):\n"
                        for stat_name, _ in parsed_stats:
                            if stat_name in baseline_stats:
                                b = baseline_stats[stat_name]
                                unit = STAT_UNITS.get(stat_name, "")
                                out += f"  {stat_name}: min={b['min']:.3f}, avg={b['avg']:.3f}, max={b['max']:.3f} {unit}\n"
                    if best_overall and (not best_species or best_overall["name"] == best_species["name"]):
                        out += f"Best: {best_overall['name']} (Species: {best_overall['species']})\n"
                        out += "Stats (selected):\n"
                        for stat_name, direction in parsed_stats:
                            val = best_overall["stats"].get(stat_name, 0)
                            unit = STAT_UNITS.get(stat_name, "")
                            dir_str = "+" if direction == 1 else "-"
                            out += f"  {dir_str}{stat_name}: {val} {unit}".rstrip() + "\n"
                    else:
                        if best_overall:
                            out += f"Best Overall: {best_overall['name']} (Species: {best_overall['species']})\n"
                            out += "Stats (selected):\n"
                            for stat_name, direction in parsed_stats:
                                val = best_overall["stats"].get(stat_name, 0)
                                unit = STAT_UNITS.get(stat_name, "")
                                dir_str = "+" if direction == 1 else "-"
                                out += f"  {dir_str}{stat_name}: {val} {unit}".rstrip() + "\n"
                        if best_species:
                            out += f"Best in Species: {best_species['name']} (Species: {best_species['species']})\n"
                            out += "Stats (selected):\n"
                            for stat_name, direction in parsed_stats:
                                val = best_species["stats"].get(stat_name, 0)
                                unit = STAT_UNITS.get(stat_name, "")
                                dir_str = "+" if direction == 1 else "-"
                                out += f"  {dir_str}{stat_name}: {val} {unit}".rstrip() + "\n"
                    prev_magic = self._opt_session.get("prev_magic", MAGIC_AFFINITY_MODE)
                    MAGIC_AFFINITY_MODE = prev_magic
                    self._opt_session = None
                    return out

                def _canon_stat(name: str) -> str:
                    lower = name.lower().strip()
                    # Accept plain element names or prefixed variants
                    elem_map = {
                        "fire": "Affinity Fire",
                        "water": "Affinity Water",
                        "earth": "Affinity Earth",
                        "air": "Affinity Air",
                        "beam": "Affinity Beam",
                        "affinity fire": "Affinity Fire",
                        "affinity water": "Affinity Water",
                        "affinity earth": "Affinity Earth",
                        "affinity air": "Affinity Air",
                        "affinity beam": "Affinity Beam",
                    }
                    if lower in elem_map:
                        return elem_map[lower]
                    for k in STAT_UNITS.keys():
                        if k.lower() == lower:
                            return k
                    return name

                def _parse_stats_spec(spec: str):
                    result = []
                    for raw in spec.split(','):
                        token = raw.strip()
                        if not token:
                            continue
                        if token[0] in ['+','-']:
                            direction = 1 if token[0] == '+' else -1
                            name = _canon_stat(token[1:].strip())
                        else:
                            direction = 1
                            name = _canon_stat(token)
                        result.append((name, direction))
                    return result

                def _numeric_value(v):
                    if isinstance(v, bool):
                        return 1.0 if v else 0.0
                    if isinstance(v, (int, float)):
                        return float(v)
                    if isinstance(v, str):
                        if '/' in v:
                            try:
                                pp = v.split('/')
                                return float(pp[1].strip())
                            except Exception:
                                pass
                        buf = []
                        out = []
                        for ch in v:
                            if ch.isdigit() or ch in '.-':
                                buf.append(ch)
                            else:
                                if buf:
                                    out.append(''.join(buf))
                                    buf = []
                        if buf:
                            out.append(''.join(buf))
                        for tok in out:
                            try:
                                return float(tok)
                            except Exception:
                                continue
                    return 0.0

                def _score_of(parsed_stats, record):
                    # Normalized scoring: per-stat value divided by species baseline average (percent-over-base)
                    # This makes cross-species comparisons fairer.
                    tup = []
                    sess = self._opt_session if self._opt_session else {}
                    baseline_by_species = sess.get("baseline_by_species", {})
                    baseline_N = sess.get("baseline_N", 100)

                    def _get_baseline_avg(species: str, stat_name: str) -> float:
                        sp = species.lower()
                        if sp not in baseline_by_species:
                            baseline_by_species[sp] = {}
                        if stat_name in baseline_by_species[sp]:
                            return baseline_by_species[sp][stat_name]
                        # Compute and cache average baseline for this species/stat
                        if sp in phenotype_genotypes:
                            vals = []
                            for _ in range(baseline_N):
                                geno = random.choice(phenotype_genotypes[sp])
                                t = top_expression(geno["top"])
                                m = mid_expression(geno["mid"])
                                b = bottom_expression(geno["bottom"])
                                stats, _ = generate_individual_stats(species, t, m, b)
                                vals.append(_numeric_value(stats.get(stat_name, 0)))
                            avg = (sum(vals) / len(vals)) if vals else 0.0
                        else:
                            avg = 0.0
                        # guard against zero/near-zero baselines
                        if avg <= 1e-9:
                            avg = 1.0
                        baseline_by_species[sp][stat_name] = avg
                        sess["baseline_by_species"] = baseline_by_species
                        return avg

                    species = record.get("species", "").lower()
                    for stat_name, direction in parsed_stats:
                        raw_val = _numeric_value(record["stats"].get(stat_name, 0))
                        base_avg = _get_baseline_avg(species, stat_name)
                        norm = raw_val / base_avg if base_avg != 0 else raw_val
                        tup.append(direction * norm)
                    return tuple(tup)

                if sub == "start":
                    if len(parts) < 4:
                        output += (
                            "Usage: optimize start <generations> <stats_spec> [species=sp1,sp2,...] [chunk=N]\n"
                            "Examples:\n"
                            "  optimize start 50 +Strength,IQ species=griffin chunk=5\n"
                            "  optimize start 1000 size centaur 50   (positional: gens stats species chunk)\n"
                        )
                        return output
                    try:
                        generations = int(parts[2])
                    except ValueError:
                        output += "Second argument must be an integer number of generations.\n"
                        return output
                    stats_spec = parts[3]
                    species_filter = None
                    chunk = 5
                    # Accept both prefixed and positional tokens after stats_spec
                    pos_species: list[str] = []
                    last_numeric: int | None = None
                    for token in parts[4:]:
                        tl = token.lower()
                        if tl.startswith("species="):
                            raw = token.split("=", 1)[1].replace(";", ",")
                            pos_species.extend([s.strip().lower() for s in raw.split(",") if s.strip()])
                        elif tl.startswith("chunk="):
                            try:
                                chunk = max(1, int(token.split("=", 1)[1]))
                            except Exception:
                                pass
                        else:
                            # positional: collect non-numeric as species tokens, numeric as chunk override
                            try:
                                val = int(token)
                                last_numeric = val
                            except Exception:
                                if token:
                                    pos_species.append(token.lower())
                    if last_numeric is not None:
                        chunk = max(1, last_numeric)
                    if pos_species:
                        species_filter = pos_species
                    parsed_stats = _parse_stats_spec(stats_spec)
                    if not parsed_stats:
                        output += "No valid stats specified.\n"
                        return output

                    # Affinity optimization: auto-enable magic mode when targeting any affinity
                    prev_magic = MAGIC_AFFINITY_MODE
                    if any(name.lower().startswith("affinity ") for name, _ in parsed_stats):
                        MAGIC_AFFINITY_MODE = True

                    # Start fresh population
                    self.SAVE_MODE = True
                    self.saved_hybrids.clear()
                    saved_hybrids = self.saved_hybrids

                    # Build phenotype helpers
                    def species_matches(species_str: str) -> bool:
                        if species_filter is None:
                            return True
                        s = species_str.lower()
                        for want in species_filter:
                            if s == want:
                                return True
                            if ' ' not in want and (s == want or s.endswith(' ' + want)):
                                return True
                        return False

                    def create_random_individual(sp: str):
                        geno = random.choice(phenotype_genotypes[sp])
                        t = top_expression(geno["top"])
                        m = mid_expression(geno["mid"])
                        b = bottom_expression(geno["bottom"])
                        stats, _ = generate_individual_stats(sp, t, m, b)
                        name = generate_unique_name(sp)
                        record = {
                            "name": name,
                            "genotype": geno,
                            "species": sp,
                            "stats": stats
                        }
                        self.saved_hybrids[name.lower()] = record
                        return name, geno

                    POP_SIZE = 20
                    # Seed POP_SIZE randoms unrestricted (keeps code simpler for session mode)
                    while len(self.saved_hybrids) < POP_SIZE:
                        sp = random.choice(list(phenotype_genotypes.keys()))
                        create_random_individual(sp)

                    # Baseline for target species (if a single filter provided)
                    target_species = None
                    if species_filter and len(species_filter) == 1:
                        target_species = species_filter[0]
                    baseline_stats = {}
                    baseline_N = 100
                    if target_species and target_species in phenotype_genotypes:
                        for stat_name, _ in parsed_stats:
                            vals = []
                            for _ in range(baseline_N):
                                geno = random.choice(phenotype_genotypes[target_species])
                                t = top_expression(geno["top"])
                                m = mid_expression(geno["mid"])
                                b = bottom_expression(geno["bottom"])
                                stats, _ = generate_individual_stats(target_species, t, m, b)
                                val = _numeric_value(stats.get(stat_name, 0))
                                vals.append(val)
                            if vals:
                                baseline_stats[stat_name] = {
                                    "min": min(vals),
                                    "max": max(vals),
                                    "avg": sum(vals)/len(vals)
                                }

                    # Save session
                    self._opt_session = {
                        "generations": generations,
                        "done": 0,
                        "stats_spec": stats_spec,
                        "parsed_stats": parsed_stats,
                        "species_filter": species_filter,
                        "target_species": target_species,
                        "baseline_stats": baseline_stats,
                        "baseline_N": baseline_N,
                        "baseline_by_species": {},
                        "POP_SIZE": POP_SIZE,
                        "chunk": chunk,
                        "prev_magic": prev_magic,
                    }
                    # Preload normalized baseline map with target species averages (if any)
                    if target_species and baseline_stats:
                        self._opt_session["baseline_by_species"][target_species] = {
                            k: v["avg"] for k, v in baseline_stats.items()
                        }
                    output += "Optimize session started. Use 'optimize step' (optionally with chunk=N) to progress.\n"
                    if target_species and baseline_stats:
                        output += f"Random {target_species} baseline (N={baseline_N}):\n"
                        for stat_name, _ in parsed_stats:
                            if stat_name in baseline_stats:
                                b = baseline_stats[stat_name]
                                unit = STAT_UNITS.get(stat_name, "")
                                output += f"  {stat_name}: min={b['min']:.3f}, avg={b['avg']:.3f}, max={b['max']:.3f} {unit}\n"
                    output += f"Progress: 0/{generations} generations completed.\n"
                    return output

                if sub in ("step", "continue"):
                    if not self._opt_session:
                        return "No active optimize session. Start one with: optimize start <gens> <stats_spec> ...\n"
                    # Allow overriding chunk
                    chunk = self._opt_session["chunk"]
                    # Accept either chunk=N or a bare integer as positional
                    for token in parts[2:]:
                        tl = token.lower()
                        if tl in ("auto", "all"):
                            # Run all remaining in one call
                            generations = self._opt_session["generations"]
                            done = self._opt_session["done"]
                            chunk = max(1, generations - done)
                            continue
                        if tl.startswith("chunk="):
                            try:
                                chunk = max(1, int(token.split("=", 1)[1]))
                            except Exception:
                                pass
                        else:
                            try:
                                val = int(token)
                                chunk = max(1, val)
                            except Exception:
                                pass
                    self._opt_session["chunk"] = chunk

                    parsed_stats = self._opt_session["parsed_stats"]
                    generations = self._opt_session["generations"]
                    done = self._opt_session["done"]
                    POP_SIZE = self._opt_session["POP_SIZE"]
                    species_filter = self._opt_session["species_filter"]

                    def species_matches(species_str: str) -> bool:
                        if species_filter is None:
                            return True
                        s = species_str.lower()
                        for want in species_filter:
                            if s == want:
                                return True
                            if ' ' not in want and (s == want or s.endswith(' ' + want)):
                                return True
                        return False

                    def get_candidates():
                        return [rec for rec in self.saved_hybrids.values() if species_matches(rec["species"])]

                    def get_priority_pairs(candidates):
                        pairs = []
                        n = len(candidates)
                        for i in range(n):
                            for j in range(i+1, n):
                                pairs.append((candidates[i], candidates[j]))
                        return pairs

                    bred_total = 0
                    steps = 0
                    while steps < chunk and done < generations:
                        candidates = list(self.saved_hybrids.values())
                        if len(candidates) < 2:
                            for _ in range(POP_SIZE - len(candidates)):
                                sp = random.choice(list(phenotype_genotypes.keys()))
                                # create_random_individual inline to avoid closure issues
                                geno = random.choice(phenotype_genotypes[sp])
                                t = top_expression(geno["top"])
                                m = mid_expression(geno["mid"])
                                b = bottom_expression(geno["bottom"])
                                stats, _ = generate_individual_stats(sp, t, m, b)
                                name = generate_unique_name(sp)
                                self.saved_hybrids[name.lower()] = {"name": name, "genotype": geno, "species": sp, "stats": stats}
                            candidates = list(self.saved_hybrids.values())

                        candidates.sort(key=lambda r: _score_of(parsed_stats, r), reverse=True)
                        pairs = get_priority_pairs(candidates)
                        random.shuffle(pairs)
                        bred = 0
                        if pairs:
                            pair_count = min(len(pairs), max(1, POP_SIZE//2))
                            used = set()
                            for i in range(pair_count):
                                p1, p2 = pairs[i]
                                n1, n2 = p1["name"].lower(), p2["name"].lower()
                                if n1 in used or n2 in used:
                                    continue
                                # Litter-aware breeding: possibly multiple offspring per pair
                                produced_any = False
                                litter_count = 1
                                if getattr(self, "LITTER_MODE", False):
                                    def _num(v):
                                        try:
                                            return float(v)
                                        except Exception:
                                            try:
                                                s = str(v)
                                                if '/' in s:
                                                    return float(s.split('/')[1])
                                                return float(''.join(ch for ch in s if (ch.isdigit() or ch in '.-')))
                                            except Exception:
                                                return 0.0
                                    lit1 = _num(p1.get("stats", {}).get("Litter Size", 1))
                                    lit2 = _num(p2.get("stats", {}).get("Litter Size", 1))
                                    avg = (lit1 + lit2) / 2.0 if (lit1 and lit2) else max(lit1, lit2, 1)
                                    litter_count = max(1, min(getattr(self, "LITTER_CAP", 10), int(round(avg))))
                                for _ in range(litter_count):
                                    result = breed_from_saved(n1, n2, silent=True)
                                    if result is not None:
                                        produced_any = True
                                if produced_any:
                                    bred += 1
                                    used.add(n1)
                                    used.add(n2)
                        all_records = list(self.saved_hybrids.values())
                        all_records.sort(key=lambda r: _score_of(parsed_stats, r), reverse=True)
                        keep = all_records[:POP_SIZE]
                        # Always keep the best of the target species, if any exist
                        target_species = self._opt_session.get("target_species")
                        if target_species:
                            best_target = next((r for r in all_records if r["species"].lower() == target_species), None)
                            if best_target and best_target not in keep:
                                # Replace the last element with the best target species candidate
                                keep[-1] = best_target
                        keep_names = set(r["name"].lower() for r in keep)
                        for name in list(self.saved_hybrids.keys()):
                            if name not in keep_names:
                                self.saved_hybrids.pop(name, None)
                        done += 1
                        steps += 1
                        bred_total += bred
                        output += f"Generation {done}: bred {bred} pair(s).\n"

                    self._opt_session["done"] = done

                    # If finished, print result and clean up (restore magic mode)
                    if done >= generations:
                        all_final = list(self.saved_hybrids.values())
                        all_final.sort(key=lambda r: _score_of(parsed_stats, r), reverse=True)
                        best_overall = all_final[0] if all_final else None
                        # Determine best in target species if applicable
                        target_species = self._opt_session.get("target_species")
                        best_species = None
                        if target_species:
                            species_final = [rec for rec in all_final if rec["species"].lower() == target_species]
                            if species_final:
                                best_species = species_final[0]
                        else:
                            best_species = best_overall

                        output += "\n--- OPTIMIZATION RESULT ---\n"
                        baseline_stats = self._opt_session.get("baseline_stats", {})
                        baseline_N = self._opt_session.get("baseline_N", 100)
                        if target_species and baseline_stats:
                            output += f"Random {target_species} baseline (N={baseline_N}):\n"
                            for stat_name, _ in parsed_stats:
                                if stat_name in baseline_stats:
                                    b = baseline_stats[stat_name]
                                    unit = STAT_UNITS.get(stat_name, "")
                                    output += f"  {stat_name}: min={b['min']:.3f}, avg={b['avg']:.3f}, max={b['max']:.3f} {unit}\n"

                        if best_overall and (not best_species or best_overall["name"] == best_species["name"]):
                            output += f"Best: {best_overall['name']} (Species: {best_overall['species']})\n"
                            output += "Stats (selected):\n"
                            for stat_name, direction in parsed_stats:
                                val = best_overall["stats"].get(stat_name, 0)
                                unit = STAT_UNITS.get(stat_name, "")
                                dir_str = "+" if direction == 1 else "-"
                                output += f"  {dir_str}{stat_name}: {val} {unit}".rstrip() + "\n"
                        else:
                            if best_overall:
                                output += f"Best Overall: {best_overall['name']} (Species: {best_overall['species']})\n"
                                output += "Stats (selected):\n"
                                for stat_name, direction in parsed_stats:
                                    val = best_overall["stats"].get(stat_name, 0)
                                    unit = STAT_UNITS.get(stat_name, "")
                                    dir_str = "+" if direction == 1 else "-"
                                    output += f"  {dir_str}{stat_name}: {val} {unit}".rstrip() + "\n"
                            if best_species:
                                output += f"Best in Species: {best_species['name']} (Species: {best_species['species']})\n"
                                output += "Stats (selected):\n"
                                for stat_name, direction in parsed_stats:
                                    val = best_species["stats"].get(stat_name, 0)
                                    unit = STAT_UNITS.get(stat_name, "")
                                    dir_str = "+" if direction == 1 else "-"
                                    output += f"  {dir_str}{stat_name}: {val} {unit}".rstrip() + "\n"
                        prev_magic = self._opt_session.get("prev_magic", MAGIC_AFFINITY_MODE)
                        MAGIC_AFFINITY_MODE = prev_magic
                        self._opt_session = None
                        return output

            # end optimize command handler
        elif cmd == "random":
            genotype, sp = random.choice(all_full_genotypes)
            output += "--- RANDOM SPECIES GENERATED ---\n"
            output += "Genotype:\n"
            output += f"  Top   : {genotype['top']}\n"
            output += f"  Mid   : {genotype['mid']}\n"
            output += f"  Bottom: {genotype['bottom']}\n"

            stats, mutations = generate_individual_stats(
                sp,
                top_expression(genotype["top"]),
                mid_expression(genotype["mid"]),
                bottom_expression(genotype["bottom"])
            )
            output += f"Species: {sp}\n"

            if self.SAVE_MODE:
                new_name = generate_unique_name(sp)
                record = {
                    "name": new_name,
                    "genotype": genotype,
                    "species": sp,
                    "stats": stats
                }
                # session-only save
                self.saved_hybrids[new_name.lower()] = record
                output += f"(Saved in session as “{new_name}”)\n"

            output += "\nStats:\n"
            for stat, val in stats.items():
                unit = STAT_UNITS.get(stat, "")
                output += f"  {stat:15s}: {val} {unit}".rstrip() + "\n"
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
        "  magic [on|off|status]     - Toggle or set elemental magic affinity display\n"
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
