# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 10:36:38 2022

@Author: Mohammad Maher Eneizat
@Email: mohammad.eneizat@iu-study.org
@Github:

The main module ties everything together: it loads the CSV datasets, stores
them in SQLite, finds the four best-fitting ideal functions, maps the test
points onto them and renders the visualisations.
"""

from __future__ import annotations

import argparse
import sys

import pandas as pd

from ideal_function import DataValidationError, TestPointMapper
from SQLiteDB import SQLiteDB
from visualizition import Visualizer


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the command-line options (every option has a sensible default)."""
    parser = argparse.ArgumentParser(
        description=(
            "Find the best-fitting ideal functions for the training data, "
            "map the test points onto them, store everything in SQLite and "
            "render Bokeh visualisations."
        )
    )
    parser.add_argument("--train", default="train.csv", help="training data CSV")
    parser.add_argument("--ideal", default="ideal.csv", help="ideal functions CSV")
    parser.add_argument("--test", default="test.csv", help="test points CSV")
    parser.add_argument(
        "--map-table", default="map_table.csv", help="output CSV for the mapping results"
    )
    parser.add_argument("--db", default="assignment.db", help="SQLite database file")
    parser.add_argument("--plots-dir", default="plots", help="directory for HTML plots")
    parser.add_argument(
        "--show", action="store_true", help="open the plots in a web browser"
    )
    return parser.parse_args(argv)


def load_csv(path: str) -> pd.DataFrame:
    """Read a CSV file, exiting with a clear message when it is unusable."""
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        sys.exit(f"Error: input file '{path}' was not found.")
    except pd.errors.ParserError as exc:
        sys.exit(f"Error: input file '{path}' could not be parsed: {exc}")


def main(argv: list[str] | None = None) -> None:
    """Run the complete assignment pipeline."""
    args = parse_args(argv)

    train = load_csv(args.train)
    ideal = load_csv(args.ideal)
    test = load_csv(args.test)

    # Persist the raw datasets in the SQLite database.
    database = SQLiteDB(args.db)
    database.load_train(train)
    database.load_ideal(ideal)

    # Find the four ideal functions with the minimum sum of squared errors.
    try:
        mapper = TestPointMapper(train, ideal)
        best_fits = mapper.find_best_fits()
    except DataValidationError as exc:
        sys.exit(f"Error: invalid input data: {exc}")

    print("Best-fitting ideal functions (least-squares criterion):")
    for fit in best_fits:
        print(
            f"  training {fit.train_column} -> ideal {fit.ideal_column} "
            f"(SSE = {fit.sse:.6f}, largest deviation = {fit.max_deviation:.6f})"
        )

    # Table with the x values and the four chosen ideal functions.
    ideal_table = ideal.iloc[:, [0] + [fit.ideal_index for fit in best_fits]]
    print()
    print(ideal_table)

    # Map every test point onto the chosen ideal functions.
    try:
        mapping = mapper.map_test_points(test)
    except DataValidationError as exc:
        sys.exit(f"Error: invalid test data: {exc}")

    print()
    print("Mapped test points:")
    print(mapping)

    # Persist the mapping results as CSV and in the database.
    mapping.to_csv(args.map_table, index=False)
    database.load_mapping(mapping)

    # Render all visualisations (saved as HTML files in the plots directory).
    visualizer = Visualizer(output_dir=args.plots_dir, show_in_browser=args.show)
    paths = [
        visualizer.visualize_training_data(train),
        visualizer.visualize_ideal_data(ideal_table, best_fits),
        visualizer.visualize_before_mapping(ideal_table, test, best_fits),
        visualizer.visualize_after_mapping(ideal_table, mapping, best_fits),
    ]
    print()
    print("Saved plots:")
    for path in paths:
        print(f"  {path}")


if __name__ == "__main__":
    main()
