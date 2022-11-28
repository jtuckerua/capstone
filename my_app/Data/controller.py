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

def create_query(data):
    """
    receives data based on city, state, or rent amount, and table name
    returns a dataframe
    """
    conn, cur = get_conn_cur()

    qry_str = """SELECT table_name FROM information_schema.tables
       WHERE table_schema = 'test' """
    cur.execute(qry_str)
    data = cur.fetchall()

    cur.close()
    conn.close()
    return data

def run_query(query):
  """
  This function will create unique queries
  """
  pass


