# -*- coding: utf-8 -*-
"""
Unit tests for the ideal-function assignment: best-fit search, test-point
mapping and the SQLite persistence layer.

Run with:  python -m unittest test_app.py
"""

import math
import os
import tempfile
import unittest

import numpy as np
import pandas as pd

from ideal_function import (
    MAPPING_FACTOR,
    DataValidationError,
    IdealFunctionFinder,
    TestPointMapper,
)
from SQLiteDB import SQLiteDB


def make_datasets():
    """Small synthetic datasets with a known correct answer.

    ideal y1 = x, y2 = x**2, y3 = -x. The training function is x with a
    constant offset of 0.4, so its best fit is y1 with SSE = 5 * 0.4**2.
    """
    x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    ideal = pd.DataFrame({"x": x, "y1": x, "y2": x**2, "y3": -x})
    train = pd.DataFrame({"x": x, "y1": x + 0.4})
    return train, ideal


class TestIdealFunctionFinder(unittest.TestCase):
    def test_finds_minimum_sse_function(self):
        train, ideal = make_datasets()
        fits = IdealFunctionFinder(train, ideal).find_best_fits()

        self.assertEqual(len(fits), 1)
        fit = fits[0]
        self.assertEqual(fit.ideal_column, "y1")
        self.assertEqual(fit.ideal_index, 1)
        self.assertAlmostEqual(fit.sse, 5 * 0.4**2)
        self.assertAlmostEqual(fit.max_deviation, 0.4)

    def test_rejects_mismatched_x_values(self):
        train, ideal = make_datasets()
        train = train.copy()
        train["x"] = train["x"] + 1.0
        with self.assertRaises(DataValidationError):
            IdealFunctionFinder(train, ideal)

    def test_rejects_mismatched_row_counts(self):
        train, ideal = make_datasets()
        with self.assertRaises(DataValidationError):
            IdealFunctionFinder(train.iloc[:-1], ideal)

    def test_rejects_missing_y_columns(self):
        train, ideal = make_datasets()
        with self.assertRaises(DataValidationError):
            IdealFunctionFinder(train[["x"]], ideal)


class TestTestPointMapper(unittest.TestCase):
    def setUp(self):
        train, ideal = make_datasets()
        self.mapper = TestPointMapper(train, ideal)
        self.threshold = 0.4 * MAPPING_FACTOR  # max_deviation * sqrt(2)

    def map_single_point(self, x, y):
        return self.mapper.map_test_points(pd.DataFrame({"x": [x], "y": [y]}))

    def test_point_within_threshold_is_mapped(self):
        result = self.map_single_point(2.0, 2.0 + self.threshold - 1e-9)
        self.assertEqual(len(result), 1)
        self.assertEqual(result["No. of ideal func"].iloc[0], 1)
        self.assertAlmostEqual(
            result["Delta Y (test func)"].iloc[0], self.threshold - 1e-9
        )

    def test_point_on_threshold_is_mapped(self):
        result = self.map_single_point(2.0, 2.0 + self.threshold)
        self.assertEqual(len(result), 1)

    def test_point_beyond_threshold_is_not_mapped(self):
        result = self.map_single_point(2.0, 2.0 + self.threshold + 1e-6)
        self.assertTrue(result.empty)

    def test_threshold_is_per_function(self):
        """A point must be compared against the max deviation of the
        specific ideal function, not against any of the four."""
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        ideal = pd.DataFrame({"x": x, "y1": x, "y2": x + 100.0})
        train = pd.DataFrame({"x": x, "t1": x + 0.1, "t2": x + 101.0})
        mapper = TestPointMapper(train, ideal)
        # t1 -> y1 with max_deviation 0.1; t2 -> y2 with max_deviation 1.0.
        # This point deviates 0.5 from y1: within y2's threshold but outside
        # y1's, so it must NOT map to y1.
        result = mapper.map_test_points(pd.DataFrame({"x": [2.0], "y": [2.5]}))
        self.assertNotIn(1, result["No. of ideal func"].tolist())

    def test_point_with_unknown_x_is_skipped(self):
        result = self.map_single_point(2.05, 2.0)
        self.assertTrue(result.empty)

    def test_result_has_expected_columns(self):
        result = self.map_single_point(1.0, 1.0)
        self.assertEqual(list(result.columns), TestPointMapper.RESULT_COLUMNS)


class TestSQLiteDB(unittest.TestCase):
    def test_round_trip_of_all_tables(self):
        train, ideal = make_datasets()
        mapping = pd.DataFrame(
            [(1.0, 1.2, 0.2, 1)], columns=TestPointMapper.RESULT_COLUMNS
        )

        with tempfile.TemporaryDirectory() as tmp:
            db = SQLiteDB(os.path.join(tmp, "test.db"))
            db.load_train(train)
            db.load_ideal(ideal)
            db.load_mapping(mapping)

            stored_train = db.read_table(SQLiteDB.TRAIN_TABLE)
            stored_ideal = db.read_table(SQLiteDB.IDEAL_TABLE)
            stored_mapping = db.read_table(SQLiteDB.MAPPING_TABLE)

        self.assertEqual(
            list(stored_train.columns), ["X", "Y1 (training func)"]
        )
        self.assertEqual(
            list(stored_ideal.columns),
            ["X", "Y1 (ideal func)", "Y2 (ideal func)", "Y3 (ideal func)"],
        )
        self.assertTrue(
            np.allclose(stored_train["Y1 (training func)"], train["y1"])
        )
        pd.testing.assert_frame_equal(stored_mapping, mapping)

    def test_load_does_not_mutate_input(self):
        train, ideal = make_datasets()
        original_columns = list(train.columns)
        with tempfile.TemporaryDirectory() as tmp:
            SQLiteDB(os.path.join(tmp, "test.db")).load_train(train)
        self.assertEqual(list(train.columns), original_columns)


if __name__ == "__main__":
    unittest.main()
