---
title: alto.learning.response_times
parent: api
package: alto.learning
permalink: /api/alto.learning.response_times/
---
{% raw %}
Rolling response times for one learner and exercise.

## ResponseTimes

```python
ResponseTimes(
    times: tuple[int, ...],
    easy_percent: int,
    hard_percent: int,
)
```

Sorted millisecond timings and the profile's fastest and slowest
tail percentages.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sample = ResponseTimes(
...     tuple(range(1, 101)), 15, 15
... )
>>> (
...     sample.grade(1).name,
...     sample.grade(50).name,
...     sample.grade(100).name,
... )
('Easy', 'Good', 'Hard')
```

### ResponseTimes.ready

```python
@property
def ready() -> bool
```

Check whether this exercise has enough eligible answers.

**Returns**

- *bool*: True once at least 40 previous answers are available.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ResponseTimes((), 15, 15).ready
False
```

### ResponseTimes.percentile

```python
def percentile(percent: int) -> float
```

Interpolate a percentile between adjacent observations in a
nonempty sample.

**Parameters**

- `percent` (*int*): Percentile from zero to 100.

**Returns**

- *float*: Elapsed milliseconds at the requested percentile.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ResponseTimes(
...     (1000, 2000), 15, 15
... ).percentile(25)
1250.0
```

### ResponseTimes.grade

```python
def grade(milliseconds: int) -> Rating
```

Grade a correct first answer against earlier answers to this
exercise.

**Parameters**

- `milliseconds` (*int*): Eligible duration, or zero if the timing is unavailable.

**Returns**

- *Rating*: Hard for slow answers, Easy for fast answers, and Good for ties or missing timings.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ResponseTimes((1000,) * 40, 15, 15).grade(
...     1000
... ).name
'Good'
```
{% endraw %}
