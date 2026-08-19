from pypdf import PdfReader 
from dotenv import load_dotenv
import os
from google import genai


load_dotenv(".env")
key_api=os.getenv("GEMINI_API_KEY")
client=genai.Client(api_key=key_api)
document=PdfReader("politica_de_ferias_empresa.pdf")
text_saved=""
for page in document.pages:
    print(page.extract_text())
    text_saved+=page.extract_text()
answer= client.models.generate_content(
    model="gemini-3.7-flash",
    contents="Explique o que eh Rag em uma frase simples"
)

print(answer.text)