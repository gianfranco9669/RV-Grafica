import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='99Techno.99',
        database='mydb'
    )

    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tablas en la base de datos:")
        for table in tables:
            print(table[0])

except pymysql.MySQLError as e:
    print("Error:", e)

finally:
    if connection:
        connection.close()
    print("Conexión cerrada")
