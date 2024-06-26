#GRUPO CONFORMADO POR:

# SOFÍA YORIO
# ANTONELLA GRASSI
# BRUNO CARDAMONE

# -------------------------------------------------------------------------

# Importamos los módulos necesarios:

import csv
from collections import defaultdict
from logging import disable
from math import ceil, floor
from os import read

import pydeck as pdk
import requests
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from streamlit_option_menu import option_menu

# -------------------------------------------------------------------------

# Ajustes de la interfaz de la página:
st.set_page_config(page_title="Grupo II",
                   page_icon=None,
                   layout="wide",
                   initial_sidebar_state="collapsed",
                   menu_items=None)


#Función para leer el archivo .CSV y 'cachear' los datos:
@st.cache_data
def read_csv():
    """
  Diseño de datos:
  data: dict
  encabezados: list[str]

  Signatura:
  read_csv: None -> dict

  Próposito:
  Recibe un archivo csv, lo lee y retorna un diccionario donde cada clave es el ID
  y cada valor es la información relacionada a ese ID (almacenada en forma de lista).
  Para acceder a los valores de un ID especifico se usará: diccionario[ID]

  -En caso de no poder acceder al archivo .CSV, nos devolverá un diccionario vacío.
                                                                               
  Ejemplos:
 * Si quisieramos abrir un archivo que contiene a alumnos con sus respectivos datos:
  read_csv() -> {"nombre" :["sofia","antonella"], "apellido": ["yorio","grassi"], "edad":[19,19]}

 * Si quisieramos abrir un archivo mas éste nos tira error/no es posible abrirlo 
    correctamente: 
  read_csv() -> {}
  """

    # Realiza la solicitud GET, con el dataset en formato .CSV:
    response = requests.get(
        'https://docs.google.com/spreadsheets/d/1alQCEmWB44HVaNkOZamE_g5VH72lGsmiOPtelJsLQCA/export?format=csv'
    )

    # Verificación de la solicitud:
    if response.status_code == 200:

        # Devuelve un diccionario
        data = defaultdict(list)

        # Decodificamos su contenido:
        contenido = response.content.decode("utf-8")

        # Itera sobre las filas del archivo (lo lee)
        reader = csv.reader(contenido.splitlines())
        encabezados = next(reader)

        for fila in reader:
            for indice, encabezado in enumerate(encabezados):
                data[encabezado].append(fila[indice])

        return data
    else:
        # En caso de ser una respuesta de tipo distinto de 200, indicando un error,
        # retorna un objeto vacío
        return {}


#------------------------------------


