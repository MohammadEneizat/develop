# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 10:36:38 2022

@Author: Mohammad Maher Eneizat
@Email: mohammad.eneizat@iu-study.org
@Github:

The visualizition module renders the training data, the chosen ideal
functions and the test-point mapping as Bokeh plots. Every visualisation is
saved to its own HTML file so no plot overwrites another.
"""

from __future__ import annotations

import os

import pandas as pd
from bokeh.io import output_file, save, show
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure

from ideal_function import BestFit


class Visualizer:
    """Creates and saves the Bokeh plots for the assignment."""

    COLORS = ["green", "red", "blue", "orange"]

    def __init__(self, output_dir: str = "plots", show_in_browser: bool = False) -> None:
        """Save plots into output_dir; optionally open them in a browser."""
        self.output_dir = output_dir
        self.show_in_browser = show_in_browser
        os.makedirs(output_dir, exist_ok=True)

    def _figure(self, title: str):
        """Return a new figure with the shared axis labels."""
        return figure(title=title, x_axis_label="X Axis", y_axis_label="Y Axis")

    def _render(self, layout, filename: str, title: str) -> str:
        """Write the layout to its HTML file (and show it if requested)."""
        path = os.path.join(self.output_dir, filename)
        output_file(path, title=title)
        if self.show_in_browser:
            show(layout)
        else:
            save(layout)
        return path

    def visualize_training_data(self, train_df: pd.DataFrame) -> str:
        """Plot the four training functions in one grid."""
        x = train_df.iloc[:, 0]
        plots = []
        for i, color in zip(range(1, train_df.shape[1]), self.COLORS):
            p = self._figure(f"Training Function {i}")
            p.line(x, train_df.iloc[:, i], line_width=2, color=color)
            plots.append(p)

        grid = gridplot(plots, ncols=2, width=450, height=300)
        return self._render(grid, "training_data.html", "Training Data")

    def visualize_ideal_data(
        self, ideal_table: pd.DataFrame, best_fits: list[BestFit]
    ) -> str:
        """Plot the four chosen ideal functions in one grid."""
        x = ideal_table.iloc[:, 0]
        plots = []
        for i, (fit, color) in enumerate(zip(best_fits, self.COLORS), start=1):
            p = self._figure(f"Ideal Function Y{fit.ideal_index}")
            p.line(x, ideal_table.iloc[:, i], line_width=2, color=color)
            plots.append(p)

        grid = gridplot(plots, ncols=2, width=450, height=300)
        return self._render(grid, "ideal_functions.html", "Ideal Functions")

    def _mapping_figure(self, title: str, ideal_table: pd.DataFrame, best_fits: list[BestFit]):
        """Return a figure with the four chosen ideal functions drawn."""
        p = self._figure(title)
        x = ideal_table.iloc[:, 0]
        for i, (fit, color) in enumerate(zip(best_fits, self.COLORS), start=1):
            p.line(
                x,
                ideal_table.iloc[:, i],
                line_width=2,
                color=color,
                legend_label=f"Y{fit.ideal_index}",
            )
        return p

    def visualize_before_mapping(
        self, ideal_table: pd.DataFrame, test_df: pd.DataFrame, best_fits: list[BestFit]
    ) -> str:
        """Plot the ideal functions with all test points (before mapping)."""
        p = self._mapping_figure("Before Mapping", ideal_table, best_fits)
        source = ColumnDataSource(
            {"x": test_df.iloc[:, 0], "y": test_df.iloc[:, 1]}
        )
        points = p.scatter(
            "x",
            "y",
            source=source,
            size=5,
            color="purple",
            alpha=0.8,
            legend_label="Test points",
        )
        p.add_tools(
            HoverTool(
                renderers=[points],
                tooltips=[("x", "@x{0.00}"), ("y", "@y{0.0000}")],
            )
        )
        return self._render(p, "before_mapping.html", "Before Mapping")

    def visualize_after_mapping(
        self, ideal_table: pd.DataFrame, mapping_df: pd.DataFrame, best_fits: list[BestFit]
    ) -> str:
        """Plot the ideal functions with the successfully mapped test points.

        Each mapped point is coloured like the ideal function it maps to, and
        hovering shows the point's coordinates, deviation and function number.
        """
        p = self._mapping_figure("After Mapping", ideal_table, best_fits)
        color_by_index = {
            fit.ideal_index: color for fit, color in zip(best_fits, self.COLORS)
        }

        x_col, y_col, delta_col, func_col = mapping_df.columns[:4]
        for ideal_index, group in mapping_df.groupby(func_col):
            source = ColumnDataSource(
                {
                    "x": group[x_col],
                    "y": group[y_col],
                    "delta": group[delta_col],
                    "func": group[func_col],
                }
            )
            points = p.scatter(
                "x",
                "y",
                source=source,
                size=6,
                color=color_by_index.get(int(ideal_index), "purple"),
                line_color="black",
                alpha=0.8,
                legend_label=f"Mapped to Y{int(ideal_index)}",
            )
            p.add_tools(
                HoverTool(
                    renderers=[points],
                    tooltips=[
                        ("x", "@x{0.00}"),
                        ("y", "@y{0.0000}"),
                        ("delta y", "@delta{0.0000}"),
                        ("ideal func", "Y@func"),
                    ],
                )
            )
        return self._render(p, "after_mapping.html", "After Mapping")
