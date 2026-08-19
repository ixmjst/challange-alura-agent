# challange-alura-agent

Agente de perguntas e respostas sobre a documentação oficial da **Nova Horizonte Store**,
construído em Python com Streamlit e a API Gemini do Google.

---

## 1. Descrição geral do projeto

Este projeto é um **assistente de atendimento** para uma loja online. O utilizador escreve
uma pergunta em linguagem natural (por exemplo, *"Como inicio um pedido de devolução?"*) e o
agente responde **exclusivamente com base no documento oficial** carregado pela aplicação.

O documento atualmente ativo é a **Política de Reembolso e Devoluções**
(`loja-online-docs/02_politica_de_reembolso_e_devolucoes.pdf`), definida na variável `path`
em [app.py:12](app.py#L12). A pasta [loja-online-docs/](loja-online-docs/) contém cinco
documentos da loja, que podem ser trocados alterando essa única linha.

O objetivo é resolver um problema comum no comércio eletrónico: as regras existem, estão
publicadas, mas ninguém as lê. Em vez de percorrer manualmente um PDF, a pessoa pergunta e
recebe a resposta.

Duas características definem o comportamento do agente:

- **Resposta ancorada no documento.** As instruções do prompt obrigam o modelo a usar
  somente o conteúdo do PDF. Se a informação não constar do documento, o agente deve
  declarar que não a encontrou, em vez de inventar (reduzindo alucinações).
- **Indicação da fonte.** Cada resposta é acompanhada do ficheiro que serviu de base,
  permitindo a verificação humana.

---

## 2. Arquitetura da solução

A solução segue um padrão simples de **RAG sem base vetorial** (*prompt stuffing*): como o
documento é pequeno, o texto integral é injetado diretamente no prompt, dispensando
*chunking*, *embeddings* e base de dados vetorial.

```
┌──────────────────────────────────────────────────────────────────┐
│                        Navegador (utilizador)                    │
│                  campo de texto  +  botão "Perguntar"            │
└───────────────────────────┬──────────────────────────────────────┘
                            │  pergunta
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                    app.py  —  interface Streamlit                │
│                                                                  │
│  1. load_dotenv(".env")        → carrega variáveis de ambiente   │
│  2. st.secrets / os.getenv     → obtém a GEMINI_API_KEY          │
│  3. PdfReader(path)            → lê o PDF indicado em `path`     │
│  4. page.extract_text()        → extrai o texto de cada página   │
│  5. monta o prompt:                                              │
│         instruções + DOCUMENTO (texto extraído) + PERGUNTA       │
└───────────────────────────┬──────────────────────────────────────┘
                            │  prompt completo
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│              Google Gemini API  (google-genai client)            │
│                client.models.generate_content(...)               │
└───────────────────────────┬──────────────────────────────────────┘
                            │  resposta em texto
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│      st.write(resposta)   +   st.write("Fonte: <ficheiro>")      │
└──────────────────────────────────────────────────────────────────┘
```

### Camadas

| Camada | Responsabilidade | Implementação |
|---|---|---|
| Interface | Recolher a pergunta e apresentar a resposta | `st.text_input`, `st.button`, `st.write` |
| Ingestão de dados | Ler o PDF e extrair texto legível | `pypdf.PdfReader` + `extract_text()` |
| Orquestração | Compor o prompt com contexto, regras e pergunta | *f-string* em `app.py` |
| Inteligência | Gerar a resposta a partir do contexto | Modelo Gemini via `google-genai` |
| Configuração | Gerir a chave de API em local e na nuvem | `python-dotenv` + `st.secrets` |

### Decisões de desenho

- **Ficheiro único (`app.py`).** O projeto foi consolidado num só módulo — a lógica do
  antigo `processador.py` foi reutilizada dentro da própria aplicação, evitando duplicação.
- **Documento configurável numa linha.** Toda a base de conhecimento do agente depende da
  variável `path`. Trocar de documento não exige qualquer outra alteração ao código.
- **Chave de API com dupla origem.** A linha
  `st.secrets.get("GEMINI_API_KEY", None) or os.getenv("GEMINI_API_KEY")`
  permite que o mesmo código corra em ambiente local (com `.env`) e no Streamlit Community
  Cloud (com *secrets*), sem alterações.
- **Sem base vetorial.** Para documentos desta dimensão, injetar o texto completo é mais
  simples, mais barato de manter e evita erros de recuperação de fragmentos.
- **Extração feita no arranque.** O PDF é lido uma vez quando o script corre, e não a cada
  pergunta.

---

## 3. Tecnologias e ferramentas utilizadas

| Tecnologia | Função no projeto |
|---|---|
| **Python 3.11** | Linguagem base do projeto |
| **Streamlit** | Interface web (campo de pergunta, botão e apresentação da resposta) |
| **Google Gemini API** (`google-genai`) | Modelo de linguagem que gera as respostas |
| **pypdf** | Leitura do PDF e extração do texto das páginas |
| **python-dotenv** | Carregamento da chave de API a partir do ficheiro `.env` |
| **Dev Container** (`.devcontainer/`) | Ambiente reprodutível em Codespaces / VS Code, com arranque automático da app na porta 8501 |
| **Git / GitHub** | Controlo de versões |

Ficheiros do repositório:

```
challange-alura-agent/
├── .devcontainer/
│   └── devcontainer.json                          # Python 3.11 + arranque automático do Streamlit
├── loja-online-docs/                              # base documental da loja
│   ├── 01_politica_de_privacidade.pdf
│   ├── 02_politica_de_reembolso_e_devolucoes.pdf  # ← documento ativo
│   ├── 03_faq.pdf
│   ├── 04_guia_de_envios_e_entregas.pdf
│   └── 05_termos_e_condicoes.pdf
├── .gitignore                                     # inclui .env (a chave nunca é versionada)
├── app.py                                         # aplicação completa
├── requirements.txt                               # dependências
└── README.md
```

---

## 4. Instruções para executar o projeto

### Pré-requisitos

- Python 3.11 ou superior
- Uma chave da API Gemini ([Google AI Studio](https://aistudio.google.com/apikey))

### Execução local

**1. Clonar o repositório**

```bash
git clone https://github.com/<utilizador>/challange-alura-agent.git
cd challange-alura-agent
```

**2. Criar e ativar um ambiente virtual**

```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate
```

**3. Instalar as dependências**

```bash
pip install -r requirements.txt
pip install streamlit
```

> Nota: o `requirements.txt` não inclui o `streamlit` — no Dev Container ele é instalado
> num passo separado (`updateContentCommand`). Localmente, instale-o com o comando acima.

**4. Configurar a chave de API**

Criar um ficheiro `.env` na raiz do projeto:

```env
GEMINI_API_KEY=a_sua_chave_aqui
```

O `.env` está listado no `.gitignore`, pelo que a chave não é enviada para o repositório.

**5. Arrancar a aplicação**

```bash
streamlit run app.py
```

A aplicação fica disponível em `http://localhost:8501`.

### Execução em GitHub Codespaces / Dev Container

Basta abrir o repositório num Codespace. O `devcontainer.json` trata do resto:
instala as dependências, arranca `streamlit run app.py` e encaminha a porta **8501**,
abrindo a pré-visualização automaticamente. A chave deve ser fornecida como *secret*
do Codespace ou num `.env` local ao contentor.

### Publicação no Streamlit Community Cloud

Ao publicar, adicionar a chave em **Settings → Secrets**:

```toml
GEMINI_API_KEY = "a_sua_chave_aqui"
```

O código lê `st.secrets` automaticamente, sem qualquer alteração.

### Trocar o documento consultado

Alterar a variável `path` em [app.py:12](app.py#L12) para qualquer um dos ficheiros de
[loja-online-docs/](loja-online-docs/):

```python
path = "loja-online-docs/04_guia_de_envios_e_entregas.pdf"
```

Guardar o ficheiro — o Streamlit recarrega automaticamente e o agente passa a responder
com base no novo documento.

---

## 5. Exemplos de perguntas que o agente consegue responder

Com o documento ativo (**Política de Reembolso e Devoluções**), estas perguntas têm
resposta no texto:

**Iniciar uma devolução**
- Como inicio um pedido de devolução?
- Que informações preciso de fornecer para devolver um produto?
- Tenho de enviar fotografias do artigo?
- Onde é que o processo de devolução deve ser iniciado?

**Condições e casos especiais**
- Em que condições o produto deve ser devolvido?
- Os produtos personalizados seguem as mesmas regras de devolução?
- A empresa pode pedir-me informações adicionais?
- Recebi um produto com defeito — o que acontece a seguir?
- Recebi um artigo diferente do que encomendei. O que posso fazer?
- Que soluções a empresa pode oferecer num caso de produto danificado?

**Reembolsos e custos**
- De que forma recebo o reembolso?
- O reembolso é feito no mesmo método de pagamento que usei?
- Porque é que o reembolso pode demorar?
- Quem suporta os custos da devolução?

**Sobre o documento**
- Qual é o objetivo desta política?
- Quando foi este documento atualizado?

**Perguntas fora do âmbito** (o agente deve recusar responder)
- Quantos dias tenho para devolver um produto?
- Qual é a morada para onde devo enviar a devolução?
- Qual é o número de telefone do apoio ao cliente?
- Quanto tempo demora a entrega de uma encomenda?
- A loja envia para fora do país?

> As três últimas pertencem a outros documentos da pasta (FAQ, guia de envios), o que
> torna evidente o limite do agente: ele só conhece o ficheiro indicado em `path`.

---

## 6. Exemplos de respostas geradas pelo agente

Os exemplos abaixo ilustram o formato típico das respostas produzidas pela aplicação.

---

**Pergunta:** Como inicio um pedido de devolução?

> De acordo com o documento, deve contactar o atendimento da Nova Horizonte Store e
> indicar:
>
> - o **número do pedido**;
> - o **motivo da devolução**.
>
> Quando lhe for solicitado, deverá ainda apresentar **fotografias ou outras evidências**.
> O processo deve ser iniciado através dos canais oficiais da Nova Horizonte Store.
>
> Fonte: loja-online-docs/02_politica_de_reembolso_e_devolucoes.pdf

---

**Pergunta:** Recebi um produto com defeito. O que é que a loja faz?

> Segundo o documento, quando o produto apresenta defeito, dano ou não corresponde ao
> pedido, a empresa analisa o caso e, quando aplicável, providencia uma destas soluções:
>
> 1. **substituição** do artigo;
> 2. **reparação**;
> 3. **crédito**;
> 4. **reembolso**.
>
> A empresa poderá solicitar informações adicionais para avaliar a ocorrência.
>
> Fonte: loja-online-docs/02_politica_de_reembolso_e_devolucoes.pdf

---

**Pergunta:** De que forma recebo o reembolso e quanto tempo demora?

> Quando aprovado, o reembolso é processado pelo **meio de pagamento utilizado** na compra
> ou por outro método permitido.
>
> Quanto ao tempo, o documento não indica um prazo em dias — refere apenas que **o prazo
> pode depender da instituição financeira**.
>
> Fonte: loja-online-docs/02_politica_de_reembolso_e_devolucoes.pdf

---

**Pergunta:** Quem paga os portes da devolução?

> O documento indica que a responsabilidade pelos custos de devolução **depende do motivo
> da devolução e da legislação aplicável**. Não é especificada uma regra fixa sobre quem
> suporta esses custos em cada situação.
>
> Fonte: loja-online-docs/02_politica_de_reembolso_e_devolucoes.pdf

---

**Pergunta:** Quantos dias tenho para devolver um produto?

> Não encontrei essa informação no documento. A Política de Reembolso e Devoluções descreve
> como pedir a devolução, as condições gerais, o tratamento de produtos defeituosos e a
> forma de processamento do reembolso, mas não indica um prazo em dias para efetuar a
> devolução.
>
> Fonte: loja-online-docs/02_politica_de_reembolso_e_devolucoes.pdf

---

Os dois últimos exemplos demonstram o comportamento mais importante do agente: **não ir
além do que o documento diz**. É essa restrição que torna o assistente utilizável num
contexto de atendimento ao cliente, onde uma resposta inventada sobre prazos ou custos de
devolução criaria uma expectativa que a loja não teria de cumprir.

---

## Limitações conhecidas

- O agente consulta **um único documento de cada vez**, definido de forma fixa no código —
  os restantes ficheiros de `loja-online-docs/` só ficam acessíveis alterando `path`.
- O documento inteiro é enviado em cada pergunta; para documentos grandes seria necessário
  adotar *chunking* e pesquisa por *embeddings*.
- Não existe histórico de conversa — cada pergunta é independente das anteriores.
- PDFs digitalizados (imagem) não são suportados, por não conterem texto extraível.

---

## Contexto

Projeto desenvolvido no âmbito do desafio de Agentes de IA da **Alura**.
