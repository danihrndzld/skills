---
name: exam-writing
description: Use when writing, reviewing, or versioning an exam, quiz, or test items (multiple choice, short answer, matching), building a table of specifications or test blueprint, making parallel versions of an exam, checking items for flaws before printing, or reading item analysis (difficulty p, point-biserial, distractors nobody chose) after an exam. Evidence-based rules with IEEE references. Works for exams written in any language.
---

# Exam writing

A workflow for classroom exams, based on published item-writing research (31 guidelines from Haladyna, Downing and Rodriguez, the NBME item-writing guide, and studies on distractors, item flaws, item order, key position and grading bias). The rules apply to exams in any language. The examples in the references are in English, so adapt grammar rules (for example, gender and number agreement) to the language of the exam.

Follow the six steps in order. Do not skip step 1 or step 4.

## 1. Build a table of specifications first

Before writing any item, build a grid of learning objectives (rows) by cognitive level (columns), with the number of items and points in each cell.

- List the objectives the exam covers, each with its revised Bloom verb (remember, understand, apply, analyze, evaluate, create). Take them from the course syllabus or the user, not from memory.
- Weight each objective by class time and importance, then choose the format by level and spread the points.
- Do not write items first and build the table afterwards to justify them.

Details: [references/table-of-specifications.md](references/table-of-specifications.md) and [references/cognitive-level.md](references/cognitive-level.md).

## 2. Write the items

Write each item for one cell of the table and tag it with that cell. Core rules:

- The stem must be answerable with the options covered. Write it in positive form; if NOT or EXCEPT is unavoidable, put it in bold capitals.
- One defensible answer. Options are homogeneous, similar in length, independent, and in logical or numeric order.
- No absolute terms, grammatical cues, words repeated from the stem in the key, paired or exhaustive options, or convergence. No "all of the above"; replace "none of the above" with the concrete action it stands for.
- Three plausible options are as good as four with a filler. Write every distractor from a real student error and name that error next to it.
- For apply and analyze, write a scenario with new data and a closed question at the end. Do not add a scenario to a recall item to make it look harder.
- For short answer, fix the verb, the scope and the points per part, and write the model answer and an analytic rubric before printing.
- For matching, keep both lists homogeneous, give more responses than premises, state the basis of the match, and keep everything on one page.

Details: [multiple choice](references/multiple-choice.md), [options and distractors](references/options-and-distractors.md), [cognitive level](references/cognitive-level.md), [constructed response](references/constructed-response.md), [matching](references/matching.md).

## 3. Run the pre-print checklist

Go through the 25 yes/no checks in [references/checklist.md](references/checklist.md) and report every "no" with the item number and the fix. Count how many items have at least one flaw. In the two reference studies, 28% to 75% of the items on real exams had at least one flaw, so finding several is expected. A high reliability coefficient does not show that items are well written.

## 4. Blind-solve pass

Have a fresh subagent take the exam without the key. The research recommends review by a colleague who answers without the key, because that finds items with two answers; the NBME guide asks whether the item can be answered with the options covered, whether anything confuses a student who knows the content, and whether anything cues a student who does not.

Give the subagent only the student-facing exam text. Never give it the key, the model answers, or the key column of the blueprint. Ask it to return one row per item:

| Item | Answer chosen | Confidence (high, medium, low) | Answerable with options covered (y/n) | Second defensible answer (y/n, which) | Cue it could use (longest option, grammar, repeated word, absolute term, convergence, paired options) | Missing or inconsistent data |
|---|---|---|---|---|---|---|

Then compare its answers with the key. Treat every disagreement, every low-confidence answer, every "y" in the second-answer column, and every cue as an item to fix, and rerun the pass on the fixed items. When the exam has parallel versions, run the pass on each version.

## 5. Build parallel versions (optional)

Use three levels of variation:

1. Shuffle the order of items within each section, keep the sections in the same order, and keep items that share a scenario together.
2. Shuffle the options, then count how often the key falls on each letter in each version and keep the count even. Do not shuffle numeric or logically ordered options; vary those items by cloning.
3. Clone items from an item model. Change only surface data (names, domain, numbers of the same size) and keep the skill, the reasoning steps, the scenario length and the error each distractor stands for.

Every version must fill the same cells of the table of specifications with the same items and points. Assign versions at random or in a pattern that separates neighbors, not alphabetically. After shuffling, recheck the key of every version against the final printed text.

Details: [references/parallel-versions.md](references/parallel-versions.md).

## 6. Item analysis after the exam

Before publishing grades, compute for each item the difficulty p (proportion correct), the point-biserial correlation with the total score, and the count of students who chose each option, split by upper and lower group.

- Check the key when discrimination is negative and p is low, because a miskeyed item produces both signals together.
- A distractor chosen by more upper-group students than the key suggests a second defensible answer.
- A distractor nobody chose does not change this exam's grades. Replace it or delete it in the next version.
- In a small class, the indices only detect gross problems. For example, with 11 students the standard error of p at p = 0.5 is about 0.15. For parallel versions, compare each clone's p across versions and only act on large differences. Do not scale grades by version.

Details: [references/item-analysis.md](references/item-analysis.md).

## Grading constructed responses

Grade without seeing the student's name, grade one question across all exams before moving to the next, and reshuffle the stack between questions. See [references/constructed-response.md](references/constructed-response.md) for the evidence and its limits.

## Sources

All claims come from the 20 sources in [references/references.md](references/references.md), which also states how much of each source was read (full text, abstract, or secondary summary). Keep those caveats when you cite a rule to the user.
