Answer: Chromosomal pairing implications in this simulator
This simulator models inheritance with three diploid loci—“top”, “mid”, and “bottom”—with two alleles per locus, plus:

Dominance resolution per locus using a fixed global dominance order derived from species counts (not biological dominance tables).
Random selection of one allele from each parental locus with tiny mutation probabilities.
Phenotype determination by the tuple of expressed alleles (top, mid, bottom) mapped to a known species list. If a combo isn’t in the list, it’s considered non-viable for breeding paths that force a species outcome.
What this implies vs. real chromosomes:

Simplified karyotype: It’s effectively 3 unlinked chromosomes/loci. There’s no modeling of chromosome count mismatches, aneuploidy, recombination, linkage, or crossover. Independent assortment is implied (one allele randomly chosen per locus), but linkage disequilibrium is ignored.
Frequency-as-dominance: Dominance is derived from how often an allele appears among defined species, which is a convenience, not Mendelian biology. Real dominance is locus- and allele-specific, not frequency-based.
Discrete viability filter: Only phenotypes in known_species are treated as “species” outcomes (especially in saved-hybrid breeding where it loops until a species is found). That acts like a hard viability/recognition barrier, which isn’t how real fertility/viability works.
Polygenic traits compressed to 3 loci: Physical/sensory traits are derived from the expressed alleles via stat source rules; in biology they’d be polygenic and environment-influenced. This is a stylized mapping to keep fantasy species coherent.
No chromosomal incompatibilities: Cross-species fertility is unrestricted by ploidy or chromosomal structure, so any two saved hybrids can breed (subject to phenomenological species mapping), which is biologically generous.
In short: The simulator behaves like a 3-locus, diploid, independent-inheritance model with a curated viability/species table and some stat blending/mutation. It’s great for fun, consistent fantasy outcomes, but it doesn’t represent full chromosomal mechanics.

Quick wins (low effort, high value)
Explicit dominance per locus (co-/incomplete dominance)

Today: dominance is frequency-based across species; not biologically grounded.
Improve: define a dominance matrix per locus that maps heterozygotes to an expressed state:
complete: A > a → express A
incomplete: A/a → blend
co-dominant: A/a → both (or trait-specific blending)
Where: replace express_gene and the three expression helpers to consult a per-locus dominance table instead of global frequency ranks.
Benefit: Better fidelity for heterozygous outcomes and decouples phenotype from species frequency artifacts.
Keep rare allele mutation in all breeding paths

Done: cross_breed_from_genotype now uses random_inherited_allele, so optimize and saved-hybrid breeding include rare genotype mutations (same as species-name breeding).
Benefit: Slow genotype drift is now consistent everywhere.
Tweak phenotype viability policy (soften the hard filter)

Today: if allele tuple isn’t in known_species, offspring is considered non-viable (especially in saved-hybrid breeding).
Improve: make unknown combos rare but not impossible:
Assign a small viability probability or classify as “chimera (unstable)” with reduced fitness/fertility instead of immediate miscarriage.
Where: in breed_from_saved after species=overall_phenotype(…), if None, sample a viability probability to either abort (miscarriage) or assign a generic “hybrid” with penalties.
Medium steps (moderate effort, large realism gains)
Phased haplotypes and recombination

Today: each locus is inherited independently (effectively unlinked), and genotypes are unordered pairs.
Improve:
Store phased haplotypes for each individual: two chromosomes (hapA, hapB) across your three loci.
During gametogenesis, recombine haplotypes with a recombination fraction r between loci (configurable linkage). Build gametes via crossover, then form the child zygote.
Where:
On first save, randomly phase the existing tuples.
Introduce a recombine(hapA, hapB, linkage_map) → gamete function.
Update cross_breed_from_genotype to build gametes via recombination, then apply rare mutation.
Benefit: Captures linkage and crossover; enables realistic hitchhiking and LD patterns.
Polygenic traits for major stats

Today: stats are derived mostly from expressed alleles and some noise; then mutated per-stat at a small rate.
Improve:
Introduce small-effect “hidden” loci that additively contribute to key traits (Size, Strength, Speed, IQ/EQ).
Include pleiotropy (one hidden locus affects multiple traits with different weights) and environment noise (normal(0, σ_env)).
Keep current species flavor effects as baselines/multipliers, but compute final values as baseline + genetic_effect + env.
Where:
Add a compact genetic_effects dict keyed by locus and allele, and a small vector of hidden loci per individual.
In generate_individual_stats, combine baseline + polygenic effects + env noise.
Benefit: Moves the simulator toward quantitative genetics rather than pure lookups.
Soft fertility/viability and hybrid breakdown

Introduce probabilistic viability and fertility penalties by species pairing and genotype distance, not just deterministic species table membership.
Add miscarriages and reduced litter sizes where appropriate; optionally apply Haldane’s rule (heterogametic sex more affected).
Where: breed_from_saved and cross_breed_random after zygote formation but before stat generation.
Deeper realism (higher effort)
Sex, sex chromosomes, and dimorphism

Add sex (M/F) with XX/XY or species-specific systems; dimorphic multipliers on some traits; sex-specific fertility.
Implement maternal/paternal imprinting for certain stats.
Where: extend saved hybrid records with sex, add sex-chromosome locus, tweak fertility and trait generation.
Better mutation model

Distinguish transition/transversion biases, locus-specific mutation rates, and occasional structural variants (duplications/deletions) that scale trait baselines.
Where: enhance allele_mutation_distribution and add a rare “structural event” path affecting trait baselines.
Population genetics dynamics

Track population size, selection (fitness), drift, migration. Let optimize operate more like selection across generations with survival/fecundity weighting, not just top-k pruning.
Where: in optimize step, weight parent choice by fitness and survival; let population size fluctuate within bounds.
Linkage map and hotspots

Expand to more loci and assign map distances; add recombination hotspots for more realistic crossover distribution.
Data shapes and “contracts” to guide implementation
Dominance tables

Inputs: locus name (top/mid/bottom), genotype pair (A, a)
Output: expressed state (A, a, blend(A,a), or vector of trait multipliers)
Error modes: missing pair → fallback to species default; log once.
Recombination

Inputs: two haplotypes, ordered loci, recombination fractions (0–0.5) between adjacent loci
Output: gamete haplotype
Edge cases: r=0 (complete linkage), r=0.5 (independent assortment)
Polygenic traits

Inputs: list of hidden loci per individual with allele effects; environment σ
Output: trait deltas summed across loci, then add env noise
Edge cases: keep effects small to avoid runaway magnitudes; cap extremes
Prioritized roadmap (what I recommend first)
Explicit dominance per locus (co-/incomplete dominance) — small refactor, big correctness gain.
Phased haplotypes + recombination with a simple linkage map for the 3 loci — makes inheritance feel real.
Polygenic small-effect contributions layered on top of current species baselines — more realistic trait distributions.
Probabilistic viability/fertility — reduces the hard “species table or bust” feel.