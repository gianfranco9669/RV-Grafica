import mysql.connector
from mysql.connector import Error

try:
    # Establecer la conexión a la base de datos
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='99Techno.99',  # Cambia esto si es necesario
        database='mydb'
    )

    if connection.is_connected():
        db_info = connection.get_server_info()
        print("Conectado a MySQL Server versión", db_info)
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        record = cursor.fetchone()
        print("Conectado a la base de datos:", record)

except Error as e:
    print("Error al conectar a MySQL", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexión a MySQL cerrada")

#EJECUCION DE CONSULTA

def ejecutar_consulta():
    try:
        # Establecer la conexión
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='99Techno.99',
            database='mydb'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM usuarios;")  # Reemplaza NombreDeLaTabla por el nombre de tu tabla
            rows = cursor.fetchall()
            for row in rows:
                print(row)

    except Error as e:
        print("Error al ejecutar la consulta:", e)
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a MySQL cerrada")

if __name__ == "__main__":
    ejecutar_consulta()

#CONSULTA SELECT

import mysql.connector

try:
    # Establecer la conexión
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='99Techno.99',
        database='mydb'
    )

    # Crear un cursor
    cursor = connection.cursor()

    # Ejecutar una consulta
    cursor.execute("SELECT * FROM Usuarios")

    # Obtener los resultados
    results = cursor.fetchall()

    for row in results:
        print(row)

except mysql.connector.Error as err:
    print("Error: {}".format(err))

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexión cerrada")

# DEFINIR LA ESTRUCTURA DE LOS DATOS

cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print("Tablas en la base de datos:")
for table in tables:
    print(table[0])

for table in tables:
    cursor.execute(f"DESCRIBE {table[0]}")
    columns = cursor.fetchall()
    print(f"Campos en la tabla {table[0]}:")
    for column in columns:
        print(column)
