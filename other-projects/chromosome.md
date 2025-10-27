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