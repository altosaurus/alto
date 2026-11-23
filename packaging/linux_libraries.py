#!/usr/bin/env python3
"""
Write the notices for the system libraries in the Linux download, and collect the sources of the copyleft ones.

PyInstaller copies the system libraries that Python and Qt link to from the machine that builds the download, so the
download contains Ubuntu's builds of them. For each library this script finds the Debian package it came from, checks that
the copy is the package's file unchanged, and installs the package's copyright file under ``licenses/Linux``. For the
packages in ``SOURCE_PACKAGES`` it downloads Ubuntu's source package of the exact version (the upstream source and Ubuntu's
changes) from Launchpad and packs them in one archive, published beside the download. A library whose source package is in
neither list stops the build, so a new one is looked at before it ships.

Run on the build machine, after PyInstaller:

    python packaging/linux_libraries.py <frozen folder> <library list> <sources archive>
"""

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
from dataclasses import (
    KW_ONLY,
    dataclass,
)
from importlib.metadata import version
from pathlib import Path

# Source packages under the LGPL or GPL (in whole, in part, or as one choice the copyright file gives), whose source is
# published with the download. GCC's runtime libraries are GPL-3 with the GCC Runtime Library Exception.
SOURCE_PACKAGES = frozenset(
    {
        "apparmor",
        "dbus",
        "flac",
        "gcc-12",
        "glib2.0",
        "keyutils",
        "libasyncns",
        "libgcrypt20",
        "libgpg-error",
        "libselinux",
        "libsndfile",
        "pulseaudio",
        "systemd",
        "util-linux",
    },
)
# Source packages under permissive licenses (MIT, BSD, zlib, Apache, public domain, or one of these as a choice), whose
# copyright file is installed.
NOTICE_PACKAGES = frozenset(
    {
        "brotli",
        "bzip2",
        "e2fsprogs",
        "expat",
        "fontconfig",
        "freetype",
        "krb5",
        "libbsd",
        "libcap2",
        "libffi",
        "libmd",
        "libogg",
        "libpng1.6",
        "libvorbis",
        "libx11",
        "libxau",
        "libxcb",
        "libxdmcp",
        "libxkbcommon",
        "libzstd",
        "lz4",
        "openssl",
        "opus",
        "pcre2",
        "pcre3",
        "sqlite3",
        "xcb-util",
        "xcb-util-cursor",
        "xcb-util-image",
        "xcb-util-keysyms",
        "xcb-util-renderutil",
        "xcb-util-wm",
        "xz-utils",
        "zlib",
    },
)
LAUNCHPAD = "https://api.launchpad.net/1.0/ubuntu/+archive/primary"
CURL = [
    "curl",
    "--fail",
    "--silent",
    "--show-error",
    "--location",
    "--retry",
    "3",
    "--connect-timeout",
    "30",
]


@dataclass(frozen=True)
class Library:
    """
    One system library in the download and the Debian package it came from.

    Parameters
    ----------
    name : str
        The file name in the download's ``_internal`` folder, such as ``libglib-2.0.so.0``.
    package : str
        The binary package that installed it, such as ``libglib2.0-0``.
    version : str
        That package's version.
    source : str
        The source package it was built from, such as ``glib2.0``.
    source_version : str
        The source package's version.
    sha256 : str
        The SHA-256 of the file.
    """

    name: str
    _: KW_ONLY
    package: str
    version: str
    source: str
    source_version: str
    sha256: str


