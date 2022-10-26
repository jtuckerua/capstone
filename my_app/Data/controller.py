"""
This function will be used to interact with the sql database.
"""
import psycopg2
import pandas as pd

def get_conn_cur(): # define function name and arguments (there aren't any)
  # Make a connection
  conn = psycopg2.connect(
    host="localhost",
    database="test",
    user="postgres",
    password="Guwap1017!",
    port='5432')
  
  cur = conn.cursor()   # Make a cursor after
  return(conn, cur)   # Return both the connection and the cursor

def tbl_names():
    # makes a connection to the db
    conn, cur = get_conn_cur()

    qry_str = """SELECT table_name FROM information_schema.tables
       WHERE table_schema = 'test' """
    cur.execute(qry_str)
    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


