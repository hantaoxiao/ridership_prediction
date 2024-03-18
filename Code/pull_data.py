import pandas as pd
import cx_Oracle
import time
import os

# Print the current working directory's parent directory
PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

# Set the data folder path (update the path as needed)
DATA_FOLDER = PATH + r'\Data'

cx_Oracle.init_oracle_client(lib_dir= DATA_FOLDER + r'\instantclient_21_13')

STATION_DICT = {'addison': "'1420'", 
                'airport': "'890', '930'",
                 'grantpark': "'1400','1490', '560', '680', '850'"
                }


def pull_data(station, cursor, start_date = "'01jan19'", end_date = "'31jan24'"):
    """
    Pull data from the Oracle database
    """

    # make STATION_DICT a global variable
    global STATION_DICT

    # Define the SQL query
    sql_query = f"""
        SELECT d3.year, d3.month, d3.service_date, s.sort_all, b.pubreportname AS Branch, s.name AS Station,
            SUM(nm.rides) AS rides
        FROM nm45dayall nm
        JOIN dim_daytype3 d3 ON nm.yyyymmdd = d3.dateid
        JOIN entrances e ON nm.entrance_id = e.entrance_id
        JOIN stations s ON e.station_id = s.station_id
        JOIN branches b ON s.branch_id = b.branch_id
        WHERE d3.service_date BETWEEN {start_date} AND {end_date}
        AND s.station_id IN ({STATION_DICT[station]})
        GROUP BY d3.year, d3.month, d3.service_date, s.sort_all, b.pubreportname, s.name
        ORDER BY d3.year, d3.month, d3.service_date, s.sort_all
    """

    try:
        # Execute the query
        cursor.execute(sql_query)

        # Fetch all rows
        result_rows = cursor.fetchall()

        # save the results to a dataframe
        time0 = time.time()
        df = pd.DataFrame(result_rows, columns=[col[0] for col in cursor.description])
        time1 = time.time()
        print(f"Time to fetch the data: {time1 - time0} seconds")
        df.to_csv(DATA_FOLDER + r'/Raw' + f'/{station}.csv', index=False)


    except cx_Oracle.DatabaseError as e:
        print(f"Error executing the query: {e}")

def main():
    
    # Define your Oracle connection details
    db_user = "planningadmin"
    db_password = "planningadmin"
    db_host = "10.48.69.67"
    db_port = "1521"
    db_service_name = "cpc2ds"

    # Construct the connection string
    dsn = cx_Oracle.makedsn(db_host, db_port, service_name=db_service_name)

    # Establish the connection
    connection = cx_Oracle.connect(user=db_user, password=db_password, dsn=dsn)

    # Create a cursor
    cursor = connection.cursor()

    # Pull data for each station
    for station in STATION_DICT.keys():
        pull_data(station, cursor)

    # Close the cursor and connection
    cursor.close()
    connection.close()




