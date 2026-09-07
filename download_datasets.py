#!/usr/bin/env python3
"""Download the public source corpora used by the consumer–AI audit.

Downloads are pinned to dataset revisions and written to the directory layout
expected by ``prepare_long_conversations.py``. Interrupted transfers resume from
``.part`` files. Hugging Face credentials are read from the process environment
and are never written by this script.
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_RAW_DIR = ROOT / "raw"
CHUNK_SIZE = 8 * 1024 * 1024
PROGRESS_INTERVAL = 128 * 1024 * 1024


@dataclass(frozen=True)
class SourceFile:
    remote_path: str
    local_name: str
    size: int


@dataclass(frozen=True)
class Dataset:
    key: str
    repository: str
    revision: str
    output_directory: str
    files: tuple[SourceFile, ...]


def _wildchat_files() -> tuple[SourceFile, ...]:
    sizes = (
        230_786_095,
        215_399_142,
        205_701_692,
        216_891_660,
        208_292_393,
        200_855_598,
        189_507_683,
        188_410_403,
        180_994_027,
        268_963_848,
        336_477_988,
        299_818_606,
        282_697_282,
        336_039_603,
    )
    return tuple(
        SourceFile(
            remote_path=f"data/train-{index:05d}-of-00014.parquet",
            local_name=f"train-{index:05d}-of-00014.parquet",
            size=size,
        )
        for index, size in enumerate(sizes)
    )


DATASETS = {
    dataset.key: dataset
    for dataset in (
        Dataset(
            key="wildchat",
            repository="allenai/WildChat-1M",
            revision="7d6490e462285cf85d91eabea0f9a954fbddcd1f",
            output_directory="wildchat",
            files=_wildchat_files(),
        ),
        Dataset(
            key="lmsys",
            repository="lmsys/lmsys-chat-1m",
            revision="200748d9d3cddcc9d782887541057aca0b18c5da",
            output_directory="lmsys",
            files=(
                SourceFile(
                    "data/train-00000-of-00006-4feeb3f83346a0e9.parquet",
                    "train-00000-of-00006-4feeb3f83346a0e9.parquet",
                    249_303_811,
                ),
                SourceFile(
                    "data/train-00001-of-00006-4030672591c2f478.parquet",
                    "train-00001-of-00006-4030672591c2f478.parquet",
                    247_222_671,
                ),
                SourceFile(
                    "data/train-00002-of-00006-1779b7cec9462180.parquet",
                    "train-00002-of-00006-1779b7cec9462180.parquet",
                    249_923_890,
                ),
                SourceFile(
                    "data/train-00003-of-00006-2fa862bfed56af1f.parquet",
                    "train-00003-of-00006-2fa862bfed56af1f.parquet",
                    247_173_225,
                ),
                SourceFile(
                    "data/train-00004-of-00006-18f4bdd50c103e71.parquet",
                    "train-00004-of-00006-18f4bdd50c103e71.parquet",
                    246_443_273,
                ),
                SourceFile(
                    "data/train-00005-of-00006-fe1acc5d10a9f0e2.parquet",
                    "train-00005-of-00006-fe1acc5d10a9f0e2.parquet",
                    248_783_380,
                ),
            ),
        ),
        Dataset(
            key="thoughttrace",
            repository="SCAI-JHU/ThoughtTrace",
            revision="0420f3d8499e477098aac7771fe9c066f2340fb3",
            output_directory="thoughttrace",
            files=(SourceFile("ThoughtTrace.jsonl", "ThoughtTrace.jsonl", 29_915_720),),
        ),
        Dataset(
            key="realuser-preview",
            repository="Gata-community/ChatGPT-RealUser-2.2M-preview",
            revision="75d746a9456680695e5fc78be305a99e4c05ff0f",
            output_directory="realuser_preview",
            files=(
                SourceFile(
                    "ChatGPT-RealUser-2.2M-preview.csv",
                    "ChatGPT-RealUser-2.2M-preview.csv",
                    4_513_903,
                ),
            ),
        ),
    )
}


def _token() -> str | None:
    return os.environ.get("HF_EPHEMERAL_TOKEN") or os.environ.get("HF_TOKEN")


def _resolve_url(dataset: Dataset, source_file: SourceFile) -> str:
    repository = urllib.parse.quote(dataset.repository, safe="/")
    revision = urllib.parse.quote(dataset.revision, safe="")
    remote_path = urllib.parse.quote(source_file.remote_path, safe="/")
    return f"https://huggingface.co/datasets/{repository}/resolve/{revision}/{remote_path}"


def _request(url: str, token: str | None, offset: int) -> urllib.request.Request:
    headers = {"User-Agent": "recursive-ai-extended-self-corpus-downloader/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if offset:
        headers["Range"] = f"bytes={offset}-"
    return urllib.request.Request(url, headers=headers)


def _download_file(
    dataset: Dataset,
    source_file: SourceFile,
    raw_directory: Path,
    token: str | None,
    force: bool,
) -> None:
    output_directory = raw_directory / dataset.output_directory
    output_directory.mkdir(parents=True, exist_ok=True)
    destination = output_directory / source_file.local_name
    partial = destination.with_suffix(destination.suffix + ".part")

    if destination.exists():
        existing_size = destination.stat().st_size
        if existing_size == source_file.size:
            print(f"{dataset.key}/{source_file.local_name}: already complete")
            return
        if not force:
            raise RuntimeError(
                f"{destination} has {existing_size:,} bytes; expected "
                f"{source_file.size:,}. Use --force to replace it."
            )
        destination.unlink()

    if force and partial.exists():
        partial.unlink()

    offset = partial.stat().st_size if partial.exists() else 0
    if offset > source_file.size:
        raise RuntimeError(
            f"Partial file {partial} exceeds the expected size; remove it or use --force."
        )
    if offset == source_file.size:
        partial.replace(destination)
        print(f"{dataset.key}/{source_file.local_name}: completed from existing partial")
        return

    url = _resolve_url(dataset, source_file)
    request = _request(url, token, offset)
    try:
        response = urllib.request.urlopen(request, timeout=120)
    except urllib.error.HTTPError as error:
        if error.code in {401, 403}:
            raise RuntimeError(
                f"Access denied for {dataset.repository}. If access requires authentication, "
                "accept the dataset terms and set HF_EPHEMERAL_TOKEN or HF_TOKEN."
            ) from error
        raise RuntimeError(
            f"Download failed for {dataset.repository}/{source_file.remote_path}: "
            f"HTTP {error.code}"
        ) from error

    with response:
        if offset and response.status != 206:
            # A server that ignores Range must be restarted rather than appended.
            partial.unlink(missing_ok=True)
            return _download_file(dataset, source_file, raw_directory, token, force=False)

        mode = "ab" if offset else "wb"
        transferred = offset
        next_progress = ((transferred // PROGRESS_INTERVAL) + 1) * PROGRESS_INTERVAL
        with partial.open(mode) as target:
            while chunk := response.read(CHUNK_SIZE):
                target.write(chunk)
                transferred += len(chunk)
                if transferred >= next_progress or transferred == source_file.size:
                    percent = min(100.0, 100 * transferred / source_file.size)
                    print(
                        f"{dataset.key}/{source_file.local_name}: "
                        f"{transferred / 1_000_000:.1f} MB ({percent:.1f}%)",
                        flush=True,
                    )
                    next_progress += PROGRESS_INTERVAL

    actual_size = partial.stat().st_size
    if actual_size != source_file.size:
        raise RuntimeError(
            f"Downloaded {actual_size:,} bytes for {dataset.key}/{source_file.local_name}; "
            f"expected {source_file.size:,}. The partial file was preserved for inspection."
        )
    partial.replace(destination)


def _selected_datasets(keys: list[str] | None) -> list[Dataset]:
    selected = keys or list(DATASETS)
    return [DATASETS[key] for key in selected]


def _print_inventory(datasets: list[Dataset], raw_directory: Path) -> None:
    for dataset in datasets:
        total = sum(source_file.size for source_file in dataset.files)
        print(
            f"{dataset.key}: {dataset.repository}@{dataset.revision} "
            f"({len(dataset.files)} files, {total / 1_000_000_000:.3f} GB) "
            f"-> {raw_directory / dataset.output_directory}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        action="append",
        choices=tuple(DATASETS),
        help="Dataset to download; repeat to select several. The default is all datasets.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=DEFAULT_RAW_DIR,
        help=f"Raw-data root (default: {DEFAULT_RAW_DIR}).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace complete or partial files instead of resuming/skipping them.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print the pinned inventory and exit without downloading.",
    )
    args = parser.parse_args()

    datasets = _selected_datasets(args.dataset)
    raw_directory = args.raw_dir.resolve()
    if args.list:
        _print_inventory(datasets, raw_directory)
        return

    token = _token()
    for dataset in datasets:
        print(f"Downloading {dataset.repository}@{dataset.revision}")
        for source_file in dataset.files:
            _download_file(dataset, source_file, raw_directory, token, args.force)

    print("All selected dataset files are complete and byte-size verified.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError) as error:
        sys.exit(f"error: {error}")
