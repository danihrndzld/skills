# Parallel versions of the same exam

The goal is that two neighboring students can't copy from each other and that no version ends up easier than another. Numbers in brackets refer to [references.md](references.md).

## Three levels of variation

| Level | What changes between versions | Risk that one version is harder | Protection against copying |
|---|---|---|---|
| A. Shuffle the order of items | Position of each item | Low, according to [14] | Medium, because the neighbor has the same item under another number |
| B. Shuffle the order of options | Letter of the key | Low if you balance the key position [15] | Medium, because the letter is useless but the option text still helps |
| C. Clone the item | Surface data in the scenario | Medium, so it has to be checked | High, because the neighbor's answer is wrong in your own version |

## Level A: order of items

Şad [14] gave 554 university students two forms of a 26-item multiple-choice exam with the same items in reverse order, easy to hard and hard to easy. The study found no difference in performance for low, medium or high achievers, and no difference in item difficulty, discrimination or point-biserial correlation between forms.

The evidence on item order isn't unanimous. Other studies, with smaller samples or specific populations, report differences. [14] is the most controlled study that was found.

- **Do:** shuffle the order within each section (multiple choice, short answer, matching) and keep the sections in the same order in every version, so the instructions and the time for each block match.
- **Do:** keep items that share a scenario or a data set together.

## Level B: order of options

Attali and Bar-Hillel [15] showed that people who write tests tend to hide the key in the middle positions, and people who take tests tend to look for it there, at a ratio of up to 3 or 4 to 1 for single questions. On a typical 4-option test, about 55% of wrong answers fall on the two middle positions. Items with the key in the middle turned out easier and less discriminating than items with the key at either end.

So if the key of an item is B in version 1 and D in version 2, the same item can have different difficulty in each version.

- **Do:** count in each version how many times the key falls on A, B, C and D, and keep the count even (with 20 items, about 5 per letter).
- **Do:** keep the logical order of guideline 21 of [1] when the options are numbers or a sequence. In that case don't shuffle them, and vary the item at level C instead.
- **Don't:** shuffle options that refer to each other ("both A and B"). That kind of option is already a flaw according to [1] and [2].

## Level C: item models and clones

Gierl, Lai and Turner [16] describe item generation in three steps. A content specialist builds the cognitive model of the content, that model is used to write an item model (a template with the parts that vary and the parts that stay fixed), and items are produced from the template. With a single model they generated 1,248 items for a surgery exam. The same procedure works by hand to produce a few versions.

A clone, or isomorph, changes the surface data and keeps the skill measured, the reasoning required and the structure of the answer.

### Example item model

Template: "The rule says the service costs [P1] from 0 to [L] [unit] and [P2] from [L+1]. The tests check [x1] and [x2], and both pass. In production, exactly [L] [unit] was charged [P2]. Which pair of values would have found the error with the fewest cases?"

| Element | Version 1 | Version 2 | Version 3 |
|---|---|---|---|
| Domain | Library late fee, days | Shipping, kilograms | Phone plan, gigabytes |
| Limit L | 7 | 20 | 5 |
| Tested values | 3 and 10 | 10 and 30 | 2 and 8 |
| Key | 7 and 8 | 20 and 21 | 5 and 6 |
| Fixed in all versions | Technique (boundary values), the error at the upper edge of the first range, the same number of options and the same kind of distractors |

### What may change and what may not

| May change | Must not change |
|---|---|
| Names, domain, numbers of the same size | The technique or concept measured |
| The order of facts within the scenario, if it doesn't change how it reads | The number of reasoning steps |
| An equivalent tool, if the course taught both | The length of the scenario |
| | The kind of error each distractor stands for |

Sharing a template doesn't guarantee the same difficulty. A "round" number (10) or a more familiar domain (one students already used in homework) can make one version easier. That's why you check after the exam (below).

**For short answer and practical tasks,** clone the task and keep the same rubric. For example, every version asks for one assertion, and only the expected value and the function under test change, while the two-criterion rubric from [constructed-response.md](constructed-response.md) stays the same.

## Grading fairly across versions

Large testing programs equate versions with equating methods, which Kolen and Brennan [17] describe in detail. Those methods estimate the relationship between the score distributions of each form, and they need large groups of test takers. With a small class split across a few versions (for example 11 students in 3 versions, so 3 or 4 per version), you can't equate statistically, and the difference in averages between versions mostly reflects which students got each one.

A workable procedure for a small class:

1. **Before:** build the versions with levels A, B and C above and from the same table of specifications ([table-of-specifications.md](table-of-specifications.md)). Each version must have the same number of items per objective and per cognitive level.
2. **Assign versions at random** or in a pattern that separates neighbors, not by alphabetical list, so the version doesn't correlate with performance.
3. **After:** for each cloned item, compare the p of its versions. With 3 or 4 students per version, only large differences count. If 4 of 4 students got one clone right and 0 of 4 got its pair right, reread that clone before publishing grades.
4. **If a clone turned out flawed** (two answers, missing data), drop it in that version only and grade those students over the remaining items, instead of dropping the item in every version.
5. **Don't scale grades** by version with so few students. A version with a lower average may just reflect who got it.
