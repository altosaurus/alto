---
title: Spaced Repetition
nav_order: 4
nav_group: Using Alto
permalink: /practice/
math: true
---

Choose a scheduling algorithm for your profile under **Settings → Practice → Question scheduling**. **ASRS** and **ARTS** let you practice for as long as you like. **SM-2** and **FSRS** give each card a review date. With either of those, the exercise pauses when you are caught up. Another review can come due later the same day.

Consider a single Note Identification question, F♯ in treble clef. A scheduler can choose whether to show F♯ on the **next turn**, or it can set a **due date** for its next review. Even schedulers that make the same kind of decision use different evidence.

| Scheduler | What changes after an answer? | How does F♯ return? |
| --- | --- | --- |
| [ASRS](#asrs) | Each attempt changes its strain. | A weighted draw on each turn. Its weight recovers as seconds pass. |
| [ARTS](#arts) | The first answer sets how fast its priority grows. | It returns when its priority ranks highest. Each intervening question raises that priority. |
| [SM-2](#sm-2) | The first answer updates its run of successes and ease factor. | Its review interval follows a sequence of day counts, with a short retry after a miss. |
| [FSRS](#fsrs) | The first answer updates its estimated memory stability and difficulty. | After the learning steps, it gets a review date near the model’s 90% recall point. |

## ASRS

The **Alto Spaced Repetition System (ASRS)** is the default scheduler. For each turn, it generates a few questions and adds some you have answered before under the same exercise settings. It draws from that pool at random, giving more weight to questions you find difficult. A question you just answered gets less weight for a while. The better you know it, the longer that effect lasts.

### Strain

Each question has a score called **strain**, which says how much practice it needs. It starts at 1.5, stays between 0 and 6, and changes with each answer.

| Answer | Change in strain |
| --- | --- |
| Wrong | Add 1.5 for each miss. |
| Right on the first try | Subtract 0.5, then adjust for speed. |
| Right after a miss | Subtract 0.2. |

### Response time

For a correct first answer, ASRS compares the time you took with the exercise’s **par time**. At par there is no speed adjustment. At half the par time or faster, ASRS subtracts another 0.6. At four times par or slower, it adds 1.0. The adjustment changes gradually in between. A slow but correct answer can therefore make the question more likely to return.

<details markdown="1">
<summary>Par times by exercise</summary>

| Exercise | Par time |
| --- | --- |
| Note Identification, Keyboard Note Identification | 3 s |
| Key Signature Identification, Clef Basics, Notation Identification | 5 s |
| Interval Identification, Keyboard Interval Identification, Chord Quality, Note Construction, Key Signature Construction | 6 s |
| Circle of Fifths | 7 s |
| Scale Identification | 8 s |
| Arpeggio Identification | 9 s |
| Order of Keys | 12 s |
| Scale Construction | 25 s |

</details>

### Probability of the next draw

For a question with strain $$s$$, ASRS sets a recovery time $$c$$ in seconds. If $$t$$ seconds have passed since the last answer, its weight $$w$$ recovers according to

$$
c = 120 \cdot 2^{3-s}
$$

$$
w = e^{0.6s}\max\left(0.02,\,1-e^{-t/c}\right).
$$

Higher strain gives a question both a higher eventual weight and a shorter recovery time. A fresh question gets a weight of $$e^{0.6\cdot 1.5}\approx 2.46$$. To get the probability of drawing a question, divide its weight by the sum of all eligible weights.

Suppose you miss F♯ once, moving its strain from 1.5 to 3, and leave it there. Later, the only two eligible candidates for a draw are F♯ and an unseen B. At strain 3 the recovery time is 120 seconds. After two minutes, F♯ has weight $$e^{1.8}(1-e^{-1})\approx 3.82$$. Its chance of coming up next is

$$
\frac{3.82}{3.82+2.46}\approx 61\%.
$$

B can still win that draw.

{% include practice/asrs.html %}

## ARTS

**Adaptive Response-Time-based Sequencing (ARTS)** measures the gap between questions in turns. Its clock advances each time you give a first answer in this exercise. Retries during the same showing and time away from practice leave the clock where it was.

### Priority per turn

Let $$h$$ be the number of intervening first answers since you last answered F♯, and $$T$$ the time in milliseconds you took on that first attempt. Alto uses a 100 ms reference time. The natural logarithm, $$\ln$$, makes a slower correct answer count more, with a diminishing increase for each extra millisecond. [Mettler, Massey, and Kellman, equation 1](https://kellmanlab.psych.ucla.edu/files/mettler_massey_kellman_2016.pdf)

| Last first answer | Priority now |
| --- | --- |
| Unseen | $$1$$ |
| Incorrect | $$2h$$ |
| Correct | $$0.11h\ln\!\left(\frac{\max(T,101)}{100}\right)$$ |

Alto compares eligible questions under the current exercise settings and selects the highest priority. It breaks ties at random.

### A fast and a slow identification

Suppose F♯ and an unseen B are eligible. If you last identified F♯ in **one second**, after three other questions its score is $$0.11\cdot 3\ln(10)\approx 0.76$$. B wins with 1. Had you taken **four seconds**, the same three questions would give F♯ a score of $$0.11\cdot 3\ln(40)\approx 1.22$$, and F♯ would win. If you missed F♯, just one intervening answer would give it a score of 2.

{% include practice/arts.html %}

## SM-2

**SuperMemo 2 (SM-2)** keeps a count of successive successful reviews, the last interval in days, and an **ease factor** $$E$$ for each card. A new card starts with $$E=2.5$$. Alto uses two grades from the SM-2 scale. The first submission in each showing supplies the grade, regardless of response speed. [Original SM-2 specification](https://super-memory.com/english/ol/sm2.htm)

### Review intervals and ease

| First submission | Change to the card | Next review |
| --- | --- | --- |
| Correct (grade 4) | Add one success. Keep the current ease. | 1 day for the first success and 6 days for the second. After that, $$I_{n}=\lceil I_{n-1}E\rceil$$, the previous interval times the ease, rounded up to a whole day. |
| Incorrect (grade 2) | Reset the success count and interval to zero. Set the ease to $$\max(1.3,E-0.32)$$. | 1 minute. A correction during this showing leaves that date in place. |

### Three reviews of F♯

Identify a new F♯ correctly on day 0 and it is due on day 1. Get it right on day 1 and it is due on day 7. A third success on day 7 gives an interval of $$6\cdot 2.5=15$$ days, so the next due date is **day 22**.

{% include practice/sm2.html %}

Suppose instead that you miss F♯ on day 7. Its ease falls to 2.18 and Alto schedules a retry one minute later. Three successive correct reviews from there give gaps of **1, 6, and 14 days**. The shorter third gap comes from the ceiling calculation $$\lceil 6\cdot 2.18\rceil=\lceil 13.08\rceil=14$$.

## FSRS

The **Free Spaced Repetition Scheduler (FSRS)** models the chance you can recall a card as time passes. Alto uses FSRS-6 with its default parameters. A correct first submission earns **Good** and a miss earns **Again**, regardless of response speed. For a new card, Good puts its next learning step ten minutes away and Again puts it one minute away. A miss on a card already in review starts a ten-minute relearning step. [Python FSRS scheduler](https://github.com/open-spaced-repetition/py-fsrs)

### Estimated recall and the review date

FSRS tracks **difficulty** ($$D$$, from 1 to 10) and **stability** ($$S$$, measured in days). A stability of 8 days means the model expects a 90% chance of recall eight days after a review. **Retrievability** ($$R$$) is the predicted chance of recall after $$t$$ whole days. With Alto’s default parameters the curve is approximately

$$
R(t)=\left(1+0.98035\,\frac{t}{S}\right)^{-0.1542}.
$$

The factor 0.98035 is chosen so that $$R(S)=0.90$$. At the 90% target the base review interval therefore equals the updated stability in days. FSRS rounds it to whole days and may vary the scheduled day slightly to spread reviews out.

{% include practice/fsrs.html %}

### A successful review on day eight

Suppose your F♯ card has $$D=5$$ and $$S=8$$ days. On day eight its predicted recall is 0.90. You identify F♯ correctly. For a **Good** review at least a day after the previous one, the stability update has two parts. The factor $$k$$ depends on the card’s current difficulty and stability.

$$
k = e^{1.8722}(11-D)S^{-0.1666}.
$$

$$
S_{\mathrm{new}}=S\left[1+k\left(e^{0.796(1-R)}-1\right)\right].
$$

The quantity in square brackets is about **3.29**, giving a new stability of **26.29 days** and a base interval of **26 days**. The term involving $$R$$ explains why timing matters. If you recall the same card earlier, $$R$$ is higher and the gain in stability is smaller. A miss uses a separate stability update before relearning.

## Review intervals for F♯

Suppose you see a new F♯ card five times in Note Identification. Each row shows your answer and the gap **until the next showing**. For ASRS and ARTS, assume you answer one other question every 10 seconds. After each of those answers, F♯ competes with one unseen card. For SM-2 and FSRS, assume you review F♯ whenever it is due.

| Showing and answer | ASRS (median gap) | ARTS | SM-2 | FSRS (base interval) |
| --- | --- | --- | --- | --- |
| 1. Correct in 4 s | 9 questions (90 s) | 3 questions (30 s) | 1 day | 10 min |
| 2. Correct in 1 s | 19 questions (190 s) | 4 questions (40 s) | 6 days | 2 days |
| 3. Correct in 1 s | 19 questions (190 s) | 4 questions (40 s) | 15 days | 11 days |
| 4. Miss, then correct on retry | 8 questions (80 s) | 1 question (10 s) | 1 min | 10 min |
| 5. Correct in 4 s | 11 questions (110 s) | 3 questions (30 s) | 1 day | 2 days |

After the first answer, ASRS draws F♯ again within nine intervening questions about half the time. ARTS picks it as soon as it outranks the unseen card, after three questions. On the fourth showing, ASRS counts both the miss and the correction. The other three schedulers use the miss as the grade for that showing. FSRS uses base intervals here. In practice, its small random adjustment to longer intervals can also change the dates of later reviews.

## Daily limits

For SM-2 and FSRS, exercise tiles show **due reviews in green** and **new cards in blue**. Due reviews come first. The default allowance for each exercise is **10 new cards and 200 reviews per local day**. Change those numbers in **Settings → Practice**, or open an exercise’s **Daily Limits** submenu and clear **Use global** to override either number for that exercise.

The two algorithms share the day’s allowances and keep separate review dates. Opening a new card uses one introduction slot. If you leave before answering, you can return to that card without using another slot. The allowances reset at local midnight, and overdue reviews remain due.

## Your profile

Alto tracks individual questions, such as identifying F♯4 in treble clef in D major. Changing the order of the answer buttons still counts as practice on the same question.

Every submission is saved under your profile. A question that takes three tries leaves three entries, each with your answer, whether it was correct, and how long it took. Switching algorithms keeps that history. You can switch profiles in the menu (☰) and see your accuracy and response times in [Statistics]({{ '/statistics/' | relative_url }}).
