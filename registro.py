import streamlit as st
from sqlalchemy import text
import time
import os
from sqlalchemy import create_engine
from sqlalchemy import create_engine, text
import pandas as pd

# Verificar si el usuario ya se registró previamente en este dispositivo
ya_registrado = st.query_params.get("registro", "false") == "true"

if ya_registrado:
    st.success("✨ ¡Hola de nuevo! Ya detectamos tu registro previo.")
    st.info("No necesitas llenar el formulario otra vez. Haz clic abajo para entrar a la clase:")
    
    link_zoom = "https://us04web.zoom.us/j/75494309875?pwd=OOGKbP8tHZrZa6rKjoxYbDsP11FSPg.1"
    
    if st.button("🚀 INGRESAR A ZOOM AHORA"):
        js = f'<script>window.open("{link_zoom}", "_blank").focus();</script>'
        st.write(js, unsafe_allow_html=True)
    
    if st.button("Necesito corregir mis datos"):
        st.query_params.clear()
        st.rerun()
    
    st.stop() # Esto detiene el resto del código para que no vea el formulario

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
        
        De conformidad con la legislación legal vigente y la Política de Tratamiento de Datos Personales de MB Educación, el tratamiento de los datos que se reportan en este Formulario se regirá por las siguientes condiciones:
        a) Yo, al diligenciar este Formulario, concedo autorización previa, expresa e informada a MB Educación, para el tratamiento de los datos que suministro, sabiendo que he sido informado que la finalidad de dichos datos es adquirir un producto o solicitar un servicio que ella ofrece ahora o en el futuro, de tal manera que puedan tramitar mi solicitud adecuadamente, contactarme en caso de que se requiera y adelantar todas las acciones para el logro del particular.
        b) Conozco y acepto que esta información será tratada de acuerdo con la Política de Tratamiento de Datos Personales de MB Educación disponible en su página Web, que declaro haber leído y conocer, en especial en lo referente a mis derechos y a los procedimientos con que la Entidad cuenta, para hacerlos efectivos ante sus autoridades.
        c) Se que los siguientes son los derechos básicos que tengo como titular de los datos que se han diligenciado en este Formulario: 1) Todos los datos registrados en este Formulario sólo serán empleados por MB Educación para cumplir la finalidad expuesta en el punto (a) del presente Aviso; 2) En cualquier momento, puedo solicitar una consulta de la información con que MB Educación cuenta sobre mí, dirigiéndome al Oficial de Protección de Datos Personales de la Entidad; 3) MB Educación velará por la confidencialidad y privacidad de los datos personales de los titulares que están siendo reportados, según las disposiciones legales vigentes; 4) En cualquier momento puedo solicitar una prueba de esta autorización.
        d) El Oficial de Protección de Datos Personales de la Entidad, ante quien puedo ejercer mis derechos, de forma gratuita, lo contactar en la siguiente dirección electrónica: usodedatos@mbeducacion.com.co 

        Acepto que MB Educación me envíe información de sus servicios o productos 
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

            # --- REDIRECCIÓN ACTUALIZADA ---
            st.success("¡Registro exitoso! Redirigiendo a la sala de Zoom...")
            st.balloons()
            
            # Guardamos en la URL que ya está registrado
            st.query_params["registro"] = "true"

            # --- REDIRECCIÓN AUTOMÁTICA A ZOOM ---            
            link_zoom = "https://us04web.zoom.us/j/75494309875?pwd=OOGKbP8tHZrZa6rKjoxYbDsP11FSPg.1"
            
            # Esperamos 2 segundos y redirigimos
            time.sleep(2)
            js = f'<meta http-equiv="refresh" content="0; url={link_zoom}">'
            st.write(js, unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"Error técnico: {e}")
    else:

        st.warning("Por favor completa los campos obligatorios (*)")








