import streamlit as st
from pathlib import Path
import struct
import pandas as pd
import random


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Monky2 BIN Analyzer B1",
    page_icon="",
    layout="wide"
)


# ============================================================
# ESTILO UNDERGROUND
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #080808;
    color: #00ff66;
}

html, body, [class*="css"] {
    font-family: "Courier New", monospace;
}

h1 {
    color: #00ff66 !important;
    font-family: "Courier New", monospace !important;
    font-weight: bold;
    letter-spacing: 3px;
    text-transform: uppercase;
}

h2, h3 {
    color: #00ff66 !important;
    font-family: "Courier New", monospace !important;
}

p {
    color: #b0ffcc;
}

input {
    background-color: #111111 !important;
    color: #00ff66 !important;
    border: 1px solid #00ff66 !important;
    font-family: "Courier New", monospace !important;
}

.stButton > button {
    background-color: #001a0a;
    color: #00ff66;
    border: 1px solid #00ff66;
    border-radius: 0px;
    font-family: "Courier New", monospace;
    font-weight: bold;
    letter-spacing: 2px;
}

.stButton > button:hover {
    background-color: #00ff66;
    color: #000000;
}

[data-testid="stMetric"] {
    background-color: #0d0d0d;
    border: 1px solid #00ff66;
    padding: 15px;
}

