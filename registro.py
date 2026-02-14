import streamlit as st
from sqlalchemy import text
import time
import os
from sqlalchemy import create_engine
from sqlalchemy import create_engine, text
import pandas as pd

# 1. Cargar credenciales desde los Secrets de Streamlit
creds = st.secrets["db_credentials"]
DB_USER = creds["user"]
DB_PASS = creds["pass"]
DB_HOST = creds["host"]
DB_NAME = creds["name"]

# 2. Crear el motor de conexión
# Agregamos pool_pre_ping para que la conexión no se caiga durante el evento
engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}",
    pool_pre_ping=True
)

# from tu_archivo_principal import engine 

st.title("Registro de Asistencia y Tratamiento de Datos")
st.subheader("Bienvenido al Curso Reforma Laboral de MB Educación")

with st.form("registro_publico", clear_on_submit=True):
    nombre = st.text_input("Nombre Completo *")
    institucion = st.text_input("Institución Educativa /Empresa /Asociacion *")
    rol_cargo = st.text_input(" Cargo en la Institución Educativa /Empresa /Asociacion*")
    email = st.text_input("Correo Electrónico")
    
    st.markdown("---")
    st.write("🔒 **Política de Tratamiento de Datos**")
    # --- MÉTODO 2: VENTANA DESPLEGABLE ---
    with st.expander("Leer Política completa de Tratamiento de Datos (Habeas Data)"):
        st.markdown("""
        ### MB EDUCACIÓN - AUTORIZACIÓN PARA EL TRATAMIENTO DE DATOS PERSONALES
        
        En cumplimiento de la **Ley 1581 de 2012** y el Decreto 1377 de 2013, le informamos que al registrarse en este evento académico, usted autoriza a **MB Educación** para:
        
        1. **Finalidad del Tratamiento:** Recolectar, almacenar y usar sus datos con el fin de gestionar su asistencia, enviar material académico, emitir certificados y grabaciones de las sesiones.
        2. **Sesiones Virtuales:** Usted entiende y acepta que las sesiones a través de Zoom pueden ser grabadas con fines pedagógicos y de evidencia institucional.
        3. **Derechos del Titular:** Usted tiene derecho a conocer, actualizar y rectificar sus datos personales en cualquier momento a través de nuestros canales de atención.
        
        ---
        **DECLARACIÓN DE MB EDUCACIÓN:**
        Nos comprometemos a no compartir, vender ni ceder su información a terceros sin su consentimiento expreso, garantizando la seguridad y confidencialidad de la información.
        
        *Para mayor información, puede solicitar el documento impreso a nuestro equipo administrativo.*
        """)

    st.caption("Al marcar la casilla, autoriza a MB Educación a utilizar sus datos según los términos expuestos anteriormente.")
    acepta = st.checkbox("He leído y acepto el tratamiento de mis datos personales")
    
    boton_registro = st.form_submit_button("REGISTRARME E INGRESAR A ZOOM")

# --- LÓGICA DE VALIDACIÓN ---
if boton_registro:
    if nombre and institucion:
        try:
            with engine.begin() as conn:
                query = text("""
                    INSERT INTO directorio_tratamiento 
                    (contacto_nombre, institucion, rol_cargo, email, habeas_data, canal_autorizacion) 
                    VALUES (:nom, :inst, :rol, :mail, :hab, :cnal)
                """)
                conn.execute(query, {
                    "nom": nombre, 
                    "inst": institucion, 
                    "mail": email,
                    "rol": rol_cargo,
                    "hab": 1 if acepta else 0,
                    "cnal": "Registro Zoom, Curso Reforma Tributria" + time.strftime("%d/%m/%Y"),
                    
                })
            
            st.success("¡Registro exitoso! Redirigiendo a la sala de Zoom...")
            st.balloons()
            
            # --- REDIRECCIÓN AUTOMÁTICA A ZOOM ---
            link_zoom = "https://us04web.zoom.us/j/75494309875?pwd=OOGKbP8tHZrZa6rKjoxYbDsP11FSPg.1" # <--- PEGA TU LINK AQUÍ
            js = f'<meta http-equiv="refresh" content="2; url={link_zoom}">'
            st.write(js, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error técnico: {e}")
    else:

        st.warning("Por favor completa los campos obligatorios (*)")






