---
title: alto.ui.answer_bank
parent: api
package: alto.ui
order: 24
permalink: /api/alto.ui.answer_bank/
---
{% raw %}
A responsive, scrollable grid for large banks of answer buttons.

**Examples**

```pycon
>>> AnswerBank().maximumHeight()
240
```

## AnswerBank

```python
AnswerBank(parent: QWidget | None = None)
```

Bases: `QScrollArea`

Wrap existing answer buttons to fit the available width and scroll long lists.

**Attributes**

- `buttons` (*list of QAbstractButton*): The answer buttons in their display and keyboard navigation order.
- `content` (*QWidget*): The grid's content widget.

**Examples**

```pycon
>>> bank = AnswerBank()
>>> bank.buttons
[]
```

**Constructor**

Create a bank that shows at most four rows before scrolling.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns the bank.

**Constructor examples**

```pycon
>>> AnswerBank().horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
True
```

### AnswerBank.set_buttons

```python
def set_buttons(buttons: list[QAbstractButton]) -> None
```

Display answer buttons in a stable order.

**Parameters**

- `buttons` (*list of QAbstractButton*): The buttons to arrange. Their caller owns answer handling.

**Examples**

```pycon
>>> from PySide6.QtWidgets import QPushButton
>>> bank = AnswerBank()
>>> bank.set_buttons([QPushButton("m3"), QPushButton("P5")])
>>> len(bank.buttons)
2
```

### AnswerBank.resizeEvent

```python
def resizeEvent(event: QResizeEvent) -> None
```

Rewrap the buttons when the exercise or settings pane changes width.

**Parameters**

- `event` (*QResizeEvent*): The resize notification.

**Examples**

```pycon
>>> bank = AnswerBank()
>>> bank.resize(300, 200)
>>> bank.width()
300
```
{% endraw %}