[data-testid="stMetricLabel"] {
    color: #00ff66 !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #00ff66;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# TÍTULO
# ============================================================

st.title("🐒 MONKY EEPROM LAB")

st.markdown(
    "### ECU / EEPROM Binary Memory Analyzer B"
)

st.caption("Concept by Ariel Calacaterra")

st.write(
    "Busca un valor exacto, realiza una búsqueda "
    "byte por byte y busca equivalentes en metros "
    "dentro de ±200 km."
)


# ============================================================
# ARCHIVO BIN
# ============================================================

archivo1 = st.file_uploader(
    "Cargar archivo BIN",
    type=["bin"]
)

if archivo1 is None:

    st.info(
        "Seleccione un archivo BIN para comenzar."
    )

    st.stop()


# ============================================================
# LEER BIN CARGADO
# ============================================================

datos = archivo1.read()

st.write(
    f"Tamaño: **{len(datos):,} bytes**"
)


# ============================================================
# CONSTRUIR DATAFRAME DE 4 BYTES
#
# AHORA SE RECORRE BYTE POR BYTE
# ============================================================

filas = []


for direccion in range(
    0,
    len(datos) - 3
):

    # Leer los 4 bytes como uint32 little-endian
    valor = struct.unpack_from(
        "<I",
        datos,
        direccion
    )[0]


    b0 = datos[direccion]
    b1 = datos[direccion + 1]
    b2 = datos[direccion + 2]
    b3 = datos[direccion + 3]


    filas.append({

        "Direccion_decimal":
            direccion,

        "Direccion_HEX":
            f"0x{direccion:04X}",

        "Valor":
            valor,

        "HEX":
            f"0x{valor:08X}",

        "B0":
            f"{b0:02X}",

        "B1":
            f"{b1:02X}",

        "B2":
            f"{b2:02X}",

        "B3":
            f"{b3:02X}",

        "Bytes":
            (
                f"{b0:02X} "
                f"{b1:02X} "
                f"{b2:02X} "
                f"{b3:02X}"
            )
    })


df_bin = pd.DataFrame(filas)


# ============================================================
# VALORES INGRESADOS POR EL USUARIO
# ============================================================

st.subheader("PARÁMETROS")


col1, col2 = st.columns(2)


with col1:

    valor_buscado = st.number_input(
        "Valor a buscar (KM)",
        min_value=0,
        value=282235,
        step=1
    )


with col2:

    nuevov = st.number_input(
        "Nuevo valor (KM)",
        min_value=0,
        value=123,
        step=1
    )


# ============================================================
# BUSCAR VALOR EXACTO
# ============================================================

resultado = df_bin[
    df_bin["Valor"] == valor_buscado
].copy()


# ============================================================
# MOSTRAR RESULTADO
# ============================================================

st.subheader(
    "BÚSQUEDA EXACTA"
)


st.write(
    f"Valor buscado: "
    f"**{int(valor_buscado):,} km**"
)


st.write(
    f"Coincidencias encontradas: "
    f"**{len(resultado)}**"
)


if len(resultado) > 0:

    st.dataframe(

        resultado[[

            "Direccion_decimal",
            "Direccion_HEX",
            "Valor",
            "HEX",
            "Bytes"

        ]],

        use_container_width=True

    )

else:

    st.warning(
        "0 coincidencias: el valor exacto "
        "no fue encontrado en el BIN."
    )


# ============================================================
# CAMBIAR VALOR EN EL PRIMER DATAFRAME
# ============================================================

df_bin.loc[
    df_bin["Valor"] == valor_buscado,
    "Valor"
] = nuevov


# ============================================================
# SEGUNDO DATAFRAME
# BÚSQUEDA DE EQUIVALENTES EN METROS
# ============================================================

valor_km = int(
    valor_buscado
)


# ============================================================
# EQUIVALENTE EN METROS
# ============================================================

valor_metros_objetivo = (
    valor_km * 1000
)


# ============================================================
# MARGEN DE BÚSQUEDA
# ============================================================

# ±200 KM

margen_km = 200


margen_metros = (
    margen_km * 1000
)


# ============================================================
# LÍMITES
# ============================================================

limite_metros_inicio = (
    valor_metros_objetivo
    - margen_metros
)


limite_metros_fin = (
    valor_metros_objetivo
    + margen_metros
)


# ============================================================
# BUSCAR VALORES EN METROS
#
# TAMBIÉN BYTE POR BYTE
# ============================================================

filas_metros = []


for direccion in range(
    0,
    len(datos) - 3
):

    valor_metros = struct.unpack_from(
        "<I",
        datos,
        direccion
    )[0]


    # --------------------------------------------------------
    # BUSCAR DENTRO DE ±200 KM
    # --------------------------------------------------------

    if (

        limite_metros_inicio
        <= valor_metros
        <= limite_metros_fin

    ):

        b0 = datos[direccion]
        b1 = datos[direccion + 1]
        b2 = datos[direccion + 2]
        b3 = datos[direccion + 3]


        filas_metros.append({

            "Direccion_decimal":
                direccion,

            "Direccion_HEX":
                f"0x{direccion:04X}",

            "Metros":
                valor_metros,

            "KM_equivalente":
                valor_metros / 1000,

            "Diferencia_KM":
                (
                    valor_metros
                    - valor_metros_objetivo
                ) / 1000,

            "HEX":
                f"0x{valor_metros:08X}",

            "B0":
                f"{b0:02X}",

            "B1":
                f"{b1:02X}",

            "B2":
                f"{b2:02X}",

            "B3":
                f"{b3:02X}",

            "Bytes":
                (
                    f"{b0:02X} "
                    f"{b1:02X} "
                    f"{b2:02X} "
                    f"{b3:02X}"
                )
        })


# ============================================================
# CREAR DATAFRAME DE METROS
# ============================================================

df_metros = pd.DataFrame(
    filas_metros
)


# ============================================================
# MOSTRAR INFORMACIÓN
# ============================================================

st.subheader(
    "EQUIVALENTES EN METROS"
)


st.write(
    f"Valor buscado: "
    f"**{valor_km:,} km**"
)


st.write(
    f"Equivalente: "
    f"**{valor_metros_objetivo:,} metros**"
)


st.write(
    f"Margen de búsqueda: "
    f"**±{margen_km} km**"
)


st.write(
    f"Rango: "
    f"**{limite_metros_inicio:,} → "
    f"{limite_metros_fin:,} metros**"
)


st.write(
    f"Coincidencias: "
    f"**{len(df_metros)}**"
)


# ============================================================
# MOSTRAR RESULTADOS
# ============================================================

if len(df_metros) > 0:

    st.dataframe(

        df_metros[[

            "Direccion_decimal",
            "Direccion_HEX",
            "Metros",
            "KM_equivalente",
            "Diferencia_KM",
            "HEX",
            "Bytes"

        ]],

        use_container_width=True

    )

else:

    st.warning(
        "0 coincidencias: no se encontraron "
        "valores dentro del rango de ±200 km."
    )


# ============================================================
# GENERAR NUEVOS VALORES EN METROS
# ============================================================

if len(df_metros) > 0:

    df_metros["Metros_nuevos"] = (

        df_metros["Metros"].apply(

            lambda x:

                int(nuevov) * 1000
                + random.randint(0, 999)

        )

    )


# ============================================================
# MOSTRAR NUEVOS VALORES
# ============================================================

if len(df_metros) > 0:

    st.subheader(
        "NUEVOS VALORES EN METROS"
    )


    st.write(
        f"Nuevo valor base: "
        f"**{int(nuevov):,} km**"
    )


    st.write(
        f"Nuevo valor base en metros: "
        f"**{int(nuevov) * 1000:,} metros**"
    )


    st.dataframe(

        df_metros[[

            "Direccion_decimal",
            "Direccion_HEX",

            "Metros",

            "Metros_nuevos",

            "KM_equivalente",

            "Diferencia_KM",

            "Bytes"

        ]],

        use_container_width=True

    )


# ============================================================
# CREAR COPIA MODIFICABLE DEL BIN
# ============================================================

datos_modificados = bytearray(
    datos
)


# ============================================================
# ESCRIBIR CAMBIOS DEL PRIMER DATAFRAME
# ============================================================

for _, fila in resultado.iterrows():

    direccion = int(
        fila["Direccion_decimal"]
    )


    nuevo_valor = int(
        nuevov
    )


    struct.pack_into(

        "<I",

        datos_modificados,

        direccion,

        nuevo_valor

    )


# ============================================================
# ESCRIBIR CAMBIOS DEL SEGUNDO DATAFRAME
# ============================================================

if len(df_metros) > 0:

    for _, fila in df_metros.iterrows():

        direccion = int(
            fila["Direccion_decimal"]
        )


        nuevo_metros = int(
            fila["Metros_nuevos"]
        )


        struct.pack_into(

            "<I",

            datos_modificados,

            direccion,

            nuevo_metros

        )


# ============================================================
# DESCARGAR BIN MODIFICADO
# ============================================================

st.subheader(
    "BIN MODIFICADO"
)


st.download_button(

    label="🐒 Descargar BIN modificado",

    data=bytes(
        datos_modificados
    ),

    file_name="EEPROM_MODIFICADO.bin",

    mime="application/octet-stream"

)


# ============================================================
# RESULTADO FINAL
# ============================================================

st.subheader(
    "RESUMEN FINAL"
)


st.write(
    f"Valor buscado: "
    f"**{int(valor_buscado):,} km**"
)


st.write(
    f"Nuevo valor: "
    f"**{int(nuevov):,} km**"
)


st.write(
    f"Valores exactos encontrados: "
    f"**{len(resultado)}**"
)


st.write(
    f"Equivalentes encontrados "
    f"en ±200 km: "
    f"**{len(df_metros)}**"
)


st.write(
    f"Total de posiciones modificadas: "
    f"**{len(resultado) + len(df_metros)}**"
)
