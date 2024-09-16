import mysql.connector

try:
    # Conexión a la base de datos
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="99Techno.99",
        database="mydb"
    )

    # Crear cursor
    cursor = connection.cursor()

    # Ejecutar consulta
    cursor.execute("SHOW TABLES")

    # Obtener resultados
    tables = cursor.fetchall()
    print(tables)

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Cerrar cursor y conexión
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()

