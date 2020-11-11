import re
import pandas as pd
import mysql.connector

global connection
global cursor
global db_name


def init_connection(host, database, user, password):
    """
    Initiates the mySQL connection, sets global variables used by functions in this module
    :param host: mySQL host
    :param database: mySQL database
    :param user: mySQL user
    :param password: mySQL password
    :return: void
    """
    from mysql.connector import Error
    global connection
    global cursor
    global db_name
    db_name = database

    try:
        connection = mysql.connector.connect(host=host,
                                             database=database,
                                             user=user,
                                             password=password)
        if connection.is_connected():
            db_Info = connection.get_server_info()
            # print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # print("You're connected to database: ", record)

    except Error as e:
        print("Error while connecting to MySQL", e)
        cursor.close()
        connection.close()


def close_connection():
    """
    Closes the mySQL connection
    :return: void
    """
    if connection.is_connected():
        cursor.close()
        connection.close()
        # print("MySQL connection is closed")


def get_all_rows(table_name):
    """
    Returns a string for a query statement to retrieve all rows in a table.
    : param table_name : name of mySQL table
    : return : string containing query statment to get all the rows
    """
    return f"select * from {table_name}"


def get_columns(table_name):
    """
    Returns the list of all columns in a mySQL database.
    : param table_name : name of mySQL table
    : return cols : columns
    """
    cols = f"Select COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' ORDER BY ORDINAL_POSITION"
    return cols


def bulk_db_insert(values, table_name):
    """
    Performs a bulk insert on a table
    : param values : values to insert into database
    : return : void
    """
    columns_tuple = get_table_columns(table_name)
    value_placeholders = '(' + f"{(len(columns_tuple) - 1) * ' %s,'}" + ' %s )'
    sql = ''

    if table_name == 'DFintent':
        sql = f"INSERT INTO {table_name} (IID, response, inputCtx, outputCtx, params, fullfillment, isConversationEnd, isDuplicate, dfEvent, dfAction, trainingPhrase) VALUES {value_placeholders};"
    elif table_name == 'DFleads_to':
        sql = f"INSERT INTO {table_name} (parentIID, childIID) VALUES {value_placeholders};"
    elif table_name == 'corresponds_to':
        sql = f"INSERT INTO {table_name} (QID, IID) VALUES {value_placeholders};"

    cursor.executemany(sql, values)
    connection.commit()


def get_table_columns(table_name):
    """
    Returns a tuple list of the columns in a table in a db
    : param table_name : name of the mySQL table
    : return column_tuples : tuple of table's column names
    """
    q = f"SHOW COLUMNS FROM {db_name}.{table_name};"
    column_list = query_db(q)
    column_tuples = tuple([a_tuple[0] for a_tuple in column_list])
    column_tuples

    return column_tuples


#   # unused function
# def single_db_insert(values, db_name, table_name):
#     """
#     Inserts a single row of values into a table in a databse
#     """
#     columns_tuple = get_table_columns(db_name, table_name)
#     value_placeholders = '(' + f"{(len(columns_tuple) - 1) * ' %s,'}" + ' %s )'
#     sql = ''
#
#     if table_name == 'DFintent':
#         sql = f"INSERT INTO {table_name} (IID, response, inputCtx, outputCtx, params, fullfillment, isConversationEnd, isDuplicate, dfEvent, dfAction, trainingPhrase) VALUES {value_placeholders};"
#     elif table_name == 'DFleads_to':
#         sql = f"INSERT INTO {table_name} (parentIID, childIID) VALUES {value_placeholders};"
#     elif table_name == 'corresponds_to':
#         sql = f"INSERT INTO {table_name} (QID, IID) VALUES {value_placeholders};"
#
#     cursor.execute(sql, values)
#
#     connection.commit()
#
#
# #     print("1 record inserted, ID:", cursor.lastrowid)

def format_columns(tuples_in):
    """
    Formats columns into a list for easy parsing.
    : param tuples_in : tuples corresponding to the columns of a mySQL table from command in @get_table_columns(table_name)
    : return out : list of columns
    """
    reject = ['\(', '\)', "\'", ',']
    out = []
    for entry in tuples_in:
        entry = re.sub("|".join(reject), "", str(entry))
        out.append(entry)
    return out


def query_db(query):
    """
    Executes a given query in the mySQL database and returns the results.
    : param query : String of the query statement.
    : return records : object containing the resulting records of query
    """
    cursor.execute(query)
    records = cursor.fetchall()
    return records


def make_df_from_query(table_name):
    """
    Creates a dataframe from the results of a mySQL query on a table in the database.
    : param table_name : Table to query.
    : return df : Dataframe of the resulting records
    """
    records = query_db(get_all_rows(table_name))
    cols = format_columns(query_db(get_columns(table_name)))
    df = pd.DataFrame.from_records(records, columns=cols)
    return df
