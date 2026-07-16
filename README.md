# Ideal Function Finder

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

## Tests

```bash
python -m unittest test_app.py
```
