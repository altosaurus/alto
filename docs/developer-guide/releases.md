---
title: Releases
parent: developer-guide
order: 5
permalink: /developer-guide/releases/
---
{% assign revision = site.source_revision | default: 'main' -%}
{% assign source = 'https://github.com/altosaurus/alto/blob/' | append: revision -%}
A maintainer starts the Release workflow on the versioned `main` commit to build a release candidate. GitHub Actions checks the changelog entry and the update signing key before starting the three native builds. Each runner then packages its own Python interpreter, Qt libraries, and executable for the operating system and processor that will run Alto. [Release workflow]({{ source }}/.github/workflows/release.yml)

## Shared PyInstaller build

Each build script uses uv and the committed lockfile to install the runtime libraries and packaging tools in a fresh environment. The runners share the CPython patch specified in `packaging/python-version`. Each script builds Alto with the locked setuptools backend, then runs PyInstaller with the same recipe, `packaging/alto.spec`. The recipe starts at `packaging/launcher.py`, which calls `alto.__main__.main()`, the same function that starts the app when you run `python -m alto`. [Launcher]({{ source }}/packaging/launcher.py) · [PyInstaller recipe]({{ source }}/packaging/alto.spec)

PyInstaller follows the launcher’s imports and bundles Alto’s Python bytecode into a native executable that starts the bundled interpreter. The recipe collects the libraries and data the program loads at runtime, including PySide6, Qt plugins, notation fonts, and sound recordings. A learner can run the resulting bundle without installing Python or Qt. The last packaging step determines how that bundle reaches the learner.

## Linux archive

On Ubuntu 22.04, `build-linux.sh` produces an x86-64 folder with the `alto` executable beside an `_internal/` directory containing its runtime. Building on this Ubuntu version sets the minimum glibc version the executable needs. The script launches the frozen app offscreen and checks that Qt’s X11 plugin can find its shared libraries. [Linux build script]({{ source }}/scripts/build-linux.sh)

The script packs the folder, icons, notices, and `install.sh` into **`alto-<version>-linux-x86_64.tar.gz`**. After extraction, `sh install.sh install` copies the app to `~/.local/opt/alto` by default, links the command at `~/.local/bin/alto`, and adds Alto to the application menu. [Linux install script]({{ source }}/packaging/linux/install.sh)

## Windows installer

On Windows, `build-windows.ps1` freezes the app into a folder containing `alto.exe` and its runtime. Inno Setup reads `packaging/windows/alto.iss` and compresses that folder into **`alto-<version>-windows-x64-setup.exe`**. Running the installer places the app under `%LOCALAPPDATA%\Programs\Alto` by default and creates a Start menu shortcut to `alto.exe`. If the required Visual C++ runtime is missing or too old, the installer downloads Microsoft’s redistributable and verifies its signature before running it. [Windows build script]({{ source }}/scripts/build-windows.ps1) · [Inno Setup recipe]({{ source }}/packaging/windows/alto.iss)

The build tests installation, launch, and removal. The release workflow then signs the finished installer with Microsoft Artifact Signing and verifies its timestamped Authenticode signature.

## macOS disk image

On an Apple Silicon Mac, PyInstaller assembles `Alto.app`, an application bundle with the launcher in `Contents/MacOS/alto`, its frameworks, and its resources. The release build uses a Developer ID Application certificate to sign the app. The build script checks its arm64 architecture and signature, runs its self-test, and opens the app before packaging it. [macOS build script]({{ source }}/scripts/build-macos.sh)

The script uses `hdiutil` to create **`alto-<version>-macos-arm64.dmg`** containing `Alto.app` and a shortcut to Applications, then signs the disk image. The workflow submits the image to Apple for notarization, attaches the returned ticket, and checks that Gatekeeper accepts both the image and the app inside it. The learner opens the image and drags Alto into Applications. [macOS packaging workflow]({{ source }}/.github/workflows/package.yml)

## Published release

The candidate contains all three verified downloads, the corresponding Qt, PySide/Shiboken, and Linux source archives, the source commit, and each platform’s installed Python package versions. After review, a maintainer pushes an annotated version tag naming the candidate artifact ID and ZIP checksum. The publisher checks the tag, commit, and hashes, stages the files in a GitHub draft, and verifies the uploaded hashes before publishing. The release includes `SHA256SUMS` and its Ed25519 signature, `SHA256SUMS.sig`. Alto’s updater verifies the signature first, then uses the authenticated checksum to verify the download for the learner’s platform. [Release downloads](https://github.com/altosaurus/alto/releases) · [Maintainer checklist]({{ '/development/#pre-release-checklist' | relative_url }})
