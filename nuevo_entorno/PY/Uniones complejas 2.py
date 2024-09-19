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

    # 1. Órdenes de compra con proveedores válidos
    query = """
    SELECT o.OrdenCompraID, p.Nombre AS Proveedor
    FROM `ordenes de compra` o
    JOIN proveedores p ON o.ProveedorID = p.ProveedoresId
    """
    cursor.execute(query)
    results = cursor.fetchall()
    print("Órdenes de compra con proveedores válidos:")
    for row in results:
        print(row)

    # 2. Facturas relacionadas con proveedores y clientes
    query = """
    SELECT f.FacturaID, c.Nombre AS Cliente, p.Nombre AS Proveedor, f.Total
    FROM facturas f
    JOIN clientes c ON f.ClienteID = c.ClientesID
    LEFT JOIN proveedores p ON f.ProveedorID = p.ProveedoresId
    """
    cursor.execute(query)
    results = cursor.fetchall()
    print("\nFacturas con proveedores y clientes asociados:")
    for row in results:
        print(row)

    # 3. Ventas totales por producto
    query = """
    SELECT p.Nombre AS Producto, SUM(i.Cantidad) AS TotalVendido
    FROM items_factura i
    JOIN productos p ON i.ProductoID = p.ProductoID
    GROUP BY p.Nombre
    """
    cursor.execute(query)
    results = cursor.fetchall()
    print("\nVentas totales por producto:")
    for row in results:
        print(row)

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()
