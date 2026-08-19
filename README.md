# challange-alura-agent

Agente de perguntas e respostas sobre documentos internos da empresa, construído em Python
com Streamlit e a API Gemini do Google.

---

## 1. Descrição geral do projeto

Este projeto é um **assistente interno de Recursos Humanos**. O colaborador escreve uma
pergunta em linguagem natural (por exemplo, *"Com quantos dias de antecedência devo pedir
férias?"*) e o agente responde **exclusivamente com base no documento interno** carregado
pela aplicação — neste caso, o ficheiro `politica_de_ferias_empresa.pdf` (Política de Férias
da *Nova Horizonte, Lda.*).

O objetivo é resolver um problema comum nas organizações: as regras existem, estão escritas,
mas ninguém as lê. Em vez de procurar manualmente num PDF de várias páginas, o colaborador
pergunta e recebe a resposta.

Duas características definem o comportamento do agente:

- **Resposta ancorada no documento.** As instruções do sistema obrigam o modelo a usar
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
│  3. PdfReader(path)            → lê o PDF                        │
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
- **Chave de API com dupla origem.** A linha
  `st.secrets.get("GEMINI_API_KEY", None) or os.getenv("GEMINI_API_KEY")`
  permite que o mesmo código corra em ambiente local (com `.env`) e no Streamlit Community
  Cloud (com *secrets*), sem alterações.
- **Sem base vetorial.** Para um documento desta dimensão, injetar o texto completo é mais
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
│   └── devcontainer.json          # ambiente Python 3.11 + arranque automático do Streamlit
├── .gitignore                     # inclui .env (a chave nunca é versionada)
├── app.py                         # aplicação completa
├── politica_de_ferias_empresa.pdf # documento interno consultado pelo agente
├── requirements.txt               # dependências
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

### Utilizar outro documento

Substituir `politica_de_ferias_empresa.pdf` e atualizar a variável `path` em
[app.py:12](app.py#L12).

---

## 5. Exemplos de perguntas que o agente consegue responder

Todas estas perguntas têm resposta no documento carregado:

**Sobre prazos e procedimentos**
- Com quantos dias de antecedência devo pedir férias?
- A quem devo apresentar o pedido de férias?
- O meu pedido fica aprovado assim que o submeto?
- Como faço para alterar um período de férias já aprovado?

**Sobre critérios e regras**
- Quais são os critérios usados para aprovar um pedido de férias?
- A empresa pode alterar as minhas férias depois de aprovadas?
- Esta política aplica-se a colaboradores contratados a termo?
- O que acontece se a política estiver em conflito com a lei laboral?

**Sobre responsabilidades**
- Quais são as minhas responsabilidades enquanto colaborador?
- O que compete à empresa na gestão das férias?
- Preciso de passar as minhas tarefas a alguém antes de sair de férias?

**Sobre o âmbito do documento**
- Qual é o objetivo desta política?
- Quando entra em vigor esta política?

**Perguntas fora do âmbito** (o agente deve recusar responder)
- Quantos dias de férias tenho direito por ano?
- Qual é o valor do subsídio de férias?
- Posso vender dias de férias?

---

## 6. Exemplos de respostas geradas pelo agente

Os exemplos abaixo ilustram o formato típico das respostas produzidas pela aplicação.

---

**Pergunta:** Com quantos dias de antecedência devo pedir férias?

> De acordo com o documento, o colaborador deve apresentar o pedido de férias ao seu
> superior hierárquico com, pelo menos, **15 dias de antecedência**, salvo em situações
> excecionais devidamente justificadas. O período solicitado só é considerado aprovado
> após confirmação formal do responsável competente.
>
> Fonte: politica_de_ferias_empresa.pdf

---

**Pergunta:** Quais são os critérios usados para aprovar um pedido de férias?

> O documento indica quatro critérios de aprovação:
>
> 1. **Continuidade do serviço** — deve ser assegurada a cobertura mínima das atividades
>    essenciais.
> 2. **Equidade** — os pedidos são avaliados de forma justa entre os colaboradores.
> 3. **Antecedência** — pedidos apresentados com maior antecedência permitem melhor
>    capacidade de planeamento.
> 4. **Necessidades excecionais** — a empresa poderá ajustar períodos quando existirem
>    necessidades operacionais justificadas.
>
> Fonte: politica_de_ferias_empresa.pdf

---

**Pergunta:** A empresa pode obrigar-me a mudar as férias já aprovadas?

> Segundo o documento, em situações de necessidade operacional devidamente fundamentada,
> a empresa poderá solicitar a alteração do período de férias, procurando acordar uma
> alternativa com o colaborador. Alterações a períodos previamente aprovados devem ser
> comunicadas ao responsável hierárquico e ao departamento de Recursos Humanos.
>
> Fonte: politica_de_ferias_empresa.pdf

---

**Pergunta:** Quantos dias de férias tenho direito por ano?

> Não encontrei essa informação no documento. A política define as regras de planeamento,
> solicitação e aprovação de férias, mas não especifica o número de dias de férias a que
> cada colaborador tem direito — remetendo, nessa matéria, para a legislação laboral
> aplicável.
>
> Fonte: politica_de_ferias_empresa.pdf

---

Este último exemplo demonstra o comportamento mais importante do agente: **admitir o que
não sabe**. É essa restrição que torna o assistente utilizável num contexto de Recursos
Humanos, onde uma resposta inventada sobre direitos laborais teria consequências reais.

---

## Limitações conhecidas

- O agente consulta **um único documento**, definido de forma fixa no código.
- O documento inteiro é enviado em cada pergunta; para documentos grandes seria necessário
  adotar *chunking* e pesquisa por *embeddings*.
- Não existe histórico de conversa — cada pergunta é independente das anteriores.
- PDFs digitalizados (imagem) não são suportados, por não conterem texto extraível.

---

## Contexto

Projeto desenvolvido no âmbito do desafio de Agentes de IA da **Alura**.
