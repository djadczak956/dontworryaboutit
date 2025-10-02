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
    cursor = connection.cursor()
    sql = f"SELECT * FROM Wines WHERE wineID = {wine_ID_input}"
    cursor.execute(sql)

    print("Wines Information")
    for wine_ID, brand, class_type, alcohol, appellation, net_content, bottler_name in cursor:
        print(f"Wine ID: {wine_ID}")
        print(f"Brand Name: {brand}")
        print(f"Class/Type: {class_type}")
        print(f"Alcohol: {alcohol}%")
        print(f"Appellation: {appellation}")
        print(f"Net Content: {net_content}")
        print(f"Bottler: {bottler_name}")

    cursor.close()


# ----------- Reps ---------------------------------
def reps(connection):
    rep_login = input("Enter Company Rep login name: ")
    cursor = connection.cursor()

    labels = "R.loginName, repID, name, phone, email, companyName"
    reps_select = "SELECT loginName, repID, companyName FROM Reps"
    accounts_select = "SELECT loginName, name, phone, email FROM Accounts"

    sql = f'''SELECT {labels} FROM ({reps_select}) R JOIN ({accounts_select}) A 
        ON R.loginName = A.loginName WHERE R.loginName = \'{rep_login}\''''
    cursor.execute(sql)

    print("Company Representative Information")
    for login_name, rep_ID, full_name, phone, email_address, company_name in cursor:
        print(f"Login Name: {login_name}")
        print(f"RepID: {rep_ID}")
        print(f"Full Name: {full_name}")
        print(f"Phone: {phone}")
        print(f"Email Address: {email_address}")
        print(f"Company Name: {company_name}")

    

# ----------- Wine Label Form ---------------------------------
def forms(connection):
    form_ID_input = input("Enter Wine Label Form ID: ")
    
    cursor = connection.cursor()
    labels = "F.formID, F.status, W.brand, F.vintage, ACC_R.name"

    forms_select = "SELECT formID, wineID, status, vintage, repID FROM Forms WHERE formID = " + form_ID_input

    sql1 = f"""SELECT {labels} FROM ({forms_select}) F 
    JOIN Wines W
        ON F.wineID = W.wineID
    JOIN Reps R
        ON F.repID = R.repID
    JOIN Accounts ACC_R
        ON R.loginName = ACC_R.loginName"""
    
    cursor.execute(sql1)
    c1 = cursor.fetchone()

    process_select = "SELECT ttbID, formID FROM Process WHERE formID = " + form_ID_input
    agents_select = "SELECT ttbID, loginName from Agents"
    accounts_select = "SELECT loginName, name FROM Accounts"
    
    sql2 = f"""SELECT name FROM ({process_select}) P
    JOIN ({agents_select}) A ON P.ttbID = A.ttbID
    JOIN ({accounts_select}) ACC_A ON A.loginName = ACC_A.loginName
    """
    cursor.execute(sql2)
    c2 = cursor.fetchall()

    print("Wine Label Form Information")

    print(f"Form ID: {c1[0]}")
    print(f"Status: {c1[1]}")
    print(f"Wine Brand: {c1[2]}")
    print(f"Vintage: {c1[3]}")
    print(f"Company Rep Full Name: {c1[4]}")
    if len(c2) == 0:
        print("N/A") 
    else:
        # please do not worry about this very stupid way to print out the agent names nicely
        agent_names_cleaned = map(lambda x: "".join(filter(lambda char: char not in ("()'"), x)), c2)
        print(*list(agent_names_cleaned), sep=", ")
        


# ----------- Update Phone ---------------------------------
def updatePhone(connection):
    login_input = input("Enter Company Rep Login Name: ")
    phone_input = input("Enter the Updated Phone Number: ")

    cursor = connection.cursor()

    sql = f""" UPDATE Accounts
        SET phone = '{(phone_input)}'
        WHERE loginName = '{login_input}'"""
    
    cursor.execute(sql)
    connection.commit()

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
    if (len(sys.argv) < 2):
        print("Username and password should be included as parameters.")
        sys.exit()

    main()

