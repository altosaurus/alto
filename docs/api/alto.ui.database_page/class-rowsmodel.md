---
title: RowsModel
parent: alto.ui.database_page
api_module: alto.ui.database_page
package: alto.ui
permalink: /api/alto.ui.database_page/class-rowsmodel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
RowsModel(
    headers: list[str],
    *,
    rows: list[list[tuple[str, object]]],
    numeric: Iterable[int] = (),
    extras: list[dict] | None = None,
    parent: QObject | None = None,
)
```

{% endraw %}{% include api-source.html name="RowsModel" line=67 %}{% raw %}

</div>

Bases: `QAbstractTableModel`

Rows of (text shown, value to sort by) cells, as a table model.
Numbers are right-aligned.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `headers` | `list of str` | The column headings. |
| `rows` | `list of list of tuple of (str, object)` | The cells: for each, the text to show and the value to sort by. |
| `numeric` | `set of int` | The columns to right-align. |
| `extras` | `list of dict` | Something about each row that is not shown, such as the stored question (see `ROW_ROLE`). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> model = RowsModel(
...     ["Name", "Count"],
...     rows=[[("Ada", "Ada"), ("3", 3)]],
...     numeric={1},
... )
>>> model.rowCount(), model.columnCount()
(1, 2)
>>> (
...     model.data(model.index(0, 1)),
...     model.data(
...         model.index(0, 1), SORT_ROLE
...     ),
... )
('3', 3)
```

**Constructor**

Create the model.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `headers` | `list of str` | The column headings. |
| `rows` | `list of list of tuple of (str, object)` | The cells. Keyword-only. |
| `numeric` | `iterable of int, default ()` | The columns to right-align. Keyword-only. |
| `extras` | `list of dict or None, default None` | Something about each row that is not shown, such as the stored question; empty for each row if None. Keyword-only. |
| `parent` | `QObject or None, default None` | The owner. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RowsModel(
...     ["Name"], rows=[[("Ada", "Ada")]]
... ).extras
[{}]
```

## RowsModel.rowCount

<div class="api-signature" markdown="1">

```python
def rowCount(parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int
```

{% endraw %}{% include api-source.html name="RowsModel.rowCount" line=139 %}{% raw %}

</div>

Return the number of rows.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QModelIndex or QPersistentModelIndex` | Only the top level has rows: an index that is valid gives 0. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | The number of rows. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RowsModel(
...     ["Name"],
...     rows=[
...         [("Ada", "Ada")],
...         [("Ben", "Ben")],
...     ],
... ).rowCount()
2
```

## RowsModel.columnCount

<div class="api-signature" markdown="1">

```python
def columnCount(parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int
```

{% endraw %}{% include api-source.html name="RowsModel.columnCount" line=169 %}{% raw %}

</div>

Return the number of columns.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QModelIndex or QPersistentModelIndex` | Only the top level has columns: an index that is valid gives 0. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | The number of columns. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RowsModel(
...     ["Name", "Count"], rows=[]
... ).columnCount()
2
```

## RowsModel.data

<div class="api-signature" markdown="1">

```python
def data(
    index: QModelIndex | QPersistentModelIndex,
    role: int = Qt.ItemDataRole.DisplayRole,
) -> object
```

{% endraw %}{% include api-source.html name="RowsModel.data" line=196 %}{% raw %}

</div>

Return one piece of a cell for a role.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `index` | `QModelIndex or QPersistentModelIndex` | The cell. |
| `role` | `int, default DisplayRole` | What is wanted: the text to show, the value to sort by (`SORT_ROLE`), the alignment, or the row's hidden details (`ROW_ROLE`). |

**Returns**

| Type | Description |
| --- | --- |
| `object` | The requested data, or None for a role the model does not use. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> model = RowsModel(
...     ["Name", "Count"],
...     rows=[[("Ada", "Ada"), ("3", 3)]],
...     numeric={1},
... )
>>> model.data(model.index(0, 0))
'Ada'
>>> align = Qt.ItemDataRole.TextAlignmentRole
>>> model.data(
...     model.index(0, 1), align
... ) != model.data(
...     model.index(0, 0), align
... )  # numbers are right-aligned
True
```

## RowsModel.headerData

<div class="api-signature" markdown="1">

```python
def headerData(
    section: int,
    orientation: Qt.Orientation,
    role: int = Qt.ItemDataRole.DisplayRole,
) -> object
```

{% endraw %}{% include api-source.html name="RowsModel.headerData" line=272 %}{% raw %}

</div>

Return a column heading.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `section` | `int` | The column. |
| `orientation` | `Qt.Orientation` | Only horizontal headings are used. |
| `role` | `int, default DisplayRole` | Only the display text is given. |

**Returns**

| Type | Description |
| --- | --- |
| `object` | The heading, or None for anything else. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> model = RowsModel(
...     ["Name", "Count"], rows=[]
... )
>>> model.headerData(
...     1, Qt.Orientation.Horizontal
... )
'Count'
```
{% endraw %}
