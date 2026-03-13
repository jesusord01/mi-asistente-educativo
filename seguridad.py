import streamlit as st
import os
from dotenv import load_dotenv

# Cargar las credenciales ocultas
load_dotenv()

def verificar_contrasena():
    """Retorna True si el usuario ingresó correctamente, False si no."""
    
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    if st.session_state['autenticado']:
        return True

    st.title("🔒 Acceso Restringido")
    st.write("Por favor, ingresa tus credenciales para usar el asistente.")
    
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        # 1. Agrupamos los usuarios y contraseñas del .env en un diccionario
        usuarios_validos = {
            os.getenv("USUARIO_1"): os.getenv("PASSWORD_1"),
            os.getenv("USUARIO_2"): os.getenv("PASSWORD_2"),
            os.getenv("USUARIO_3"): os.getenv("PASSWORD_3")
        }
        
        # 2. Verificamos si el usuario escrito existe en el diccionario Y si su clave coincide
        if usuario in usuarios_validos and usuarios_validos[usuario] == contrasena:
            st.session_state['autenticado'] = True
            st.rerun() 
        else:
            st.error("❌ Usuario o contraseña incorrectos")
            
    return False