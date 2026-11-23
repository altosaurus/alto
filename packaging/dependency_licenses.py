#!/usr/bin/env python3
"""
Install the notices of the Python packages and native code in a desktop build, and verify them after installation.

``copy`` writes them into the frozen program's ``licenses`` folder:

- the license file of each Python package frozen into the program, from the wheel the build installed;
- the interpreter's own ``LICENSE.txt`` and CPython's notices for the software it incorporates (``Doc/license.rst`` of the
  same version);
- certifi's notice, the Mozilla Public License it is under, and where to get the source of that version;
- the license of native code compiled into a wheel or supplied with Qt: LibYAML in PyYAML, libffi in cffi, ICU in the Linux
  Qt libraries, and OpenSSL in the Windows program. Each version is read from the built files and its license fetched from
  that version's upstream source.

It lists what it wrote, with checksums, in ``licenses/notices.json`` and summarizes it in ``licenses/README.txt``. ``verify``
checks an installed copy against that list and the wheels, and checks Alto's own credits.
"""

import hashlib
import json
import platform
import re
import subprocess
import sys
import sysconfig
from argparse import ArgumentParser
from dataclasses import (
    KW_ONLY,
    dataclass,
    field,
)
from importlib.metadata import (
    distribution,
    version,
)
from pathlib import Path

# The license files of the Python packages frozen into the program: (distribution, file name in its metadata, installed path).
# libsodium is included in the PyNaCl wheel and carries a separate notice.
LICENSE_FILES = (
    ("genanki", "LICENSE.txt", "genanki/LICENSE.txt"),
    ("PyNaCl", "LICENSE", "PyNaCl/LICENSE"),
    ("PyNaCl", "LICENSE.libsodium.txt", "libsodium/LICENSE.libsodium.txt"),
    ("fsrs", "LICENSE", "fsrs/LICENSE"),
    ("typing_extensions", "LICENSE", "typing_extensions/LICENSE"),
    ("chevron", "LICENSE", "chevron/LICENSE"),
    ("cached-property", "LICENSE", "cached-property/LICENSE"),
    ("PyYAML", "LICENSE", "PyYAML/LICENSE"),
    ("cffi", "LICENSE", "cffi/LICENSE"),
    ("certifi", "LICENSE", "certifi/LICENSE"),
)
RAW = "https://raw.githubusercontent.com"
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


@dataclass
class Notice:
    """
    One component's notices written into the program, for the README.

    Parameters
    ----------
    component : str
        What the notices cover, such as ``LibYAML 0.2.6``.
    _ : KW_ONLY
        Marks the following fields as keyword-only.
    where : str
        Where the component's code is in the program.
    files : list of str
        The notice files, relative to the ``licenses`` folder.
    note : str
        Anything a recipient needs beyond the files, such as where to get source.
    """

    component: str
    _: KW_ONLY
    where: str
    files: list[str] = field(default_factory=list)
    note: str = ""


def fetch(url: str, *, expect: str) -> bytes:
    """
    Download a notice and check that it is the text expected.

    Parameters
    ----------
    url : str
        Where it is.
    expect : str
        Text the notice must contain, so that an error page or a moved file is not installed as a notice.

    Returns
    -------
    bytes
        The notice.

    Raises
    ------
    SystemExit
        If it lacks the expected text.
    """
    data = subprocess.check_output([*CURL, url])
    if expect.encode() not in data:
        raise SystemExit(f"{url} does not contain {expect!r}")
    return data


def binary_version(path: Path, *, pattern: bytes) -> str:
    r"""
    Read a version number from a compiled file.

    Parameters
    ----------
    path : Path
        The file.
    pattern : bytes
        A regular expression whose first group is the version.

    Returns
    -------
    str
        The version.

    Raises
    ------
    SystemExit
        If the file has no such version, or more than one.

    Examples
    --------
    >>> import tempfile
    >>> with tempfile.TemporaryDirectory() as folder:
    ...     file = Path(folder) / "lib"
    ...     _ = file.write_bytes(b"\x00junk\x000.2.6\x00more")
    ...     binary_version(file, pattern=rb"\x00(0\.\d+\.\d+)\x00")
    '0.2.6'
    """
    found = {match.decode() for match in re.findall(pattern, path.read_bytes())}
    if len(found) != 1:
        raise SystemExit(f"Expected one version in {path.name}, found {sorted(found) or 'none'}")
    return found.pop()


