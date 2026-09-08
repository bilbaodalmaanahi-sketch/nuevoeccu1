import streamlit as st
import struct
import pandas as pd
import random


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="BIN Analyzer",
    page_icon="",
    layout="wide"
)


# ============================================================
# TÍTULO
# ============================================================

st.title("BIN Analyzer")
st.write("Análisis y modificación de valores en archivos BIN")


# ============================================================
# SUBIR ARCHIVO BIN
# ============================================================

archivo_subido = st.file_uploader(
    "Subir archivo BIN",
    type=["bin"]
)


if archivo_subido is not None:

    # ========================================================
    # LEER ARCHIVO BIN
    # ========================================================

    datos = archivo_subido.read()

    st.success(
        f"Archivo cargado: {archivo_subido.name}"
    )

    st.write(
        f"Tamaño: {len(datos):,} bytes"
    )


    # ========================================================
    # DATOS DE ENTRADA
    # ========================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        valor_buscado = st.number_input(
            "Valor buscado (km)",
            min_value=0,
            value=282235,
            step=1
        )

    with col2:

        nuevo_valor = st.number_input(
            "Nuevo valor (km)",
            min_value=0,
            value=283000,
            step=1
        )

    with col3:

        margen_metros = st.number_input(
            "Margen de búsqueda (metros)",
            min_value=0,
            value=1_000_000,
            step=1000
        )


    # ========================================================
    # BOTÓN PROCESAR
    # ========================================================

    if st.button(
        "PROCESAR BIN",
        type="primary"
    ):

        # ====================================================
        # CONSTRUIR SEGUNDO DATAFRAME
        # ====================================================

        valor_km = valor_buscado

        # Equivalente en metros
        valor_metros_objetivo = valor_km * 1000

        # Margen de búsqueda
        limite_metros_inicio = (
            valor_metros_objetivo
            - margen_metros
        )

        limite_metros_fin = (
            valor_metros_objetivo
            + margen_metros
        )


        # ====================================================
        # BUSCAR VALORES EN METROS
        # ====================================================

        filas_metros = []

        for direccion in range(
            0,
            len(datos) - 3,
            4
        ):

            valor_metros = struct.unpack_from(
                "<I",
                datos,
                direccion
            )[0]


            # Buscar valores dentro del rango
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


        # ====================================================
        # CREAR DATAFRAME
        # ====================================================

        df_metros = pd.DataFrame(
            filas_metros
        )


        # ====================================================
        # MOSTRAR INFORMACIÓN
        # ====================================================

        st.subheader(
            "Información de búsqueda"
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Valor buscado",
            f"{valor_km:,} km"
        )

        c2.metric(
            "Equivalente",
            f"{valor_metros_objetivo:,} m"
        )

        c3.metric(
            "Margen",
            f"±{margen_metros:,} m"
        )

        c4.metric(
            "Coincidencias",
            len(df_metros)
        )


        st.write(
            f"Rango: "
            f"{limite_metros_inicio:,} → "
            f"{limite_metros_fin:,} metros"
        )


        # ====================================================
        # SI NO HAY COINCIDENCIAS
        # ====================================================

        if df_metros.empty:

            st.warning(
                "No se encontraron valores dentro del rango."
            )

            st.stop()


        # ====================================================
        # MOSTRAR DATAFRAME ORIGINAL
        # ====================================================

        st.subheader(
            "Valores encontrados"
        )

        st.dataframe(
            df_metros,
            use_container_width=True
        )


        # ====================================================
        # ACTUALIZAR VALORES EN METROS
        # ====================================================

        df_metros["Metros"] = (
            df_metros["Metros"].apply(
                lambda x:
                    nuevo_valor * 1000
                    + random.randint(0, 999)
            )
        )


        # ====================================================
        # ESCRIBIR CAMBIOS EN EL BIN
        # ====================================================

        datos_modificados = bytearray(
            datos
        )


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


        # ====================================================
        # NOMBRE DEL ARCHIVO DE SALIDA
        # ====================================================

        archivo_salida = (
            "EDC17C54 EEPROM_MODIFICADO.bin"
        )


        # ====================================================
        # RESULTADO
        # ====================================================

        st.success(
            "BIN modificado correctamente."
        )

        st.write(
            f"Valores modificados: "
            f"{len(df_metros)}"
        )


        # ====================================================
        # MOSTRAR VALORES NUEVOS
        # ====================================================

        st.subheader(
            "Valores modificados"
        )

        st.dataframe(
            df_metros,
            use_container_width=True
        )


        # ====================================================
        # DESCARGAR BIN
        # ====================================================

        st.download_button(
            label="DESCARGAR BIN MODIFICADO",
            data=bytes(datos_modificados),
            file_name=archivo_salida,
            mime="application/octet-stream"
        )

