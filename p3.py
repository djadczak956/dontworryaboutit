# Damian Jadczak and Micah Kurland-Cohen

import sys
import getpass
import oracledb

# ----------- Login ------------------------------
def login():
    USERID = sys.argv[1] # djadczak
    PASSWORD = sys.argv[2] # 12345
    DSN = "oracle.wpi.edu:1521/orcl.cs.wpi.edu"  

    try:    
        connection = oracledb.connect(
            user=USERID,
            password=PASSWORD,
            dsn=DSN
        )
        #print("Oracle Database Connected!")
    except oracledb.Error as e:
        print("Connection Failed! Check output console")
        print(e)
        exit(1)

    return connection

# ----------- Wines ---------------------------------
def wines(connection):
    wine_ID_input = input("Enter Wine ID: ")

    sql = "SELECT wineID, brand, classType, alcohol, appellation, netContent, bottlerName FROM Wines WHERE wineID = :id"

    # Use a 'with' statement for safe handling of the cursor
    with connection.cursor() as cursor:
        cursor.execute(sql, id=wine_ID_input)
        result = cursor.fetchone() # Fetch one result since wineID is a primary key

    if result:
        # Unpack the tuple for clarity
        wine_ID, brand, class_type, alcohol, appellation, net_content, bottler_name = result
        
        print("Wines Information")
        print(f"Wine ID: {wine_ID}")
        print(f"Brand Name: {brand}")
        print(f"Class/Type: {class_type}")
        print(f"Alcohol: {alcohol}%")
        print(f"Appellation: {appellation}")
        print(f"Net Content: {net_content}")
        print(f"Bottler: {bottler_name}")
    else:
        print(f"No wine found with ID: {wine_ID_input}")


# ----------- Reps ---------------------------------
def reps(connection):
    rep_login = input("Enter Company Rep login name: ")

    # The SQL query uses a named placeholder ':login_name'
    sql = """
        SELECT A.loginName, R.repID, A.name, A.phone, A.email, R.companyName
        FROM Accounts A
        JOIN Reps R ON A.loginName = R.loginName
        WHERE A.loginName = :login_name
    """
    
    with connection.cursor() as cursor:
        # The user input is passed safely as a parameter
        cursor.execute(sql, login_name=rep_login)
        result = cursor.fetchone() # Fetch one since loginName is unique

    if result:
        login_name, rep_ID, full_name, phone, email_address, company_name = result

        print("Company Representative Information")
        print(f"Login Name: {login_name}")
        print(f"RepID: {rep_ID}")
        print(f"Full Name: {full_name}")
        print(f"Phone: {phone}")
        print(f"Email Address: {email_address}")
        print(f"Company Name: {company_name}")
    else:
        print(f"No company representative found with login: {rep_login}")

    

# ----------- Wine Label Form ---------------------------------
def forms(connection):
    form_ID_input = input("Enter Wine Label Form ID: ")
    
    # LISTAGG is an Oracle function to combine strings from multiple rows.
    sql = """
        SELECT
            F.formID, F.status, W.brand, F.vintage, REP_ACC.name AS rep_name,
            LISTAGG(AGENT_ACC.name, ', ') WITHIN GROUP (ORDER BY AGENT_ACC.name) AS agent_names
        FROM Forms F
        LEFT JOIN Wines W ON F.wineID = W.wineID
        LEFT JOIN Reps R ON F.repID = R.repID
        LEFT JOIN Accounts REP_ACC ON R.loginName = REP_ACC.loginName
        LEFT JOIN Process P ON F.formID = P.formID
        LEFT JOIN Agents A ON P.ttbID = A.ttbID
        LEFT JOIN Accounts AGENT_ACC ON A.loginName = AGENT_ACC.loginName
        WHERE F.formID = :form_id
        GROUP BY F.formID, F.status, W.brand, F.vintage, REP_ACC.name
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, form_id=form_ID_input)
        result = cursor.fetchone()

        if not result:
            print(f"No form found with ID: {form_ID_input}")
            return

        form_id, status, brand, vintage, rep_name, agent_names = result
        
        print("Wine Label Form Information")
        print(f"Form ID: {form_id}")
        print(f"Status: {status}")
        print(f"Wine Brand: {brand}")
        print(f"Vintage: {vintage}")
        print(f"Company Rep Full Name: {rep_name}")
        # Use agent_names if not null, otherwise print N/A
        print(f"Agent Full Names: {agent_names if agent_names else 'N/A'}")
        


# ----------- Update Phone ---------------------------------
def updatePhone(connection):
    login_input = input("Enter Company Rep Login Name: ")
    phone_input = input("Enter the Updated Phone Number: ")

    with connection.cursor() as cursor:
        sql = """UPDATE Accounts
                 SET phone = :new_phone
                 WHERE loginName = :login"""
        
        cursor.execute(sql, new_phone=phone_input, login=login_input)
        
        # Check if any row was actually updated
        if cursor.rowcount == 0:
            print(f"Update failed. No user found with login name: {login_input}")
        else:
            connection.commit() # Only commit if the update was successful
            print(f"Phone number updated for {login_input}.")


# ----------- Main ---------------------------------
def main():
    connection = login()
    option = sys.argv[3]

    match option:
        case '1':
            wines(connection)
        case '2':
            reps(connection)
        case '3': 
            forms(connection)
        case '4': 
            updatePhone(connection)
    
if __name__ == "__main__":

    # 1. Check for insufficient arguments (must have user, pass)
    if len(sys.argv) < 3:
        print("Username and password should be included as parameters.")
        sys.exit(1)

    # 2. Handle the case where no option is provided (print menu)
    if len(sys.argv) == 3:
        print("1 – Report Wine Information")
        print("2 – Report Company Rep Information")
        print("3 – Report Wine Label Form Information")
        print("4 – Update Phone Number")
        sys.exit(0)

    # 3. Proceed if user, pass, and option are provided
    main()

