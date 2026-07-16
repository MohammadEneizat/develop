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

import os

from bokeh.io import output_file, save, show
from bokeh.layouts import gridplot
from bokeh.plotting import figure


class Visualizer:
    """Creates and saves the Bokeh plots for the assignment."""

    COLORS = ["green", "red", "blue", "orange"]

    def __init__(self, output_dir="plots", show_in_browser=False):
        """Save plots into output_dir; optionally open them in a browser."""
        self.output_dir = output_dir
        self.show_in_browser = show_in_browser
        os.makedirs(output_dir, exist_ok=True)

    def _figure(self, title):
        """Return a new figure with the shared axis labels."""
        return figure(title=title, x_axis_label="X Axis", y_axis_label="Y Axis")

    def _render(self, layout, filename, title):
        """Write the layout to its HTML file (and show it if requested)."""
        path = os.path.join(self.output_dir, filename)
        output_file(path, title=title)
        if self.show_in_browser:
            show(layout)
        else:
            save(layout)
        return path

    def visualize_training_data(self, train_df):
        """Plot the four training functions in one grid."""
        x = train_df.iloc[:, 0]
        plots = []
        for i, color in zip(range(1, train_df.shape[1]), self.COLORS):
            p = self._figure(f"Training Function {i}")
            p.line(x, train_df.iloc[:, i], line_width=2, color=color)
            plots.append(p)

        grid = gridplot(plots, ncols=2, width=450, height=300)
        return self._render(grid, "training_data.html", "Training Data")

    def visualize_ideal_data(self, ideal_table, best_fits):
        """Plot the four chosen ideal functions in one grid."""
        x = ideal_table.iloc[:, 0]
        plots = []
        for i, (fit, color) in enumerate(zip(best_fits, self.COLORS), start=1):
            p = self._figure(f"Ideal Function Y{fit.ideal_index}")
            p.line(x, ideal_table.iloc[:, i], line_width=2, color=color)
            plots.append(p)

        grid = gridplot(plots, ncols=2, width=450, height=300)
        return self._render(grid, "ideal_functions.html", "Ideal Functions")

    def _mapping_figure(self, title, ideal_table, best_fits):
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

    def visualize_before_mapping(self, ideal_table, test_df, best_fits):
        """Plot the ideal functions with all test points (before mapping)."""
        p = self._mapping_figure("Before Mapping", ideal_table, best_fits)
        p.scatter(
            test_df.iloc[:, 0],
            test_df.iloc[:, 1],
            size=4,
            color="purple",
            alpha=0.8,
            legend_label="Test points",
        )
        return self._render(p, "before_mapping.html", "Before Mapping")

    def visualize_after_mapping(self, ideal_table, mapping_df, best_fits):
        """Plot the ideal functions with the successfully mapped test points."""
        p = self._mapping_figure("After Mapping", ideal_table, best_fits)
        p.scatter(
            mapping_df.iloc[:, 0],
            mapping_df.iloc[:, 1],
            size=4,
            color="purple",
            alpha=0.8,
            legend_label="Test points Mapping",
        )
        return self._render(p, "after_mapping.html", "After Mapping")
