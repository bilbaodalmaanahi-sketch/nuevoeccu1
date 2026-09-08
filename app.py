import streamlit as st
import struct
import pandas as pd
import random
from io import BytesIO


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Monky BIN Analyzer by pipi Cabral",
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

st.title("🐒 MONKY BIN ANALYZER by Pipi Cabral")

st.write(
    "Busca un valor exacto, realiza un barrido de las tres "
    "últimas cifras y analiza equivalentes en metros dentro "
    "de todo el archivo BIN."
)


# ============================================================
# CARGAR ARCHIVO
# ============================================================

archivo = st.file_uploader(
    "Seleccionar archivo BIN",
    type=["bin"]
)


# ============================================================
# KILOMETRAJE / VALOR A BUSCAR
# ============================================================

ingrekk = st.number_input(
    "Kilometraje / valor exacto a buscar",
    min_value=0,
    value=234570,
    step=1
)


# ============================================================
# KILOMETRAJE FIJO PARA REEMPLAZO
# ============================================================

nuevo_km = st.number_input(
    "Nuevo kilometraje fijo",
    min_value=0,
    value=280000,
    step=1
)


# ============================================================
# MARGEN DE METROS
# ============================================================

margen = st.number_input(
    "Margen de búsqueda en metros",
    min_value=0,
    value=1_000_000,
    step=100_000
)


# ============================================================
# BOTÓN
# ============================================================

buscar = st.button(
    "🔎 Buscar y preparar modificación",
    type="primary"
)


# ============================================================
# PROCESAMIENTO
# ============================================================