def sha256(path: Path) -> str:
    """
    Return the SHA-256 of a file.

    Parameters
    ----------
    path : Path
        The file.

    Returns
    -------
    str
        The hexadecimal digest.

    Examples
    --------
    >>> import tempfile
    >>> with tempfile.TemporaryDirectory() as folder:
    ...     file = Path(folder) / "a"
    ...     _ = file.write_bytes(b"abc")
    ...     sha256(file)[:16]
    'ba7816bf8f01cfea'
    """
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def owner(path: Path) -> str:
    """
    Return the binary package that installed a file, with its architecture.

    Ubuntu keeps libraries in ``/usr/lib``, with ``/lib`` a link to it, and a package may have recorded either path, so both
    are tried.

    Parameters
    ----------
    path : Path
        The file, with links resolved.

    Returns
    -------
    str
        The package, such as ``libglib2.0-0:amd64``.

    Raises
    ------
    SystemExit
        If no package installed the file.
    """
    text = str(path)
    alternatives = [text, text.removeprefix("/usr")] if text.startswith("/usr/") else [text, "/usr" + text]
    for candidate in alternatives:
        found = subprocess.run(["dpkg", "-S", candidate], capture_output=True, text=True, check=False)
        if found.returncode == 0:
            return found.stdout.splitlines()[0].split(": ", 1)[0]
    raise SystemExit(f"No package installed {path}, so its license cannot be checked")


def unchanged(path: Path, *, package: str) -> bool:
    """
    Tell whether a file is the one its package installed, by the checksum the package recorded.

    Parameters
    ----------
    path : Path
        The installed file, with links resolved.
    package : str
        The binary package, with its architecture.

    Returns
    -------
    bool
        True if the package lists the file and its MD5 checksum matches.
    """
    name = package.split(":", 1)[0]
    lists = [Path(f"/var/lib/dpkg/info/{package}.md5sums"), Path(f"/var/lib/dpkg/info/{name}.md5sums")]
    relative = {str(path).lstrip("/"), str(path).removeprefix("/usr").lstrip("/"), "usr" + str(path)}
    digest = hashlib.md5(path.read_bytes(), usedforsecurity=False).hexdigest()
    for listing in (entry for entry in lists if entry.is_file()):
        for line in listing.read_text(encoding="utf-8").splitlines():
            recorded, _, file = line.partition("  ")
            if file in relative:
                return recorded == digest
    return False


def identify(bundle: Path, *, entries: list[dict[str, str]]) -> list[Library]:
    """
    Find the package of each system library the build copied, and check that the copy is unchanged.

    Parameters
    ----------
    bundle : Path
        The frozen program's ``_internal`` folder.
    entries : list of dict of str to str
        The libraries the build listed, each with its ``name`` in the bundle and the ``source`` it was copied from.

    Returns
    -------
    list of Library
        The libraries, sorted by name.

    Raises
    ------
    SystemExit
        If a library is missing, differs from its package's file, or comes from a source package in neither list.
    """
    libraries = []
    for entry in entries:
        copy = bundle / entry["name"]
        real = Path(entry["source"]).resolve()
        if not copy.is_file() or sha256(copy) != sha256(real):
            raise SystemExit(f"{copy} is missing or differs from {real}")
        package = owner(real)
        if not unchanged(real, package=package):
            raise SystemExit(f"{real} differs from the file {package} installed")
        fields = subprocess.check_output(
            [
                "dpkg-query",
                "--show",
                "--showformat",
                "${Version}\t${source:Package}\t${source:Version}",
                package,
            ],
            text=True,
        ).split("\t")
        library = Library(
            entry["name"],
            package=package.split(":", 1)[0],
            version=fields[0],
            source=fields[1],
            source_version=fields[2],
            sha256=sha256(copy),
        )
        if library.source not in SOURCE_PACKAGES | NOTICE_PACKAGES:
            raise SystemExit(
                f"{library.name} comes from {library.source}, which is not in packaging/linux_libraries.py: "
                "check its license and add it to SOURCE_PACKAGES or NOTICE_PACKAGES, or keep it out of the build",
            )
        libraries.append(library)
    return sorted(libraries, key=lambda found: found.name)


def common_licenses(text: str) -> set[str]:
    """
    Return the license texts in ``/usr/share/common-licenses`` that a copyright file refers to.

    Parameters
    ----------
    text : str
        The copyright file.

    Returns
    -------
    set of str
        The file names, such as ``LGPL-2.1``.

    Examples
    --------
    >>> sorted(common_licenses("see /usr/share/common-licenses/LGPL-2.1 and `/usr/share/common-licenses/GPL-2'."))
    ['GPL-2', 'LGPL-2.1']
    """
    return {name.rstrip(".") for name in re.findall(r"/usr/share/common-licenses/([A-Za-z0-9.+-]+)", text)}


