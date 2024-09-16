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

    # Consulta compleja: Unir tablas para obtener información de facturas y clientes
    query = """
    SELECT f.FacturaID, c.Nombre, f.Total
    FROM facturas f
    JOIN clientes c ON f.ClienteID = c.ClientesID
    WHERE f.`Fecha de Comprobante` >= '2024-01-01'
    """
    cursor.execute(query)
    results = cursor.fetchall()
    print("Facturas recientes:")
    for row in results:
        print(row)

    # Otra consulta compleja: Verificar productos con ventas mayores a 100 unidades
    query = """
    SELECT p.Nombre, SUM(i.Cantidad) AS TotalVendido
    FROM items_factura i
    JOIN productos p ON i.ProductoID = p.ProductoID
    GROUP BY p.Nombre
    HAVING TotalVendido > 100
    """
    cursor.execute(query)
    results = cursor.fetchall()
    print("\nProductos con ventas mayores a 100 unidades:")
    for row in results:
        print(row)

    # Consulta para verificar integridad referencial
    query = """
    SELECT o.OrdenCompraID
    FROM `ordenes de compra` o
    LEFT JOIN proveedores p ON o.ProveedorID = p.ProveedoresId
    WHERE p.ProveedoresId IS NULL
    """
    cursor.execute(query)
    results = cursor.fetchall()
    print("\nÓrdenes de compra con proveedores no existentes:")
    for row in results:
        print(row)

    # Consulta compleja con múltiples uniones
    query = """
    SELECT o.OrdenProduccionID, e.Nombre AS Empleado, p.Nombre AS Producto, o.`Cantidad Producida`
    FROM `ordenes de producción` o
    JOIN empleados e ON o.EmpleadoID = e.EmpleadoID
    JOIN productos p ON o.ProductoID = p.ProductoID
    WHERE o.Fecha BETWEEN '2024-01-01' AND '2024-12-31'
    """
    cursor.execute(query)
    results = cursor.fetchall()
    print("\nÓrdenes de producción del año 2024:")
    for row in results:
        print(row)

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()