if buscar:

    if archivo is None:

        st.warning(
            "Primero debes cargar un archivo BIN."
        )

    else:

        # ====================================================
        # LEER BIN
        # ====================================================

        datos_originales = archivo.read()
        datos_modificados = bytearray(datos_originales)

        tamaño = len(datos_originales)

        objetivo = int(ingrekk)
        nuevo_km = int(nuevo_km)

        # ====================================================
        # RANGO DE LAS 3 ÚLTIMAS CIFRAS
        # ====================================================

        rango_inicio = (
            objetivo // 1000
        ) * 1000

        rango_fin = (
            rango_inicio + 999
        )

        # ====================================================
        # OBJETIVO EN METROS
        # ====================================================

        objetivo_metros = objetivo * 1000

        limite_inicio = (
            objetivo_metros - int(margen)
        )

        limite_fin = (
            objetivo_metros + int(margen)
        )

        # ====================================================
        # INFORMACIÓN
        # ====================================================

        st.success(
            f"Archivo cargado correctamente: {archivo.name}"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Tamaño BIN",
            f"{tamaño:,} bytes"
        )

        col2.metric(
            "Valor buscado",
            f"{objetivo:,}"
        )

        col3.metric(
            "Rango 3 últimas cifras",
            f"{rango_inicio:,} → {rango_fin:,}"
        )

        col4.metric(
            "Objetivo metros",
            f"{objetivo_metros:,}"
        )


        # ====================================================
        # LISTAS
        # ====================================================

        resultados_barrido = []
        resultados_metros = []

        # Direcciones que serán modificadas
        direcciones_metros = []


        # ====================================================
        # BARRIDO COMPLETO DEL BIN
        # ====================================================

        for direccion in range(0, tamaño - 3):

            valor = struct.unpack_from(
                "<I",
                datos_originales,
                direccion
            )[0]

            bytes_valor = datos_originales[
                direccion:direccion + 4
            ]


            # =================================================
            # BÚSQUEDA DEL RANGO DE KM
            # =================================================

            if rango_inicio <= valor <= rango_fin:

                resultados_barrido.append({

                    "Dirección":
                        f"0x{direccion:04X}",

                    "Valor":
                        valor,

                    "Diferencia desde exacto":
                        valor - objetivo,

                    "Exacto":
                        "🔴" if valor == objetivo else "",

                    "HEX":
                        f"0x{valor:08X}",

                    "Bytes":
                        bytes_valor.hex(" ").upper()

                })


            # =================================================
            # BÚSQUEDA POR METROS
            # =================================================

            if limite_inicio <= valor <= limite_fin:

                diferencia = (
                    valor - objetivo_metros
                )

                resultados_metros.append({

                    "Dirección":
                        f"0x{direccion:04X}",

                    "Valor":
                        valor,

                    "Kilómetros":
                        round(valor / 1000, 3),

                    "Metros":
                        valor,

                    "Diferencia (m)":
                        diferencia,

                    "Distancia absoluta":
                        abs(diferencia),

                    "HEX":
                        f"0x{valor:08X}",

                    "Bytes":
                        bytes_valor.hex(" ").upper()

                })

                direcciones_metros.append(
                    direccion
                )


        # ====================================================
        # DATAFRAME BARRIDO
        # ====================================================

        resultado_barrido = pd.DataFrame(
            resultados_barrido
        )


        # ====================================================
        # DATAFRAME METROS
        # ====================================================

        resultado_metros = pd.DataFrame(
            resultados_metros
        )


        # ====================================================
        # RESULTADOS BARRIDO
        # ====================================================

        st.subheader(
            "Barrido de las tres últimas cifras"
        )

        st.write(
            f"Se buscaron todos los valores desde "
            f"**{rango_inicio:,}** hasta **{rango_fin:,}**."
        )


        if resultado_barrido.empty:

            st.warning(
                f"No se encontraron valores entre "
                f"{rango_inicio:,} y {rango_fin:,}."
            )

        else:

            resultado_barrido = (
                resultado_barrido
                .sort_values(
                    ["Valor", "Dirección"]
                )
                .reset_index(drop=True)
            )

            st.success(
                f"Se encontraron "
                f"{len(resultado_barrido)} coincidencias."
            )

            st.dataframe(
                resultado_barrido,
                use_container_width=True,
                hide_index=True
            )


            # =================================================
            # VALORES EXACTOS
            # =================================================

            exactos = resultado_barrido[
                resultado_barrido["Valor"] == objetivo
            ]


            st.subheader(
                f"Valor exacto: {objetivo:,}"
            )


            if exactos.empty:

                st.warning(
                    f"No se encontró el valor exacto "
                    f"{objetivo:,}."
                )

            else:

                st.success(
                    f"Se encontraron "
                    f"{len(exactos)} apariciones exactas."
                )

                st.dataframe(
                    exactos,
                    use_container_width=True,
                    hide_index=True
                )


            # =================================================
            # RESUMEN
            # =================================================

            st.subheader(
                "Resumen del barrido"
            )

            resumen = (
                resultado_barrido[
                    "Valor"
                ]
                .value_counts()
                .sort_index()
                .reset_index()
            )

            resumen.columns = [
                "Valor",
                "Cantidad de apariciones"
            ]

            st.dataframe(
                resumen,
                use_container_width=True,
                hide_index=True
            )


        # ====================================================
        # RESULTADOS METROS
        # ====================================================

        st.subheader(
            "Resultados de búsqueda por metros"
        )

        st.write(
            f"Objetivo: **{objetivo_metros:,} metros**  \n"
            f"Margen: **±{margen:,} metros**  \n"
            f"Rango: **{limite_inicio:,} → {limite_fin:,} metros**"
        )


        if resultado_metros.empty:

            st.warning(
                "No se encontraron valores dentro del "
                "margen seleccionado."
            )

        else:

            resultado_metros = (
                resultado_metros
                .sort_values(
                    "Distancia absoluta"
                )
                .reset_index(drop=True)
            )

            st.success(
                f"Se encontraron "
                f"{len(resultado_metros)} coincidencias."
            )

            st.dataframe(
                resultado_metros,
                use_container_width=True,
                hide_index=True
            )


            # =================================================
            # MÁS CERCANO
            # =================================================

            cercano = resultado_metros.iloc[0]

            st.info(
                f"Más cercano al objetivo: "
                f"{cercano['Metros']:,} metros | "
                f"{cercano['Kilómetros']} km | "
                f"Diferencia: "
                f"{cercano['Diferencia (m)']:+,} m | "
                f"Dirección: "
                f"{cercano['Dirección']}"
            )


        # ====================================================
        # MODIFICACIÓN DE EQUIVALENTES EN METROS
        # ====================================================

        st.subheader(
            "Modificación de equivalentes en metros"
        )

        st.write(
            f"Valor base nuevo: "
            f"**{nuevo_km:,} km**"
        )

        st.write(
            f"Valor base en metros: "
            f"**{nuevo_km * 1000:,} m**"
        )

        st.write(
            "Las últimas tres cifras serán generadas "
            "aleatoriamente para cada aparición."
        )


        if not direcciones_metros:

            st.warning(
                "No hay valores en metros para modificar."
            )

        else:

            # =================================================
            # GENERAR SUFIJOS ALEATORIOS
            # =================================================

            cantidad = len(direcciones_metros)

            # Si hay hasta 1000 coincidencias intentamos
            # que cada una tenga un sufijo diferente.
            if cantidad <= 1000:

                sufijos = random.sample(
                    range(1000),
                    cantidad
                )

            else:

                sufijos = [
                    random.randint(0, 999)
                    for _ in range(cantidad)
                ]


            modificaciones = []


            # =================================================
            # REALIZAR REEMPLAZOS
            # =================================================

            for direccion, sufijo in zip(
                direcciones_metros,
                sufijos
            ):

                valor_anterior = struct.unpack_from(
                    "<I",
                    datos_originales,
                    direccion
                )[0]


                # ---------------------------------------------
                # 280000 + tres cifras
                # ---------------------------------------------

                nuevo_valor = (
                    nuevo_km * 1000
                ) + sufijo


                # ---------------------------------------------
                # UINT32 LITTLE-ENDIAN
                # ---------------------------------------------

                nuevos_bytes = struct.pack(
                    "<I",
                    nuevo_valor
                )


                # ---------------------------------------------
                # ESCRIBIR EN COPIA DEL BIN
                # ---------------------------------------------

                datos_modificados[
                    direccion:direccion + 4
                ] = nuevos_bytes


                modificaciones.append({

                    "Dirección":
                        f"0x{direccion:04X}",

                    "Valor anterior":
                        valor_anterior,

                    "HEX anterior":
                        f"0x{valor_anterior:08X}",

                    "Bytes anteriores":
                        datos_originales[
                            direccion:direccion + 4
                        ].hex(" ").upper(),

                    "Nuevo valor":
                        nuevo_valor,

                    "Kilómetros":
                        nuevo_valor / 1000,

                    "Últimas 3 cifras":
                        f"{sufijo:03d}",

                    "HEX nuevo":
                        f"0x{nuevo_valor:08X}",

                    "Bytes nuevos":
                        nuevos_bytes.hex(" ").upper()

                })


            resultado_modificaciones = pd.DataFrame(
                modificaciones
            )


            # =================================================
            # MOSTRAR MODIFICACIONES
            # =================================================

            st.success(
                f"Se modificaron "
                f"{len(modificaciones)} valores."
            )

            st.dataframe(
                resultado_modificaciones,
                use_container_width=True,
                hide_index=True
            )


            # =================================================
            # VERIFICACIÓN
            # =================================================

            st.subheader(
                "Verificación"
            )

            errores = 0

            for direccion, sufijo in zip(
                direcciones_metros,
                sufijos
            ):

                valor_esperado = (
                    nuevo_km * 1000
                ) + sufijo

                valor_verificado = struct.unpack_from(
                    "<I",
                    datos_modificados,
                    direccion
                )[0]

                if valor_verificado != valor_esperado:
                    errores += 1


            if errores == 0:

                st.success(
                    "✓ Todos los reemplazos fueron "
                    "verificados correctamente."
                )

            else:

                st.error(
                    f"Se detectaron {errores} errores "
                    f"durante la verificación."
                )


            # =================================================
            # NOMBRE DEL ARCHIVO
            # =================================================

            nombre_original = archivo.name

            if nombre_original.lower().endswith(".bin"):

                nombre_salida = (
                    nombre_original[:-4]
                    + "_MODIFICADO.bin"
                )

            else:

                nombre_salida = (
                    nombre_original
                    + "_MODIFICADO.bin"
                )


            # =================================================
            # DESCARGAR BIN MODIFICADO
            # =================================================

            st.subheader(
                "Descargar BIN modificado"
            )

            st.download_button(
                label="⬇️ Descargar BIN MODIFICADO",
                data=bytes(datos_modificados),
                file_name=nombre_salida,
                mime="application/octet-stream",
                type="primary"
            )


            # =================================================
            # DESCARGAR TABLA DE MODIFICACIONES
            # =================================================

            csv_modificaciones = (
                resultado_modificaciones
                .to_csv(index=False)
                .encode("utf-8")
            )

            st.download_button(
                label="⬇️ Descargar registro de modificaciones",
                data=csv_modificaciones,
                file_name="registro_modificaciones.csv",
                mime="text/csv"
            )
