import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar la llave secreta
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Buscando modelos disponibles en tu cuenta de Gemini...\n")

# Consultar a la API por los modelos
try:
    for m in genai.list_models():
        # Filtramos solo los modelos que sirven para generar texto (generateContent)
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Modelo compatible encontrado: {m.name}")
            
    print("\n¡Prueba terminada! Copia uno de los nombres de arriba (quitando la parte de 'models/').")
except Exception as e:
    print(f"Hubo un error al consultar: {e}")