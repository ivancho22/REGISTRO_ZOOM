import streamlit as st
from sqlalchemy import create_engine, text
import time
import pandas as pd
from streamlit_javascript import st_javascript

# --- 1. CONFIGURACIÓN DE LA BASE DE DATOS ---
try:
    creds = st.secrets["db_credentials"]
    engine = create_engine(
        f"mysql+pymysql://{creds['user']}:{creds['pass']}@{creds['host']}/{creds['name']}",
        pool_pre_ping=True
    )
    conexion_db_exitosa = True
except Exception as e:
    st.error(f"Error de configuración de base de datos: {e}")
    conexion_db_exitosa = False
    engine = None

# --- 2. CAPTURA DEL EVENTO DINÁMICO (LA MAGIA) ---
# Leemos el slug desde la URL (?curso=slug)
slug_url = st.query_params.get("curso")

if not slug_url:
    st.error("⚠️ Enlace no válido. Por favor, utiliza el link oficial proporcionado por MB Educación.")
    st.stop()

# --- 3. BUSCAR INFORMACIÓN DEL EVENTO EN LA BASE DE DATOS ---
@st.cache_data(ttl=60) # Cache de 1 minuto para no saturar la DB
def obtener_datos_evento(slug):
    if not engine: return None
    try:
        with engine.connect() as conn:
            query = text("SELECT * FROM agenda_cursos WHERE slug = :s AND estado = 'activo'")
            return conn.execute(query, {"s": slug}).fetchone()
    except:
        return None

evento = obtener_datos_evento(slug_url)

if not evento:
    st.error("❌ El evento solicitado no existe o ya no se encuentra disponible.")
    st.stop()

# Asignación de variables desde la base de datos
ID_REUNION = evento.slug
NOMBRE_EVENTO = evento.titulo_curso
LINK_ZOOM = evento.link_zoom
LINK_YOUTUBE = evento.link_youtube if evento.link_youtube else "https://www.youtube.com/@mbeducacion"
CUPO_MAXIMO = evento.capacidad_max

# --- 4. VERIFICAR REGISTRO PREVIO Y CONTEO ---
try:
    registro_previo = st_javascript(f"localStorage.getItem('mbeducacion_registro_{ID_REUNION}');")
except:
    registro_previo = None

conteo_actual = 0
if conexion_db_exitosa:
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM directorio_tratamiento 
                WHERE canal_autorizacion LIKE :filtro
            """), {"filtro": f"%{ID_REUNION}%"})
            conteo_actual = result.scalar()
    except:
        conteo_actual = 0

# Determinar destino
if conteo_actual >= CUPO_MAXIMO:
    link_destino = LINK_YOUTUBE
    mensaje_cupo = "⚠️ ¡Sala de Zoom llena! Podrás ver la transmisión en vivo por YouTube."
else:
    link_destino = LINK_ZOOM
    mensaje_cupo = "✨ Tienes un cupo reservado en la sala de Zoom."

# --- 5. VISTA PARA USUARIOS YA REGISTRADOS ---
if registro_previo == "true":
    st.title(NOMBRE_EVENTO)
    st.success("✨ ¡Bienvenido de nuevo! Ya te encuentras registrado.")
    st.info(mensaje_cupo)
    
    st.markdown(f"""
        <a href="{link_destino}" target="_blank" style="
            text-decoration: none; background-color: #2D8CFF; color: white;
            padding: 15px 25px; border-radius: 10px; font-weight: bold;
            display: inline-block; text-align: center; width: 100%;
        ">🚀 INGRESAR A LA TRANSMISIÓN</a>
    """, unsafe_allow_html=True)
    
    if st.button("No soy yo / Registrar nuevos datos"):
        st_javascript(f"localStorage.removeItem('mbeducacion_registro_{ID_REUNION}');")
        st.rerun()
    st.stop()

# --- 6. FORMULARIO DE REGISTRO ---
st.title("Registro de Asistencia")
st.subheader(f"Bienvenido al {NOMBRE_EVENTO}")

with st.form("registro_publico", clear_on_submit=True):
    nombre = st.text_input("Nombre Completo *")
    col1, col2 = st.columns([1, 2])
    with col1:
        tipo_doc = st.selectbox("Tipo Doc *", ["C.C.", "NIT", "C.E.", "Pasaporte", "T.I.", "Otro"])
    with col2:
        doc_identidad = st.text_input("Número de Documento *")

    institucion = st.text_input("Institución / Empresa *")
    rol_cargo = st.text_input("Cargo *")
    email = st.text_input("Correo Electrónico *")
    
    st.markdown("---")
    st.write("🔒 **Habeas Data**")
    with st.expander("Leer Autorización"):
        st.write("Autorizo el tratamiento de mis datos para la gestión del servicio y envío de información comercial.")

    acepta = st.checkbox("He leído y autorizo el tratamiento de mis datos *")
    acepta_promos = st.checkbox("Acepto envío de información comercial y productos")
    
    boton_registro = st.form_submit_button("REGISTRARME E INGRESAR")

# --- 7. LÓGICA DE VALIDACIÓN Y GUARDADO ---
if boton_registro:
    errores = []
    if not nombre or not doc_identidad or not email or not acepta:
        st.error("⚠️ Por favor completa todos los campos obligatorios y acepta los términos.")
    else:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO directorio_tratamiento 
                    (contacto_nombre, tipo_documento, documento_identidad, institucion, rol_cargo, email, habeas_data, autoriza_env_info, canal_autorizacion) 
                    VALUES (:nom, :tdoc, :doc, :inst, :rol, :mail, 1, :env, :cnal)
                """), {
                    "nom": nombre, "tdoc": tipo_doc, "doc": doc_identidad,
                    "inst": institucion, "rol": rol_cargo, "mail": email,
                    "env": 1 if acepta_promos else 0,
                    "cnal": f"Registro Zoom - {ID_REUNION} - {time.strftime('%d/%m/%Y')}"
                })

            st_javascript(f"localStorage.setItem('mbeducacion_registro_{ID_REUNION}', 'true');")
            st.success("✅ Registro exitoso.")
            st.info(f"🔄 {mensaje_cupo}")
            time.sleep(2)
            st.markdown(f'<meta http-equiv="refresh" content="0; url={link_destino}">', unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")
