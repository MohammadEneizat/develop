# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 10:36:38 2022

@Author: Mohammad Maher Eneizat
@Email: mohammad.eneizat@iu-study.org
@Github:

The SQLiteDB module persists the assignment datasets in a single SQLite
database with one table per dataset (train, ideal, mapping).
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine


class SQLiteDB:
    """Wraps the SQLite database used to store the assignment data."""

    TRAIN_TABLE = "train"
    IDEAL_TABLE = "ideal"
    MAPPING_TABLE = "mapping"

    def __init__(self, db_path: str = "assignment.db") -> None:
        """Create (or open) the SQLite database at db_path."""
        self.engine = create_engine(f"sqlite:///{db_path}")

    def load_train(self, train_df: pd.DataFrame) -> None:
        """Store the training data in the 'train' table.

        Columns are renamed to the assignment convention
        (X, Y1 (training func), ...) without mutating the caller's dataframe.
        """
        renamed = train_df.copy()
        renamed.columns = ["X"] + [
            f"Y{i} (training func)" for i in range(1, train_df.shape[1])
        ]
        renamed.to_sql(
            self.TRAIN_TABLE, self.engine, if_exists="replace", index=False
        )

    def load_ideal(self, ideal_df: pd.DataFrame) -> None:
        """Store the ideal functions in the 'ideal' table.

        Columns are renamed to the assignment convention
        (X, Y1 (ideal func), ...) without mutating the caller's dataframe.
        """
        renamed = ideal_df.copy()
        renamed.columns = ["X"] + [
            f"Y{i} (ideal func)" for i in range(1, ideal_df.shape[1])
        ]
        renamed.to_sql(
            self.IDEAL_TABLE, self.engine, if_exists="replace", index=False
        )

    def load_mapping(self, mapping_df: pd.DataFrame) -> None:
        """Store the test-point mapping results in the 'mapping' table."""
        mapping_df.to_sql(
            self.MAPPING_TABLE, self.engine, if_exists="replace", index=False
        )

    def read_table(self, table_name: str) -> pd.DataFrame:
        """Return the given table as a dataframe (used for verification)."""
        return pd.read_sql_table(table_name, self.engine)
