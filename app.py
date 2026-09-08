import streamlit as st
import struct
import pandas as pd
import random


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Monky BIN Analyzer",
    page_icon="",
    layout="wide"
)

 st.caption("Concept by Ariel Calacaterra| Develop DAB")
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

st.title("🐒 MONKY BIN ANALYZER ")

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
# KILOMETRAJE / VALOR EXACTO A BUSCAR
# ============================================================

ingrekk = st.number_input(
    "Kilometraje / valor exacto a buscar",
    min_value=0,
    value=None,
    placeholder="Ingrese el kilometraje",
    step=1
)


# ============================================================
# NUEVO KILOMETRAJE FIJO
# ============================================================

nuevo_km_input = st.number_input(
    "Nuevo kilometraje fijo",
    min_value=0,
    value=None,
    placeholder="Ingrese el nuevo kilometraje",
    step=1
)


# ============================================================
# MARGEN DE METROS
# ============================================================
# FIJO: 1.000.000 metros
# ============================================================

margen = 1_100_000

st.number_input(
    "Margen de búsqueda en metros",
    min_value=0,
    value=margen,
    step=100_000,
    disabled=True
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

    # ========================================================
    # VALIDACIONES
    # ========================================================

    if archivo is None:

        st.warning(
            "Primero debes cargar un archivo BIN."
        )

    elif ingrekk is None:

        st.warning(
            "Ingrese el kilometraje / valor exacto a buscar."
        )

    elif nuevo_km_input is None:

        st.warning(
            "Ingrese el nuevo kilometraje fijo."
        )

    else:

        # ====================================================
        # LEER BIN
        # ====================================================

        datos_originales = archivo.read()

        datos_modificados = bytearray(
            datos_originales
        )

        tamaño = len(
            datos_originales
        )

        objetivo = int(
            ingrekk
        )

        nuevo_km = int(
            nuevo_km_input
        )


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

        objetivo_metros = (
            objetivo * 1000
        )

        limite_inicio = (
            objetivo_metros - margen
        )

        limite_fin = (
            objetivo_metros + margen
        )


        # ====================================================
        # INFORMACIÓN DEL ARCHIVO
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

        # Direcciones donde aparece EXACTAMENTE
        # el kilometraje buscado
        direcciones_km = []

        # Direcciones donde aparece un equivalente
        # en metros dentro del margen
        direcciones_metros = []


        # ====================================================
        # BARRIDO COMPLETO DEL BIN
        # ====================================================

        for direccion in range(
            0,
            tamaño - 3
        ):

            valor = struct.unpack_from(
                "<I",
                datos_originales,
                direccion
            )[0]


            bytes_valor = (
                datos_originales[
                    direccion:direccion + 4
                ]
            )


            # =================================================
            # BÚSQUEDA DEL RANGO DE KM
            # =================================================

            if (
                rango_inicio
                <= valor
                <= rango_fin
            ):

                resultados_barrido.append({

                    "Dirección":
                        f"0x{direccion:04X}",

                    "Valor":
                        valor,

                    "Diferencia desde exacto":
                        valor - objetivo,

                    "Exacto":
                        "🔴"
                        if valor == objetivo
                        else "",

                    "HEX":
                        f"0x{valor:08X}",

                    "Bytes":
                        bytes_valor.hex(
                            " "
                        ).upper()

                })


                # =============================================
                # GUARDAR SOLO LOS VALORES EXACTOS
                # =============================================

                if valor == objetivo:

                    direcciones_km.append(
                        direccion
                    )


            # =================================================
            # BÚSQUEDA POR METROS
            # =================================================

            if (
                limite_inicio
                <= valor
                <= limite_fin
            ):

                diferencia = (
                    valor
                    - objetivo_metros
                )


                resultados_metros.append({

                    "Dirección":
                        f"0x{direccion:04X}",

                    "Valor":
                        valor,

                    "Kilómetros":
                        round(
                            valor / 1000,
                            3
                        ),

                    "Metros":
                        valor,

                    "Diferencia (m)":
                        diferencia,

                    "Distancia absoluta":
                        abs(diferencia),

                    "HEX":
                        f"0x{valor:08X}",

                    "Bytes":
                        bytes_valor.hex(
                            " "
                        ).upper()

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
        # RESULTADOS DEL BARRIDO
        # ====================================================

        st.subheader(
            "Barrido de las tres últimas cifras"
        )


        st.write(
            f"Se buscaron todos los valores desde "
            f"**{rango_inicio:,}** hasta "
            f"**{rango_fin:,}**."
        )


        if resultado_barrido.empty:

            st.warning(
                f"No se encontraron valores entre "
                f"{rango_inicio:,} y "
                f"{rango_fin:,}."
            )

        else:

            resultado_barrido = (
                resultado_barrido
                .sort_values(
                    [
                        "Valor",
                        "Dirección"
                    ]
                )
                .reset_index(
                    drop=True
                )
            )


            st.success(
                f"Se encontraron "
                f"{len(resultado_barrido)} "
                f"coincidencias."
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
                resultado_barrido[
                    "Valor"
                ] == objetivo
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
                    f"{len(exactos)} "
                    f"apariciones exactas."
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
            f"Objetivo: "
            f"**{objetivo_metros:,} metros**  \n"
            f"Margen fijo: "
            f"**±{margen:,} metros**  \n"
            f"Rango: "
            f"**{limite_inicio:,} → "
            f"{limite_fin:,} metros**"
        )


        if resultado_metros.empty:

            st.warning(
                "No se encontraron valores dentro "
                "del margen seleccionado."
            )

        else:

            resultado_metros = (
                resultado_metros
                .sort_values(
                    "Distancia absoluta"
                )
                .reset_index(
                    drop=True
                )
            )


            st.success(
                f"Se encontraron "
                f"{len(resultado_metros)} "
                f"coincidencias."
            )


            st.dataframe(
                resultado_metros,
                use_container_width=True,
                hide_index=True
            )


            # =================================================
            # VALOR MÁS CERCANO
            # =================================================

            cercano = (
                resultado_metros.iloc[0]
            )


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
        # MODIFICACIÓN
        # ====================================================

        st.subheader(
            "Modificación de valores"
        )


        st.write(
            f"Valor original exacto: "
            f"**{objetivo:,} km**"
        )


        st.write(
            f"Nuevo kilometraje: "
            f"**{nuevo_km:,} km**"
        )


        st.write(
            f"Nuevo valor base en metros: "
            f"**{nuevo_km * 1000:,} m**"
        )


        # ====================================================
        # CANTIDADES
        # ====================================================

        cantidad_km = len(
            direcciones_km
        )


        cantidad_metros = len(
            direcciones_metros
        )


        total_modificaciones = (
            cantidad_km
            + cantidad_metros
        )


        col1, col2, col3 = st.columns(3)


        col1.metric(
            "KM exactos",
            cantidad_km
        )


        col2.metric(
            "Valores en metros",
            cantidad_metros
        )


        col3.metric(
            "Total modificaciones",
            total_modificaciones
        )


        # ====================================================
        # REALIZAR MODIFICACIONES
        # ====================================================

        if total_modificaciones == 0:

            st.warning(
                "No se encontraron valores "
                "para modificar."
            )


        else:

            modificaciones = []


            # =================================================
            # MODIFICAR VALORES EXACTOS EN KM
            # =================================================

            for direccion in direcciones_km:

                valor_anterior = (
                    struct.unpack_from(
                        "<I",
                        datos_originales,
                        direccion
                    )[0]
                )


                # Nuevo valor en KM
                nuevo_valor = nuevo_km


                # Convertir a UINT32 LITTLE-ENDIAN
                nuevos_bytes = struct.pack(
                    "<I",
                    nuevo_valor
                )


                # Escribir en el BIN
                datos_modificados[
                    direccion:
                    direccion + 4
                ] = nuevos_bytes


                # Registrar modificación
                modificaciones.append({

                    "Tipo":
                        "KM exacto",

                    "Dirección":
                        f"0x{direccion:04X}",

                    "Valor anterior":
                        valor_anterior,

                    "Nuevo valor":
                        nuevo_valor,

                    "Kilómetros":
                        nuevo_valor,

                    "Últimas 3 cifras":
                        "",

                    "HEX anterior":
                        f"0x{valor_anterior:08X}",

                    "HEX nuevo":
                        f"0x{nuevo_valor:08X}",

                    "Bytes anteriores":
                        datos_originales[
                            direccion:
                            direccion + 4
                        ].hex(
                            " "
                        ).upper(),

                    "Bytes nuevos":
                        nuevos_bytes.hex(
                            " "
                        ).upper()

                })


            # =================================================
            # GENERAR SUFIJOS PARA VALORES EN METROS
            # =================================================

            cantidad = len(
                direcciones_metros
            )


            if cantidad <= 1000:

                sufijos = random.sample(
                    range(1000),
                    cantidad
                )

            else:

                sufijos = [

                    random.randint(
                        0,
                        999
                    )

                    for _ in range(
                        cantidad
                    )

                ]


            # =================================================
            # MODIFICAR VALORES EN METROS
            # =================================================

            for direccion, sufijo in zip(
                direcciones_metros,
                sufijos
            ):

                valor_anterior = (
                    struct.unpack_from(
                        "<I",
                        datos_originales,
                        direccion
                    )[0]
                )


                # Nuevo valor en metros
                nuevo_valor = (
                    nuevo_km * 1000
                ) + sufijo


                # Convertir a UINT32 LITTLE-ENDIAN
                nuevos_bytes = struct.pack(
                    "<I",
                    nuevo_valor
                )


                # Escribir en el BIN
                datos_modificados[
                    direccion:
                    direccion + 4
                ] = nuevos_bytes


                # Registrar modificación
                modificaciones.append({

                    "Tipo":
                        "Metros",

                    "Dirección":
                        f"0x{direccion:04X}",

                    "Valor anterior":
                        valor_anterior,

                    "Nuevo valor":
                        nuevo_valor,

                    "Kilómetros":
                        round(
                            nuevo_valor / 1000,
                            3
                        ),

                    "Últimas 3 cifras":
                        f"{sufijo:03d}",

                    "HEX anterior":
                        f"0x{valor_anterior:08X}",

                    "HEX nuevo":
                        f"0x{nuevo_valor:08X}",

                    "Bytes anteriores":
                        datos_originales[
                            direccion:
                            direccion + 4
                        ].hex(
                            " "
                        ).upper(),

                    "Bytes nuevos":
                        nuevos_bytes.hex(
                            " "
                        ).upper()

                })


            # =================================================
            # DATAFRAME DE MODIFICACIONES
            # =================================================

            resultado_modificaciones = (
                pd.DataFrame(
                    modificaciones
                )
            )


            # =================================================
            # MOSTRAR MODIFICACIONES
            # =================================================

            st.subheader(
                "Registro de modificaciones"
            )


            st.success(
                f"Se realizaron "
                f"{len(modificaciones)} "
                f"modificaciones."
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


            # =================================================
            # VERIFICAR KM EXACTOS
            # =================================================

            for direccion in direcciones_km:

                valor_verificado = (
                    struct.unpack_from(
                        "<I",
                        datos_modificados,
                        direccion
                    )[0]
                )


                if (
                    valor_verificado
                    != nuevo_km
                ):

                    errores += 1


            # =================================================
            # VERIFICAR METROS
            # =================================================

            for direccion, sufijo in zip(
                direcciones_metros,
                sufijos
            ):

                valor_esperado = (
                    nuevo_km * 1000
                ) + sufijo


                valor_verificado = (
                    struct.unpack_from(
                        "<I",
                        datos_modificados,
                        direccion
                    )[0]
                )


                if (
                    valor_verificado
                    != valor_esperado
                ):

                    errores += 1


            # =================================================
            # RESULTADO DE VERIFICACIÓN
            # =================================================

            if errores == 0:

                st.success(
                    "✓ Todos los reemplazos fueron "
                    "verificados correctamente."
                )

            else:

                st.error(
                    f"Se detectaron "
                    f"{errores} errores "
                    f"durante la verificación."
                )


            # =================================================
            # NOMBRE DEL ARCHIVO
            # =================================================

            nombre_original = (
                archivo.name
            )


            if nombre_original.lower().endswith(
                ".bin"
            ):

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
                data=bytes(
                    datos_modificados
                ),
                file_name=nombre_salida,
                mime="application/octet-stream",
                type="primary"
            )


            # =================================================
            # DESCARGAR CSV
            # =================================================

            csv_modificaciones = (
                resultado_modificaciones
                .to_csv(
                    index=False
                )
                .encode("utf-8")
            )


            st.download_button(
                label="⬇️ Descargar registro de modificaciones",
                data=csv_modificaciones,
                file_name="registro_modificaciones.csv",
                mime="text/csv"
            )



