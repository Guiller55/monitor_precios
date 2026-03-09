# Monitor de precios

Un monitor de precios para Mercado Libre y Amazon que rastrea precios de productos específicos y los guarda en una base de datos **SQLite**.

## Características
* Scraping automático con BeautifulSoup.
* Almacenamiento local con SQLite.
* Registro de disponibilidad.

## Instalación

1. Clona el repositorio
```bash
git clone git@github.com:Guiller55/monitor_precios.git
```

## Uso

1. Instala las dependencias del requirements.txt

2. Crea la base de datos ejecutando *database.py*

3. Hay un artículo de prueba ejecutando *insertar_prueba.py*

4. Renombrar el archivo *.env.example* y modificarlo:

5. Finalmente ejecutar *main.py*