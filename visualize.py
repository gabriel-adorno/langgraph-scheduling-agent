"""
visualize.py — Gera a visualização limpa do fluxo do agente de agendamento.

Uso:
    python visualize.py

Gera e abre no navegador:
    • graph_flow.html
"""

import sys
import webbrowser
from pathlib import Path

CURRENT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(CURRENT_DIR))


def generate_flow_html() -> Path:
    """Gera o HTML com o Diagrama de Fluxo e o painel explicativo interativo."""
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Diagrama do Fluxo de Execução — LangGraph</title>
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: #111827;
      --card-border: #1f293d;
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --purple: #c084fc;
      --blue: #38bdf8;
      --green: #34d399;
      --yellow: #fbbf24;
      --pink: #f472b6;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text-main);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      padding: 32px 20px;
      line-height: 1.5;
    }

    .container {
      max-width: 1100px;
      margin: 0 auto;
    }

    /* ─── HEADER LIMPO ─── */
    .header {
      margin-bottom: 24px;
    }
    h1 {
      font-size: 1.8rem;
      font-weight: 800;
      color: #fff;
      margin-bottom: 6px;
      letter-spacing: -0.02em;
    }
    .subtitle {
      color: var(--text-muted);
      font-size: 0.95rem;
    }

    /* ─── DIAGRAMA DO FLUXO (SVG) ─── */
    .graph-wrapper {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 18px;
      padding: 32px 20px 24px;
      margin-bottom: 24px;
      box-shadow: 0 16px 40px rgba(0,0,0,0.5);
    }

    svg.flow-svg {
      width: 100%;
      height: auto;
      max-height: 440px;
      display: block;
      margin: 0 auto;
    }

    /* Nós Interativos */
    .node-group {
      cursor: pointer;
      transition: all 0.25s ease;
    }
    .node-group:hover rect,
    .node-group:hover polygon,
    .node-group:hover ellipse {
      filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.4));
      stroke-width: 3px !important;
    }
    .node-group.active rect,
    .node-group.active polygon,
    .node-group.active ellipse {
      stroke: #ffffff !important;
      stroke-width: 3.5px !important;
      filter: drop-shadow(0 0 16px rgba(255, 255, 255, 0.75)) !important;
    }

    /* ─── CONTROLES INTERATIVOS ─── */
    .controls-bar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 16px;
    }

    .step-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .pill {
      background: #1e293b;
      border: 1px solid #334155;
      color: #94a3b8;
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }
    .pill:hover {
      background: #334155;
      color: #fff;
    }
    .pill.active {
      background: rgba(192, 132, 252, 0.18);
      border-color: var(--purple);
      color: #fff;
    }

    .nav-buttons {
      display: flex;
      gap: 8px;
    }
    .btn {
      background: #1e293b;
      border: 1px solid #334155;
      color: #fff;
      padding: 7px 14px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn:hover {
      background: #334155;
    }
    .btn-primary {
      background: #6366f1;
      border-color: #4f46e5;
    }
    .btn-primary:hover {
      background: #4f46e5;
    }

    /* ─── PAINEL DA ETAPA (LOGO ABAIXO DO GRAFO) ─── */
    .step-box {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-left: 5px solid var(--yellow);
      border-radius: 14px;
      padding: 22px 24px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.3);
      transition: border-left-color 0.3s;
    }

    .step-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;
    }
    .step-tag {
      background: rgba(251, 191, 36, 0.15);
      color: var(--yellow);
      font-size: 0.78rem;
      font-weight: 800;
      padding: 4px 10px;
      border-radius: 6px;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }
    .step-title {
      font-size: 1.25rem;
      font-weight: 800;
      color: #fff;
      margin-bottom: 10px;
    }
    .step-desc {
      color: #cbd5e1;
      font-size: 0.95rem;
      line-height: 1.6;
      margin-bottom: 16px;
    }

    .step-details-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 12px;
      padding-top: 14px;
      border-top: 1px solid #1f293d;
    }
    .detail-card {
      background: #0b0f19;
      border: 1px solid #1f293d;
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 0.85rem;
    }
    .detail-title {
      color: var(--text-muted);
      font-weight: 700;
      margin-bottom: 4px;
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .detail-content {
      color: #e2e8f0;
      line-height: 1.4;
    }
  </style>
</head>
<body>

<div class="container">

  <!-- 1. DIAGRAMA DO FLUXO DE EXECUÇÃO (APARECE PRIMEIRO NO TOPO) -->
  <div class="header">
    <h1>Diagrama do Fluxo de Execução</h1>
    <p class="subtitle">Estrutura cíclica do LangGraph com tomada de decisão, execução de ferramentas e máquina de estados</p>
  </div>

  <div class="graph-wrapper">
    <svg class="flow-svg" viewBox="0 0 1000 460" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path d="M 0 0 L 8 4 L 0 8 Z" fill="#94a3b8" />
        </marker>
        <marker id="arrow-green" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path d="M 0 0 L 8 4 L 0 8 Z" fill="#34d399" />
        </marker>
        <marker id="arrow-pink" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path d="M 0 0 L 8 4 L 0 8 Z" fill="#f472b6" />
        </marker>
        <marker id="arrow-purple" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path d="M 0 0 L 8 4 L 0 8 Z" fill="#c084fc" />
        </marker>
      </defs>

      <!-- CONEXÕES / ARESTAS -->
      <!-- START -> AGENT -->
      <line x1="140" y1="80" x2="220" y2="80" stroke="#94a3b8" stroke-width="2.5" marker-end="url(#arrow)"/>
      <text x="180" y="70" fill="#94a3b8" font-size="11" text-anchor="middle" font-weight="600">inicia</text>

      <!-- AGENT -> DECISION -->
      <line x1="390" y1="80" x2="470" y2="80" stroke="#c084fc" stroke-width="2.5" marker-end="url(#arrow-purple)"/>
      <text x="430" y="70" fill="#c084fc" font-size="11" text-anchor="middle" font-weight="600">avalia</text>

      <!-- DECISION -> TOOL (SIM) -->
      <path d="M 545 125 L 545 220" stroke="#34d399" stroke-width="3" marker-end="url(#arrow-green)" fill="none"/>
      <rect x="555" y="155" width="165" height="36" rx="6" fill="#064e3b" stroke="#34d399" stroke-width="1"/>
      <text x="637" y="172" fill="#34d399" font-size="11" text-anchor="middle" font-weight="bold">SIM: Precisa de Ação</text>
      <text x="637" y="184" fill="#a7f3d0" font-size="9" text-anchor="middle">(ex: checar vaga, cadastrar)</text>

      <!-- DECISION -> END (NÃO) -->
      <line x1="620" y1="80" x2="800" y2="80" stroke="#f472b6" stroke-width="3" marker-end="url(#arrow-pink)"/>
      <rect x="640" y="50" width="135" height="32" rx="6" fill="#3f1737" stroke="#f472b6" stroke-width="1"/>
      <text x="707" y="65" fill="#f472b6" font-size="11" text-anchor="middle" font-weight="bold">NÃO: Resposta Pronta</text>
      <text x="707" y="76" fill="#fbcfe8" font-size="9" text-anchor="middle">(conversa ou pós-tool)</text>

      <!-- TOOL -> TOOL_EXECUTER -->
      <line x1="460" y1="260" x2="380" y2="260" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arrow)"/>

      <!-- TOOL_EXECUTER -> UPDATE_STEP -->
      <line x1="210" y1="260" x2="140" y2="260" stroke="#34d399" stroke-width="2.5" marker-end="url(#arrow)"/>

      <!-- UPDATE_STEP -> LOOP BACK TO AGENT -->
      <path d="M 85 295 L 85 390 L 305 390 L 305 130" stroke="#f59e0b" stroke-width="3" stroke-dasharray="6,4" marker-end="url(#arrow)" fill="none"/>
      <rect x="130" y="372" width="230" height="26" rx="6" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
      <text x="245" y="389" fill="#fef3c7" font-size="11" text-anchor="middle" font-weight="bold">🔁 LOOP: Volta ao LLM com resultado da Tool</text>

      <!-- NÓS -->
      <!-- 1. START -->
      <g class="node-group" id="node-0" onclick="selectStep(0)">
        <ellipse cx="75" cy="80" rx="55" ry="32" fill="#1e1b4b" stroke="#818cf8" stroke-width="2"/>
        <text x="75" y="75" fill="#fff" font-size="12" font-weight="800" text-anchor="middle">🚀 START</text>
        <text x="75" y="92" fill="#c7d2fe" font-size="10" text-anchor="middle">Msg do Cliente</text>
      </g>

      <!-- 2. AGENT (LLM) -->
      <g class="node-group" id="node-1" onclick="selectStep(1)">
        <rect x="220" y="35" width="170" height="90" rx="14" fill="#2e1065" stroke="#c084fc" stroke-width="2.5"/>
        <text x="305" y="60" fill="#c084fc" font-size="11" font-weight="800" text-anchor="middle">CÉREBRO DO SISTEMA</text>
        <text x="305" y="80" fill="#fff" font-size="15" font-weight="900" text-anchor="middle">🧠 agent (LLM)</text>
        <text x="305" y="100" fill="#e9d5ff" font-size="10" text-anchor="middle">GPT-4o-mini + Prompts</text>
        <text x="305" y="114" fill="#a855f7" font-size="9" text-anchor="middle">Decide se chama Tool ou responde</text>
      </g>

      <!-- 3. DECISION (should_use_tool) -->
      <g class="node-group" id="node-2" onclick="selectStep(2)">
        <polygon points="545,35 620,80 545,125 470,80" fill="#1f2937" stroke="#fbbf24" stroke-width="3"/>
        <text x="545" y="73" fill="#fbbf24" font-size="11" font-weight="900" text-anchor="middle">DECISÃO</text>
        <text x="545" y="87" fill="#fff" font-size="10" font-weight="700" text-anchor="middle">Chamar Tool?</text>
      </g>

      <!-- 4. TOOL NODE -->
      <g class="node-group" id="node-3" onclick="selectStep(3)">
        <rect x="460" y="220" width="170" height="80" rx="14" fill="#082f49" stroke="#38bdf8" stroke-width="2"/>
        <text x="545" y="246" fill="#38bdf8" font-size="10" font-weight="800" text-anchor="middle">EXECUÇÃO TÉCNICA</text>
        <text x="545" y="268" fill="#fff" font-size="15" font-weight="900" text-anchor="middle">⚙️ tool (ToolNode)</text>
        <text x="545" y="286" fill="#bae6fd" font-size="10" text-anchor="middle">15 ferramentas em Python</text>
      </g>

      <!-- 5. TOOL EXECUTER -->
      <g class="node-group" id="node-4" onclick="selectStep(4)">
        <rect x="210" y="220" width="170" height="80" rx="14" fill="#064e3b" stroke="#34d399" stroke-width="2"/>
        <text x="295" y="246" fill="#34d399" font-size="10" font-weight="800" text-anchor="middle">PERSISTÊNCIA DE DADOS</text>
        <text x="295" y="268" fill="#fff" font-size="14" font-weight="900" text-anchor="middle">📦 tool_executer</text>
        <text x="295" y="286" fill="#a7f3d0" font-size="10" text-anchor="middle">Salva dados no Estado (JSON)</text>
      </g>

      <!-- 6. UPDATE STEP -->
      <g class="node-group" id="node-5" onclick="selectStep(5)">
        <rect x="30" y="220" width="110" height="80" rx="14" fill="#78350f" stroke="#f59e0b" stroke-width="2"/>
        <text x="85" y="246" fill="#f59e0b" font-size="9" font-weight="800" text-anchor="middle">MÁQUINA</text>
        <text x="85" y="266" fill="#fff" font-size="13" font-weight="900" text-anchor="middle">🔄 update_step</text>
        <text x="85" y="284" fill="#fde68a" font-size="9" text-anchor="middle">Avança Etapa</text>
      </g>

      <!-- 7. END -->
      <g class="node-group" id="node-6" onclick="selectStep(6)">
        <ellipse cx="860" cy="80" rx="60" ry="32" fill="#3f1737" stroke="#f472b6" stroke-width="2.5"/>
        <text x="860" y="75" fill="#fff" font-size="13" font-weight="900" text-anchor="middle">🏁 END</text>
        <text x="860" y="92" fill="#fbcfe8" font-size="10" text-anchor="middle">Envia Texto/Áudio</text>
      </g>
    </svg>
  </div>

  <!-- 2. CONTROLES E PAINEL EXPLICATIVO (LOGO ABAIXO DO GRAFO) -->
  <div class="controls-bar">
    <div class="step-pills">
      <button class="pill" id="pill-0" onclick="selectStep(0)">1. START</button>
      <button class="pill" id="pill-1" onclick="selectStep(1)">2. AGENT (LLM)</button>
      <button class="pill active" id="pill-2" onclick="selectStep(2)">3. BIFURCAÇÃO</button>
      <button class="pill" id="pill-3" onclick="selectStep(3)">4. TOOL</button>
      <button class="pill" id="pill-4" onclick="selectStep(4)">5. ESTADO</button>
      <button class="pill" id="pill-5" onclick="selectStep(5)">6. UPDATE STEP</button>
      <button class="pill" id="pill-6" onclick="selectStep(6)">7. END</button>
    </div>
    <div class="nav-buttons">
      <button class="btn" onclick="prevStep()">⬅️ Anterior</button>
      <button class="btn btn-primary" onclick="nextStep()">Próximo ➡️</button>
    </div>
  </div>

  <div class="step-box" id="stepBox">
    <div class="step-header">
      <span class="step-tag" id="stepTag">ETAPA 3 DE 6 · BIFURCAÇÃO</span>
    </div>
    <div class="step-title" id="stepTitle">3. A Decisão Condicional (should_use_tool)</div>
    <div class="step-desc" id="stepDesc">
      Avalia o output gerado pelo LLM. Se o modelo identificou a necessidade de consultar o sistema ou cadastrar algo, o grafo desvia para o nó de ferramentas. Se já gerou a resposta pronta para o usuário, o grafo encerra a execução e despacha a mensagem.
    </div>

    <div class="step-details-grid">
      <div class="detail-card">
        <div class="detail-title" id="d1Title">Se SIM (tool_edge)</div>
        <div class="detail-content" id="d1Content">O LLM gerou chamada de ferramenta (ex: consultar vagas, registrar pet). Segue para o nó <b>tool</b>.</div>
      </div>
      <div class="detail-card">
        <div class="detail-title" id="d2Title">Se NÃO (end_edge)</div>
        <div class="detail-content" id="d2Content">Resposta conversacional concluída. Vai direto para o <b>END</b> e envia ao cliente.</div>
      </div>
    </div>
  </div>

