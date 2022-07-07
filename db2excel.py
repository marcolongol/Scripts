import os
import sys
from collections import namedtuple
import pandas as pd
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

DBNAME = "Polaris Production"
BASE_DIR = Path(__file__).parent.absolute()
OUTPUT_FILE = BASE_DIR / "SmartCM.xlsx"

DBConnection = namedtuple(
    "DBConnection", ["name", "host", "port", "service", "user", "pwd"]
)

Table = namedtuple("Table", ["tablename", "description", "query"])

DBSet = [
    DBConnection(
        "Polaris Production",
        "gbl-prfcm11.eitoracle.gsm1900.org",
        "7732",
        "prfcm1",
        os.environ["DB_USER"],
        os.environ["DB_PASS"],
    )
]

tables = [
    Table(
        "Prediction_Model",
        """Table that holds the prediction model information.""",
        """SELECT * FROM PREDICTION_MODEL""",
    )
]

if __name__ == "__main__":
    DB = filter(lambda x: x.name == DBNAME, DBSet)[0]
    try:
        logging.info(f"Starting Connection to {DB.name}...")
        engine = sqlalchemy.create_engine(
            f"oracle+cx_oracle://{DB.user}:{DB.pwd}@{DB.host}:{DB.port}/?service_name={DB.service}",
            arraysize=1000,
        )
        logging.info(f"Retrieving Tables...")
        for table in tables:
            df = pd.read_sql(table.query, engine)
            df.to_excel(OUTPUT_FILE, sheet_name=table.tablename, index=False)
    except SQLAlchemyError as e:
        print(e)