def install_notices(frozen: Path, *, libraries: list[Library], archive: str) -> None:
    """
    Install each package's copyright file, the license texts they refer to, and a README listing the libraries.

    Parameters
    ----------
    frozen : Path
        The frozen program's folder.
    libraries : list of Library
        The system libraries in it.
    archive : str
        The file name of the sources archive published beside the download.

    Raises
    ------
    SystemExit
        If a package has no copyright file, or one refers to a license text this system lacks.
    """
    destination = frozen / "licenses" / "Linux"
    shutil.rmtree(destination, ignore_errors=True)
    (destination / "common-licenses").mkdir(parents=True)
    referred: set[str] = set()
    for package in sorted({library.package for library in libraries}):
        copyright_file = Path("/usr/share/doc") / package / "copyright"
        if not copyright_file.is_file():
            raise SystemExit(f"{package} has no copyright file at {copyright_file}")
        text = copyright_file.read_text(encoding="utf-8", errors="replace")
        referred |= common_licenses(text)
        (destination / package).mkdir()
        (destination / package / "copyright").write_text(text, encoding="utf-8")
    for name in sorted(referred):
        text_file = Path("/usr/share/common-licenses") / name
        if not text_file.is_file():
            raise SystemExit(f"A copyright file refers to {text_file}, which this system does not have")
        shutil.copyfile(text_file, destination / "common-licenses" / name)
    rows = [
        f"{library.name}  {library.package} {library.version}  (source {library.source} {library.source_version})"
        f"{'  [source published]' if library.source in SOURCE_PACKAGES else ''}\n    SHA-256 {library.sha256}"
        for library in libraries
    ]
    readme = f"""System libraries in Alto's Linux download

Alto's Linux download contains these libraries from Ubuntu {ubuntu_release()}, copied unchanged from the packages named
below. Each package's copyright and license terms are in the folder named after it, and the license texts they refer to
are in common-licenses. Alto's own code is under the MIT license; these libraries keep their own licenses.

The libraries marked [source published] are under the GNU LGPL or GPL, in whole or in part. Their corresponding source,
Ubuntu's source package of the exact version listed (the upstream source with Ubuntu's changes, and the .dsc file that
describes them), is in {archive} on Alto's GitHub release page:
https://github.com/altosaurus/alto/releases/tag/v{version("alto")}
The same source packages are also kept by Ubuntu at https://launchpad.net/ubuntu/+source/<source package>.

You may replace any of these libraries with a compatible build of your own, for example one you have modified: close Alto,
and put your build in the _internal folder under the same file name.

"""
    (destination / "README.txt").write_text(readme + "\n".join(rows) + "\n", encoding="utf-8")


def ubuntu_release() -> str:
    """
    Return the Ubuntu release the build runs on.

    Returns
    -------
    str
        The version and code name, such as ``22.04 (jammy)``, or ``unknown`` if the system does not say.
    """
    fields = {}
    release = Path("/etc/os-release")
    if release.is_file():
        for line in release.read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition("=")
            fields[key] = value.strip('"')
    if "VERSION_ID" not in fields:
        return "unknown"
    return f"{fields['VERSION_ID']} ({fields.get('VERSION_CODENAME', '')})"


def launchpad(url: str) -> object:
    """
    Fetch a Launchpad API resource.

    Parameters
    ----------
    url : str
        The resource.

    Returns
    -------
    object
        Its JSON.
    """
    return json.loads(subprocess.check_output([*CURL, "--header", "Accept: application/json", url], text=True))


