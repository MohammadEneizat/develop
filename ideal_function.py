# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 10:36:38 2022

@Author: Mohammad Maher Eneizat
@Email: mohammad.eneizat@iu-study.org
@Github:

The ideal_function module finds the best-fitting ideal functions for the
training data (least-squares criterion) and maps test points onto them.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# A test point maps to an ideal function when its deviation does not exceed
# the largest training deviation of that function by more than sqrt(2).
MAPPING_FACTOR = np.sqrt(2)


class DataValidationError(Exception):
    """Raised when an input dataset does not have the expected structure."""


@dataclass
class BestFit:
    """Result of fitting one training function against all ideal functions.

    Attributes:
        train_column: name of the training column (e.g. "y1").
        ideal_column: name of the chosen ideal column (e.g. "y25").
        ideal_index: 1-based positional index of the ideal column.
        sse: minimum sum of squared errors between the two functions.
        max_deviation: largest absolute deviation between the two functions.
    """

    train_column: str
    ideal_column: str
    ideal_index: int
    sse: float
    max_deviation: float


class IdealFunctionFinder:
    """Finds, for every training function, the ideal function that minimises
    the sum of squared errors (least-squares criterion)."""

    def __init__(self, train_df: pd.DataFrame, ideal_df: pd.DataFrame) -> None:
        """Validate and store the training and ideal datasets.

        Both dataframes must share the same x values in their first column;
        every remaining column is treated as one function.
        """
        self._validate(train_df, ideal_df)
        self.train_df = train_df
        self.ideal_df = ideal_df
        self.best_fits: list[BestFit] = []

    @staticmethod
    def _validate(train_df: pd.DataFrame, ideal_df: pd.DataFrame) -> None:
        """Check that both datasets are usable and aligned on x."""
        if train_df.shape[1] < 2:
            raise DataValidationError(
                "training data needs an x column and at least one y column"
            )
        if ideal_df.shape[1] < 2:
            raise DataValidationError(
                "ideal data needs an x column and at least one y column"
            )
        if len(train_df) != len(ideal_df):
            raise DataValidationError(
                "training and ideal data must have the same number of rows"
            )
        if not np.allclose(
            train_df.iloc[:, 0].to_numpy(dtype=float),
            ideal_df.iloc[:, 0].to_numpy(dtype=float),
        ):
            raise DataValidationError(
                "training and ideal data must share the same x values"
            )

    def find_best_fits(self) -> list[BestFit]:
        """Return one BestFit per training function.

        For each training column the sum of squared errors against every
        ideal column is computed in one vectorised step; the ideal function
        with the smallest SSE wins.
        """
        ideal_y = self.ideal_df.iloc[:, 1:].to_numpy(dtype=float)

        self.best_fits = []
        for column in self.train_df.columns[1:]:
            train_y = self.train_df[column].to_numpy(dtype=float)
            sse = ((ideal_y - train_y[:, np.newaxis]) ** 2).sum(axis=0)
            best = int(np.argmin(sse))
            max_deviation = np.abs(ideal_y[:, best] - train_y).max()

            self.best_fits.append(
                BestFit(
                    train_column=column,
                    ideal_column=self.ideal_df.columns[best + 1],
                    ideal_index=best + 1,
                    sse=float(sse[best]),
                    max_deviation=float(max_deviation),
                )
            )
        return self.best_fits


class TestPointMapper(IdealFunctionFinder):
    """Extends IdealFunctionFinder with the mapping of test points onto the
    chosen ideal functions."""

    RESULT_COLUMNS = [
        "X (test func)",
        "Y (test func)",
        "Delta Y (test func)",
        "No. of ideal func",
    ]

    def map_test_points(self, test_df: pd.DataFrame) -> pd.DataFrame:
        """Map every x-y test pair onto the chosen ideal functions.

        A pair maps to an ideal function when the absolute deviation between
        the test y and the ideal y at the same x does not exceed that
        function's largest training deviation multiplied by sqrt(2).

        Returns a dataframe with the test point, its deviation and the number
        of the ideal function it maps to (one row per successful mapping).
        """
        if test_df.shape[1] < 2:
            raise DataValidationError(
                "test data needs an x column and a y column"
            )
        if not self.best_fits:
            self.find_best_fits()

        x_ideal = self.ideal_df.iloc[:, 0].to_numpy(dtype=float)
        ideal_y = self.ideal_df.iloc[:, 1:].to_numpy(dtype=float)

        rows = []
        for x_test, y_test in test_df.iloc[:, :2].itertuples(index=False):
            matches = np.nonzero(np.isclose(x_ideal, x_test))[0]
            if matches.size == 0:
                continue
            row = matches[0]

            for fit in self.best_fits:
                delta = abs(y_test - ideal_y[row, fit.ideal_index - 1])
                if delta <= fit.max_deviation * MAPPING_FACTOR:
                    rows.append((x_test, y_test, delta, fit.ideal_index))

        return pd.DataFrame(rows, columns=self.RESULT_COLUMNS)
