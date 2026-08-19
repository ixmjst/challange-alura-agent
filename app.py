import streamlit as st

from pypdf import PdfReader 
from dotenv import load_dotenv
import os
from google import genai


load_dotenv(".env")
key_api = st.secrets.get("GEMINI_API_KEY", None) or os.getenv("GEMINI_API_KEY")
client=genai.Client(api_key=key_api)
path="politica_de_ferias_empresa.pdf"
document=PdfReader(path)
text_saved=""
for page in document.pages:
    text_saved+=page.extract_text()
    


question = st.text_input("Faça uma pergunta")
button=st.button("Perguntar")

if ((question!="") and (button)) :        
 prompt = f"""
 Você é um assistente que responde perguntas de colaboradores com base
 em documentos internos da empresa. Responda usando SOMENTE o documento
 abaixo. Se a resposta não estiver no documento, diga que não encontrou
 essa informação.

 DOCUMENTO:
 {text_saved}

 PERGUNTA:
 {question}
 """
 answer= client.models.generate_content(
    model="gemini-3.7-flash",
    contents=prompt
 )

 st.write(answer.text)
 st.write(f"Fonte:{path}")


