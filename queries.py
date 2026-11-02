"""Small, readable SQL queries. Values use ? parameters."""

import sqlite3
from pathlib import Path
import pandas as pd

DATABASE = Path(__file__).resolve().parent / "data" / "phonepe.db"
# Table names come only from these fixed dictionaries, never from user text.
TABLES = {
    "Transactions": ("aggregated_transaction", "map_map", "top_map"),
    "Users": ("aggregated_user", "map_user", "top_user"),
    "Insurance": ("aggregated_insurance", "map_insurance", "top_insurance"),
}


def run_query(sql, parameters=()):
    connection = sqlite3.connect(f"{DATABASE.as_uri()}?mode=ro", uri=True)
    try:
        return pd.read_sql_query(sql, connection, params=parameters)
    finally:
        connection.close()


def periods(topic):
    table = TABLES[topic][0]
    return run_query(f"SELECT DISTINCT year, quarter FROM {table} ORDER BY year, quarter")


def state_summary(topic, year, quarter):
    table = TABLES[topic][0]
    metrics = ("SUM(registered_users) AS registered_users, SUM(app_opens) AS app_opens"
               if topic == "Users" else
               "SUM(transaction_count) AS transaction_count, SUM(amount) AS amount")
    return run_query(f"SELECT state, {metrics} FROM {table} "
                     "WHERE year = ? AND quarter = ? GROUP BY state", (year, quarter))


def districts(topic, year, quarter, state):
    table = TABLES[topic][1]
    sql = f"SELECT * FROM {table} WHERE year = ? AND quarter = ?"
    parameters = [year, quarter]
    if state != "india":
        sql += " AND state = ?"
        parameters.append(state)
    return run_query(sql, parameters)


def categories(topic, year, quarter, state):
    table = TABLES[topic][0]
    sql = (f"SELECT category, SUM(transaction_count) AS transaction_count, SUM(amount) AS amount "
           f"FROM {table} WHERE year = ? AND quarter = ?")
    parameters = [year, quarter]
    if state != "india":
        sql += " AND state = ?"
        parameters.append(state)
    return run_query(sql + " GROUP BY category ORDER BY transaction_count DESC", parameters)


def top_places(topic, year, quarter, state, entity_type, metric):
    allowed = ["registered_users"] if topic == "Users" else ["transaction_count", "amount"]
    if metric not in allowed or entity_type not in ["states", "districts", "pincodes"]:
        raise ValueError("Unknown ranking option")
    if entity_type == "states":
        data = state_summary(topic, year, quarter)
        if state != "india":
            data = data[data["state"] == state]
        return data.rename(columns={"state": "entity_name"}).sort_values(metric, ascending=False).head(10)
    if entity_type == "districts":
        data = districts(topic, year, quarter, state)
        # Keep state names: two states can have districts with the same name.
        data["entity_name"] = data["district"] + " · " + data["state"]
        return data.sort_values(metric, ascending=False).head(10)
    table = TABLES[topic][2]
    return run_query(f"SELECT entity_name, {metric} FROM {table} "
                     "WHERE year = ? AND quarter = ? AND scope_state = ? AND entity_type = ? AND entity_name IS NOT NULL "
                     f"ORDER BY {metric} DESC LIMIT 10", (year, quarter, state, entity_type))


def trend(topic, state):
    table = TABLES[topic][0]
    metrics = ("SUM(registered_users) AS registered_users, SUM(app_opens) AS app_opens"
               if topic == "Users" else
               "SUM(transaction_count) AS transaction_count, SUM(amount) AS amount")
    sql = f"SELECT year, quarter, {metrics} FROM {table}"
    parameters = []
    if state != "india":
        sql += " WHERE state = ?"
        parameters.append(state)
    return run_query(sql + " GROUP BY year, quarter ORDER BY year, quarter", parameters)
