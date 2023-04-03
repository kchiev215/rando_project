import mysql.connector
from data_extraction import credentials

cnn = mysql.connector.connect(user=credentials.user, password=credentials.password, host=credentials.host,
                              database=credentials.database)
cursor = cnn.cursor()

create_db = """CREATE TABLE IF NOT EXISTS rando_project_login(
id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
username VARCHAR(50) NOT NULL,
password VARCHAR(255) NOT NULL,
email VARCHAR(100) NOT NULL,
image VARCHAR(255),
profile_description VARCHAR(255),
) AUTO_INCREMENT=2"""

cursor.execute(create_db)

# Testing database, mock data insert

add_data = """INSERT INTO rando_project_login(id, username, password, email) VALUES(0, '1234', '1234', 
'1234@test.com') """

cursor.execute(add_data)

cnn.commit()
