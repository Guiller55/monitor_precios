import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def detectar_tienda(url: str) -> str:
    """
    Funcion que usa urlparse para buscar a que sitio pertenece el enlace.

    Args:
        url (str): URL
    
    
    Returns:
        str: Palabra clave del sitio al que pertenece
    """
    dominio = urlparse(url).netloc.lower()
    
    if "amazon" in dominio:
        return "amazon"
    elif "mercadolibre" in dominio:
        return "mercadolibre"
    else:
        return "desconocida"

def obtener_precio(url: str) -> float:
    """
    Funcion que visita un enlace de mercado libre y obtiene el precio del producto.

    Args:
        url (str): URL del articulo
    
    Returns:
        float: Precio del articulo
    """
    # User-Agent para hacer creer a Mercado Libre que se pide
    # desde un navegador
    headers = {
        'authority': 'www.amazon.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'device-memory': '8',
        'downlink': '10',
        'ect': '4g',
        'rtt': '50',
        'sec-ch-device-memory': '8',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'viewport-width': '1920'
    }

    # Se encuentra el sitio
    sitio = detectar_tienda(url)

    try:
        # Descarga la página
        respuesta = requests.get(url, headers=headers)
        respuesta.raise_for_status() #Error si no existe la página

        # Usa soup para navegar en el html
        soup = BeautifulSoup(respuesta.text, 'html.parser')

        # Busca de forma diferente dependiendo del sitio
        precio_real = None
        if (sitio == 'mercadolibre'):
            padre = soup.find('div', class_='ui-pdp-price__second-line') # Aqui selecciona la etiqueta div con esa class
            if padre:
                precio_real = padre.find('span', class_='andes-money-amount__fraction') # Dentro de esa busca la etiqueta span con esa clase
        elif (sitio == 'amazon'):
            padre = soup.find('div', id='corePriceDisplay_desktop_feature_div')
            if padre:
                precio_real = padre.find('span', class_='a-price-whole')

        # Si lo encontró le quita las comas
        if precio_real:
            precio_real = precio_real.text.replace(',', '')
            return float(precio_real)
        else:
            print("No se encontró la etiqueta del precio. " \
            "puede que la clase haya cambiado o que el producto" \
            "no se encuentre disponible")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return None
    except ValueError:
        print("Se encontró el elemento pero hubo un error al" \
        "convertirlo a número.")
        return None

#Prueba
if __name__ == "__main__":
    #url_prueba = "https://www.mercadolibre.com.mx/cargador-pilas-recargables-duracell-cef-7-aa-aaa-c-4-aa-baterias/p/MLM28200091#polycard_client=search-desktop&search_layout=grid&position=5&type=product&tracking_id=2bfa2cc1-f036-48f9-bcc2-8cafe96982d6&wid=MLM2319150661&sid=search"
    url_prueba = "https://www.amazon.com/Monster-High-McFlytrap-Chewlian-Accessories/dp/B0CMGQK5D7?crid=1C0SFUGIIQTIN&dib=eyJ2IjoiMSJ9.U0i0p1PpJAt7GsE9I8xxDIAFTtoL26Sg8z_KJSUaog8oWGuwtEehBpp2PM4vnCV91RMFMcHnR97OZhMZDuBTE0N25_87BxkEXNrMYSrBTiNi2jbJuNv6sSQ-Asw5rfLGkbqItc96-hpZwY5CqV6YyAs-XVj2imCiyDNezzRSU_1_DZRqjIIjq7GC6Q85NnzmYrE31xR7qd1zVReN4qU9gieVG3wm6b8hK1bCUPTWCiq-5PBTnpgTm-lnV16SW4KT8ItctNnrzkM_aYG5rNV-k-lhiNwJ539IQKQ0HAEB3RA.fXhFUciV9Vb0w4qbQhICznGBk4nP-dQaueQxV6bc-R0&dib_tag=se&keywords=creeproduction%2Bmonster%2Bhigh%2Bvenus&qid=1773021063&sprefix=%2Caps%2C139&sr=8-1&th=1"
    #url_prueba = "https://www.amazon.com/Monster-High-Birthday-Draculaura-Accessories/dp/B0DLCHQFFH?dib=eyJ2IjoiMSJ9.U0i0p1PpJAt7GsE9I8xxDIAFTtoL26Sg8z_KJSUaog8oWGuwtEehBpp2PM4vnCV91RMFMcHnR97OZhMZDuBTE0N25_87BxkEXNrMYSrBTiNi2jbJuNv6sSQ-Asw5rfLGkbqItc96-hpZwY5CqV6YyAs-XVj2imCiyDNezzRSU_1_DZRqjIIjq7GC6Q85NnzmQw0dg369p0wICey3gx4u87wyC2eKQRTad8j5RTI529e-5PBTnpgTm-lnV16SW4KT8ItctNnrzkM_aYG5rNV-k-lhiNwJ539IQKQ0HAEB3RA.TSTn7bfP9HrxC3MQwHj4Dqv3Q6IW6GkmeZ66BY-xDKY&dib_tag=se&keywords=creeproduction%2Bmonster%2Bhigh%2Bvenus&qid=1773023851&sr=8-35&th=1"

    precio = obtener_precio(url_prueba)

    if precio:
        print(f"Exito {precio}")