def one(folder: Path, *, pattern: str) -> Path:
    """
    Return the one file in a folder tree whose name matches a pattern.

    Parameters
    ----------
    folder : Path
        Where to look.
    pattern : str
        A glob pattern for the name.

    Returns
    -------
    Path
        The file.

    Raises
    ------
    SystemExit
        If there is not exactly one.
    """
    found = [path for path in folder.rglob(pattern) if path.is_file() and not path.is_symlink()]
    if len(found) != 1:
        raise SystemExit(f"Expected one {pattern} in {folder}, found {len(found)}")
    return found[0]


def python_notices(licenses: Path) -> Notice:
    """
    Install the interpreter's license and CPython's notices for the software it incorporates.

    Parameters
    ----------
    licenses : Path
        The program's ``licenses`` folder.

    Returns
    -------
    Notice
        What was installed.

    Raises
    ------
    SystemExit
        If the interpreter has no license file.
    """
    candidates = [Path(sys.base_prefix) / "LICENSE.txt", Path(sysconfig.get_path("stdlib")) / "LICENSE.txt"]
    own = next((path for path in candidates if path.is_file()), None)
    if own is None:
        raise SystemExit(f"The Python that builds the program has no LICENSE.txt in {[str(path) for path in candidates]}")
    python = platform.python_version()
    (licenses / "Python").mkdir(parents=True, exist_ok=True)
    (licenses / "Python" / "LICENSE.txt").write_bytes(own.read_bytes())
    incorporated = fetch(
        f"{RAW}/python/cpython/v{python}/Doc/license.rst",
        expect="Licenses and Acknowledgements for Incorporated Software",
    )
    (licenses / "Python" / "license.rst").write_bytes(incorporated)
    return Notice(
        f"Python {python}",
        where="the program itself, _internal (the interpreter, its standard library and extension modules)",
        files=["Python/LICENSE.txt", "Python/license.rst"],
        note="LICENSE.txt is the interpreter's own license file. license.rst is CPython's list of the licenses and "
        "acknowledgements for the software incorporated in it.",
    )


def certifi_notices(licenses: Path) -> Notice:
    """
    Install certifi's Mozilla Public License text and say where its source is.

    Parameters
    ----------
    licenses : Path
        The program's ``licenses`` folder.

    Returns
    -------
    Notice
        What was installed.

    Raises
    ------
    SystemExit
        If PyPI lists no source distribution for the version.
    """
    certifi = version("certifi")
    release = json.loads(subprocess.check_output([*CURL, f"https://pypi.org/pypi/certifi/{certifi}/json"]))
    sources = [entry for entry in release["urls"] if entry["packagetype"] == "sdist"]
    if len(sources) != 1:
        raise SystemExit(f"Expected one source distribution of certifi {certifi} on PyPI, found {len(sources)}")
    mpl = fetch("https://www.mozilla.org/media/MPL/2.0/index.txt", expect="Mozilla Public License Version 2.0")
    (licenses / "certifi" / "MPL-2.0.txt").write_bytes(mpl)
    return Notice(
        f"certifi {certifi}",
        where="_internal/certifi (cacert.pem, the list of certificate authorities, and the module that finds it)",
        files=["certifi/LICENSE", "certifi/MPL-2.0.txt"],
        note="certifi is under the Mozilla Public License 2.0. cacert.pem is in source form in the program. The Python "
        f"module is compiled into the program; its source is in certifi's source distribution: {sources[0]['url']} "
        f"(SHA-256 {sources[0]['digests']['sha256']}).",
    )


def libyaml_notices(licenses: Path, *, internal: Path) -> Notice:
    """
    Install the license of the LibYAML version compiled into PyYAML's extension.

    Parameters
    ----------
    licenses : Path
        The program's ``licenses`` folder.
    internal : Path
        The program's ``_internal`` folder.

    Returns
    -------
    Notice
        What was installed.
    """
    extension = one(internal / "yaml", pattern="_yaml*")
    libyaml = binary_version(extension, pattern=rb"\x00(0\.\d+\.\d+)\x00")
    text = fetch(f"{RAW}/yaml/libyaml/{libyaml}/License", expect="Permission is hereby granted")
    (licenses / "LibYAML").mkdir(parents=True, exist_ok=True)
    (licenses / "LibYAML" / "License").write_bytes(text)
    return Notice(f"LibYAML {libyaml}", where=f"compiled into _internal/yaml/{extension.name}", files=["LibYAML/License"])


