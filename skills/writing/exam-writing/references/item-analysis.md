# Item flaws and item analysis

Numbers in brackets refer to [references.md](references.md).

## How much flawed items change grades

| Study | Sample | Items with a flaw | Main result |
|---|---|---|---|
| Downing [6] | 4 basic science exams, 1st and 2nd year of medical school | 36% to 65%, depending on the exam | Flawed items were 0 to 15 percentage points harder than unflawed items that measured the same thing. With only unflawed items, 646 students passed (53%); with only flawed items, 575 passed (47%) |
| Tarrant and Ware [7] | 10 summative nursing exams in Hong Kong, reviewed by a panel of 4 | 28% to 75%, depending on the exam; 47.3% overall | With only unflawed items, fewer students passed (748, 90.6%) than with the full exam (779, 94.3%), but more students reached 80% or higher (173, 20.9%, against 120, 14.5%) |

Downing [6] also reported that the flaws barely changed the reliability or the other psychometric indices of the exam. The effect shows up in individual grades and in who passes. Note that [6] was read from an abstract quoted by third parties, not from the full text.

The two results look opposite. In Downing [6] the flaws lowered grades, and in Tarrant and Ware [7] the full exam, with its flaws, passed 31 more students than the cleaned version. Tarrant and Ware [7] conclude that the flaws did not hurt borderline students and did hurt the high achievers.

One reading that fits both, which neither article proves on its own, uses the two families from the NBME guide [2]. Irrelevant difficulty takes points away from students who know the content, and testwiseness cues give points to students who don't. An exam mixes the two families in different proportions, so the net effect on a grade can't be predicted and doesn't cancel out by itself.

A worked example, using the worst case of [6]:

| Assumption | Value |
|---|---|
| Multiple-choice items | 20, worth 0.25 points each |
| Items with a flaw | 10 |
| Extra difficulty per flawed item, worst case of [6] | 15 percentage points |
| Expected loss per student | 10 x 0.15 x 0.25 = 0.375 points |

Losing up to 0.375 points to wording rather than content is enough to change the result for a student near the pass mark.

- **Do:** review the whole exam against the flaw list of [2] before printing (see [checklist.md](checklist.md)). Tarrant and Ware [7] used a panel of 4 reviewers. With a single instructor, ask a colleague (or a fresh agent) to answer the exam without the key, which finds items with two answers.
- **Do:** count how many items have at least one flaw. The two studies found 28% to 75% of items flawed per exam [6], [7], so finding several is expected.
- **Don't:** take a high reliability coefficient as proof that the items are well written. Downing [6] found it almost the same with and without flaws.

## Analysis after the exam

The NBME guide [2] recommends running item analysis before publishing grades. Three indices are enough for a classroom exam.

| Index | How to compute it | How to read it, per [2] |
|---|---|---|
| Difficulty p | Proportion of students who got the item right | p > 0.95 is very easy and gives little information. p < 0.30 is very hard or not aligned with what was taught |
| Discrimination (point-biserial correlation) | Correlation between getting the item right (0/1) and the total exam score | Positive and high means it discriminates well. Near 0 means it doesn't rank students. Negative means a flaw in the item or a miskeyed answer |
| Option analysis | How many students chose each option, split into upper and lower groups | An option nobody chose is implausible or easy to rule out because of a flaw. A distractor chosen more often than the key suggests a second answer or a wrong key |

**Discrimination index by groups.** Rank students by total score, take the upper and lower groups, and subtract, so D = p of the upper group minus p of the lower group. The NBME guide [2] says that the top 27% and bottom 27% give the best information, a rule that goes back to Kelley [20], and that in practice it is rounded to 25%. Kelley [20] was not read directly; the 27% rule is taken from [2].

### Small classes

In a small class the analysis finds gross problems and can't rank items finely. For example, with 11 students:

| Computation with 11 students | Value |
|---|---|
| Size of each group (27% of 11) | 3 students |
| Possible values of D | from -1 to 1, in steps of 1/3 |
| Standard error of p when p = 0.5, sqrt(0.5 x 0.5 / 11) | 0.15 |

In general, the standard error of p is sqrt(p(1 - p) / n), where n is the number of students.

| Signal in a small class | Action |
|---|---|
| Negative discrimination and low p | Check the key before publishing grades. [2] says that a miskeyed item produces both signals together |
| A distractor chosen by more upper-group students than the key | Reread the item looking for a second defensible answer |
| p = 1.00 (everyone got it right) | Keep it if it measures something central. It gives no discrimination |
| A distractor nobody chose | Rewrite or remove it in the next version (below) |

## What to do with a distractor nobody chose

Tarrant, Ware and Mohammed [4] count as non-functioning any distractor chosen by fewer than 5% of examinees. With 11 students, 5% is less than one person, so the rule reduces to "nobody chose it".

1. **This exam:** it doesn't change the grade. The item is still valid. It just had fewer effective options.
2. **Next version:** replace it with an error you saw while grading, or delete it and leave the item with 3 options. Rodriguez [3] supports removing the least chosen distractor rather than one at random.
3. **If the exam has many such distractors:** the NBME guide [2] warns that many distractors almost nobody chooses point to implausible options or structural flaws that skilled test takers exploit.

## What to do with a flawed item after the exam

| Finding | Usual decision |
|---|---|
| Miskeyed item | Fix the key and regrade |
| Two defensible options | Accept both as correct |
| Item with no correct answer, or ambiguous | Drop it for everyone and recompute the total over the remaining items |

These decisions apply the NBME criteria [2] on wrong keys and double answers. How exactly to regrade is the instructor's decision.

For parallel versions, see the per-clone check in [parallel-versions.md](parallel-versions.md).
