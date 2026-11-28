---
title: Getting started
nav_order: 2
nav_group: Using Alto
permalink: /getting-started/
---
{% include os-icons.html logos_only=true %}

<fieldset class="os-picker" id="os-picker">
  <legend>Operating system</legend>
  <label><input type="radio" name="guide-os" value="linux" checked><span><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="#os-linux"/></svg>Linux</span></label>
  <label><input type="radio" name="guide-os" value="windows"><span><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="#os-windows"/></svg>Windows</span></label>
  <label><input type="radio" name="guide-os" value="macos"><span><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="#os-apple"/></svg>Mac</span></label>
</fieldset>

{% assign release = 'https://github.com/altosaurus/alto/releases' %}
{% assign v = site.app_version %}
{% capture mac_file %}{% include macos-download.html %}{% endcapture %}
{% if v != empty and v %}
{% assign assets = release | append: '/download/v' | append: v | append: '/' %}
{% assign linux_download = assets | append: 'alto-' | append: v | append: '-linux-x86_64.tar.gz' %}
{% assign windows_download = assets | append: 'alto-' | append: v | append: '-windows-x64-setup.exe' %}
{% endif %}
<span id="what-you-need"></span><span id="download-and-install"></span>

## Install and run

<div data-platforms="linux" markdown="1">

### Linux download
{: .no-toc}

1. [Download Alto for Linux]({{ linux_download | default: release }}) for an x86-64 desktop. The archive includes Python and Qt.
2. Extract the archive, open a terminal in the extracted folder, and run `sh install.sh install`.
3. Open **Alto** from your application menu.