def libffi_notices(licenses: Path, *, internal: Path) -> Notice:
    """
    Install the license of the libffi compiled into cffi's extension.

    cffi's Linux wheels are built with a libffi release that its CI downloads; its Windows wheels use the copy of libffi in
    its own source.

    Parameters
    ----------
    licenses : Path
        The program's ``licenses`` folder.
    internal : Path
        The program's ``_internal`` folder.

    Returns
    -------
    Notice
        What was installed.

    Raises
    ------
    SystemExit
        If cffi's build recipe names no libffi release.
    """
    cffi = version("cffi")
    extension = one(internal, pattern="_cffi_backend*")
    if sys.platform == "win32":
        url = f"{RAW}/python-cffi/cffi/v{cffi}/src/c/libffi_x86_x64/LICENSE"
        component = f"libffi (the copy in cffi {cffi}'s source, src/c/libffi_x86_x64)"
    else:
        recipe = fetch(f"{RAW}/python-cffi/cffi/v{cffi}/.github/workflows/ci.yaml", expect="libffi").decode()
        releases = set(re.findall(r"libffi/libffi/archive/v([\d.]+)\.tar\.gz", recipe))
        if len(releases) != 1:
            raise SystemExit(f"Expected one libffi release in cffi {cffi}'s build recipe, found {sorted(releases)}")
        libffi = releases.pop()
        url = f"{RAW}/libffi/libffi/v{libffi}/LICENSE"
        component = f"libffi {libffi}"
    (licenses / "libffi").mkdir(parents=True, exist_ok=True)
    (licenses / "libffi" / "LICENSE").write_bytes(fetch(url, expect="Permission is hereby granted"))
    return Notice(component, where=f"compiled into _internal/{extension.name} (cffi {cffi})", files=["libffi/LICENSE"])


def icu_notices(licenses: Path, *, internal: Path) -> Notice:
    """
    Install the license of the ICU version in the Linux Qt libraries.

    Parameters
    ----------
    licenses : Path
        The program's ``licenses`` folder.
    internal : Path
        The program's ``_internal`` folder.

    Returns
    -------
    Notice
        What was installed.
    """
    library = one(internal / "PySide6" / "Qt" / "lib", pattern="libicuuc.so.*")
    major = library.name.rsplit(".", 1)[1]
    icu = binary_version(library, pattern=rb"\x00(" + major.encode() + rb"\.\d+)\x00")
    text = fetch(f"{RAW}/unicode-org/icu/release-{icu.replace('.', '-')}/icu4c/LICENSE", expect="UNICODE, INC. LICENSE AGREEMENT")
    (licenses / "ICU").mkdir(parents=True, exist_ok=True)
    (licenses / "ICU" / "LICENSE").write_bytes(text)
    return Notice(
        f"ICU {icu}",
        where="_internal/PySide6/Qt/lib/libicudata, libicui18n and libicuuc (from the PySide6 wheel)",
        files=["ICU/LICENSE"],
    )


def openssl_notices(licenses: Path, *, internal: Path) -> Notice:
    """
    Install the license of the OpenSSL version in the Windows program's OpenSSL libraries.

    Python and Qt each bring a pair of OpenSSL libraries (libcrypto and libssl).

    Parameters
    ----------
    licenses : Path
        The program's ``licenses`` folder.
    internal : Path
        The program's ``_internal`` folder.

    Returns
    -------
    Notice
        What was installed.

    Raises
    ------
    SystemExit
        If there is no OpenSSL library, or the libraries are of different versions.
    """
    libraries = sorted(path for path in internal.rglob("lib*-3*.dll") if path.name.startswith(("libcrypto", "libssl")))
    cryptos = [path for path in libraries if path.name.startswith("libcrypto")]
    versions = {binary_version(path, pattern=rb"OpenSSL (\d+\.\d+\.\d+) ") for path in cryptos}
    if not cryptos or len(versions) != 1:
        raise SystemExit(f"Expected OpenSSL libraries of one version, found {sorted(versions)} in {cryptos}")
    openssl = versions.pop()
    text = fetch(f"{RAW}/openssl/openssl/openssl-{openssl}/LICENSE.txt", expect="Apache License")
    (licenses / "OpenSSL").mkdir(parents=True, exist_ok=True)
    (licenses / "OpenSSL" / "LICENSE.txt").write_bytes(text)
    names = ", ".join(str(path.relative_to(internal)) for path in libraries)
    return Notice(f"OpenSSL {openssl}", where=f"_internal: {names}", files=["OpenSSL/LICENSE.txt"])


def wheel_notices(licenses: Path) -> list[Notice]:
    """
    Install the license file of each frozen Python package from the wheel the build installed.

    Parameters
    ----------
    licenses : Path
        The program's ``licenses`` folder.

    Returns
    -------
    list of Notice
        What was installed, one per package.
    """
    notices: dict[str, Notice] = {}
    for package, filename, relative_path in LICENSE_FILES:
        target = licenses / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(wheel_file(package, filename=filename))
        notice = notices.setdefault(
            package,
            Notice(f"{package} {version(package)}", where="compiled into the program, or in _internal"),
        )
        notice.files.append(relative_path)
    return list(notices.values())


