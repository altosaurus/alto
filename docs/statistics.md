---
title: Statistics
nav_order: 5
nav_group: Using Alto
permalink: /statistics/
---
Open **Statistics** using the chart button at the upper right of the main window. They always show the active
profile's own answers. Use **← Back** or <kbd>Esc</kbd> to return to the page you came from.

## Filters

- **Exercise:** all exercises, or any one of them.
- **Timeframe:** today, the last 7, 30 or 90 days, the last year, or all time.

{% include shot.html src="stats.png" alt="Statistics for the last 30 days with Week selected in the upper-right corner of the Questions answered chart" caption="Each bar counts a week of questions. The neighboring accuracy chart still shows one point per day." %}

Choose **Response-time distribution…** below the speed chart to see the recent times used for automatic grading. The tool opens on the selected exercise and uses its latest 100 eligible answers across timeframes. [Response-time grading]({{ '/practice/' | relative_url }}#response-time-grading).

## What you see

- **Summary tiles:** questions answered, how often the first answer was right, the typical time to a first answer,
  attempts per question, days practiced, and time spent practicing. A single answer counts for at most two minutes of
  practice time, so leaving the app open does not inflate it.
- **Questions answered** shows first-try correct answers in green and misses in red. Use **Granularity** in the chart’s upper-right corner to
  choose **Hour**, **Day**, **Week**, or **Month** for each bar. **Auto** picks a period based on the timeframe.
  If your choice produces more than 48 bars, scroll left beneath the chart to see earlier periods.
- **Right on the first try:** your first-try accuracy over time. Days with no answers leave a gap.
- **Typical time to first answer:** the median, over time, so a single slow answer does not distort it.
- **By exercise:** accuracy, number of questions and typical time for each exercise.
- **Reviews:** a calendar of the last 12 months, a square per day (weeks run left to right, Monday at the top), darker
  the more questions you answered. Use the outward diagonal arrows to separate the months and the inward arrows to close the gaps. Hover a square for the exact count. It follows the exercise filter but ignores the
  timeframe.
- **Questions that need practice:** the questions with the highest strain, how often you missed them, and how many times you have answered them.

## Pointing and clicking

Every chart responds to the pointer. **Hover** a bar, a point, an exercise row or a calendar day and it brightens while the
rest of the chart fades back, with its numbers in a tooltip. **Click** one and the answers behind it are listed in a panel under the charts:

- a bar or point lists the answers given during its hour, day, week, or month within the selected timeframe;
- a row of the by-exercise chart lists the answers to that exercise within the timeframe;
- a square of the calendar lists the answers given on that day.

The clicked element stays bright and the rest stay faded while the panel is open. Click it again, or press **Close**, to put the panel away; it
also closes when you change the exercise or the timeframe, because its numbers would no longer match. Periods and days with no
answers cannot be clicked. The list has the same columns as the [database browser]({{ '/data/' | relative_url }}#browsing-the-database), sorts when you click a heading, and
**double-clicking** a row previews the question. It shows the newest 500 answers, and says when there are more.

Double-click any cell in **Questions that need practice** to open the saved question and its answer.
The **Question Statistics** button on the card opens that question’s speed and accuracy graphs.

{% include shot.html src="stats-heatmap.png" alt="A calendar heatmap of the last twelve months, a square per day in shades of green with a small gap between months, above the list of questions that need practice" caption="The Reviews calendar: a year of practice at a glance. Days without reviews use the lightest shade, and the darkest squares are your busiest days." %}

A question counts as **right** only if your first answer was right. That is the same rule the
[practice scheduler]({{ '/practice/' | relative_url }}) uses, so the numbers match what Alto thinks about your progress.
