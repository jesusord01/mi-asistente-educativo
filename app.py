import streamlit as st
import google.generativeai as genai
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from fpdf import FPDF

from curriculo_5to import matematica, religion, comunicacion
from seguridad import verificar_contrasena

# =====================================================================
# PORTERO LÓGICO (LOGIN)
# =====================================================================
if not verificar_contrasena():
    st.stop() 

# Extraemos el nombre del usuario logueado para usarlo en toda la base de datos
usuario_actual = st.session_state.get('usuario_actual', 'desconocido')

with st.sidebar:
    st.markdown(f"👤 **Usuario activo:** `{usuario_actual}`")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()
    st.divider()

# =====================================================================
# CONFIGURACIÓN INICIAL Y BASE DE DATOS
# =====================================================================
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
modelo = genai.GenerativeModel('gemini-2.5-flash')

def inicializar_bd():
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    # NUEVO: Agregamos la columna 'usuario' a las sesiones
    c.execute('''
        CREATE TABLE IF NOT EXISTS sesiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            fecha TEXT, grado TEXT, curso TEXT, tema TEXT, contenido TEXT
        )
    ''')
    # NUEVO: La clave principal ahora es el 'usuario', permitiendo 1 proyecto por profesor
    c.execute('''
        CREATE TABLE IF NOT EXISTS proyecto_activo (
            usuario TEXT PRIMARY KEY,
            titulo TEXT, dificultad TEXT, actividades TEXT, barrio TEXT, interes TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- Funciones para el Historial de Sesiones (FILTRADO POR USUARIO) ---
def guardar_sesion_bd(usuario, grado, curso, tema, contenido):
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute('INSERT INTO sesiones (usuario, fecha, grado, curso, tema, contenido) VALUES (?, ?, ?, ?, ?, ?)',
              (usuario, fecha_actual, grado, curso, tema, contenido))
    conn.commit()
    conn.close()

def obtener_historial(usuario):
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    c.execute('SELECT id, fecha, grado, curso, tema, contenido FROM sesiones WHERE usuario = ? ORDER BY id DESC', (usuario,))
    datos = c.fetchall()
    conn.close()
    return datos

def borrar_historial_bd(usuario):
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    c.execute('DELETE FROM sesiones WHERE usuario = ?', (usuario,))
    conn.commit()
    conn.close()

def borrar_sesion_bd(id_sesion, usuario):
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    c.execute('DELETE FROM sesiones WHERE id = ? AND usuario = ?', (id_sesion, usuario))
    conn.commit()
    conn.close()

# --- Funciones para el Proyecto Bimestral (FILTRADO POR USUARIO) ---
def obtener_proyecto_activo(usuario):
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    c.execute('SELECT titulo, dificultad, actividades, barrio, interes FROM proyecto_activo WHERE usuario = ?', (usuario,))
    datos = c.fetchone() 
    conn.close()
    return datos

def guardar_proyecto_activo(usuario, titulo, dificultad, act, barrio, interes):
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    c.execute('DELETE FROM proyecto_activo WHERE usuario = ?', (usuario,)) 
    c.execute('''
        INSERT INTO proyecto_activo (usuario, titulo, dificultad, actividades, barrio, interes) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (usuario, titulo, dificultad, act, barrio, interes))
    conn.commit()
    conn.close()

def borrar_proyecto_activo(usuario):
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    c.execute('DELETE FROM proyecto_activo WHERE usuario = ?', (usuario,))
    conn.commit()
    conn.close()

# --- Función para Generar PDF ---
def generar_pdf(curso, tema, contenido):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=11)
    
    pdf.cell(200, 10, txt=f"Sesion de Aprendizaje: {curso}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Tema: {tema}", ln=True, align='C')
    pdf.ln(10)
    
    contenido_limpio = contenido.replace('**', '')
    contenido_limpio = contenido_limpio.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=contenido_limpio)
    return pdf.output(dest='S').encode('latin-1')

inicializar_bd()