The installer puts Alto in `~/.local/opt/alto` and creates the command `~/.local/bin/alto` for your account.
For other processor architectures, see [Running from a source checkout](#running-from-a-source-checkout).

</div>

<div data-platforms="windows" markdown="1">

### Windows installer
{: .no-toc}

> **Windows installer signature.** Alto 0.0.2 and earlier shipped unsigned. For releases that list a signed installer,
> right-click the downloaded file and open **Properties → Digital Signatures → Details** to check its publisher.
> [Help with Windows installation warnings](#windows-installer-troubleshooting)
{: role="note" aria-label="Windows installer notice"}

1. [Download the 64-bit Windows installer]({{ windows_download | default: release }}) for Windows 10 or 11.
2. Open the downloaded `.exe` and follow the setup prompts.
3. Open **Alto** from the Start menu.

The installer includes Python and Qt and installs Alto for your account.

</div>

<div data-platforms="macos" markdown="1">

{% if mac_file != empty %}
### Apple Silicon disk image
{: .no-toc}

1. In **Apple menu → About This Mac**, check the **Chip** field. The disk image runs on Macs with an Apple M-series chip.
2. [Download the disk image]({{ assets }}{{ mac_file }}) and double-click it in Finder.
3. Drag **Alto** into **Applications**, eject the disk image, and open **Alto** from Applications.

{% endif %}
### Mac source installation
{: .no-toc}

You can also run Alto from source, including on Intel Macs.
With Git and Python 3.11 or newer installed, open **Terminal** and run:

{% include source-install-unix.md %}

To open Alto again, run `.venv/bin/python -m alto` from the same `alto` folder.

</div>

<div data-platforms="linux windows{% if mac_file != empty %} macos{% endif %}" markdown="1">

### Check your download
{: .no-toc}

Download `SHA256SUMS` from the same [release]({{ release }}) as your download. It lists the SHA-256 checksum of each file.

<div data-platforms="linux" markdown="1">
In the folder containing the archive and `SHA256SUMS`, run:

```bash
sha256sum --check --ignore-missing SHA256SUMS
```

Look for `OK` after the archive name.
</div>

{% if mac_file != empty %}
<div data-platforms="macos" markdown="1">
In Terminal, run `shasum -a 256 "{{ mac_file }}"` in the download folder. Compare the result with the line for the disk image in `SHA256SUMS`.
</div>
{% endif %}

<div data-platforms="windows" markdown="1">
Open PowerShell in the folder containing the installer. Use the exact name of the file you downloaded:

```powershell
Get-FileHash ".\alto-{{ v | default: '<version>' }}-windows-x64-setup.exe" -Algorithm SHA256
```

Open `SHA256SUMS` in Notepad and find the line naming that same `.exe`. Every character in its checksum should match
the **Hash** printed by PowerShell (uppercase and lowercase are equivalent). If they differ, discard the installer
and download it again from the official Alto release.
</div>

</div>

<div data-platforms="windows" markdown="1">

### Windows installer troubleshooting
{: .no-toc}

#### Edge says the download is uncommon

An uncommon-download warning means Microsoft Edge has little download history for that file. Check that you started
from the **altosaurus/alto** GitHub release. If you choose to keep the file, [check its checksum](#check-your-download)
before opening it. If the browser or antivirus identifies a specific threat, stop and leave the file blocked.
[Microsoft’s SmartScreen guidance](https://learn.microsoft.com/en-us/windows/security/threat-protection/microsoft-defender-smartscreen/microsoft-defender-smartscreen-overview)

#### “Windows protected your PC” or “Unknown publisher”

If SmartScreen calls Alto an unrecognized app, select **More info** to see the filename and publisher. For releases that list a signed
installer, check that Windows reports a valid signature under **Properties → Digital Signatures → Details** and that the
checksum matches the release. If Windows reports **Unknown publisher** for a signed release, cancel setup and check the
download. For the unsigned 0.0.2 and earlier installers, verify the checksum before deciding whether to run setup.
[How SmartScreen checks app reputation](https://learn.microsoft.com/windows/apps/package-and-deploy/smartscreen-reputation)

#### Windows blocks the installer with no “Run anyway” option

On a work or school PC, your organization may control which apps can run. Give your IT team the Alto release link
and the exact message so they can review it. If Windows 11 names **Smart App Control**, it has no per-app exception.
Keep the protection enabled while you check the installer’s signature and the release download. [Microsoft’s Smart App Control FAQ](https://support.microsoft.com/en-gb/windows/security/threat-malware-protection/smart-app-control-frequently-asked-questions)

#### Setup stops at “Microsoft Visual C++ Runtime”

Alto needs Microsoft’s **x64 Visual C++ Redistributable**. If setup asks for administrator permission for that component,
check that the prompt identifies **Microsoft Corporation** as the publisher. If its download fails or you’re installing
offline, get the x64 package from Microsoft, install it, restart if prompted, then run Alto’s installer again.
[Microsoft’s runtime download](https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist)

If you’re still stuck, include the Alto installer filename, your Windows version, and the exact message when you
[report an installation issue](https://github.com/altosaurus/alto/issues).

</div>

<div data-platforms="linux" markdown="1">

### Install as a program (Linux)
{: .no-toc}

To install from GitHub with [uv](https://docs.astral.sh/uv/), run `sh scripts/alto-install.sh install` from the repository.
Open Alto from the application menu. Use `sh scripts/alto-install.sh update` to update the program and refresh its menu entry
and icon. The in-app updater can update this installation too. Choose **Follow the main branch** in **Settings → Updates**
to get changes before release. Packaged installations follow releases.
</div>

<div data-platforms="linux windows" markdown="1">

### Running from a source checkout
{: .no-toc}

For development, install Git and Python 3.11 or newer. Alto installs PySide6 and the other dependencies into the virtual
environment. Run the following commands, then use `git pull` from the checkout to get source updates.

<div data-platforms="linux" markdown="1">
{% include source-install-unix.md %}
</div>

<div data-platforms="windows" markdown="1">
```powershell
git clone https://github.com/altosaurus/alto.git
cd alto
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m alto
```
</div>

</div>

## Updating Alto

Open **☰ → Tools** and choose **Check for updates…** to check manually. Alto also checks for releases when the main grid is active,
up to once every 24 hours. **Settings → Updates** shows your version and lets you turn automatic checks off.

<div data-platforms="linux windows" markdown="1">
For a packaged installation, choose **Yes** to download an offered release, **No** for a reminder after 24 hours, or
**Don’t remind me again** to skip it. Alto verifies the signature on `SHA256SUMS` with its built-in public key and
checks the package against the signed list before installation. Press **OK** when prompted to restart.
</div>

<div data-platforms="linux" markdown="1">
You can also unpack a newer archive and run `sh install.sh install` again. A failed installation keeps your previous
copy. If you run Alto straight from the unpacked folder, download the new archive yourself.
</div>

<div data-platforms="windows" markdown="1">
You can also run a newer Windows installer to update your copy.
</div>

<div data-platforms="macos" markdown="1">
{% if mac_file != empty %}
For the Apple Silicon app, quit Alto and drag the app from the new disk image into **Applications**. Choose **Replace** when prompted.

{% endif %}
For a source installation, quit Alto and run these commands in Terminal from your `alto` folder:

```bash
git pull
.venv/bin/python -m pip install -e .
.venv/bin/python -m alto
```
</div>

## Uninstalling Alto

<div data-platforms="linux" markdown="1">
For the Linux download, run `sh install.sh uninstall` from the extracted folder. For the uv installation, run
`sh scripts/alto-install.sh uninstall` from the repository. Both commands remove the program and its menu entry
and keep your practice history and settings. Add `--purge` to delete them too.
</div>

<div data-platforms="windows" markdown="1">
Open **Settings → Apps**, select **Alto**, and choose **Uninstall**. The uninstaller asks whether to also remove your
practice history and settings.
</div>

<div data-platforms="macos" markdown="1">
Quit Alto. {% if mac_file != empty %}For a disk image installation, move **Alto** from **Applications** to the Trash. {% endif %}For a source installation, move the cloned `alto` folder, including its `.venv`, to the Trash.
Your practice history is stored separately in `~/Library/Application Support/Alto/alto.db`.
</div>

To keep a copy of your practice history and settings, choose **Export backup…** in Alto before uninstalling. [Database]({{ '/data/' | relative_url }})

## First launch

The first time you open Alto it asks you to create a profile.

{% include shot.html src="home.png" alt="The home screen after creating a profile" %}

Type a name and press **Create profile**. There is no password, and the name is only a label that keeps your history
separate from anyone else who uses the same computer. Next time Alto opens straight into the profile you used last.

To switch to someone else, or add another profile, open the menu (☰) and choose **Profile**.

Alto includes the default Finale Maestro notation font. To use the optional Noto Music style, install the Noto Music
font on your system and choose it in [Settings]({{ '/settings/' | relative_url }}).

## Your first session

1. Click an exercise on the home screen.
2. Follow the prompt. Click an answer button or use the shortcut in its tooltip. For a construction question, place the requested note or sign.
3. A correct answer turns green. With the default scheduler, try a missed question again. With SM-2 or FSRS, a miss moves the card to the learning queue for a later retry.
4. The counter at the top shows how many you have right and your current streak.

The **Exercises / Lessons** control at the top left selects what to browse. Alto starts with tiles. **Navigation Pane**
opens the matching list on the left; before you start an activity, the main panel says "Select an exercise to begin." or
"Select a lesson to begin." Use the separate **Tiles** grid button to return to tiles without losing your place.

The icon-only **Exercises / Lessons** pair sits at the top left, followed by an open/close navigation-pane button, a divider,
and a separate grid button for returning to tiles. Hover over an icon to see its name. The search field below filters the
selected section by name, description or category, and follows the sidebar's width. On the tile grid or during an exercise, click the funnel icon
at the right end of the search row to open the filter sidebar. Click it again to collapse the sidebar and keep your filters.
The sidebar opens on the right with every category expanded. Check or clear a category to include or
hide its activities, or check individual exercises or lessons. The tiles and navigation list show the same matches.
A dash means some activities in a category are checked. **All categories** selects or clears the whole list.

Turn on **Shuffle exercises**, just left of the funnel, to practice the exercises in your filtered list. After each
right or wrong answer, Alto prefers an exercise from another category. If the other available exercises are in the
current category, it picks one of those. For example, selecting only **Note Identification** and **Keyboard Note
Identification** makes them alternate when both have questions available. Your **Next Question** setting controls when
the switch happens. With **Wait**, click **Next** after reviewing your answer. You can change the filters while answering
a question. Shuffle uses the updated list for the next question and returns to the tiles if the list is empty.
Click the highlighted shuffle icon again to turn it off.

{% include shot.html src="filtered-practice.png" alt="Exercise grid with two checked note exercises in the right sidebar and the blue shuffle icon above it" caption="Only the checked exercises appear in the grid. The New, Learn, and Due totals at the left count cards from these two exercises." %}

During an exercise or lesson, **Exercises / Lessons** switches the list while keeping your activity on screen. Selecting
an item starts or resumes it. The top-left pane button hides and shows the list without leaving your activity.
**Statistics** and **Browse database** are at the top right. The sliders button opens the exercise's own settings, and **?**
explains it.

{% include shot.html src="filtered-exercise.png" alt="Note Identification with two exercises in the navigation pane, Shuffle enabled, and the Easy, Good, and Hard intervals beside the staff" caption="The navigation pane lists the same two exercises as the filtered grid. The blue shuffle button stays available while you practice." %}

## Glossary

Open **Glossary** in the top toolbar to look up a term. Search for *minor*, for example, and select **harmonic minor scale**. You can hear the scale, try another example, or open a related exercise from the same page.

{% include shot.html src="glossary.png" alt="Glossary search results for minor with harmonic minor scale selected and its notes labeled on a staff" caption="In A harmonic minor, listen for the three half steps from F to G♯ and the half step from G♯ to A." %}

## Running the tests

From a source checkout, install the development dependencies and run the test suite.

<div data-platforms="linux macos" markdown="1">
```bash
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
```
</div>

<div data-platforms="windows" markdown="1">
```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```
</div>

<script src="{{ '/assets/js/downloads.js' | relative_url }}?v={{ site.time | date: '%s' }}" defer></script>
