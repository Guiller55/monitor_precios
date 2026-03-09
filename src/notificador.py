import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar las variables del archivo .env a la memoria del sistema
load_dotenv()

# Extraer las credenciales de forma segura
REMITENTE = os.getenv("EMAIL_USUARIO")
PASSWORD = os.getenv("EMAIL_PASSWORD")

def enviar_alerta(destinatario: str, nombre_producto: str, precio: float, url: str) -> None:
    """
    Empaqueta y envía un correo HTML usando SMTP y MIME.

    Args:
        destinatario (str): Cadena del correo del destinatario
        nombre_producto (str): Cadena del nombre del producto
        precio (float): Precio del producto
        url (str): Cadena con el link al producto
    """

    # Validación de seguridad: si falta el .env, el programa te avisa
    if not REMITENTE or not PASSWORD:
        print("Error: Faltan credenciales en el archivo .env")
        return

    # EMPAQUETADO (MIME):
    mensaje = MIMEMultipart()
    mensaje['From'] = REMITENTE
    mensaje['To'] = destinatario
    mensaje['Subject'] = f"🚨 Oferta detectada: {nombre_producto} a ${precio}"

    # Cuerpo del correo en HTML
    cuerpo_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #2E86C1;">El bot encontró una oferta</h2>
            <p>El producto que estás monitoreando ha bajado de precio:</p>
            <ul>
                <li><strong>Producto:</strong> {nombre_producto}</li>
                <li><strong>Precio actual:</strong> <span style="color: #27AE60; font-size: 18px;"><b>${precio}</b></span></li>
            </ul>
            <a href="{url}" style="background-color: #F1C40F; color: #000; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                Ir a la tienda
            </a>
            <p style="font-size: 12px; color: #777; margin-top: 30px;">
                * Este es un correo automatizado enviado por el script de Python de @Guiller55.
            </p>
        </body>
    </html>
    """
    
    # Empaquetar HTML en el mensaje MIME (se adjunta)
    mensaje.attach(MIMEText(cuerpo_html, 'html'))

    # ENVÍO (SMTP):
    try:
        print("Conectando al servidor SMTP de Google...")
        # Conectarse al puerto 587
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        
        # Iniciar tunel de encriptación TLS (requisito de seguridad)
        servidor.starttls()
        
        # Identificarse
        servidor.login(REMITENTE, PASSWORD)
        
        # Entregar paquete MIME
        servidor.send_message(mensaje)
        print(f"Alerta enviada exitosamente a {destinatario}")
        
    except Exception as e:
        print(f"Ocurrió un error al enviar el correo: {e}")
        
    finally:
        # Cerrar conexión al finalizar
        servidor.quit()

# Pruebas
if __name__ == "__main__":

    correo_destino = "guill3rmovalencia@gmail.com" 
    
    print("Iniciando prueba de notificador...")
    enviar_alerta(
        destinatario=correo_destino,
        nombre_producto="Laptop Gamer de Prueba",
        precio=12500.00,
        url="https://mercadolibre.com.mx"
    )