# 🐾 Agente Autônomo de Agendamento com LangGraph & OpenAI

Agente inteligente de agendamento para clínicas veterinárias e petshops, construído com **LangGraph**, **LangChain** e **GPT-4o-mini**.

Esta versão é **100% autônoma e local**: utiliza arquivos JSON como camada de persistência thread-safe, dispensando a necessidade de banco de dados relacional externo ou serviços de mensageria complexos para testes e demonstrações.

---

## 🌟 Principais Recursos

- **🧠 Orquestração Cíclica com LangGraph**: Grafo de estados com máquina finita que guia o cliente pelas etapas de agendamento (Cliente ➔ Serviço ➔ Pet ➔ Horário ➔ Confirmação).
- **🔀 Tomada de Decisão Condicional (`should_use_tool`)**: O LLM decide dinamicamente quando executar ações técnicas (15 ferramentas locais) ou quando responder diretamente em linguagem natural.
- **🎙️ Suporte a Áudio Multimodal**:
  - Transcrição automática de mensagens de voz com **OpenAI Whisper**.
  - Gravação de áudio em tempo real pelo microfone no terminal (`/gravar`).
  - Geração de resposta em áudio com **OpenAI TTS** e reprodução automática via alto-falantes.
  - A reprodução de áudio só é acionada quando o agente responde com mensagem de voz.
- **🧪 Benchmark de Avaliação (`evals/`)**: Suíte completa com **25 cenários reais de atendimento** (cliente confuso, restrições de agenda, cancelamentos, multimodal, pedidos fora do escopo) com **100% de taxa de acerto**.
- **📊 Visualizador de Fluxo (`visualize.py`)**: Interface interativa que renderiza o grafo de execução em SVG com navegação passo a passo.

---

## 📁 Estrutura do Projeto

```
langgraph-scheduling-agent/
├── agent/                       # Núcleo da lógica do agente (LangGraph)
│   ├── db/                      # Funções de envio e integração (WhatsApp/Áudio)
│   ├── graph/                   # Definição do StateGraph e pipeline de mensagens
│   ├── nodes/                   # Nós do grafo (agent, tool_executer, update_step, reset_state)
│   ├── states/                  # Schemas do estado global (AgentState)
│   ├── tools/                   # 15 ferramentas locais chamadas pelo LLM
│   └── utils/                   # Prompts dinâmicos, cálculos de data e funções auxiliares
│
├── data/                        # Banco de dados local em JSON (editável)
│   ├── agent_config.json        # Configuração do agente (nome, tom, voz, modo de áudio)
│   ├── appointments.json        # Agendamentos confirmados
│   ├── blocked_schedules.json   # Bloqueios de feriados e manutenções
│   ├── clinic_config.json       # Dados da clínica (horários de funcionamento, endereço, GPS)
│   ├── clients.json             # Clientes cadastrados
│   ├── conversations.json       # Histórico de conversas
│   ├── pets.json                # Pets cadastrados
│   ├── products.json            # Catálogo de produtos da loja
│   └── services.json            # Serviços disponíveis e preços
│
├── database/                    # Camada de persistência local thread-safe
│   ├── local_db.py              # Gerenciador Singleton de leitura/escrita JSON
│   ├── schemas.py               # Modelos Pydantic
│   └── services.py              # Interface de serviços de dados
│
├── evals/                       # 🧪 Framework de Benchmark e Testes
│   ├── conversations/           # 25 cenários reais de teste em JSON
│   ├── evaluator.py             # Motor de validação de intenções, steps e tools
│   ├── run_evals.py             # Script de execução do benchmark
│   └── EVAL_REPORT.md           # Relatório consolidado de resultados
│
├── chat.py                      # 💬 Terminal interativo com suporte a texto e microfone
├── visualize.py                 # 📊 Gerador do visualizador interativo do fluxo
├── main.py                      # Servidor FastAPI para recepção de webhooks (Evolution API)
├── requirements.txt
├── .env.example
├── LICENSE
└── README.md
```

---

## 🚀 Instalação e Execução

### 1. Pré-requisitos
- Python 3.10+
- FFmpeg (opcional, necessário para gravação de áudio pelo microfone):
  ```bash
  # macOS (Homebrew)
  brew install ffmpeg
  ```