def source_files(source: str, *, source_version: str) -> list[str]:
    """
    Return the download addresses of the files of one Ubuntu source package version.

    Parameters
    ----------
    source : str
        The source package.
    source_version : str
        Its exact version.

    Returns
    -------
    list of str
        The addresses of the .dsc file and the archives it lists.

    Raises
    ------
    SystemExit
        If Launchpad has no such version.
    """
    query = urllib.parse.urlencode(
        {
            "ws.op": "getPublishedSources",
            "source_name": source,
            "version": source_version,
            "exact_match": "true",
        },
    )
    found = launchpad(f"{LAUNCHPAD}?{query}")
    entries = found.get("entries") if isinstance(found, dict) else None
    first = entries[0] if isinstance(entries, list) and entries else None
    if not isinstance(first, dict) or not isinstance(first.get("self_link"), str):
        raise SystemExit(f"Launchpad has no source package {source} {source_version}")
    urls = launchpad(f"{first['self_link']}?ws.op=sourceFileUrls")
    if not isinstance(urls, list) or not urls:
        raise SystemExit(f"Launchpad lists no files for {source} {source_version}")
    return [str(url) for url in urls]


def check_dsc(folder: Path, *, dsc: Path) -> None:
    """
    Check the archives a source package's .dsc file lists against the checksums it gives.

    Parameters
    ----------
    folder : Path
        The folder with the downloaded files.
    dsc : Path
        The .dsc file.

    Raises
    ------
    SystemExit
        If a listed file is missing or its checksum differs.
    """
    text = dsc.read_text(encoding="utf-8", errors="replace")
    block = re.search(r"^Checksums-Sha256:\n((?: .+\n?)+)", text, re.MULTILINE)
    if block is None:
        raise SystemExit(f"{dsc.name} lists no SHA-256 checksums")
    for line in block.group(1).splitlines():
        digest, _size, name = line.split()
        if not (folder / name).is_file() or sha256(folder / name) != digest:
            raise SystemExit(f"{name} is missing or differs from the checksum in {dsc.name}")


def collect_sources(libraries: list[Library], *, archive: Path) -> None:
    """
    Download the source packages of the copyleft libraries and pack them in one uncompressed tar archive.

    Each source package is in a folder named after it and its version. The archives in it are compressed already.

    Parameters
    ----------
    libraries : list of Library
        The system libraries in the download.
    archive : Path
        The tar archive to write.

    Raises
    ------
    SystemExit
        If a source package has no .dsc file or a file differs from it.
    """
    wanted = sorted({(library.source, library.source_version) for library in libraries if library.source in SOURCE_PACKAGES})
    archive.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as work, tarfile.open(archive, "w") as tar:
        listing = []
        for source, source_version in wanted:
            # Debian's file names leave out the version's epoch, the number before a colon.
            folder = Path(work) / f"{source}_{source_version.split(':', 1)[-1]}"
            folder.mkdir()
            for url in source_files(source, source_version=source_version):
                name = urllib.parse.unquote(url.rsplit("/", 1)[1])
                subprocess.run([*CURL, "--output", str(folder / name), url], check=True)
            dscs = list(folder.glob("*.dsc"))
            if len(dscs) != 1:
                raise SystemExit(f"Expected one .dsc file for {source} {source_version}, found {len(dscs)}")
            check_dsc(folder, dsc=dscs[0])
            listing += [f"{sha256(file)}  {folder.name}/{file.name}" for file in sorted(folder.iterdir())]
            tar.add(folder, arcname=folder.name)
        sums = Path(work) / "SHA256SUMS"
        sums.write_text("\n".join(listing) + "\n", encoding="utf-8")
        tar.add(sums, arcname="SHA256SUMS")


def main(arguments: list[str]) -> None:
    """
    Install the notices in the frozen program and write the sources archive.

    Parameters
    ----------
    arguments : list of str
        The frozen program's folder, the library list the build wrote, and the sources archive to write.
    """
    frozen, listing, archive = (Path(argument) for argument in arguments)
    entries = json.loads(listing.read_text(encoding="utf-8"))
    libraries = identify(frozen / "_internal", entries=entries)
    install_notices(frozen, libraries=libraries, archive=archive.name)
    collect_sources(libraries, archive=archive)
    sources = sorted({library.source for library in libraries if library.source in SOURCE_PACKAGES})
    print(f"{len(libraries)} system libraries; sources of {', '.join(sources)} in {archive}")


if __name__ == "__main__":
    main(sys.argv[1:])
