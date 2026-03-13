import streamlit as st
import os
from dotenv import load_dotenv

# Cargar las credenciales ocultas
load_dotenv()

def verificar_contrasena():
    """Retorna True si el usuario ingresó correctamente, False si no."""
    
    # 1. Creamos la memoria de la sesión si no existe
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    # 2. Si ya entró antes, lo dejamos pasar de frente
    if st.session_state['autenticado']:
        return True

    # 3. Si no ha entrado, le mostramos el formulario
    st.title("🔒 Acceso Restringido")
    st.write("Por favor, ingresa tus credenciales para usar el asistente.")
    
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        # Comparamos lo que escribió con lo que está en el .env
        if usuario == os.getenv("USUARIO_APP") and contrasena == os.getenv("PASSWORD_APP"):
            st.session_state['autenticado'] = True
            st.rerun() # Recargamos la página para que desaparezca el login
        else:
            st.error("❌ Usuario o contraseña incorrectos")
            
    # Retorna False mientras no ponga la clave correcta
    return False
