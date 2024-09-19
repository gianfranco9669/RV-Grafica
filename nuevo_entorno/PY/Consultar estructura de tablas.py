import mysql.connector

try:
    # Conectar a la base de datos
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="99Techno.99",
        database="mydb"
    )
    cursor = connection.cursor()

    # Consultar la estructura de todas las tablas
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("Tablas en la base de datos:")
    for table in tables:
        print(table[0])

        # Consultar estructura de cada tabla
        cursor.execute(f"DESCRIBE `{table[0]}`")
        table_structure = cursor.fetchall()
        print(f"Estructura de {table[0]}:")
        for column in table_structure:
            print(column)

    # Consultar datos de la tabla 'clientes'
    cursor.execute("SELECT * FROM clientes LIMIT 10")
    result = cursor.fetchall()
    print("\nDatos en la tabla 'clientes':")
    for row in result:
        print(row)

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()