def wheel_file(package: str, *, filename: str) -> bytes:
    """
    Return a license file from an installed package's metadata.

    Parameters
    ----------
    package : str
        The distribution.
    filename : str
        The file's name.

    Returns
    -------
    bytes
        Its contents.

    Raises
    ------
    SystemExit
        If the metadata has no such file, more than one, or an empty one.
    """
    wheel = distribution(package)
    matches = [entry for entry in wheel.files or () if entry.name == filename and entry.parts[0].endswith(".dist-info")]
    if len(matches) != 1:
        raise SystemExit(f"Expected one {filename} in {package} {wheel.version} metadata, found {len(matches)}")
    contents = matches[0].read_binary()
    if not contents.strip():
        raise SystemExit(f"Empty upstream notice in {package} {wheel.version}: {filename}")
    return contents


def copy(app: Path) -> None:
    """
    Install every notice in a frozen program and write the list of them and the README.

    Parameters
    ----------
    app : Path
        The frozen program's folder.
    """
    licenses = app / "licenses"
    internal = app / "_internal"
    # certifi's wheel notice is listed again with its source information.
    notices = [notice for notice in wheel_notices(licenses) if not notice.component.startswith("certifi ")]
    notices += [
        python_notices(licenses),
        certifi_notices(licenses),
        libyaml_notices(licenses, internal=internal),
        libffi_notices(licenses, internal=internal),
    ]
    if sys.platform == "win32":
        notices.append(openssl_notices(licenses, internal=internal))
    else:
        notices.append(icu_notices(licenses, internal=internal))
    written = sorted({file for notice in notices for file in notice.files})
    manifest = {file: hashlib.sha256((licenses / file).read_bytes()).hexdigest() for file in written}
    (licenses / "notices.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    lines = [
        "Notices of the Python packages and native code in Alto",
        "",
        "Alto's own code is under the MIT license (LICENSE, beside the program). The components below keep their own",
        "licenses; their notices are in the files named, relative to this folder. Qt, PySide and Shiboken are in Qt/, and on",
        "Linux the system libraries from Ubuntu are in Linux/.",
        "",
    ]
    for notice in notices:
        lines += [notice.component, f"  In: {notice.where}", *(f"  Notice: {file}" for file in notice.files)]
        lines += [f"  {notice.note}"] if notice.note else []
        lines.append("")
    (licenses / "README.txt").write_text("\n".join(lines), encoding="utf-8")


def verify(app: Path) -> None:
    """
    Check an installed program's notices against the wheels and the list ``copy`` wrote, and check Alto's credits.

    Parameters
    ----------
    app : Path
        The installed program's folder.

    Raises
    ------
    SystemExit
        If a notice is missing or altered, or the credits differ from the checkout.
    """
    licenses = app / "licenses"
    for package, filename, relative_path in LICENSE_FILES:
        target = licenses / relative_path
        if not target.is_file() or target.read_bytes() != wheel_file(package, filename=filename):
            raise SystemExit(f"Missing or altered installed notice: {target}")
    manifest = json.loads((licenses / "notices.json").read_text(encoding="utf-8"))
    for file, digest in manifest.items():
        target = licenses / file
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise SystemExit(f"Missing or altered installed notice: {target}")
    if not (licenses / "README.txt").is_file():
        raise SystemExit(f"Missing {licenses / 'README.txt'}")
    root = Path(__file__).resolve().parents[1]
    sample_credits = Path("alto/assets/samples/SOURCE.txt")
    notices = Path("THIRD_PARTY_NOTICES.md")
    wheel_metadata = Path(f"alto-{distribution('alto').version}.dist-info")
    for source, installed in (
        (notices, notices),
        (notices, Path("_internal") / wheel_metadata / "licenses" / notices),
        (sample_credits, Path("_internal") / sample_credits),
    ):
        expected = (root / source).read_text(encoding="utf-8")
        if (app / installed).read_text(encoding="utf-8") != expected:
            raise SystemExit(f"Installed credits differ from {source}: {installed}")


def main() -> None:
    """Write the notices into a frozen program, or verify an installed one."""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("copy", "verify"))
    parser.add_argument("app_directory", type=Path)
    args = parser.parse_args()
    if args.action == "copy":
        copy(args.app_directory)
    else:
        verify(args.app_directory)


if __name__ == "__main__":
    main()