# =====================================================================
# BARRA LATERAL (HISTORIAL DE SESIONES)
# =====================================================================
with st.sidebar:
    st.header("📚 Mi Historial de Clases")
    
    historial = obtener_historial(usuario_actual)
    
    if len(historial) == 0:
        st.info("Aún no has guardado ninguna sesión.")
    else:
        if st.button("🗑️ Eliminar todo mi historial", type="primary"):
            borrar_historial_bd(usuario_actual)
            st.rerun() 
            
        st.divider()
        
        for sesion in historial:
            id_ses, fecha_str, grado_str, curso_str, tema_str, contenido_str = sesion
            etiqueta = f"{fecha_str} - {grado_str} - {curso_str} - {tema_str}"
            
            with st.expander(etiqueta):
                st.write(contenido_str)
                if st.button("❌ Eliminar esta clase", key=f"borrar_{id_ses}"):
                    borrar_sesion_bd(id_ses, usuario_actual)
                    st.rerun()

# =====================================================================
# INTERFAZ PRINCIPAL (EL PORTERO LÓGICO)
# =====================================================================
st.title("Asistente Educativo - Diseño de Proyecto Bimestral")

proyecto_db = obtener_proyecto_activo(usuario_actual)

if proyecto_db is None:
    st.info("👋 ¡Bienvenido! Parece que iniciamos un nuevo bimestre. Configuremos el proyecto base.")
    
    st.subheader("Paso 1: Contexto del Aula (Fe y Alegría 59 - 5to Grado)")
    col1, col2 = st.columns(2)
    with col1:
        dificultad = st.selectbox("1. Dificultad académica más común:", ["Comprensión lectora", "Matemática", "Concentración en clase", "Organización para estudiar"])
        actividades = st.selectbox("2. Actividades que más ayudan:", ["Explicaciones teóricas", "Actividades prácticas", "Trabajo en grupo", "Uso de videos visuales"])
    with col2:
        barrio = st.selectbox("3. Ambiente del barrio:", ["Seguro y tranquilo", "Moderadamente seguro", "Con problemas de seguridad", "Inseguro o conflictivo"])
        interes = st.selectbox("4. Mayor interés de los estudiantes:", ["Deportes y Olimpiadas", "Videojuegos y Tecnología", "Música y Arte", "Naturaleza y Animales"])

    st.divider()

    st.subheader("Paso 2: Definir el Tema del Proyecto")
    opcion_tema = st.radio("Selecciona una ruta:", ("Quiero ingresar el tema yo mismo", "Quiero que la IA me sugiera opciones"))

    if opcion_tema == "Quiero ingresar el tema yo mismo":
        tema_manual = st.text_input("Escribe el título de tu Proyecto Bimestral:")
        if st.button("Guardar Proyecto y Comenzar Bimestre"):
            if tema_manual:
                guardar_proyecto_activo(usuario_actual, tema_manual, dificultad, actividades, barrio, interes)
                st.rerun() 
            else:
                st.warning("Por favor, escribe un tema.")

    elif opcion_tema == "Quiero que la IA me sugiera opciones":
        if st.button("Generar Sugerencias con IA"):
            with st.spinner("Consultando con Gemini..."):
                prompt = f"Diseña 3 propuestas de Proyecto Bimestral para 5to de primaria. Dificultad: {dificultad}, Interés: {interes}, Entorno: {barrio}."
                respuesta = modelo.generate_content(prompt)
                st.session_state['propuestas_ia'] = respuesta.text

        if 'propuestas_ia' in st.session_state:
            st.success("Propuestas diseñadas por Gemini:")
            st.markdown(st.session_state['propuestas_ia'])
            tema_elegido = st.text_input("Copia y pega aquí el título del proyecto que elegiste:")
            if st.button("Confirmar Selección y Comenzar Bimestre"):
                if tema_elegido:
                    guardar_proyecto_activo(usuario_actual, tema_elegido, dificultad, actividades, barrio, interes)
                    st.rerun() 

