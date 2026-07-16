# Ideal Function Finder

[![CI](https://github.com/MohammadEneizat/develop/actions/workflows/ci.yml/badge.svg)](https://github.com/MohammadEneizat/develop/actions/workflows/ci.yml)

A Python application that selects, for each of four training functions, the
best-fitting "ideal function" out of 50 candidates (least-squares criterion),
maps test points onto the chosen functions, stores everything in a SQLite
database and visualises the results with Bokeh.

## How it works

1. `train.csv` (x plus 4 training functions) and `ideal.csv` (x plus 50 ideal
   functions) are loaded and stored in the SQLite database `assignment.db`
   (tables `train` and `ideal`).
2. For every training function the ideal function with the minimum sum of
   squared errors is selected.
3. Every x-y pair from `test.csv` is mapped onto one of the four chosen ideal
   functions if its deviation does not exceed that function's largest
   training deviation by more than a factor of sqrt(2). The results are
   written to `map_table.csv` and to the `mapping` table of the database.
4. Four interactive plots are saved to the `plots/` directory: the training
   data, the chosen ideal functions, and the test points before and after
   mapping.

## Project structure

| File               | Purpose                                              |
| ------------------ | ---------------------------------------------------- |
| `main.py`          | Entry point; runs the complete pipeline              |
| `ideal_function.py`| Best-fit search and test-point mapping logic         |
| `SQLiteDB.py`      | SQLite persistence layer                             |
| `visualizition.py` | Bokeh visualisations                                 |
| `test_app.py`      | Unit tests                                           |

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

The console shows the chosen ideal functions (with SSE and largest
deviation) and the mapping table; the plots are written to `plots/*.html`.
In the "After Mapping" plot each test point is coloured like the ideal
function it maps to, and hovering over a point shows its coordinates,
deviation and function number.

All paths are configurable:

```text
python main.py --help

  --train TRAIN          training data CSV (default: train.csv)
  --ideal IDEAL          ideal functions CSV (default: ideal.csv)
  --test TEST            test points CSV (default: test.csv)
  --map-table MAP_TABLE  output CSV for the mapping results (default: map_table.csv)
  --db DB                SQLite database file (default: assignment.db)
  --plots-dir PLOTS_DIR  directory for HTML plots (default: plots)
  --show                 open the plots in a web browser
```

## Continuous integration

Every push and pull request runs the unit tests and a full pipeline smoke
test on Python 3.10–3.12 via GitHub Actions (`.github/workflows/ci.yml`).

## Tests

```bash
python -m unittest test_app.py
```
