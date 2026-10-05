"""Reconstruct the documented English ISO locally; never overwrite an output."""

import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile

ISO_SIZE = 4699979776
SOURCE_SHA256 = "35f1f53687c4976fb80ca087133dcbaae426bf4fad1f5163426f7e890454876c"
OUTPUT_SHA256 = "44027eec9ebd2ad6b421dbf30406991e03da3f5d480462442e8b6dc6554a6ea2"


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def verify(path, expected):
    if path.stat().st_size != ISO_SIZE:
        raise ValueError(f"Unexpected ISO size: {path.stat().st_size} bytes")
    if digest(path) != expected:
        raise ValueError("ISO SHA-256 does not match the documented build")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("patch", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--xdelta-bin", default="xdelta3")
    args = parser.parse_args()
    try:
        source, patch, output = (p.resolve() for p in (args.source, args.patch, args.output))
        if not source.is_file() or not patch.is_file():
            raise ValueError("Source ISO and xdelta must both be existing files")
        if output.exists():
            raise ValueError("Output already exists; choose a new filename")
        if not output.parent.is_dir():
            raise ValueError("Output directory does not exist")
        executable = shutil.which(args.xdelta_bin)
        if executable is None:
            raise ValueError("xdelta3 was not found; use --xdelta-bin to specify it")
        print("Checking original ISO...", flush=True)
        verify(source, SOURCE_SHA256)
        # Reconstruction and final copy can coexist, requiring two ISO sizes.
        if shutil.disk_usage(output.parent).free < 2 * ISO_SIZE + 64 * 1024 * 1024:
            raise ValueError("Allow about 9.5 GB of free space in the output directory")
        with tempfile.TemporaryDirectory(prefix="dq25-", dir=output.parent) as temporary:
            candidate = Path(temporary) / "reconstructed.iso"
            print("Applying xdelta...", flush=True)
            subprocess.run([executable, "-d", "-s", str(source), str(patch), str(candidate)], check=True)
            print("Checking reconstructed ISO...", flush=True)
            verify(candidate, OUTPUT_SHA256)
            # Exclusive creation also protects a file created during patching.
            destination = output.open("xb")
            try:
                with destination, candidate.open("rb") as stream:
                    shutil.copyfileobj(stream, destination, 8 * 1024 * 1024)
            except BaseException:
                output.unlink(missing_ok=True)
                raise
        print(f"Verified English ISO: {output}")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
