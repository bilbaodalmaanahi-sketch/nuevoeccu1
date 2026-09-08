import streamlit as st
from pathlib import Path
import struct
import pandas as pd
import random


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Monky2 BIN Analyzer",
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
    "### ECU / EEPROM Binary Memory Analyzer"
)

st.caption("Concept by Ariel Calacaterra")

st.write(
    "Busca un valor exacto, realiza un barrido de las "
    "tres últimas cifras y busca equivalentes en metros "
    "dentro de todo el archivo BIN."
)


# ============================================================
# ARCHIVO BIN
# ============================================================

archivo1 = st.file_uploader(
    "Cargar archivo BIN",
    type=["bin"]
)

if archivo1 is None:
    st.info("Seleccione un archivo BIN para comenzar.")
    st.stop()


# Leer BIN cargado por el usuario
datos = archivo1.read()

print("Tamaño:", len(datos), "bytes")


# ============================================================
# CONSTRUIR DATAFRAME DE 4 BYTES
# ============================================================

filas = []

for direccion in range(0, len(datos) - 3, 4):

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
        "Direccion_decimal": direccion,
        "Direccion_HEX": f"0x{direccion:04X}",

        "Valor": valor,

        "HEX": f"0x{valor:08X}",

        "B0": f"{b0:02X}",
        "B1": f"{b1:02X}",
        "B2": f"{b2:02X}",
        "B3": f"{b3:02X}",

        "Bytes": (
            f"{b0:02X} "
            f"{b1:02X} "
            f"{b2:02X} "
            f"{b3:02X}"
        )
    })


df_bin = pd.DataFrame(filas)


# ============================================================
# VALORES
# ============================================================

valor_buscado = st.number_input(
    "Valor a buscar",
    min_value=0,
    value=282235,
    step=1
)

nuevov = st.number_input(
    "Nuevo valor",
    min_value=0,
    value=123,
    step=1
)


# ============================================================
# BUSCAR VALOR EN EL PRIMER DATAFRAME
# ============================================================

resultado = df_bin[
    df_bin["Valor"] == valor_buscado
].copy()


st.write(
    f"Coincidencias encontradas: {len(resultado)}"
)

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


# ============================================================
# CAMBIAR VALOR EN EL PRIMER DATAFRAME
# ============================================================

df_bin.loc[
    df_bin["Valor"] == valor_buscado,
    "Valor"
] = nuevov


# ============================================================
# CONSTRUIR SEGUNDO DATAFRAME
# ============================================================

valor_km = valor_buscado


# Equivalente en metros
valor_metros_objetivo = valor_km * 1000


# Margen de búsqueda
margen_metros = 1_100_000


limite_metros_inicio = (
    valor_metros_objetivo - margen_metros
)

limite_metros_fin = (
    valor_metros_objetivo + margen_metros
)


# ============================================================
# BUSCAR VALORES EN METROS
# ============================================================

filas_metros = []

for direccion in range(0, len(datos) - 3, 4):

    valor_metros = struct.unpack_from(
        "<I",
        datos,
        direccion
    )[0]

    # Buscar valores dentro del rango de metros
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
# MOSTRAR DATAFRAME DE METROS
# ============================================================

st.write(
    f"Equivalente: {valor_metros_objetivo:,} metros"
)

st.write(
    f"Margen: ±{margen_metros:,} metros"
)

st.write(
    f"Rango: "
    f"{limite_metros_inicio:,} → "
    f"{limite_metros_fin:,}"
)

st.write(
    f"Coincidencias: {len(df_metros)}"
)

st.dataframe(
    df_metros,
    use_container_width=True
)


# ============================================================
# ACTUALIZAR VALORES EN METROS
# ============================================================

df_metros["Metros"] = df_metros["Metros"].apply(
    lambda x:
        nuevov * 1000
        + random.randint(0, 999)
)


# ============================================================
# MOSTRAR NUEVOS VALORES DE METROS
# ============================================================

st.write("Nuevos valores en metros")

st.dataframe(
    df_metros[[
        "Direccion_decimal",
        "Direccion_HEX",
        "Metros",
        "HEX",
        "Bytes"
    ]],
    use_container_width=True
)

# ============================================================
# CREAR COPIA MODIFICABLE DEL BIN
# ============================================================

datos_modificados = bytearray(datos)


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

for _, fila in df_metros.iterrows():

    direccion = int(
        fila["Direccion_decimal"]
    )

    nuevo_metros = int(
        fila["Metros"]
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

st.download_button(
    label="Descargar BIN modificado",
    data=bytes(datos_modificados),
    file_name="EEPROM_MODIFICADO.bin",
    mime="application/octet-stream"
)


# ============================================================
# RESULTADO FINAL
# ============================================================

st.write(
    f"Valores km modificados: {len(resultado)}"
)

st.write(
    f"Valores metros modificados: {len(df_metros)}"
)

st.write(
    f"Total de posiciones modificadas: "
    f"{len(resultado) + len(df_metros)}"
)
