from pypdf import PdfReader 

document=PdfReader("politica_de_ferias_empresa.pdf")
text_saved=""
for page in document.pages:
    print(page.extract_text())
    text_saved+=page.extract_text()
