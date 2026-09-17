"""
Stage 7 Data Ingestion and Source Traceability Module

Provides immutable access to raw candidate historical data files with explicit SHA-256 verification
and record-level provenance tracking.
"""

import csv
import hashlib
import logging
import os
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Generator, Tuple

logger = logging.getLogger("football_ml.data.stage7.ingestion")

MATCHES_EXPECTED_SHA256 = (
    "d724472b2022f71f77f218552660da5fc9f815450155bb6503b3000d5e3f868b"
)
ELO_EXPECTED_SHA256 = (
    "e9f6020b2bca88ec5974aa934b5e1f3b59220729119c768404bd962a71da1343"
)

MATCHES_REMOTE_URL = "https://huggingface.co/datasets/xgabora/club-football-match-data/resolve/main/Matches.csv"
ELO_REMOTE_URL = "https://huggingface.co/datasets/xgabora/club-football-match-data/resolve/main/EloRatings.csv"

PROJECT_RAW_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "app", "data", "candidate_data"
    )
)
CACHE_DIR = "/tmp/stage7_cache"


@dataclass
class SourceProvenance:
    source_dataset: str = "xgabora/club-football-match-data"
    source_file: str = ""
    source_row_index: int = 0
    source_sha256: str = ""
    pipeline_version: str = "v1.0.0-stage7"
    transformation_timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def resolve_and_verify_source_file(
    filename: str, expected_sha256: str, remote_url: str
) -> str:
    """
    Resolves source file path, checking local candidate_data directory first.
    If local file is a pointer or missing, uses verified cached file from CACHE_DIR or downloads it.
    """
    local_path = os.path.join(PROJECT_RAW_DIR, filename)

    if os.path.exists(local_path):
        with open(local_path, "rb") as f:
            content = f.read()
            sha = hashlib.sha256(content).hexdigest()
            if sha == expected_sha256:
                logger.info(f"Local file '{filename}' verified matching SHA-256.")
                return local_path

    # Check cache directory
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, filename)
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            content = f.read()
            sha = hashlib.sha256(content).hexdigest()
            if sha == expected_sha256:
                logger.info(f"Cached file '{filename}' verified matching SHA-256.")
                return cache_path

    # Download from remote source
    logger.info(f"Downloading '{filename}' from remote URL: {remote_url}")
    req = urllib.request.Request(remote_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(cache_path, "wb") as out:
        content = resp.read()
        sha = hashlib.sha256(content).hexdigest()
        if sha != expected_sha256:
            raise ValueError(
                f"SHA-256 mismatch for downloaded file '{filename}': got {sha}, expected {expected_sha256}"
            )
        out.write(content)

    logger.info(
        f"File '{filename}' successfully downloaded and verified ({len(content)} bytes)."
    )
    return cache_path


def stream_raw_matches() -> Generator[Tuple[int, Dict[str, str], SourceProvenance], None, None]:
    """
    Streams raw match rows from Matches.csv with provenance metadata.
    """
    filepath = resolve_and_verify_source_file(
        "Matches.csv", MATCHES_EXPECTED_SHA256, MATCHES_REMOTE_URL
    )
    # Handle UTF-8 with optional BOM
    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            prov = SourceProvenance(
                source_file="Matches.csv",
                source_row_index=idx,
                source_sha256=MATCHES_EXPECTED_SHA256,
            )
            yield idx, row, prov


def stream_raw_elo_ratings() -> Generator[Tuple[int, Dict[str, str], SourceProvenance], None, None]:
    """
    Streams raw Elo rating snapshot rows from EloRatings.csv with provenance metadata.
    """
    filepath = resolve_and_verify_source_file(
        "EloRatings.csv", ELO_EXPECTED_SHA256, ELO_REMOTE_URL
    )
    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            prov = SourceProvenance(
                source_file="EloRatings.csv",
                source_row_index=idx,
                source_sha256=ELO_EXPECTED_SHA256,
            )
            yield idx, row, prov
