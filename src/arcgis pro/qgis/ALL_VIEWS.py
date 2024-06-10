import cx_Oracle

# Replace these variables with your actual database connection details
username = 'u'
password = 'p'
dsn = 'ayxap07-scan.sce.com:1526/p701DG_CGIS'  # Or 'hostname:port:SID'

# SQL query to fetch view names
query = "SELECT VIEW_NAME FROM ALL_VIEWS"

try:
    # Connect to the Oracle database
    connection = cx_Oracle.connect(username, password, dsn)
    
    # Create a cursor
    cursor = connection.cursor()
    
    # Execute the query
    cursor.execute(query)
    
    # Fetch all results
    views = cursor.fetchall()
    
    # Extract view names into a list
    view_names = [view[0] for view in views]
    
    # Print or use the view names list
    print(view_names)
    
except cx_Oracle.DatabaseError as e:
    print(f"Database connection error: {e}")