</div>

<script>
  const steps = [
    {
      nodeId: "node-0",
      tag: "ETAPA 1 DE 6 · ENTRADA",
      color: "#818cf8",
      title: "1. Chegada da Mensagem (START)",
      desc: "O fluxo se inicia quando o cliente envia uma mensagem de texto ou áudio pelo WhatsApp. Se for áudio, o sistema transcreve automaticamente via Whisper antes de injetar a mensagem no estado do grafo.",
      d1Title: "Entrada",
      d1Content: "Mensagem do usuário (ID, texto, modo 'text' ou 'audio').",
      d2Title: "Destino",
      d2Content: "Direciona diretamente para o nó principal <b>agent</b>."
    },
    {
      nodeId: "node-1",
      tag: "ETAPA 2 DE 6 · CÉREBRO LLM",
      color: "#c084fc",
      title: "2. Processamento do Modelo (agent)",
      desc: "O modelo GPT-4o-mini é executado com as mensagens anteriores e o System Prompt específico da etapa atual (ex: orientações para registro de pet, escolha de serviço ou confirmação). O LLM avalia a intenção e decide se precisa chamar alguma ferramenta.",
      d1Title: "Ação do LLM",
      d1Content: "Gera Tool Calls estruturadas ou produz a resposta em JSON (content, mode).",
      d2Title: "Próximo Ponto",
      d2Content: "Passa para a função condicional <b>should_use_tool</b>."
    },
    {
      nodeId: "node-2",
      tag: "ETAPA 3 DE 6 · BIFURCAÇÃO",
      color: "#fbbf24",
      title: "3. A Decisão Condicional (should_use_tool)",
      desc: "Avalia o output gerado pelo LLM. Se o modelo identificou a necessidade de consultar o sistema ou cadastrar algo, o grafo desvia para o nó de ferramentas. Se já gerou a resposta pronta para o usuário, o grafo encerra a execução e despacha a mensagem.",
      d1Title: "Se SIM (tool_edge)",
      d1Content: "O LLM gerou chamada de ferramenta (ex: consultar vagas, registrar pet). Segue para o nó <b>tool</b>.",
      d2Title: "Se NÃO (end_edge)",
      d2Content: "Resposta conversacional concluída. Vai direto para o <b>END</b> e envia ao cliente."
    },
    {
      nodeId: "node-3",
      tag: "ETAPA 4 DE 6 · EXECUÇÃO TÉCNICA",
      color: "#38bdf8",
      title: "4. Execução de Ferramenta (tool)",
      desc: "O ToolNode nativo do LangGraph executa a função Python correspondente com os argumentos extraídos pelo modelo (ex: check_availability_tool com data e horário). Acessa a camada de dados local JSON com total agilidade.",
      d1Title: "Execução",
      d1Content: "Roda a ferramenta solicitada e obtém o resultado técnico.",
      d2Title: "Saída",
      d2Content: "Gera uma ToolMessage anexada ao histórico de mensagens."
    },
    {
      nodeId: "node-4",
      tag: "ETAPA 5 DE 6 · PERSISTÊNCIA",
      color: "#34d399",
      title: "5. Atualização do Estado (tool_executer)",
      desc: "O nó tool_executer analisa a resposta da ferramenta e salva os dados nas variáveis estruturadas do estado em memória (como client_info, pet_info e schedule_info), garantindo que as escolhas fiquem salvas.",
      d1Title: "Persistência",
      d1Content: "Atualiza os campos estruturados no estado global.",
      d2Title: "Continuidade",
      d2Content: "Encaminha para a máquina de estados (<b>update_step</b>)."
    },
    {
      nodeId: "node-5",
      tag: "ETAPA 5.1 · MÁQUINA DE ESTADOS",
      color: "#f59e0b",
      title: "6. Avanço da Etapa (update_step & Loop)",
      desc: "A máquina de estados verifica se a etapa atual foi completada (ex: se o pet foi selecionado, avança para CHOOSE_DATE). Em seguida, faz o LOOP de volta para o nó 'agent' com o resultado da ferramenta para o LLM formular a resposta final.",
      d1Title: "Transição de Etapa",
      d1Content: "REGISTER_CLIENT ➔ CHOOSE_SERVICE ➔ CHOOSE_PET ➔ CHOOSE_DATE ➔ CONFIRM.",
      d2Title: "Loop",
      d2Content: "Retorna ao <b>agent</b>, que agora tem a resposta da tool para responder ao cliente."
    },
    {
      nodeId: "node-6",
      tag: "ETAPA 6 DE 6 · RESPOSTA & FIM",
      color: "#f472b6",
      title: "7. Finalização e Envio (END)",
      desc: "O ciclo da mensagem é finalizado. A mensagem é enviada ao WhatsApp ou exibida no chat do terminal. Se a resposta for em áudio, o áudio é sintetizado e reproduzido nos alto-falantes.",
      d1Title: "Entrega de Mensagem",
      d1Content: "Texto exibido em tela; se mode == 'audio', toca voz no Mac.",
      d2Title: "Estado",
      d2Content: "Estado salvo localmente, aguardando a próxima mensagem do usuário."
    }
  ];

  // Inicia mostrando por padrão a ETAPA 3 DE 6 · BIFURCAÇÃO (índice 2)
  let currentStepIdx = 2;

  function updateUI() {
    const s = steps[currentStepIdx];

    // Atualiza Painel
    const stepBox = document.getElementById("stepBox");
    stepBox.style.borderLeftColor = s.color;

    const stepTag = document.getElementById("stepTag");
    stepTag.innerText = s.tag;
    stepTag.style.color = s.color;
    stepTag.style.background = s.color + "22";

    document.getElementById("stepTitle").innerText = s.title;
    document.getElementById("stepDesc").innerText = s.desc;
    document.getElementById("d1Title").innerText = s.d1Title;
    document.getElementById("d1Content").innerHTML = s.d1Content;
    document.getElementById("d2Title").innerText = s.d2Title;
    document.getElementById("d2Content").innerHTML = s.d2Content;

    // Atualiza pílulas
    document.querySelectorAll(".pill").forEach((p, idx) => {
      p.classList.toggle("active", idx === currentStepIdx);
    });

    // Atualiza nós SVG
    document.querySelectorAll(".node-group").forEach((el, idx) => {
      el.classList.toggle("active", idx === currentStepIdx);
    });
  }

  function nextStep() {
    currentStepIdx = (currentStepIdx + 1) % steps.length;
    updateUI();
  }

  function prevStep() {
    currentStepIdx = (currentStepIdx - 1 + steps.length) % steps.length;
    updateUI();
  }

  function selectStep(idx) {
    currentStepIdx = idx % steps.length;
    updateUI();
  }

  // Inicializa na ETAPA 3 DE 6 · BIFURCAÇÃO
  updateUI();
</script>

</body>
</html>"""

    output = CURRENT_DIR / "graph_flow.html"
    output.write_text(html, encoding="utf-8")
    return output


def main():
    flow_path = generate_flow_html()
    print("=" * 60)
    print("🐾 Diagrama do Fluxo de Execução Gerado")
    print("=" * 60)
    print(f"📄 Arquivo: {flow_path.name}")
    print("🌐 Abrindo no navegador padrão...")
    webbrowser.open(f"file://{flow_path}")


if __name__ == "__main__":
    main()