def fuentes():
    """
    Signatura:
    fuentes: None -> None

    Próposito: Modaliza las fonts que utilizamos en la página
    """
    links = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400..700&family=Nunito:ital,wght@0,200..1000;1,200..1000&family=Varela+Round&display=swap" rel="stylesheet">
    
    """
    st.markdown(links, unsafe_allow_html=True)


# -------------------------------------------------------------------------
# Resolución Página 1 - Mapa, según filtros dados:


# Selectores de filtros:
def selectorTipo(dataMain):
    """
    Diseño de datos:
    dataMain: dict
    tipo: list[str]

    Signatura:
    selectorTipo: dict -> list[str]

    Próposito: 
    Genera una lista de tipos de combustible, para que el usuario pueda seleccionar 
    entre ellas mediante un checkbox y luego retorna una lista de las opciones elegidas.

    Ejemplo:
    Diccionario_Ejemplo =
    {
    "provincia":["Buenos Aires","Córdoba","Santa Fe","Buenos Aires","Salta","San Juan"],
    "empresa": ["Pretosar","Chabas","Pegorine","Presenti","Maipu","Filippine" ], 
    "precio": ["100.0","303.0","456,89","1876","976.4","59.4"], 
    "producto": ["Gas Oil","Premium","Gas Oil", "Gas Oil", "Premium", "Gas Oil"]
    "latitud": ["-32.6754", "41.8925"," -14.3026", "22.5378", "55.0341", "-5.9337"]  
    "longitud": ["-58.6415", "12.5113", "-170.7106", "114.0165", "-3.4388", "-75.0152"]
    }

    selectorTipo(Diccionario_Ejemplo)
    Entrada (por checkbox): ["Gas Oil"]. -> Salida: ["Gas Oil"].
    Entrada (por checkbox): ["Gas Oil","Premium"]. -> Salida: ["Gas Oil","Premium"].
    """

    # Crea una lista de los tipos de combustible:
    result = []  # Resultado de la unión de tipo con su estado "opcion"
    # Manejo de los valores obtenidos:
    tipos = []
    valor = []

    # Itera sobre los valores del diccionario y crea la lista de los tipos:
    for tipo in dataMain["producto"]:
        if tipo not in tipos:
            tipos.append(tipo)

    # Crea dos columnas para mostrar las opciones del checkbox:
    col1, col2 = st.columns(2)
    with col1:
        for tipo in tipos[:3]:
            # Checkbox de Streamlit
            opcion = st.checkbox(tipo)
            result.append((tipo, opcion))

    with col2:
        for tipo in tipos[3:]:
            # Checkbox de Streamlit
            opcion = st.checkbox(tipo)
            result.append((tipo, opcion))

    # Itera sobre los resultados obtenidos y realiza el append a
    # aquellos que hayan sido seleccionados:
    for tipo, opcion in result:
        if opcion:
            valor.append(tipo)

    return valor


def selectorEmpresa(dataMain):
    """
    Diseño de datos:
    dataMain: dict
    empresas: list[str]

    Signatura:
    selectorEmpresa: dict -> list[str]

    Próposito: 
    Genera una lista de empresas, para que el usuario pueda seleccionar entre ellas 
    mediante un checkbox y luego retorna una lista de las opciones elegidas.

    Ejemplo:
    Diccionario_Ejemplo =
    {"provincia": ["Buenos Aires","Córdoba","Santa Fe","Buenos Aires","Salta","San Juan"],
    "empresa": ["Pretosar","Chabas","Pegorine","Presenti","Maipu","Filippine" ], 
    "precio": ["100.0","303.0","456,89","1876","976.4","59.4"], 
    "producto": ["Gas Oil","Premium","Gas Oil", "Gas Oil", "Premium", "Gas Oil"],
    "latitud": ["-32.6754", "41.8925"," -14.3026", "22.5378", "55.0341", "-5.9337"],  
    "longitud": ["-58.6415", "12.5113", "-170.7106", "114.0165", "-3.4388", "-75.0152"]}

    selectorEmpresa(Diccionario_Ejemplo)
    Entrada (por checkbox): ["Pretosar"]. -> Salida: ["Pretosar"].
    Entrada (por checkbox): ["Pretosar","Chabas"]. -> Salida: ["Pretosar","Chabas"].
    """

    # Crea una lista de empresas:
    result = []  # Resultado de la unión de empresa con su estado "opcion"
    # Manejo de los valores obtenidos:
    empresas = []
    valor = []

    # Itera sobre los valores del diccionario y crea la lista de las empresas:
    for empresa in dataMain["empresabandera"]:
        if empresa not in empresas:
            empresas.append(empresa)

    # Crea 4 columnas para mostrar las opciones del checkbox:
    col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 2])
    with col1:
        for empresa in empresas[:3]:
            # Checkbox de Streamlit
            opcion = st.checkbox(empresa)
            result.append((empresa, opcion))
    with col2:
        for empresa in empresas[3:6]:
            # Checkbox de Streamlit
            opcion = st.checkbox(empresa)
            result.append((empresa, opcion))

    with col3:
        for empresa in empresas[6:-2]:
            # Checkbox de Streamlit
            opcion = st.checkbox(empresa)
            result.append((empresa, opcion))

    with col4:
        for empresa in empresas[-2:]:
            # Checkbox de Streamlit
            opcion = st.checkbox(empresa)
            result.append((empresa, opcion))

    # Itera sobre los resultados obtenidos y realiza el append a aquellos que hayan
    # sido seleccionados:
    for empresa, opcion in result:
        if opcion:
            valor.append(empresa)

    return valor


def selectorProvincia(dataMain):
    """
    Diseño de datos:
    dataMain: dict
    provincias: list[str]

    Signatura:
    selectorProvincia: dict -> str

    Próposito: 
    Genera una lista de provincias, para que el usuario pueda seleccionar una de ellas 
    mediante un selectbox y luego retorna la opción elegida.

    Ejemplo:
    Diccionario_Ejemplo =
    {
    "provincia":["Buenos Aires","Córdoba","Santa Fe","Buenos Aires","Salta","San Juan"],
    "empresa": ["Pretosar","Chabas","Pegorine","Presenti","Maipu","Filippine" ], 
    "precio": ["100.0","303.0","456,89","1876","976.4","59.4"], 
    "producto": ["Gas Oil","Premium","Gas Oil", "Gas Oil", "Premium", "Gas Oil"]
    "latitud": ["-32.6754", "41.8925"," -14.3026", "22.5378", "55.0341", "-5.9337"]  
    "longitud": ["-58.6415", "12.5113", "-170.7106", "114.0165", "-3.4388", "-75.0152"]
    }

    selectorProvincia(Diccionario_Ejemplo)
    Entrada (por selectbox): "Buenos Aires". -> Salida: "Buenos Aires".
    Entrada (por selectbox): "Santa Fe". -> Salida: "Santa Fe".
    """

    # Crea una lista de provincias posibles.
    provincias = []

    # Itera sobre los valores del diccionario y crea la lista de los provincias:
    for provincia in dataMain["provincia"]:
        if provincia not in provincias:
            provincias.append(provincia)

    # Selectbox de Streamlit
    opcion = st.selectbox("-",
                          provincias,
                          placeholder="Seleccione una provincia: ",
                          index=None,
                          key="selectorProvincia",
                          label_visibility="collapsed")

    # Retorna la opción seleccionada por el usuario
    return opcion


def selectorPrecioMin(dataMain):
    """
    Diseño de datos:
    dataMain: dict
    precios: list[float]

    Signatura:
    selectorPrecioMin: dict -> float

    Próposito: 
    Encuentra el rango de precios desde el más bajo hasta el más alto, y permite que el 
    usuario seleccione el precio minimo que quiera ver en el mapa mediante un slider.

    Ejemplo:
    Diccionario_Ejemplo =
    {
        "provincia":["Buenos Aires","Córdoba","Santa Fe",
                     "Buenos Aires","Salta","San Juan"],
        "empresa": ["Pretosar","Chabas","Pegorine","Presenti","Maipu","Filippine" ], 
        "precio": ["100.0","303.0","456,89","1876","976.4","59.4"], 
        "producto": ["Gas Oil","Premium","Gas Oil", "Gas Oil", "Premium", "Gas Oil"]
        "latitud": ["-32.6754", "41.8925"," -14.3026", "22.5378", "55.0341", "-5.9337"]
        "longitud": ["-58.6415", "12.5113", "-170.7106", 
                     "114.0165", "-3.4388", "-75.0152"]
    }

    selectorPrecioMin(Diccionario_Ejemplo)
    Entrada (por slider): "670". -> Salida: 670.0
    Entrada (por slider): "784". -> Salida: 784.0
    """

    precios = []

    # Crea una lista con todos los precios
    for precio in dataMain["precio"]:
        precios.append(floor(float(precio)))

    # Encuentra el rango de precios desde el más bajo hasta el más alto
    precioMin = min(precios)
    precioMax = max(precios)

    # Slider de Streamlit
    precio_min = st.slider("Precio Mínimo:",
                           precioMin,
                           precioMax,
                           precioMin,
                           label_visibility="visible")

    # Retorna el precio minimo seleccionado por el usuario
    return float(precio_min)


def selectorPrecioMax(dataMain):
    """
    Diseño de datos:
    dataMain: dict
    precios: list[float]

    Signatura:
    selectorPrecioMax: dict -> float

    Próposito: 
    Encuentra el rango de precios desde el más bajo hasta el más alto, y permite que el 
    usuario seleccione el precio máximo que quiera ver en el mapa mediante un slider.

    Ejemplo:
    Diccionario_Ejemplo =
    {"provincia":["Buenos Aires","Córdoba","Santa Fe","Buenos Aires","Salta","San Juan"],
    "empresa": ["Pretosar","Chabas","Pegorine","Presenti","Maipu","Filippine" ], 
    "precio": ["100.0","303.0","456,89","1876","976.4","59.4"], 
    "producto": ["Gas Oil","Premium","Gas Oil", "Gas Oil", "Premium", "Gas Oil"]
    "latitud": ["-32.6754", "41.8925"," -14.3026", "22.5378", "55.0341", "-5.9337"]  
    "longitud": ["-58.6415", "12.5113", "-170.7106", "114.0165", "-3.4388", "-75.0152"]}

    selectorPrecioMax(Diccionario_Ejemplo)
    Entrada (por slider): "670". -> Salida: 670.0
    Entrada (por slider): "784". -> Salida: 784.0
    """

    precios = []

    # Crea una lista con todos los precios
    for precio in dataMain["precio"]:
        precios.append(ceil(float(precio)))

    # Encuentra el rango de precios desde el más bajo hasta el más alto
    precioMin = min(precios)
    precioMax = max(precios)

    # Slider de Streamlit
    precio_max = st.slider("Precio Máximo:",
                           precioMin,
                           precioMax,
                           precioMax,
                           label_visibility="visible")

    # Retorna el precio máximo seleccionado por el usuario
    return float(precio_max)


# Filtrado:
def getdataMap(valor, newData, datatype, precio=None):
    """
    Diseño de datos:
    valor: str or float or list
    newData: dict
    datatype: str
    precio: str
    index_notInFilter: list

    Signatura:
    getdataMap: (str or float,dict,str,str) -> dict

    Próposito:
    Está función es la encargada en filtrar los datos para que después puedan ser 
    mostrados en el mapa. Su objetivo es sacar del diccionario cada ubicación que no 
    cumpla con el filtro dado por el usuario.
    Es decir, si el usuario selecciona una provincia (datatype), por ejemplo 
    Buenos Aires (valor), entonces sacará del diccionario cada ubicación, utilizando su 
    index, cuyo valor de la clave "provincia" no sea Buenos Aires.
    
    Para hacer esto, primero crea una lista (index_notInFilter) con todos los indices 
    de las ubicaciones que no cumplen con el filtro, y luego elimina cada uno de esos 
    indices en cada clave del diccionario relevante para los filtros.

    Ejemplo:
    Diccionario_Ejemplo =
    {"provincia":["Buenos Aires","Córdoba","Santa Fe","Buenos Aires","Salta","San Juan"],
    "empresa": ["Pretosar","Chabas","Pegorine","Presenti","Maipu","Filippine" ], 
    "precio": ["100.0","303.0","456,89","1876","976.4","59.4"], 
    "producto": ["Gas Oil","Premium","Gas Oil", "Gas Oil", "Premium", "Gas Oil"]
    "latitud": ["-32.6754", "41.8925"," -14.3026", "22.5378", "55.0341", "-5.9337"]  
    "longitud": ["-58.6415", "12.5113", "-170.7106", "114.0165", "-3.4388", "-75.0152"]}

    ("Buenos Aires", Diccionario_Ejemplo, "provincia") ->
    {"provincia":["Buenos Aires","Buenos Aires"],
    "empresa": ["Pretosar","Presenti"], # Quedan solamentes los valores que compartan indice
    "precio": ["100.0","1876"],         # con el valor Buenos Aires en la clave "provincia"
    "producto": ["Gas Oil", "Gas Oil"]
    "latitud": ["-32.6754", "22.5378"]  
    "longitud": ["-58.6415", "114.0165"]}

    """
    # Crea una lista vacia para guardar los indices de las ubicaciones que no
    # cumplen con el filtro.
    index_notInFilter = []

    # Revisa si el filtro es de tipo precio.
    if datatype == "precio":
        # Revisa si el valor dado por el usuario es el precio máximo permitido
        if precio == "Max":
            for i in range(len(newData[datatype])):
                # Revisa si el precio de la ubicación es mayor al
                # precio máximo permitido.
                if valor < float(newData[datatype][i]):
                    # Si es así, agrega el indice de esa ubicación a la lista de
                    # indices que no cumplen con el filtro.
                    index_notInFilter.append(i)

        # Realiza lo mismo que el anterior si el precio es menor o igual al valor dado.
        if precio == "Min":
            for i in range(len(newData[datatype])):
                if valor >= float(newData[datatype][i]):
                    index_notInFilter.append(i)

    elif datatype == "empresabandera" or datatype == "producto":
        for i in range(len(newData[datatype])):
            # Si no es del tipo precio, simplemente compara si el valor del i-ésimo
            # elemento de la lista de la clave del filtro es distino al valor
            # dado por el usuario.
            if newData[datatype][i] not in valor:
                index_notInFilter.append(i)

    else:
        for i in range(len(newData[datatype])):
            # Si no es del tipo precio, simplemente compara si el valor del i-ésimo
            # elemento de la lista de la clave del filtro es distino al valor
            # dado por el usuario.
            if valor != newData[datatype][i]:
                index_notInFilter.append(i)

    # Elimina las ubicaciones en los indices que no cumplen con el filtro.
    for i in sorted(index_notInFilter, reverse=True):
        del newData["latitud"][i]
        del newData["longitud"][i]
        del newData["provincia"][i]
        del newData["empresabandera"][i]
        del newData["producto"][i]
        del newData["precio"][i]

    # Retorna el diccionario filtrado
    return newData


def test_getdataMap():
    # Función de testeo de getdataMap
    Diccionario_Ejemplo = {
        "provincia": [
            "Buenos Aires", "Córdoba", "Santa Fe", "Buenos Aires", "Salta",
            "San Juan"
        ],
        "empresabandera":
        ["Pretosar", "Chabas", "Pegorine", "Presenti", "Maipu", "Filippine"],
        "precio": ["100.0", "303.0", "456,89", "1876", "976.4", "59.4"],
        "producto":
        ["Gas Oil", "Premium", "Gas Oil", "Gas Oil", "Premium", "Gas Oil"],
        "latitud":
        ["-32.6754", "41.8925", " -14.3026", "22.5378", "55.0341", "-5.9337"],
        "longitud": [
            "-58.6415", "12.5113", "-170.7106", "114.0165", "-3.4388",
            "-75.0152"
        ]
    }

    assert (getdataMap("Buenos Aires", Diccionario_Ejemplo, "provincia") == {
        "provincia": ["Buenos Aires", "Buenos Aires"],
        "empresabandera": ["Pretosar", "Presenti"],
        "precio": ["100.0", "1876"],
        "producto": ["Gas Oil", "Gas Oil"],
        "latitud": ["-32.6754", "22.5378"],
        "longitud": ["-58.6415", "114.0165"]
    })


# MAPA:
def mapaVacio():
    """
    Signatura:
    mapaVacio: None -> None
    
    Próposito:
    Muestra en pantalla un mapa vacío de Argentina, para ser utilizado como estado 
    inicial, cuando se limpian los filtros, o cuando ninguna ubicación cumple 
    con los filtros dados.
    """

    # Crea la capa vacía del mapa.
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=[],
        get_position=["lat", "lon"],
        get_radius=200,
    )

    # Crea el estado de vista con coordenadas aproximadas de Argentina.
    view_state = pdk.ViewState(latitude=-38.416097,
                               longitude=-63.616672,
                               zoom=3,
                               bearing=0)

    # Genera el pydeck que muestra el mapa.
    deck = pdk.Deck(layers=[layer],
                    map_style="light",
                    initial_view_state=view_state)
    st.pydeck_chart(deck)


def mapa(dataMain,
         provincia=None,
         empresa=None,
         tipo=None,
         precioMax=None,
         precioMin=None):
    """
    Diseño de datos:
    dataMain: dict
    provincia: str
    empresa: str
    tipo: str
    precioMax: float
    precioMin: float
    newData: dict

    Signatura:
    mapa: dict str list[str] list[str] float float -> None

    Próposito:
    Esta función se encarga de mostrar en pantalla un mapa de Argentina destacando 
    ubicaciones en acuerdo a los valores brindados por el usuario, 
    en la funcion pantalla1_Mapa.
    Esta función crea un nuevo diccionario cuyos valores, originalmente todos 
    los del dataset, son modificados según cada filtro con la función getdataMap, 
    y luego se accede a los valores modificados de latitud y longitud en el diccionario
    para darle las ubicaciones a destacar al mapa.
    Si no se cumple ningún filtro, se muestra un mapa de Argentina vacío usando pydeck.
    """
    # Genera un nuevo diccionario que pueda ser modificable.
    newData = dataMain

    # Modifica los valores del diccionario newData según los filtros dados.
    if provincia:
        newData = getdataMap(provincia, newData, "provincia")
    if empresa:
        newData = getdataMap(empresa, newData, "empresabandera")
    if tipo:
        newData = getdataMap(tipo, newData, "producto")
    if precioMax:
        newData = getdataMap(precioMax, newData, "precio", "Max")
    if precioMin:
        newData = getdataMap(precioMin, newData, "precio", "Min")

    # Accede a los valores de latitud y longitud del diccionario newData y crea dos listas.
    latitudes = [float(lat) for lat in newData["latitud"] if lat]
    longitudes = [float(lon) for lon in newData["longitud"] if lon]

    # Lista de diccionarios para st.map con las ubicaciones a destacar.
    dataUbicacion = [{
        "lat": lat,
        "lon": lon
    } for lat, lon in zip(latitudes, longitudes)]

    if dataUbicacion:
        # Muestra el mapa si existen ubicaciones a destacar en el diccionario
        st.map(dataUbicacion, color="#669bbc90", use_container_width=True)
    else:
        # Si no existen ubicaciones a destacar, muestra un mapa vacio de Argentina
        mapaVacio()


# Función para imprimir la pantalla del Mapa:
def pantalla1_Mapa(dataMain):
    """
    Diseño de datos: 
    provincia: list[str]
    empresa: list[str]
    tipo: list[str]
    precioMin: float
    precioMax: float

    Signatura:
    pantalla1_mapa(): dict -> None

    Próposito: Muestra en pantalla los filtros y el mapa para que el usuario los pueda 
    usar a libre elección y determinar qué tan preciso será el mapa de los combustibles.

    EJEMPLO:
    data1 = {
        "provincia": ["Buenos Aires", "Córdoba", "Santa Fe", "Buenos Aires", 
                      "Salta","San Juan","Buenos Aires"],
        "empresabandera": ["Pretosar", "Chabas", "Pegorine", 
                           "Presenti", "Maipu", "Filippine"],
        "precio": ["100.0", "303.0", "456,89", "1876", "976.4", "59.4","500"],
        "producto":["Gas Oil", "Premium", "Gas Oil", 
                    "Gas Oil", "Premium", "Gas Oil","Super"],
        "latitud": ["-32.6754", "41.8925", " -14.3026", 
                    "22.5378", "55.0341", "-5.9337","54.343"],
        "longitud": ["-58.6415", "12.5113", "-170.7106", 
                     "114.0165", "-3.4388","-75.0152","45.334"]
        }

    pantalla1_Mapa(data1)--> (1) v (2) v (3)

    *(1): Si seleccionamos 'provincia = San Juan' y 'producto = Premium' 
    se mostrará en pantalla un mapa vacío.
    *(2): Si seleccionamos 'provincia=San Juan' y 'producto=Gas Oil' 
    se mostrará en pantalla un mapa con las coordenadas destacadas: [(-5.9337,-75.0152)].
    *(3): Si seleccionamos 'provincia = Buenos Aires' , 'producto= Premium, Gas Oil' y 'precioMax = 1000' 
    se mostrará en pantalla un mapa con las coordenadas destacadas: [(-32.6754,-58.6415)]
    """
    # Crea el estilo para la página usando CSS
    css_pagina = """
    <style>
    
    /* Color de toda la ventana*/
    .main {
       background: #09293d;    
    }
    
    /* Card centrado: */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    /*Para que el texto no quede amontonado*/
    p {
        margin-bottom: 0px;
    }
    
    /* Color encabezado */
    [data-testid="stHeader"] {
        background-color: #09293d;
        color: #fff;
    }
    
    #stVerticalBlock {
        column-gap: 10px;
    }
    </style>
    """
    st.markdown(css_pagina, unsafe_allow_html=True)

    st.markdown(
        "<p style='color: white; font-weight:light; font-size: 20px; text-align: center;font-family: \"Varela Round\", sans-serif; font-style: normal; text-wrap: nowrap; margin-bottom: 2rem;'> Seleccione los parámetros de interés y presione buscar para poder visualizarlos en el mapa: </p>",
        unsafe_allow_html=True)

    with stylable_container(
            key="map_coloreable",
            css_styles="""{ background-color: #540b0eff;
                            width: 100%;
                            border-radius: 20px;
                            padding: 25px;
                            padding-top: 5px;
                            }
                            """,
    ):
        # Crea el estilo para los selectores de los filtros usando CSS
        css_selectores = """<style>

            /*-----ESTILOS DEL SELECTBOX:------*/
            
            /* Estilo */
            .stSelectbox div[data-baseweb="select"] > div {
                background-color: #669bbc90;
                border-color: white;
                border-radius: 0px;
            }

            /* color label */
            .stSelectbox div[data-baseweb="select"] > div > div > div {
                color: white;
            }

            /* Color de la flecha*/
            [data-baseweb="select"] {
                svg {
                    color: #fff;
                }
            }

            /* Estilo del fondo */
            [data-testid="stVirtualDropdown"] {
                background-color:  #003049b9 !important;
                border: 0.3px solid white !important;
                border-radius: 0px !important;
                backdrop-filter: blur(2px) !important;
                li {
                    color: #fff;
                }
            }

            /* Fondo BLUR */
            [data-baseweb="popover"] div {
                background: none !important;
                color: white;
            }

            /* estilo del fondo */
            [data-baseweb="popover"] {
                background: #003049b9 !important;   

            }

            /*---- ESTILO DEL CHECKBOX -----*/

            /* Focus */
            .st-emotion-cache-2n7b7j {
                background-color: #669bbc90;
            }
            .st-emotion-cache-2n7b7j:hover {
                background-color: #669bbc90;
            }

            /* color letra */
            [data-baseweb="checkbox"] p {
                color: white;
            }

            /* estilo de las casillas */
            [data-testid="stCheckbox"] label span {
                background-color: #669bbc90;
                border: 0.6mm ridge white;
                border-radius: 0px;
            }

            
            

            /*--- ATRIBUTOS DEL SLIDER------*/

            /* color de la letra */
            .stSlider{
                color:white;
            }

            .stSlider > label { 
                color:white; padding-top:5px;
            }

            /* Estilo (fondo) para el precio */
            div.stSlider > div[data-baseweb="slider"] > div[data-testid="stTickBar"] > div {
                background: #540b0eff !important;
            }

            /* Estilo para el cursor del Slider */
            div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"] {
                background-color: #669bbc;
            }

            /* Estilo para el precio seleccionado en el Slider */
            div.stSlider > div[data-baseweb="slider"] > div > div > div > div {
                color: white;
                font-weight: bold;
            }

            /* Estilo para la barra del Slider */
            div.stSlider > div[data-baseweb="slider"] > div > div {
                background: #669bbc;
            }

            /*------- Estilo para los Botones------- */
            .stButton button{
                background-color: white;
                color: #540b0eff;
                border: none; 
                width: 90%;
                height: 3rem;
            }

            /* Estilo para la letra de los Botones */
            [data-testid="stButton"] p {
                font-size: 25px;
                justify-content: center;
            }

            /* Estilo para los Botones al pasar el mouse */
            .stButton button:hover{
                color:white;
                border: none;
                background:#780000b9;
            }

        </style>"""
        st.markdown(css_selectores, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        btn1, btn2, btn3, btn4 = st.columns(4)

        # Columna de los selectores de Filtros:
        with col1:
            # Crea los títulos de los filtros usando HTML
            html_filtros = """
            <style>
            t {
                color: white; 
                font-weight: bold; 
                font-size: 18px;
                text-shadow: 2px 2px black;
                margin-bottom: 3px;
            }
            </style>
            """
            st.markdown(html_filtros, unsafe_allow_html=True)

            # Crea los selectores del filtro usando selectorProvincia
            st.markdown("<t>PROVINCIA(S):</t>", unsafe_allow_html=True)
            provincia = selectorProvincia(dataMain)

            # Crea los checkBox del filtro usando selectorEmpresa
            st.markdown("<t>EMPRESA(S):</t>", unsafe_allow_html=True)
            empresa = selectorEmpresa(dataMain)

            # Crea los checkBox del filtro usando selectorTipo
            st.markdown("<t>TIPO(S):</t>", unsafe_allow_html=True)
            tipo = selectorTipo(dataMain)

            # Crea los sliders del filtro usando selectorPrecioMax
            st.markdown("<t>RANGO DE PRECIO:</t>", unsafe_allow_html=True)
            precioMin = selectorPrecioMin(dataMain)
            precioMax = selectorPrecioMax(dataMain)

            with btn1:
                buscar = st.button("**BUSCAR**", type="primary")
            with btn2:
                limpiar = st.button("**LIMPIAR**", type="primary")

        # Columna del mapa:
        with col2:
            # Crea el estilo para el mapa usando CSS
            css_mapa = """
            <style>
            #deckgl-wrapper {
                height: 600px !important;
            }
            #view-default-view > div:nth-child(1) {
                height: 600px !important;
            }
            #view-default-view > div:nth-child(2) > div {
                height: 38px;
            }
            </style>
            """
            st.markdown(css_mapa, unsafe_allow_html=True)

            if buscar and not limpiar:  # Si se cliqueó buscar llama a la función mapa
                mapa(dataMain, provincia, empresa, tipo, precioMax, precioMin)
            else:  # Si no, llama al mapa vacío
                mapaVacio()


# -------------------------------------------------------------------------
# Resolución Página 2 – Línea de tiempo, promedio según el tipo de combustible:


def seleccion_fechas(dataMain):
    """
        Diseño de datos:
        fechas: list

        Sinatura:
        seleccion_fechas: dict -> list

        Próposito: 
        A través de la información del dataset obtenido, recolecta las fechas del mismo 
        y luego, las retorna ordenadas de forma ascendiente -- A través de una lista.

        EJEMPLOS:
        Sea data1 = {"indice_tiempo": ["2010-04", "1991-05", "2010-07"],
                     "años": ["2010", "1991"]}

        seleccion_fechas(data1) == ["1991-05", "2010-04", "2010-07"]

        Sea data2 = {
                     "indice_tiempo": ["2005-04", "2004-05", "2001-07", "1990-07", 
                                       "2004-07", "2005-02", "2005-06"],
                     "meses": ["agosto", "julio", "junio", "septiembre", "febrero"]}

        seleccion_fechas(data2) == ["1990-07", "2001-07", "2004-05", 
                                    "2004-07", "2005-02", "2005-04", "2005-06"]
    """

    fechas = []

    # Recorre el diccionario de fechas y añade a la lista las fechas evitando repetidas
    for x in range(len(dataMain["indice_tiempo"])):
        if dataMain["indice_tiempo"][x] not in fechas:
            fechas.append(dataMain["indice_tiempo"][x])

    fechas = sorted(fechas)  # La ordenamos de menor a mayor

    return fechas


def test_seleccion_fechas():
    data1 = {
        "indice_tiempo": ["2010-04", "1991-05", "2010-07"],
        "años": ["2010", "1991"]
    }
    data2 = {
        "indice_tiempo": [
            "2005-04", "2004-05", "2001-07", "1990-07", "2004-07", "2005-02",
            "2005-06"
        ],
        "meses": ["agosto", "julio", "junio", "septiembre", "febrero"]
    }

    assert (seleccion_fechas(data1) == ["1991-05", "2010-04", "2010-07"])
    assert (seleccion_fechas(data2) == [
        "1990-07", "2001-07", "2004-05", "2004-07", "2005-02", "2005-04",
        "2005-06"
    ])


def promedio_TipoFecha(gasolina_tipo, date, dataMain):
    """
    Diseño de datos:
    promedio: float
    precios: list

    Signatura:
    promedio_TipoFecha:str,str,dict->float

    Próposito: 
    Según el tipo de combustible seleccionado y la fecha seleccionada 
    (extraídos del dataset), devuelve el promedio de todos los productos 
    (es decir, las compras del combustible) que correspondan con el anterior criterio

    EJEMPLOS:
        Sea data1 = {
                    "indice_tiempo": ["2010-04", "2010-04", "1991-05", "2012-02", 
                                      "2010-04", "2010-04", "2010-12", "2002-01", 
                                      "2002-02", "2010-04"],
                    "años": ["2010", "1991"],
                    "precio": ["192", "2090", "200.4", "200", "12", "14", "140", "1442",
                               "1355", "1"],
                    "producto": ["GNC", "GNC", "Nafta (súper) entre 92 y 95 Ron", 
                                 "Gas Oil Grado 3", "GNC", "GNC", "Gas Oil Grado 2", 
                                 "Gas Oil Grado 3", "Natfa (súper) entre 92 y 95 Ron", 
                                 "GNC"]
                    }

        promedio_TipoFecha("GNC", "2010-04", data1) ==4 61.8
        (con precios = ["192", "2090", "12", 14", "1"])

        Sea data2 = {
                     "indice_tiempo": ["2004-05", "2001-07", "2024-07", "1990-07", 
                                       "2024-07", "2024-07", "2004-07", "2024-07", 
                                       "2005-02", "2024-07", "2024-07", "2005-06", 
                                       "2024-07"],
                     "meses": ["agosto", "julio", "junio", "septiembre", "febrero"],
                     "precio": ["192", "2090", "200.4", "200", "12", "14", "140", 
                                "1442", "1355", "1", "1", "4785", "140"],
                     "producto": ["GNC", "Gas Oil Grado 3", 
                                  "Nafta (premium) de más de 95 Ron", "GNC", 
                                  "Nafta (premium) de más de 95 Ron", 
                                  "Nafta (premium) de más de 95 Ron", 
                                  "Nafta (súper) entre 92 y 95 Ron", 
                                  "Nafta (premium) de más de 95 Ron", 
                                  "Gas Oil Grado 3", "Nafta (premium) de más de 95 Ron",
                                  "Nafta (premium) de más de 95 Ron", 
                                  "Gas Oil Grado 2", "Nafta (premium) de más de 95 Ron"]
                    }

        promedio_TipoFecha("Nafa Premium","2024-07",data2) == 258.63
        (con precios = ["200.4", "14", "12", "1442", "1", "1", "140"])

        Sea data3 = {"indice_tiempo": ["2004-01", "2002-03", "2002-06"], 
                     "producto": ["GNC", "Gas Oil Grado 2", "Gas Oil Grado 3"], 
                     "precio": ["20", "100", "4"]}

        promedio_TipoFecha("Gas Oil Grado 3", "2002-03", data3)==0 
        (con precios = []) OPCIÓN EN DONDE LA FECHA NO CONTIENE NINGÚN DATO DE PRECIO.
    """

    # Moficamos el nombre "Nafta (premium) de más de 95 Ron" a "Nafta Premium"
    # y "Nafta Super" a "Nafta (súper) entre 92 y 95 Ron" por estilo
    if gasolina_tipo == "Nafta Premium":
        gasolina_tipo = "Nafta (premium) de más de 95 Ron"
    elif gasolina_tipo == "Nafta Super":
        gasolina_tipo = "Nafta (súper) entre 92 y 95 Ron"

    # Inicializamos las variables:
    promedio = 0
    # Lista de precios
    precios = []

    # Recorremos el diccionario y de ser valido el indice_tiempo en ese indice y el
    # tipo de gasolina agrega el precio en ese indice a la lista de precios
    for x in range(len(dataMain["precio"])):
        # Por motivos de identacion correcta (que no supere la columna 80)
        # utilizamos () dentro de la condicion del if
        if (dataMain["indice_tiempo"][x] == date
                and dataMain["producto"][x] == gasolina_tipo):
            precios.append(float(dataMain["precio"][x]))

    if precios:  #Es decir, si la lista contiene al menos 1 valor
        promedio = round(sum(precios) / len(precios), 2)

    return promedio


def test_promedio_TipoFecha():
    data1 = {
        "indice_tiempo": [
            "2010-04", "2010-04", "1991-05", "2012-02", "2010-04", "2010-04",
            "2010-12", "2002-01", "2002-02", "2010-04"
        ],
        "años": ["2010", "1991"],
        "precio": [
            "192", "2090", "200.4", "200", "12", "14", "140", "1442", "1355",
            "1"
        ],
        "producto": [
            "GNC", "GNC", "Nafta (súper) entre 92 y 95 Ron", "Gas Oil Grado 3",
            "GNC", "GNC", "Gas Oil Grado 2", "Gas Oil Grado 3",
            "Natfa (súper) entre 92 y 95 Ron", "GNC"
        ]
    }

    # precios = ["192", "2090", "12", "14", "1"]
    assert (promedio_TipoFecha("GNC", "2010-04", data1) == 461.8)

    data2 = {
        "indice_tiempo": [
            "2004-05", "2001-07", "2024-07", "1990-07", "2024-07", "2024-07",
            "2004-07", "2024-07", "2005-02", "2024-07", "2024-07", "2005-06",
            "2024-07"
        ],
        "meses": ["agosto", "julio", "junio", "septiembre", "febrero"],
        "precio": [
            "192", "2090", "200.4", "200", "12", "14", "140", "1442", "1355",
            "1", "1", "4785", "140"
        ],
        "producto": [
            "GNC", "Gas Oil Grado 3", "Nafta (premium) de más de 95 Ron",
            "GNC", "Nafta (premium) de más de 95 Ron",
            "Nafta (premium) de más de 95 Ron",
            "Nafta (súper) entre 92 y 95 Ron",
            "Nafta (premium) de más de 95 Ron", "Gas Oil Grado 3",
            "Nafta (premium) de más de 95 Ron",
            "Nafta (premium) de más de 95 Ron", "Gas Oil Grado 2",
            "Nafta (premium) de más de 95 Ron"
        ]
    }

    # precios = ["200.4", "14", "12", "1442", "1", "1", "140"]
    assert (promedio_TipoFecha("Nafta Premium", "2024-07", data2) == 258.63)

    data3 = {
        "indice_tiempo": ["2004-01", "2002-03", "2002-06"],
        "producto": ["GNC", "Gas Oil Grado 2", "Gas Oil Grado 3"],
        "precio": ["20", "100", "4"]
    }

    # precios = []
    assert (promedio_TipoFecha("Gas Oil Grado 3", "2002-03", data3) == 0)


# Función para imprimir la pantalla de la Línea de tiempo
def pantalla2_lineaDeTiempo(dataMain):
    """
        Diseño de datos:
        dataMain: dict
        gasolinas: componente 'radio' extraído del streamlit
        fecha: componente 'slider' extraído del streamlit
        promedio: float

        Signatura:
        pantalla2_lineaDeTiempo: dict -> None

        Próposito: 
        Mostrar en pantalla una serie de opciones, para que el usuario pueda elegir el 
        tipo de combustible que prefiere con un radio,  y luego, con un slider 
        donde el usuario podrá desplazarse a la fecha de su interés, se le mostrará 
        el precio, usando la función 'promedio_TipoFecha', del tipo de combustible 
        seleccionado en la fecha seleccionada.
        -En caso de ser con fecha actual (2024): 
            Se mostrará el mensaje con tiempo verbal en Presente
        -En caso de ser con otra fecha: 
            Se mostrará el mensaje con tiempo verbal en Pasado.
        -En caso de no haber ninguna fecha en ese período: 
            Se le indicará a través de un mensaje.

        EJEMPLOS: 
        ( ACLARACIÓN, PRETENDAMOS QUE EL RESULTADO DEL PROMEDIO ES EL DEL EJEMPLO DE LA 
        ANTERIOR FUNCIÓN, 'promedio_TipoFecha' )
        ** promedio_TipoFecha("GNC", "2010-04", data1) == 461.8
        ** promedio_TipoFecha("Nafta Premium", "2024-07", data2) == 258.63
        ** promedio_TipoFecha("Gas Oil Grado 3", "2002-03", data3) == 0

        Sea data1 = {
                    "indice_tiempo": ["2010-04", "2010-04", "1991-05", 
                                       "2012-02", "2010-04", "2010-04", 
                                       "2010-12", "2002-01", "2002-02", "2010-04"],
                    "años": ["2010", "1991"],
                    "precio": ["192", "2090", "200.4", "200", "12", 
                               "14", "140", "1442", "1355", "1"],
                    "producto": ["GNC", "GNC", "Nafta (súper) entre 92 y 95 Ron", 
                                 "Gas Oil Grado 3", "GNC", "GNC", "Gas Oil Grado 2", 
                                 "Gas Oil Grado 3", "Natfa (súper) entre 92 y 95 Ron", 
                                 "GNC"]
                    }


        pantalla2_lineaDeTiempo(data1)
        Entrada: Checkbox = “GNC”. Slider = “2010-04”. -> (Se mostrará en pantalla): 
        El título y subtítulo de la página, un contenedor azul con las opciones 
        del checkbox, el slider y un contenedor rojo con el mensaje 
        "El promedio fue: $461.8"

        Sea data2 = {
                     "indice_tiempo": ["2004-05", "2001-07", "2024-07", "1990-07", 
                                       "2024-07", "2024-07", "2004-07", "2024-07", 
                                       "2005-02", "2024-07", "2024-07", "2005-06", 
                                       "2024-07"],
                     "meses": ["agosto", "julio", "junio", "septiembre", "febrero"],
                     "precio": ["192", "2090", "200.4", "200", "12", "14", "140", 
                                "1442", "1355", "1", "1", "4785", "140"],
                     "producto": ["GNC", "Gas Oil Grado 3", 
                                  "Nafta (premium) de más de 95 Ron", "GNC", 
                                  "Nafta (premium) de más de 95 Ron", 
                                  "Nafta (premium) de más de 95 Ron", 
                                  "Nafta (súper) entre 92 y 95 Ron", 
                                  "Nafta (premium) de más de 95 Ron", 
                                  "Gas Oil Grado 3", 
                                  "Nafta (premium) de más de 95 Ron", 
                                  "Nafta (premium) de más de 95 Ron", 
                                  "Gas Oil Grado 2", 
                                  "Nafta (premium) de más de 95 Ron"]
                    }

        pantalla2_lineaDeTiempo(data2)
        Entrada: Checkbox = “Nafta Premium”. 
        Slider = “2024-07”. -> (Se mostrará en pantalla): 
        El título y subtítulo de la página, un contenedor azul con las opciones 
        del checkbox, el slider y un contenedor rojo con el mensaje 
        "El promedio es: $258.63".

        Sea data3 = {
                     "indice_tiempo": ["2004-01", "2002-03", "2002-06"],  
                     "producto": ["GNC", "Gas Oil Grado 2", "Gas Oil Grado 3"],  
                     "precio": ["20", "100", "4"]
                     }

        pantalla2_lineaDeTiempo(data3)
        Entrada: Checkbox = “Gas Oil Grado 3”. 
        Slider = “2002-03”. -> (Se mostrará en pantalla): 
        El título y subtítulo de la página, un contenedor azul con las opciones 
        del checkbox, el slider y un contenedor rojo con el mensaje 
        "No hubo ningún registro de precios en esa fecha."
    """
    fechas_opcion = seleccion_fechas(dataMain)

    with st.container():
        # Crea el estilo para la página completa usando CSS
        css = """
            <style>
            .block-container {
                padding: 2rem;
            }
            .title {
                font-size: 2em;
                font-weight: 800;
                color: #540b0e;
                margin-bottom: 6px;
                font-family: "Nunito", sans-serif;
                
            }
            .subtitle {
                font-size: 1.2em;
                color: #9e2a2b;
                margin-bottom: 30px;
                font-family: "Varela Round", sans-serif;
            }
            /* LABEL: */
            .subheader {
                font-size: 25px;
                color: #fff;
                text-align: center;
                margin-bottom: 2px;
                font-family: "Nunito", sans-serif;
            }

            </style>
        """
        st.markdown(css, unsafe_allow_html=True)
        st.markdown('<div class="title"> LÍNEA DEL TIEMPO </div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="subtitle"> Podrás visualizar cuál fue el promedio, según el tipo del combustible que usted eliga, a lo largo de los años </div>',
            unsafe_allow_html=True)

        with stylable_container(key="radio_coloreable",
                                css_styles="""
                                    {
                                    background: #09293df5;
                                    padding: 6rem 0;
                                    width: 95%;
                                    margin: auto;
                                    margin-bottom: 40px;
                                    justify-content: center;
                                    border-radius:4px;
                                    }
            """):
            st.markdown(
                '<div class="subheader"> Elige el tipo de combustible: </div>',
                unsafe_allow_html=True)
            gasolinas = st.radio("-", [
                "GNC", "Gas Oil Grado 2", "Gas Oil Grado 3", "Nafta Super",
                "Nafta Premium"
            ],
                                 label_visibility="collapsed",
                                 index=0,
                                 horizontal=True,
                                 key="radio_gasolinas")

        fecha = st.select_slider("-",
                                 options=fechas_opcion,
                                 label_visibility="hidden",
                                 key="fechas_slider")

        # Crea el estilo para st.radio usando CSS
        css_radio = """
            <style>
            
            /* Tamaño text*/
            [data-testid="stMarkdownContainer"] p {
                font-size: 20px;
                font-family: "Nunito", sans-serif;
            }

            /* center button radio */
            label[data-baseweb="radio"] {
                display: flex;
                align-items:center;
                p {
                    margin-top: 0.1rem
                }
            }

        
            /* COLOR LETRAS Y RADIO CUADRADO */
            [data-baseweb="radio"] div {
                color: white;
                border-radius: 2px;
            }

            /* CENTRAR CHECKBOX*/
            .stRadio > div[role="radiogroup"] {
                justify-content: center;
                margin-top: 1rem;
            }
        
            /* FONDO NADA CUANDO NO SELECCIONADO */
            input[type="radio"] + div {
                background: none !important;
             }

            /* BORDE DEL CHECK RADIO*/
            div.row-widget.stRadio > div[role="radiogroup"] > 
            label[data-baseweb="radio"] > div{
                background: #669bbc8f;
            }
            </style>
            """

        st.markdown(css_radio, unsafe_allow_html=True)

        # Crea el estilo para el st.slider usando CSS
        css_slider = """
            <style>
            /* colorMinMax */
            div.stSlider>div[data-baseweb="slider"]>div[data-testid="stTickBar"] > div  {
                color: #003049ff;
                font-size: 20px;
                font-weight: 600;
                width: 10%;
                margin: 0px;
                margin-left: 30px;
                background: white;
            }
            
            /* Slider_Cursor */
            div.stSlider>div[data-baseweb="slider"]>div>div>div[role="slider"]{
                background-color: #540b0eff;
            }
            
            /* Slider_Cursor_hover */
            div.stSlider>div[databaseweb="slider"]>div>div>div[role="slider"]:hover{
                color:  #892428;
            }
            
            /* Slider_Number */
            div.stSlider>div[data-baseweb="slider"]>div>div>div>div{
                color: white;
                background: #540b0eff;
                padding: 7px;
                position: relative;
                top: -30px;
                border-radius: 20px 20px 20px 2px !important;
                margin-left: 4.8rem;
            }
            
            /* ColorSlider */
            div.stSlider > div[data-baseweb="slider"] > div > div { 
                background: linear-gradient(to right, #003049ff 0%, 
                            #09293df5 25%, #669bbc90 75%, #E3E3E3 100%);
                width: 90%;
                margin: auto;
            }
            </style>
        """

        st.markdown(css_slider, unsafe_allow_html=True)

        #------------------------------------------------

        promedio = promedio_TipoFecha(gasolinas, fecha, dataMain)

        with stylable_container(key="promedio",
                                css_styles=""" {
                                background: #540b0eff;
                                padding-top: 1.3rem;
                                padding-bottom: 2.5rem;
                                margin: auto;
                                border-radius: 4px;
                                }
                            """):

            css_promedio = """
                <style>
                .caja {
                    font-size: 20px;
                    color: white; 
                    justify-content: center;
                    display: flex;
                    gap: .5rem;
                    font-family: "Varela Round", sans-serif;
                }
                span {
                    font-weight: 700;
                }
                </style>
            """
            st.markdown(css_promedio, unsafe_allow_html=True)
            if promedio == 0:
                st.markdown(
                    "<div class='caja'> No hubo ningún registro de precios en esa fecha. </div>",
                    unsafe_allow_html=True)
            else:
                if "2024" in fecha:
                    st.markdown(
                        f"<div class='caja'>El promedio es: <span>${promedio}</span></div>",
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"<div class='caja''> El promedio fue: <span> ${promedio} </span> </div>",
                        unsafe_allow_html=True)


# -------------------------------------------------------------------------
# Resolución Página 3 – Tabla de Promedio por Provincia:


def promedio_Tabla(precios, num):
    """
      Diseño de datos: 
      precio: List[Number]
      num: List[Number]
      
      Signatura: 
      promedio_Tabla: List[Number] List[Number] -> List[Number]
      
      Próposito: Toma una lista de suma de precios y divide por la cantidad de veces 
                 que se sumó cada uno, para obtener un promedio de estos.
      
      Ejemplos:    
      promedio_Tabla([100, 200, 300], [3, 3, 3]) == [33.33, 66.67, 100]
      promedio_Tabla([100], [4]) == [25]
    """
    for i in range(len(precios)):
        precios[i] = round(precios[i] / num[i], 2)
    return precios


def test_promedio_precio():
    assert (promedio_Tabla([100, 200, 300], [3, 3, 3]) == [33.33, 66.67, 100])
    assert (promedio_Tabla([100], [4]) == [25])


def getDataTable(dataMain):
    """
      Diseño de datos: 
      dataMain: dict
      
      Signatura:
      getDataTable: dict -> dict
      
      Próposito:
      Dado un diccionario, la función obtiene los datos correspondientes a 
      las provincias cuyos precios corresponden al año 2024. Luego, 
      retorna un diccionario el cual tiene 2 claves: Provincia y Precio Promedio. 
      En la primera clave, estarán las provincias que tuvieron al menos un precio 
      registrado el 2024 y en el segundo su respectivo precio promedio.
      
      EJEMPLOS: 
        Sea data1 = {
                     "indice_tiempo": ["2024-01", "2024-02", "2023-12", 
                                       "2024-04", "2009-08", "2024-05"],
                     "precio": ["30", "35.5", "900", "845", "5", "9"],
                     "provincia": ["Salta", "Salta", "Jujuy", 
                                   "Jujuy", "Jujuy", "Neuquen"]
                    }

        Sea data2 = {
                     "indice_tiempo": ["2023-01", "2023-02", 
                                       "2023-12", "2024-04", "2024-08"],
                     "precio": ["300", "35.5", "900", "8.45", "58"],
                     "provincia": ["Tucumán", "Salta", "Jujuy", "Jujuy", "Neuquen"]}

       getDataTable(data1) == {
                                "Provincia": ["Salta", "Jujuy", "Neuquen"], 
                                "Precio Promedio":[32.75, 845.0, 9]
                              }

       getDataTable(data2) == {
                                "Provincia": ["Jujuy", "Neuquen"], 
                                "Precio Promedio":[8.45,  58]
                              }
    """

    # Creamos el diccionario que contendrá los resultados
    resultado = {"Provincia": [], "Precio Promedio": []}

    indexPromedio = []  # Index de precios promedios

    año = dataMain["indice_tiempo"]  # Obtenemos la lista de años

    # Recorremos el diccionario para obtener los precios promedios
    for index in range(0, len(año)):
        year = año[index].split("-")  # Obtenemos la lista de años
        year = year[0]  # Obtenemos el año

        # Comparamos si es el año que estamos buscando
        if year == "2024":
            # Obtenemos un precio a través de un indice
            precios = dataMain["precio"][index]
            # Obtenemos una provincia a través de un indice
            provincias = dataMain["provincia"][index]
            precios = float(precios)
            indexProvincias = 0

            # Si la provincia no está en el diccionario, la agregamos,
            # agregamos el precio, agremamos un indice al indexPromedio
            if provincias not in resultado['Provincia']:
                resultado['Provincia'].append(provincias)
                resultado['Precio Promedio'].append(precios)

                indexPromedio.append(1)
            else:
                # Si la provincia ya está en el diccionario, buscamos su indice y
                # sumamos el precio actual al que ya tiene la provincia
                # y sumamos 1 al indexPromedio
                indexProvincias = resultado['Provincia'].index(provincias)
                resultado['Precio Promedio'][indexProvincias] += precios

                indexPromedio[indexProvincias] += 1

    # Obtenemos el precio promedio entre los precios registrados
    promedio_Tabla(resultado['Precio Promedio'], indexPromedio)
    return resultado


def test_getDataTable():
    data1 = {
        "indice_tiempo":
        ["2024-01", "2024-02", "2023-12", "2024-04", "2009-08", "2024-05"],
        "precio": ["30", "35.5", "900", "845", "5", "9"],
        "provincia": ["Salta", "Salta", "Jujuy", "Jujuy", "Jujuy", "Neuquen"]
    }

    assert (getDataTable(data1) == {
        "Provincia": ["Salta", "Jujuy", "Neuquen"],
        "Precio Promedio": [32.75, 845.0, 9]
    })

    data2 = {
        "indice_tiempo":
        ["2023-01", "2023-02", "2023-12", "2024-04", "2024-08"],
        "precio": ["300", "35.5", "900", "8.45", "58"],
        "provincia": ["Tucumán", "Salta", "Jujuy", "Jujuy", "Neuquen"]
    }

    assert (getDataTable(data2) == {
        "Provincia": ["Jujuy", "Neuquen"],
        "Precio Promedio": [8.45, 58]
    })


# Función para imprimir la pantalla de la Tabla
def pantalla3_Tabla(diccionario):
    """
      Diseño de datos:
      diccionario: dict

      Signatura:
      pantalla3_Tabla: dict -> None

      Próposito:
      Recibe un diccionario y genera una tabla que utiliza las claves de ese diccionario 
      como encabezados de la tabla y utiliza la información almacenada en forma de 
      lista en los valores para generar las filas con cada casillero en la columna 
      de su encabezado (clave) correspondiente. Muestra en la pantalla el título 
      y el subtítulo de la página, y debajo muestra la tabla generada.

      EJEMPLOS:
        Sea dict_1 = {
                        "Provincia": ["Santa Fe", "Jujuy", "Tucumán"], 
                        "Precio Promedio":[200, 600, 1000]
                     }
        
        Sea dict_2 = {
                        "Provincia": ["Grand-Est", "Occitaine", "Hauts-de-France", 
                                      "Centre-Val de Loire", "Corse", 
                                      "Auvergne-Rhone-Alpes", "Bretagne"], 
                        "Precio Promedio":[232, 2.4, 244.2, 656.4, 6, 55,90]
                     }

        pantalla3_Tabla(dict_1) == (Se muestra por pantalla) El título y subtítulo 
        de la página, y una tabla en donde el encabezado "Provincia" 
        está compuesta por: Santa Fe, Jujuy y Tucumán, y el encabezado "Precio Promedio"
        está compuesto por: 200, 600 y 1000.

        pantalla3_Tabla(dict_2) == (Se muestra por pantalla) El título y subtítulo 
        de la página, y una tabla en donde el encabezado "Provincia" 
        está compuesta por: Grand-Est, Occitaine, Hauts-de-Frabce, Centre-Val de Loire, 
        Corse, Auvergne-Rhone-Alpes y Bretragne, y el encabezado "Precio Promedio" 
        está compuesto por: 232,2.4, 244.2, 656.4, 6, 55 y 90.
      """
    # Genera una tabla usando HTML
    table_html = "<table style='border: 2px solid #003049ff; padding: 8px; width: 100%;heigth:100%;'>"

    # Crea la fila del Encabezado
    table_html += "<tr>"
    for key in diccionario.keys():
        table_html += f"<th style ='border: 1px solid #003049ff; background-color: #09293df5;font-family: \"Varela Round\", sans-serif;font-size: 25px; color: white; text-align: center;padding-top:15px;padding-bottom:10px;'> {key} </th>"
    table_html += "</tr>"

    # Crea las filas de los datos
    for i in range((len(diccionario["Provincia"]))):
        table_html += "<tr>"
        for key in diccionario.keys():
            table_html += f"<td style ='border: 1px solid #003049ff; background-color: #669bbc90;font-family: \"Varela Round\", sans-serif; font-size: 20px; color: #003049; text-align: center; box-shadow:0px 1px black;heigth:24px;padding:10px;padding-top:15px;'> {diccionario[key][i]} </td>"
        table_html += "</tr>"

    table_html += "</table>"

    # Muestra la tabla en la pantalla con Streamlit
    with st.container():
        # Crea el estilo para la página completa usando CSS
        css = """<style>
        .block-container {
            padding: 3rem;
        }
        .title {
            font-size: 2em;
            font-weight: 800;
            color: #540b0e;
            font-family: "Nunito", sans-serif;
        }
        .subtitle {
            font-size: 1.2em;
            color: #9e2a2b;
            margin-bottom: 30px;
            font-family: "Varela Round", sans-serif;
        }
        </style>"""

        st.markdown('<div class="title"> TABLA DE PROMEDIOS </div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="subtitle"> Tabla del precio promedio del combustible, por provincia, en el año 2024. </div>',
            unsafe_allow_html=True)

        st.markdown(css, unsafe_allow_html=True)
        st.markdown(table_html, unsafe_allow_html=True)


# -------------------------------------------------------------------------
# Función para imprimir la pantalla de Inicio
def pantalla_Inicio():
    """
    Signatura:
    pantalla_Inicio: None -> None

    Próposito: 
    Modulaliza los componentes que utilizamos para presentar la página de Inicio.
    """

    # Crea el estilo para la página completa usando CSS
    css = """
        <style>
        .title {
            font-size: 40px; 
            text-align:center;
            font-family: "Dancing Script", cursive;
            font-weight: 555;
            width: 90%;
            margin-left: 2%;
            margin-top: 3%;
        }

        .subheader {
            font-size: 55px; 
            text-align: center;
            font-family: "Dancing Script", cursive;
            font-weight: 900;
            width: 90%;
            margin-left: 2%;
            margin-bottom: 3%;
        }

        .block-container {
            max-width: 85vw !important;
        }
        
        .subheader_sub {
            font-size: 1.2em;
            font-family: "Varela Round", sans-serif;
            font-weight: 800;
            color: white;
            text-align: center;
            margin-bottom: 7px;
            min-height: 4rem;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .write {
            font-size: 1em;
            font-family: "Nunito", sans-serif;
            font-weight: 400;
            color: black;
            margin-bottom: 20px;
            line-height: 1.5;
            text-align:center;
            width: 90%;
            margin-left: 2%;
            text-wrap: balance;
        }

        .write_sub {
            font-size: .85em;
            font-family: "Nunito", sans-serif;
            font-weight: 400;
            color: #ffffffe6;
            margin-bottom: 20px;
            line-height: 1.5;
            text-justify: inter-word;
        }

        .container {
            background-color: #540b0eff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3), 0 6px 20px rgba(0, 0, 0, 0.2), -5px -5px 8px inset #00000026;
            border-radius: 10px;
            padding: 10px 7px 0 12px;
            border: 2px solid #3a1f2c;
            color: white;
            min-height: 13rem;
            margin-top: 10px;
        }
        
        [data-testid="stHorizontalBlock"] .stMarkdown  {
            width: 100% !important;
        }

        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

    c1, c2 = st.columns([2, 5])

    with c1:
        # Añade una imagen de Argentina
        st.image("argentina.png", width=360)

    with c2:
        with stylable_container(key="Inicio",
                                css_styles="""{
                width: 100%;
                background: #09293d;
                padding: 2rem;
                border-radius: 4px;
            }"""):
            with stylable_container(key="Inicio_card",
                                    css_styles="""{
                    width: 100%;
                    background: white;
                    border: 10px solid #540b0eff;
                    padding: 1rem;
                    border-radius: 8px;
                    gap: 0;
                }
                """):
                st.markdown('<div class="title"> Grupo II </div>',
                            unsafe_allow_html=True)

                st.markdown(
                    '<div class="subheader"> Análisis del Combustible</div>',
                    unsafe_allow_html=True)

                st.markdown(
                    '<div class="write">Nos preguntábamos qué tanta información se podía sacar de los combustibles en Argentina. Para ello, hemos desarrollado tres perspectivas diferentes que detallamos a continuación:</div>',
                    unsafe_allow_html=True)

            c3, c4, c5 = st.columns(3)

            with c3:
                st.markdown("""
                            <div class="container">
                                <div class="subheader_sub"> PROMEDIO </br> DE PRECIOS </div> 
                                <div class="write_sub"> En ésta página se encuentra el precio promedio actual del combustible según la provincia Argentina. </div>
                            </div>
                            """,
                            unsafe_allow_html=True)
            with c4:
                st.markdown("""
                            <div class="container">
                                <div class="subheader_sub"> LÍNEA </br> DEL TIEMPO </div>
                                <div class="write_sub"> En ésta página se puede ver el cambio del precio promedio de cada tipo de combustible a lo largo del tiempo.</div>
                            </div>
                            """,
                            unsafe_allow_html=True)
            with c5:
                st.markdown("""
                            <div class="container">
                               <div class="subheader_sub"> EL MAPA </div>
                               <div class="write_sub"> Aquí puede localizar las distintas ubicaciones de las empresas en Argentina según los filtros dados. </div>
                            </div>
                            """,
                            unsafe_allow_html=True)


#------------------
def main():
    dataMain = read_csv()  # Leemos el dataset una única vez.

    fuentes()  # Llamamos a las fonts, para utilizarlas en el código.

    # Crea el estilo para la página completa usando CSS
    st.markdown("""
    <style>
    /* Aspecto del Sidebar: */
    [data-testid="stSidebar"] {
        box-shadow: 0px 0px 20px rgb(0,0,0,0.5);
        position: fixed !important;
        z-index: 9999999999999999;    
    }

    /* Menú fijo */
    [style="position: absolute; user-select: none; width: 8px; height: 100%; top: 0px; cursor: col-resize; right: -6px;"]  {
        display: none;
    }

    /* Contenido fijo */
    [data-testid="stSidebarContent"] {
        display: inline-block;
    }

    .stApp {
        background-color: #fff;
    }

    [data-testid="stHeader"] {
        background-color: #fff;
    }

    /* sidebar block atributos */
    [data-testid="stSidebar"] div {
        background-color: #09293d;
        padding: 0px;
        padding-top: 6px;
        padding-left: 0px;
    }

    /* Card Centrada */
    .container {
        min-height: 16rem;
        margin-bottom: 1rem;
    }
    </style>
    """,
                unsafe_allow_html=True)

    with st.sidebar:
        menu = option_menu(
            None, ["Inicio", "Mapa", "Línea del tiempo", "Precios Promedios"],
            icons=[
                'bi bi-house-door-fill', 'bi bi-globe-americas',
                "bi bi-clock-history", 'bi bi-coin'
            ],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
            styles={
                "container": {
                    "padding": "0px!important",
                    "background-color": "#09293d",
                    "color": "white",
                    "border-radius": "0px",
                    "margin": "0px",
                    "width": "500px",
                    "padding-left": "0px",
                    "font-family": "Varela Round, sans-serif",
                },
                "icon": {
                    "color": "#94c9ea",
                    "font-size": "30px",
                },
                "nav-link": {
                    "font-size": "20px",
                    "text-align": "left",
                    "margin": "0px",
                    "margin-top": "8px",
                    "--hover-color": " rgba(238, 39, 72, 0.422)",
                    "color": "white",
                    "width": "103vw",
                    "border-radius": "0px",
                    "font-family": "Varela Round, sans-serif",
                },
                "nav-link-selected": {
                    "background-color": "#94c9ea50",
                    "color": "white",
                    "font": "bold",
                    "text-align": "left",
                    "font-family": "Varela Round, sans-serif",
                },
            })

    # SELECCIÓN DE OPCIONES:
    if menu == 'Mapa':
        pantalla1_Mapa(dataMain)
    elif menu == "Línea del tiempo":
        pantalla2_lineaDeTiempo(dataMain)
    elif menu == "Precios Promedios":
        pantalla3_Tabla(getDataTable(dataMain))
    else:
        pantalla_Inicio()


# EJECUTAR CÓDIGO:
if __name__ == "__main__":
    main()
