---
title: alto.updates
parent: api
package: alto
order: 5
permalink: /api/alto.updates/
---
{% raw %}
Whether an installed copy of Alto can update itself, and the commands that check for a newer version and install it.

Alto is installed as a program with `scripts/alto-install.sh`, which uses `uv tool` to install it from a git address. The
installed package records that address and the commit it was built from, so the newest commit at the address can be compared
with it. This module only decides and describes; `alto.ui.update_flow` runs the commands and asks the questions.

**Examples**

```pycon
>>> short("b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe")
'b6e2091'
```

## Source

```python
Source(
    url: str,
    commit: str,
    ref: str = 'HEAD',
)
```

Where an installed copy of Alto came from.

**Attributes**

- `url` (*str*): The git address it was installed from.
- `commit` (*str*): The commit it was built from.
- `ref` (*str*): The branch or tag it follows; "HEAD", the address's default branch, unless the install named one.

**Examples**

```pycon
>>> Source("https://github.com/altosaurus/alto.git", commit="b6e2091").ref
'HEAD'
```

## short

```python
def short(commit: str) -> str
```

Shorten a commit id to the seven characters people use for it.

**Parameters**

- `commit` (*str*): The full commit id.

**Returns**

- *str*: Its first seven characters.

**Examples**

```pycon
>>> short("b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe")
'b6e2091'
```

## parse_direct_url

```python
def parse_direct_url(text: str) -> Source | None
```

Read where a package was installed from, out of the `direct_url.json` that the installer leaves with it.

**Parameters**

- `text` (*str*): The contents of the file.

**Returns**

- *Source or None*: The git address, the commit and the ref, or None if the package was not installed from a git address (a copy that runs from a source folder has a folder there instead).

**Examples**

```pycon
>>> parse_direct_url('{"url": "https://example.org/a.git", "vcs_info": {"vcs": "git", "commit_id": "abc1234"}}')
Source(url='https://example.org/a.git', commit='abc1234', ref='HEAD')
>>> named = '{"url": "https://x.org/a.git", "vcs_info": {"vcs": "git", "commit_id": "abc1234", "requested_revision": "dev"}}'
>>> # noinspection PyUnresolvedReferences
>>> parse_direct_url(named).ref
'dev'
>>> parse_direct_url('{"url": "file:///home/me/alto", "dir_info": {"editable": true}}') is None
True
>>> parse_direct_url("not json") is None
True
```

## installed_source

```python
def installed_source() -> Source | None
```

Say where the Alto that is running was installed from.

**Returns**

- *Source or None*: Its git address and commit, or None if it was not installed from a git address.

**Examples**

```pycon
>>> source = installed_source()
>>> source is None or len(source.commit) == COMMIT_LENGTH
True
```

## is_tool_install

```python
def is_tool_install(
    *,
    prefix: Path | None = None,
) -> bool
```

Say whether Alto is running from an environment that `uv tool` made, which is what the install script makes.

**Parameters**

- `prefix` (*Path or None, default None*): The environment to look at; the one that is running if None. Keyword-only.

**Returns**

- *bool*: True if the environment has the receipt that `uv tool install` leaves in it.

**Examples**

```pycon
>>> is_tool_install(prefix=Path("/nowhere"))
False
```

## updatable

```python
def updatable(
    source: Source | None,
    *,
    tool: bool,
) -> Source | str
```

Decide whether a copy of Alto can update itself, and say why not if it cannot.

**Parameters**

- `source` (*Source or None*): Where it was installed from, if it was installed from a git address.
- `tool` (*bool*): Whether it runs from an environment that `uv tool` made. Keyword-only.

**Returns**

- *Source or str*: The source, if the copy can update itself; otherwise a sentence that says why it cannot.

**Examples**

```pycon
>>> here = Source("https://example.org/a.git", commit="abc1234")
>>> updatable(here, tool=True) is here
True
>>> updatable(None, tool=True) == SOURCE_FOLDER
True
>>> updatable(here, tool=False) == NOT_BY_SCRIPT
True
```

## find_program

```python
def find_program(
    name: str,
    *,
    home: Path | None = None,
) -> str | None
```

Find a program to run, also in the places the installers put them, which a program started from the dock may not search.

**Parameters**

- `name` (*str*): The program's name, such as "git" or "uv".
- `home` (*Path or None, default None*): The home folder to look in besides the search path; the user's own if None. Keyword-only.

**Returns**

- *str or None*: Its path, or None if it is nowhere to be found.

**Examples**

```pycon
>>> find_program("no-such-program-anywhere") is None
True
```

## check_command

```python
def check_command(
    source: Source,
    *,
    git: str,
) -> tuple[str, list[str]]
```

Give the command that asks the address Alto came from for its newest commit.

**Parameters**

- `source` (*Source*): Where the running copy came from.
- `git` (*str*): The path of the `git` program. Keyword-only.

**Returns**

- *tuple of str and list of str*: The program and its arguments.

**Examples**

```pycon
>>> check_command(Source("https://example.org/a.git", commit="abc1234"), git="git")
('git', ['ls-remote', 'https://example.org/a.git', 'HEAD'])
```

## upgrade_command

```python
def upgrade_command(
    *,
    uv: str,
) -> tuple[str, list[str]]
```

Give the command that installs the newest version of Alto over the installed one.

**Parameters**

- `uv` (*str*): The path of the `uv` program. Keyword-only.

**Returns**

- *tuple of str and list of str*: The program and its arguments.

**Examples**

```pycon
>>> upgrade_command(uv="uv")
('uv', ['tool', 'upgrade', 'alto'])
```

## parse_ls_remote

```python
def parse_ls_remote(text: str) -> str | None
```

Read the commit id out of what `git ls-remote` printed.

**Parameters**

- `text` (*str*): The output: a line for each ref, each a commit id, a tab and the ref's name.

**Returns**

- *str or None*: The commit id on the first line, or None if there is none (the ref does not exist, or git printed an error).

**Examples**

```pycon
>>> parse_ls_remote("b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe\tHEAD\n")
'b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe'
>>> parse_ls_remote("") is None, parse_ls_remote("fatal: repository not found") is None
(True, True)
```
{% endraw %}
