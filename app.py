import streamlit as st
import google.generativeai as genai
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

from curriculo_5to import matematica, religion, comunicacion
from seguridad import verificar_contrasena # <-- IMPORTAMOS TU NUEVO ARCHIVO

# =====================================================================
# PORTERO LÓGICO (LOGIN)
# =====================================================================
# Si la contraseña no es correcta, detenemos toda la aplicación aquí mismo
if not verificar_contrasena():
    st.stop() 

# Botón opcional para cerrar sesión (lo ponemos arriba de todo)
with st.sidebar:
    if st.button("🚪 Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()


# =====================================================================
# CONFIGURACIÓN INICIAL Y BASE DE DATOS
# =====================================================================
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
modelo = genai.GenerativeModel('gemini-2.5-flash')

def inicializar_bd():
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sesiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT, grado TEXT, curso TEXT, tema TEXT, contenido TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS proyecto_activo (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            titulo TEXT, dificultad TEXT, actividades TEXT, barrio TEXT, interes TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- Funciones para el Historial de Sesiones ---
def guardar_sesion_bd(grado, curso, tema, contenido):
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute('INSERT INTO sesiones (fecha, grado, curso, tema, contenido) VALUES (?, ?, ?, ?, ?)',
              (fecha_actual, grado, curso, tema, contenido))
    conn.commit()
    conn.close()

def obtener_historial():
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    # ATENCIÓN: Ahora también pedimos el 'id' a la base de datos
    c.execute('SELECT id, fecha, grado, curso, tema, contenido FROM sesiones ORDER BY id DESC')
    datos = c.fetchall()
    conn.close()
    return datos

def borrar_historial_bd():
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    c.execute('DELETE FROM sesiones')
    conn.commit()
    conn.close()

# NUEVA FUNCIÓN: Borrar una sesión específica usando su ID
def borrar_sesion_bd(id_sesion):
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    c.execute('DELETE FROM sesiones WHERE id = ?', (id_sesion,))
    conn.commit()
    conn.close()

# --- Funciones para el Proyecto Bimestral ---
def obtener_proyecto_activo():
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    c.execute('SELECT titulo, dificultad, actividades, barrio, interes FROM proyecto_activo WHERE id = 1')
    datos = c.fetchone() 
    conn.close()
    return datos

def guardar_proyecto_activo(titulo, dificultad, act, barrio, interes):
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    c.execute('DELETE FROM proyecto_activo') 
    c.execute('''
        INSERT INTO proyecto_activo (id, titulo, dificultad, actividades, barrio, interes) 
        VALUES (1, ?, ?, ?, ?, ?)
    ''', (titulo, dificultad, act, barrio, interes))
    conn.commit()
    conn.close()

def borrar_proyecto_activo():
    conn = sqlite3.connect('colegio_feyalegria.db')
    c = conn.cursor()
    c.execute('DELETE FROM proyecto_activo')
    conn.commit()
    conn.close()

inicializar_bd()

# =====================================================================
# BARRA LATERAL (HISTORIAL DE SESIONES)
# =====================================================================
with st.sidebar:
    st.header("📚 Mi Historial de Clases")
    st.write("Aquí se guardan tus sesiones generadas.")
    
    historial = obtener_historial()
    
    if len(historial) == 0:
        st.info("Aún no has guardado ninguna sesión.")
    else:
        # Botón para eliminar TODO
        if st.button("🗑️ Eliminar todo el historial", type="primary"):
            borrar_historial_bd()
            st.rerun() 
            
        st.divider()
        
        # Bucle para mostrar cada sesión con su propio botón de borrar
        for sesion in historial:
            # Desempaquetamos los 6 datos (incluyendo el ID)
            id_ses, fecha_str, grado_str, curso_str, tema_str, contenido_str = sesion
            etiqueta = f"{fecha_str} - {grado_str} - {curso_str} - {tema_str}"
            
            with st.expander(etiqueta):
                st.write(contenido_str)
                # BOTÓN NUEVO: Eliminar solo esta sesión (usando un key único)
                if st.button("❌ Eliminar esta clase", key=f"borrar_{id_ses}"):
                    borrar_sesion_bd(id_ses)
                    st.rerun()

# =====================================================================
# INTERFAZ PRINCIPAL (EL PORTERO LÓGICO)
# =====================================================================
st.title("Asistente Educativo - Diseño de Proyecto Bimestral")

proyecto_db = obtener_proyecto_activo()

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
                guardar_proyecto_activo(tema_manual, dificultad, actividades, barrio, interes)
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
                    guardar_proyecto_activo(tema_elegido, dificultad, actividades, barrio, interes)
                    st.rerun() 

else:
    titulo_proy, dif_proy, act_proy, bar_proy, int_proy = proyecto_db
    st.session_state['proyecto_actual'] = titulo_proy 

    st.success(f"🚀 **Proyecto Bimestral Activo:** {titulo_proy}")
    
    if st.button("⚠️ Terminar Bimestre y Crear Nuevo Proyecto"):
        borrar_proyecto_activo()
        st.rerun()
        
    st.divider()

# --- PASO 3: SESIÓN DE CLASE CON GUARDADO ---
    st.subheader("Paso 3: Diseño de la Sesión de Clase (Diaria)")

    # 1. Empaquetamos los cursos en un diccionario para poder seleccionarlos
    cursos_disponibles = {
        "Matemática": matematica,
        "Educación Religiosa": religion,
        "Comunicación": comunicacion
    }
    
    # 2. El usuario primero elige el CURSO
    curso_seleccionado = st.selectbox("1. Selecciona el Curso:", list(cursos_disponibles.keys()))
    
    # 3. Extraemos la data solo del curso que eligió
    data_curso = cursos_disponibles[curso_seleccionado]
    
    st.write(f"**Grado:** {data_curso['grado']}")
    
    # 4. Los menús de abajo ahora se alimentan de 'data_curso'
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
                st.session_state['curso_actual_guardado'] = data_curso['curso'] # Guardamos el curso para la BD

    if 'sesion_actual' in st.session_state:
        st.markdown("### 📝 Tu Sesión de Clase Generada")
        st.info(st.session_state['sesion_actual'])
        
        if st.button("💾 Guardar esta Sesión en mi Historial"):
            guardar_sesion_bd(
                grado=data_curso['grado'], 
                curso=st.session_state.get('curso_actual_guardado', data_curso['curso']), 
                tema=st.session_state.get('tema_actual', 'Tema sin nombre'), 
                contenido=st.session_state['sesion_actual']
            )
            st.success("✅ ¡Sesión guardada correctamente! Revisa el menú lateral izquierdo.")