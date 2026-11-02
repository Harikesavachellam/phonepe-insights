# PhonePe Transaction Insights

A beginner-friendly dashboard built with Python, SQLite, Pandas, Plotly and Streamlit.

## Features

- Explore transactions, users and insurance by year, quarter and state.
- View India maps, district data, rankings and quarterly trends.
- Compare payment categories and explore five SQL business cases.
- Download the displayed data as CSV.

## Run

Install Python 3.10 or newer. In the project folder:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The prepared SQLite database and map files are included.

## Main files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit dashboard |
| `load_data.py` | Extract JSON and load SQL tables |
| `schema.sql` | Define the nine database tables |
| `queries.py` | Query the database |
| `charts.py` | Create maps and charts |
| `case_studies.py` | Business questions and SQL queries |

## Data

Uses a preserved [PhonePe Pulse snapshot](https://github.com/sunil-chaudhary-phonepe-com/pulse)
at commit `bf862f22ce42949a183bf65a9b8aa50110101199`.
Transaction/user coverage: Q1 2018-Q4 2024. Insurance: Q2 2020-Q4 2024.
This legacy series is kept separate from PhonePe's 2026 restated dataset.

To rebuild the database, install Git, stop the dashboard and run `python load_data.py`.

Registered users are cumulative. PIN-code rankings cover published top subsets.
All India totals sum state records; some historical national totals differ slightly.
District boundaries are older; unmatched districts remain in numerical results.

PhonePe data is licensed under CDLA-Permissive-2.0; see
`data/PHONEPE_DATA_LICENSE.txt`. Map attribution and applicable usage terms are
in [assets/SOURCES.md](assets/SOURCES.md). District maps use GADM data for
academic/non-commercial use. This project is intended for education.
