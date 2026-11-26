---
title: AnswerBank
parent: alto.ui.answer_bank
api_module: alto.ui.answer_bank
package: alto.ui
permalink: /api/alto.ui.answer_bank/class-answerbank/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
AnswerBank(
    parent: QWidget | None = None,
    *,
    show_all_rows: bool = False,
)
```

{% endraw %}{% include api-source.html name="AnswerBank" line=26 %}{% raw %}

</div>

Bases: `QScrollArea`

Wrap existing answer buttons to fit the available width and scroll
long lists.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `buttons` | `list of QAbstractButton` | The answer buttons in their display and keyboard navigation order. |
| `content` | `QWidget` | The grid's content widget. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> bank = AnswerBank()
>>> bank.buttons
[]
```

**Constructor**

Create a bank that can show all rows or scroll longer lists.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns the bank. |
| `show_all_rows` | `bool, default False` | Let the bank grow to fit every row. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     AnswerBank().horizontalScrollBarPolicy()
...     == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
... )
True
```

## AnswerBank.set_buttons

<div class="api-signature" markdown="1">

```python
def set_buttons(
    buttons: list[QAbstractButton],
    *,
    positions: list[tuple[int, int]] | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="AnswerBank.set_buttons" line=93 %}{% raw %}

</div>

Display answer buttons in a stable order.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `buttons` | `list of QAbstractButton` | The buttons to arrange. Their caller owns answer handling. |
| `positions` | `list of tuple of (int, int) or None` | Optional row and column for each button. Each row wraps independently when space is limited. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtWidgets import QPushButton
>>> bank = AnswerBank()
>>> bank.set_buttons(
...     [QPushButton("m3"), QPushButton("P5")]
... )
>>> len(bank.buttons)
2
```

## AnswerBank.resizeEvent

<div class="api-signature" markdown="1">

```python
def resizeEvent(event: QResizeEvent) -> None
```

{% endraw %}{% include api-source.html name="AnswerBank.resizeEvent" line=191 %}{% raw %}

</div>

Rewrap the buttons when the exercise or settings pane changes
width.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QResizeEvent` | The resize notification. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> bank = AnswerBank()
>>> bank.resize(300, 200)
>>> bank.width()
300
```
{% endraw %}