### 2. Clonar e Instalar Dependências
```bash
git clone https://github.com/gabriel-adorno/langgraph-scheduling-agent.git
cd langgraph-scheduling-agent

python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente
Crie o arquivo `.env` a partir do modelo:
```bash
cp .env.example .env
```
Adicione sua chave da OpenAI no `.env`:
```env
OPENAI_API_KEY="sk-..."
```

---

## 💬 Modo Terminal Interativo (`chat.py`)

Execute o chat interativo para conversar diretamente com o agente no terminal:

```bash
python chat.py
```

### Comandos disponíveis no chat:
- **Digitar mensagem**: Envia mensagem de texto convencional.
- **`/gravar` ou `/mic`**: Grava sua voz no microfone do computador (pressione `ENTER` para enviar).
- **`/audio <texto>`**: Simula envio de áudio sintetizado para teste rápido.
- **`sair`**: Encerra a sessão.

> 🔊 **Regra de reprodução de voz**: Respostas do agente em texto permanecem em silêncio; respostas em áudio são sintetizadas e reproduzidas automaticamente nos alto-falantes.

---

## Como os prompts são construídos

A cada turno, `agent/nodes/agent_node.py` monta um `SystemMessage` com `get_prompt(state)` (`agent/utils/prompts.py`) e envia esse texto mais o histórico para o modelo, com as 15 tools. O prompt **não é um arquivo estático**.

**Partes dinâmicas** (concatenadas nessa ordem):

1. **Prompt-base** — papel (assistente de agendamento pet), tom, formato JSON de resposta (`mode`, `reply_to`, `content`) e regras de tool call.
2. **Áudio** — só entra se `personality.audio_use == "none"`; nesse caso força `"mode": "text"`. Com o `data/agent_config.json` atual (`audio_use: "moderate"`), esse bloco **não** é incluído.
3. **Personalidade e clínica** — nome do agente, clínica, tom, idioma, horário de funcionamento, timezone e data/hora local.
4. **Nome do usuário** — só se `client_info.name` já existir no estado.
5. **Instruções do passo atual** — `REGISTER_CLIENT`, `CHOOSE_SERVICE`, `CHOOSE_PET`, `CHOOSE_DATE` ou `CONFIRM_SCHEDULE`. O passo é definido pelo nó `update_step` (campos do estado), não pelo LLM. Outros valores de `step` deixam esse trecho vazio.
6. **Agendamentos anteriores** — se `has_previous_appointments` for verdadeiro, inclui regras de listar / cancelar / remarcar; senão, diz que o usuário não tem agendamentos.

**Regras de tools no prompt (por passo):** `register_client_tool` após o nome; em serviço, `get_services_list_tool` antes e `choose_service_tool` só após confirmação; em pet, `list_pets_tool` antes de falar com o usuário; em data, `check_availability_tool` antes de `choose_date_tool`; na confirmação, `get_schedule_summary_tool` ao entrar e `confirm_schedule_tool` só com confirmação explícita. Se o modelo anuncia uma tool, o prompt exige chamá-la no mesmo turno.

**Fora de escopo:** o prompt de produção **não** tem um bloco de recusa. Há só o papel (“scheduling assistant … pet care”), “never invent data” e “only act through tools”. Recusar pizza, receita humana, etc. depende do modelo. Os casos `fora_do_escopo` estão nos JSONs de `evals/`; o modo simulado usa palavras-chave, não este prompt.

Trecho fiel do prompt-base (sem dados de cliente):

```
You are an intelligent scheduling assistant specialized in managing pet care
services like baths, grooming, and consultations.
You talk naturally with users, understand their intent, and perform real
actions using tools when needed.

- Never invent data. If something isn’t known, ask the user politely.
- You can only act through your tools — never assume results or make up data.
- When you say you will use a tool, you MUST call it immediately in the same turn.
- If calling a tool, do NOT return the JSON above.
- Tool calls must follow the standard OpenAI tool-call format.
```

---

## 🧪 Suíte de Avaliação (`evals/`)

O projeto inclui um framework de avaliação que testa o comportamento do agente em **25 cenários reais**:

```bash
# Executar a suíte de 25 testes (modo simulado, instantâneo e offline)
python evals/run_evals.py

# Executar em modo live (conectando à API OpenAI)
python evals/run_evals.py --live

# Filtrar por categoria
python evals/run_evals.py --category cliente_confuso
python evals/run_evals.py --category horario_ocupado
```

### Resultados do Benchmark:
| Categoria | Casos | Taxa de Acerto |
|---|:---:|:---:|
| 🤔 Cliente Confuso / Hesitante | 5 | 100.0% |
| 📅 Horário Ocupado / Restrições | 5 | 100.0% |
| 🔄 Remarcação e Cancelamento | 5 | 100.0% |
| 🚫 Pedidos Fora do Escopo | 5 | 100.0% |
| 🎙️ Áudio e Multimodal | 3 | 100.0% |
| ✨ Fluxo Padrão Ponta a Ponta | 1 | 100.0% |
| 🛒 Produtos e Localização | 1 | 100.0% |
| **Geral Consolidado** | **25** | **100.0%** |

---

## 📊 Visualizador de Arquitetura (`visualize.py`)

Para gerar e abrir o diagrama interativo do grafo:

```bash
python visualize.py
```

Gera o arquivo `graph_flow.html` com o diagrama de execução em SVG e explicação detalhada da tomada de decisão `should_use_tool`.

---

## 🌐 Integração com WhatsApp (Evolution API)

Para conectar o agente a um número real de WhatsApp:

1. Configure as credenciais em `data/agent_config.json`:
```json
{
  "evolution_info": {
    "server_url": "https://sua-evolution-api.com",
    "instance": "instancia-petfy",
    "api_key": "sua-chave-api"
  }
}
```
2. Inicie o servidor FastAPI:
```bash
python main.py
# ou
uvicorn main:app --host 0.0.0.0 --port 8000
```
3. Aponte o Webhook da Evolution API para `http://SEU_IP:8000/receive-message`.

---

## 🛠️ Tecnologias Utilizadas

- **LangGraph & LangChain**: Orquestração de grafos cíclicos com estado compartilhado.
- **OpenAI GPT-4o-mini**: Modelo de linguagem para raciocínio e chamada de ferramentas (Function Calling).
- **OpenAI Whisper & TTS**: Transcrição e síntese de voz multimodal.
- **FastAPI & Uvicorn**: API assíncrona para recebimento de webhooks.
- **Pydantic**: Validação de esquemas de dados.

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para mais informações.
