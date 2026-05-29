"""Lazy, once-per-process loaders for observation and taxa tables."""

from __future__ import annotations

import logging
import threading
from typing import Tuple

import pandas as pd

import parse_viz as pv

logger = logging.getLogger("bee_api.data_store")

SUBSET_PATH = "../data/b-team/plant-pollinators-OBA-2025-assigned-subset-labels.viz"
TAXA_PATH = "../data/b-team/plant-pollinators-OBA-2025-assigned-taxa.viz"

_lock = threading.Lock()
_observations_df: pd.DataFrame | None = None
_taxa_df: pd.DataFrame | None = None


def get_datasets() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load and cache both DataFrames on first use (thread-safe, one load per worker)."""
    global _observations_df, _taxa_df
    if _observations_df is not None and _taxa_df is not None:
        return _observations_df, _taxa_df

    with _lock:
        if _observations_df is None:
            logger.info("Loading observation subset from %s", SUBSET_PATH)
            _observations_df = pv.parse_viz_to_dataframe(SUBSET_PATH)
            logger.info("Loaded %s observation rows", len(_observations_df.index))
        if _taxa_df is None:
            logger.info("Loading taxa lookup from %s", TAXA_PATH)
            _taxa_df = pv.parse_viz_to_dataframe(TAXA_PATH)
            logger.info("Loaded %s taxa rows", len(_taxa_df.index))

    return _observations_df, _taxa_df
