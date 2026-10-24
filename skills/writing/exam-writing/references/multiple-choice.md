# Writing multiple-choice items

Main sources: the taxonomy of 31 guidelines by Haladyna, Downing and Rodriguez [1] and the NBME item-writing guide [2]. Numbers in brackets refer to [references.md](references.md).

## Where the rules come from

Haladyna, Downing and Rodriguez [1] validated 31 guidelines by reviewing 27 measurement textbooks and 27 studies published since 1990. The list replaces an earlier taxonomy of 43 rules that the first two authors published in 1989, and it is meant for classroom exams. The guidelines fall into five groups: content (1 to 8), format (9 and 10), style (11 to 13), stem (14 to 17) and options (18 to 31). The handbook by Haladyna and Rodriguez [19] updates the same taxonomy.

The NBME guide [2] uses a single format, "one best answer" (type A), and sorts technical flaws into two families:

| Family | What it causes | Flaws listed in [2] |
|---|---|---|
| Irrelevant difficulty | The item is hard for reasons unrelated to what it measures, and it affects everyone | Long or complicated options; inconsistent numeric data; vague terms; options that are not homogeneous; options in no logical order; "none of the above"; a needlessly complex stem; a negative stem |
| Testwiseness | A skilled test taker gets it right without knowing the content | Grammatical cues; paired or exhaustive options; absolute terms ("always", "never"); a correct answer that is longer or more complete; a word repeated between stem and answer; convergence (the correct option shares the most elements with the others) |

## Rules for the stem

**Rule 1. Apply the "cover the options" rule.** The NBME guide [2] asks that someone who knows the topic can answer after reading the stem and the lead-in with the options covered. Haladyna et al. [1] state the same idea as guideline 15, which says the central idea goes in the stem and not in the options.

Before:
> About the water cycle:
> A. Evaporation happens only at night.
> B. Condensation forms clouds when water vapor cools.
> C. Precipitation replaces groundwater completely.
> D. Rivers do not take part in it.

After:
> A cold glass of water sits on a table in a warm room, and after a few minutes drops of water form on the outside of the glass. Which process forms the drops?
> A. Evaporation of water from inside the glass
> B. Condensation of water vapor from the air
> C. Water seeping through the walls of the glass
> D. Melting of frost that formed on the glass

The "before" version bundles four unrelated true/false statements. The "after" version can be answered with the options covered.

**Rule 2. Write the stem in positive form.** Guideline 17 of [1] asks you to avoid NOT and EXCEPT, and to highlight them if you use them. The NBME guide [2] counts a negative stem as irrelevant difficulty, because a student who knows the topic can miss the word "except".

Before: "Which of the following is NOT a renewable energy source?"
After: "A town gets its electricity from a plant that burns coal, a wind farm and a solar farm. Which of the three sources will run out if the town keeps using it?"

**Rule 3. Remove decorative text.** Guideline 16 of [1] forbids window dressing, and guideline 13 asks you to minimize reading. Keep a scenario only if every fact in it helps answer the question.

**Rule 4. One closed question per item.** The NBME guide [2] advises against open endings such as "The diagnosis is:" because they invite grammatical cues and force the student to compare options that are not alike.

**Rule 5. Avoid trick items and opinion items.** Guidelines 6 and 7 of [1]. If two instructors of the course could argue about which option is the key, the item does not work.

## Rules for the options

**Rule 6. One correct answer and homogeneous options.** Guidelines 19 and 23 of [1]. The NBME guide [2] requires that all options can be judged on a single dimension. If the key is a tool, the other options are tools too.

Before: A. A thermometer  B. That the liquid boils  C. 100 degrees  D. Heating
After: A. A thermometer  B. A barometer  C. A hygrometer  D. An anemometer

**Rule 7. Keep option lengths similar.** Guideline 24 of [1]. In [2], a longer or more complete answer is a testwiseness flaw, because writers tend to qualify and refine the key and leave the wrong options short.

Before:
> A. Mitosis.
> B. A process of cell division that produces two daughter cells, each with the same number of chromosomes as the parent cell.
> C. Osmosis.
> D. Diffusion.

After: four options of about the same length, all built the same way ("a process in which...").

**Rule 8. Remove absolute terms.** Guideline 28a of [1] and a testwiseness flaw in [2]. Words like "always", "never", "completely" and "absolutely" usually mark a false option, and students know it.

Before: "Metals always conduct electricity better than any other material."
After: "Copper is used in electrical wiring because it conducts electricity well."

**Rule 9. Keep grammatical agreement.** Guideline 28c of [1]. In English, a stem that ends in "an" rules out every option that starts with a consonant sound. In languages with grammatical gender or number, a stem whose article or adjective agrees with only some options gives those options away.

Before: "A substance that speeds up a reaction without being used up is an..." with the options "catalyst", "enzyme", "inhibitor", "reactant".
After: "What is a substance called that speeds up a reaction without being used up?"

**Rule 10. Do not repeat words from the stem in the key.** Guideline 28b of [1] (clang association) and a testwiseness flaw in [2].

Before: "Which type of rock forms from cooled *magma*?" with the key "*magmatic* (igneous) rock".
After: describe a rock sample and how it formed, and ask which type of rock it is.

**Rule 11. Do not use "all of the above", and use "none of the above" with care.** Guidelines 25 and 26 of [1]. The NBME guide [2] counts "none of the above" as irrelevant difficulty, because it turns the item into four true/false questions. With "all of the above", recognizing two correct options is enough to get the item right.

The fix proposed by [2] is to replace "none of the above" with the concrete action it stands for. For example, instead of "none of the above", write "Leave the setting unchanged and record the reading as unreliable".

**Rule 12. Avoid paired or exhaustive options.** Guideline 28e of [1] and a testwiseness flaw in [2]. If two options are "the value goes up" and "the value does not go up", they cover every case and one of them is the key.

**Rule 13. Avoid convergence.** The NBME guide [2] defines convergence as a key that shares more elements with the other options than any other option does.

Before:
> A. `sort -n file`
> B. `sort -n -r file`
> C. `uniq -r file`
> D. `sort -r -u file`

B shares `sort`, `-n` and `-r` with the other three, so a student who doesn't know the answer can pick the most repeated element of each part.

After: vary the options on one dimension only (the command, or the flag, or the argument), not on three at once.

**Rule 14. Order the options logically or numerically.** Guideline 21 of [1]. Put numbers from smallest to largest and commands in alphabetical order. Vary the position of the key (guideline 20) and balance how often it falls on each letter. See [parallel-versions.md](parallel-versions.md) for the bias toward middle positions [15].

**Rule 15. Keep options independent.** Guideline 22 of [1]. If option A ("more than 70%") includes option B ("more than 80%"), there are two correct answers.

## Final review of each item

Rule 5 of the NBME guide [2] asks you to review each item with four questions. Can it be answered with the options covered? Is there anything that confuses someone who knows the content? Are there cues for someone who doesn't? Has a colleague reviewed it? [checklist.md](checklist.md) turns these rules into yes/no checks.
