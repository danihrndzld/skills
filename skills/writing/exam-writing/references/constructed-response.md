# Short answer and constructed response

Covers questions such as "explain the cause" or "write one line of code". The handbook by Haladyna and Rodriguez [19] covers these formats together with multiple choice. Numbers in brackets refer to [references.md](references.md).

## State the task precisely

A badly scoped open question produces answers that can't be compared with each other, and then the rubric has nothing to apply to. Three elements fix the task:

| Element | Question it answers | Example |
|---|---|---|
| Observable verb | What does the student have to do? | "Write", "name and justify", "point to the line" |
| Scope | How much do they have to produce? | "one formula", "in 2 or 3 sentences", "one cause" |
| Visible criterion | What counts as a complete answer? | "give the cause and the data in the table that supports it" |

Before:
> Explain what happened in the experiment.

After:
> The table below shows the readings from the experiment. In 2 or 3 sentences, name the reason the final temperature was lower than predicted, and quote the reading that shows it. (1 point: 0.5 for the reason, 0.5 for the reading)

Before:
> Write a test for the function.

After:
> `area(width, height)` must return 0 when either side is 0. Write **one** assertion that fails if `area(0, 5)` returns anything else. (0.5 points)

The "before" versions accept anything from a full page to one line, and each answer would need a different grading criterion.

## Assign the points

- **Do:** publish the points for each question and, if it has parts, for each part. Students plan their time with that information.
- **Do:** make the points proportional to the work. A one-line answer and a causal explanation with evidence aren't worth the same as one multiple-choice item if they take five times longer.
- **Don't:** ask for two things and give one score with no breakdown ("explain and fix: 1 point"). When grading, the correct half has no rule.

## Analytic rubrics

Jonsson and Svingby [11] reviewed the research on rubrics and concluded, according to the articles that cite them, that rubrics improve grading reliability when they are analytic (one score per criterion), specific to the task, and come with example answers or rater training. The conclusions of [11] were taken from two citing articles, not from the original text.

Analytic rubric for the experiment question:

| Criterion | 0 | 0.25 | 0.5 |
|---|---|---|---|
| Reason | Gives no reason, or one the data contradicts | Says "something went wrong" without saying what or why | Names the specific cause and how it lowered the temperature |
| Evidence | Doesn't quote the data | Quotes a related reading but not the deciding one | Quotes the reading that shows the cause |

Rubric for "write one assertion":

| Criterion | Points |
|---|---|
| The assertion compares the result of `area(0, 5)` with 0 | 0.25 |
| The syntax runs as written in the language used in class (list each accepted form) | 0.25 |

- **Do:** write the model answer to every question before printing the exam. If the instructor can't write it in the space and time given, the student can't either.
- **Do:** list the acceptable alternative answers in the rubric (for example, two valid syntaxes) before grading the first exam.

## Grade blind and question by question

**Blind grading.** The meta-analysis by Malouff and Thorsteinsson [12] pooled 23 analyses from 20 experimental studies with 1,935 graders. When the grader knew information about the student that had nothing to do with the performance (ethnicity, low earlier performance, physical attractiveness, learning difficulties), the grade changed with an effect size of g = 0.36. The effect was similar in primary school and in university.

To apply it, ask students to write their name only on the cover or on the back, fold the cover before grading, and number the exams.

**Contrast effect.** Yeates, Moreau and Eva [13] found in real clinical exams that the score for one performance moved in the opposite direction from the performances seen just before it. After a good one, the next one got a lower score. The effect explained up to 11% of the variance on some occasions.

**Question by question.** No verified study was found that directly compares grading question by question with grading exam by exam. The recommendation is inferred from [12] and [13]. Grading question 1 on every exam, then question 2, and so on, stops the impression from the same student's previous answer from weighing on the next one, and it keeps a single question's rubric in the grader's head.

- **Do:** change the order of the stack between one question and the next, so the same student doesn't always come right after the best exam.
- **Do:** when the rubric changes partway through grading (an unexpected answer shows up), write down the change and go back to that question on the exams already graded.
