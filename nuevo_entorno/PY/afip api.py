import requests

# URL del endpoint de AFIP
api_url = 'https://wswhomo.afip.gov.ar/wsfev1/service.asmx?op=FECAEAConsultar'  # Para pruebas, usa el endpoint correcto.

# Rutas al certificado y clave (actualiza las rutas a donde están los archivos correctos)
cert_path = 'C:/Users/Usuario/Downloads/GIANINNOVATE_120b3d92e5fa69c9.crt'  # Ruta del archivo CRT que descargaste
key_path = 'C:/Program Files/OpenSSL-Win64/bin/private_no_pass.key'          # Ruta del archivo KEY que generaste

# Realiza una solicitud de prueba
try:
    response = requests.get(
        api_url,
        cert=(cert_path, key_path),
        timeout=10
    )
    response.raise_for_status()
    print("Respuesta de la API:", response.text)
except requests.exceptions.RequestException as e:
    print("Error al conectar con la API:", e)
