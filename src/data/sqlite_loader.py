import sqlite3
from pathlib import Path

import pandas as pd


def load_xlsx_to_sqlite(
    xlsx_path: str,
    db_path: str,
) -> None:

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)

    excel_file = pd.ExcelFile(xlsx_path)

    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(
            xlsx_path,
            sheet_name=sheet_name,
        )

        # SQLite table names should be simple
        table_name = sheet_name.lower().strip()

        df.to_sql(
            table_name,
            connection,
            if_exists="replace",
            index=False,
        )

    connection.close()

def query_db(
    db_path: str,
    query: str,
) -> pd.DataFrame:

    connection = sqlite3.connect(db_path)

    try:
        return pd.read_sql_query(
            query,
            connection,
        )

    finally:
        connection.close()