import pyodbc


def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=.;"
        "DATABASE=banco;"
        "Trusted_Connection=yes;"
    )
