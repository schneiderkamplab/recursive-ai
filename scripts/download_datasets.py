#!/usr/bin/env python3
"""Download the public source corpora used by the consumer–AI audit.

Downloads are pinned to dataset revisions and written to the directory layout
expected by the corpus-preparation scripts. Interrupted transfers resume from
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
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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


def _wildchat_4_8m_files() -> tuple[SourceFile, ...]:
    sizes = (
        125_527_585,
        120_499_402,
        115_463_083,
        111_331_332,
        126_873_194,
        114_861_320,
        116_894_276,
        119_347_100,
        105_238_405,
        106_372_202,
        106_465_090,
        102_841_742,
        93_221_542,
        129_110_204,
        168_003_355,
        188_687_810,
        195_987_104,
        156_064_968,
        158_654_366,
        175_368_628,
        191_655_778,
        182_873_201,
        138_085_341,
        134_695_370,
        142_303_607,
        162_745_428,
        166_054_540,
        185_259_420,
        183_605_707,
        169_848_284,
        215_958_271,
        140_234_157,
        129_753_926,
        72_070_510,
        80_445_922,
        144_345_325,
        121_529_823,
        106_094_815,
        91_029_244,
        132_314_808,
        112_325_169,
        85_601_395,
        100_908_554,
        134_836_162,
        178_996_989,
        71_012_685,
        163_609_724,
        116_124_638,
        221_199_791,
        103_170_595,
        142_241_146,
        156_188_404,
        217_887_036,
        204_207_011,
        190_323_883,
        160_219_119,
        192_970_337,
        69_567_568,
        268_021_931,
        63_544_556,
        70_833_528,
        97_859_176,
        97_674_635,
        84_508_864,
        129_959_637,
        86_476_263,
        102_379_733,
        166_945_361,
        136_181_360,
        113_771_808,
        429_379_222,
        443_104_768,
        561_212_647,
        350_815_505,
        430_081_448,
        203_068_659,
        270_361_626,
        239_863_313,
        108_060_533,
        276_821_905,
        186_001_659,
        234_968_053,
        431_597_604,
        507_065_268,
        546_361_015,
        496_266_956,
    )
    return tuple(
        SourceFile(
            remote_path=f"data/train-{index:05d}-of-00086.parquet",
            local_name=f"train-{index:05d}-of-00086.parquet",
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
            key="wildchat-4.8m",
            repository="allenai/WildChat-4.8M",
            revision="c827c6df8fcf008219ffaffa4d1dd77491099367",
            output_directory="wildchat_4_8m",
            files=_wildchat_4_8m_files(),
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
        Dataset(
            key="sharegpt-x",
            repository="DSULT-Core/ShareGPT-X",
            revision="65d708977cdf929f09734b0c1b25d8345d51d121",
            output_directory="sharegpt_x",
            files=(
                SourceFile(
                    "ChatGPT-Simple_ShareGPT_Full.json",
                    "ChatGPT-Simple_ShareGPT_Full.json",
                    1_492_229_945,
                ),
            ),
        ),
        Dataset(
            key="prism",
            repository="HannahRoseKirk/prism-alignment",
            revision="18ab5cfb37456f4ec8cbc00212ce54cf7b1239f6",
            output_directory="prism",
            files=(
                SourceFile("conversations.jsonl", "conversations.jsonl", 60_331_783),
                SourceFile("metadata.jsonl", "metadata.jsonl", 85_080_000),
                SourceFile("survey.jsonl", "survey.jsonl", 4_863_301),
            ),
        ),
        Dataset(
            key="sharechat",
            repository="anoynsharechat/sharechat",
            revision="6fb3e27bba4185e8c05f9b8b3c5ca972192ad036",
            output_directory="sharechat",
            files=(
                SourceFile(
                    "chatgpt_results_final_language_filtered.csv",
                    "chatgpt.csv",
                    2_289_475_894,
                ),
                SourceFile(
                    "claude_results_final_language_filtered.csv",
                    "claude.csv",
                    282_846_983,
                ),
                SourceFile(
                    "gemini_results_final_language_filtered.csv",
                    "gemini.csv",
                    112_104_516,
                ),
                SourceFile(
                    "grok_results_final_language_filtered.csv",
                    "grok.csv",
                    1_094_604_743,
                ),
                SourceFile(
                    "perplexity_results_final_language_filtered.csv",
                    "perplexity.csv",
                    221_594_825,
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
    return (
        f"https://huggingface.co/datasets/{repository}/resolve/{revision}/{remote_path}"
    )


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
        print(
            f"{dataset.key}/{source_file.local_name}: completed from existing partial"
        )
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
            return _download_file(
                dataset, source_file, raw_directory, token, force=False
            )

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
        "--workers",
        type=int,
        default=1,
        help="Parallel file downloads (default: 1). Each file remains independently resumable.",
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
    if args.workers < 1:
        parser.error("--workers must be at least 1")

    token = _token()
    for dataset in datasets:
        print(f"Downloading {dataset.repository}@{dataset.revision}")
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [
                executor.submit(
                    _download_file,
                    dataset,
                    source_file,
                    raw_directory,
                    token,
                    args.force,
                )
                for source_file in dataset.files
            ]
            for future in futures:
                future.result()

    print("All selected dataset files are complete and byte-size verified.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError) as error:
        sys.exit(f"error: {error}")
