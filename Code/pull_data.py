import pandas as pd
import cx_Oracle
import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))



DB_USER = "planningadmin"   # Replace with your own username
DB_PASSWORD = "planningadmin"  # Replace with your own password

# START_TIME = "'01jan23'" # Replace with your own start date
# END_TIME = "'31dec23'"  # Replace with your own end date

# STATION_DICT = {'addison': "'1420'", 
#                 'airport': "'890', '930'",
#                  'grantpark': "'1400','1490', '560', '680', '850'"
#                 }


PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
DATA_FOLDER = PATH + r'\Data'
cx_Oracle.init_oracle_client(lib_dir= DATA_FOLDER + r'\instantclient_21_13')




def main(START_TIME, END_TIME, STATION_DICT):

    # Define your Oracle connection details
    db_user = DB_USER
    db_password = DB_PASSWORD
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
        pull_data(station, cursor, start_date = START_TIME, end_date = END_TIME, STATION_DICT = STATION_DICT)

    # Close the cursor and connection
    cursor.close()
    connection.close()



def pull_data(station, cursor, start_date, end_date, STATION_DICT):
    """
    Pull data from the Oracle database
    """

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