else:
    titulo_proy, dif_proy, act_proy, bar_proy, int_proy = proyecto_db
    st.session_state['proyecto_actual'] = titulo_proy 

    st.success(f"🚀 **Proyecto Bimestral Activo:** {titulo_proy}")
    
    if st.button("⚠️ Terminar Bimestre y Crear Nuevo Proyecto"):
        borrar_proyecto_activo(usuario_actual)
        st.rerun()
        
    st.divider()

    st.subheader("Paso 3: Diseño de la Sesión de Clase (Diaria)")

    cursos_disponibles = {
        "Matemática": matematica,
        "Educación Religiosa": religion,
        "Comunicación": comunicacion
    }
    
    curso_seleccionado = st.selectbox("1. Selecciona el Curso:", list(cursos_disponibles.keys()))
    data_curso = cursos_disponibles[curso_seleccionado]
    
    st.write(f"**Grado:** {data_curso['grado']}")
    
    nombres_competencias = [comp["nombre"] for comp in data_curso["competencias"]]
    competencia_elegida = st.selectbox("2. Selecciona la Competencia a trabajar hoy:", nombres_competencias)
    
    capacidades_disponibles = []
    for comp in data_curso["competencias"]:
        if comp["nombre"] == competencia_elegida:
            capacidades_disponibles = comp["capacidades"]
            break
            
    capacidades_elegidas = st.multiselect("3. Selecciona las Capacidades:", capacidades_disponibles)
    tema_sesion = st.text_input("4. Tema específico de la clase (Ej: Los milagros, Multiplicación de fracciones):")
    
    if st.button("Generar Sesión de Clase con IA"):
        if not capacidades_elegidas or not tema_sesion:
            st.warning("⚠️ Selecciona al menos una capacidad y escribe el tema.")
        else:
            with st.spinner("Diseñando la sesión pedagógica con Gemini..."):
                prompt_sesion = f"""
                Diseña una sesión de aprendizaje para {data_curso['grado']}.
                Proyecto: {st.session_state['proyecto_actual']}. Curso: {data_curso['curso']}. Tema: {tema_sesion}.
                Competencia: {competencia_elegida}. Capacidades: {', '.join(capacidades_elegidas)}.
                Contexto del Aula: Alumnos con problemas de {dif_proy}, aprenden mejor con {act_proy}, barrio {bar_proy}, les interesa {int_proy}.
                
                ESTRUCTURA OBLIGATORIA DE LA SESIÓN:
                1. Propósito, Desempeño y Criterio de Evaluación.
                2. Secuencia Didáctica:
                   - INICIO: Motivación y recojo de saberes previos.
                   - DESARROLLO: DEBE iniciar obligatoriamente con una "Problematización" (un reto, problema o conflicto cognitivo claro), seguido de la gestión y acompañamiento del aprendizaje.
                   - CIERRE: Evaluación y metacognición.
                3. Estrategia DUA adaptada al contexto.
                4. Pausa Activa relacionada al tema.
                """
                respuesta_sesion = modelo.generate_content(prompt_sesion)
                st.session_state['sesion_actual'] = respuesta_sesion.text
                st.session_state['tema_actual'] = tema_sesion
                st.session_state['curso_actual_guardado'] = data_curso['curso']

    if 'sesion_actual' in st.session_state:
        st.markdown("### 📝 Tu Sesión de Clase Generada")
        st.info(st.session_state['sesion_actual'])
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("💾 Guardar esta Sesión en mi Historial"):
                guardar_sesion_bd(
                    usuario=usuario_actual, # AHORA GUARDAMOS CON EL NOMBRE DE USUARIO
                    grado=data_curso['grado'], 
                    curso=st.session_state.get('curso_actual_guardado', data_curso['curso']), 
                    tema=st.session_state.get('tema_actual', 'Tema sin nombre'), 
                    contenido=st.session_state['sesion_actual']
                )
                st.success("✅ ¡Sesión guardada correctamente! Revisa el menú lateral izquierdo.")
                
        with col_btn2:
            pdf_bytes = generar_pdf(
                curso=st.session_state.get('curso_actual_guardado', data_curso['curso']),
                tema=st.session_state.get('tema_actual', 'Tema sin nombre'),
                contenido=st.session_state['sesion_actual']
            )
            
            st.download_button(
                label="📄 Descargar como PDF",
                data=pdf_bytes,
                file_name=f"Sesion_{st.session_state.get('tema_actual', 'Clase')}.pdf",
                mime="application/pdf"
            )