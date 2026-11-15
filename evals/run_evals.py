#!/usr/bin/env python3
"""
run_evals.py — Suite de Avaliação e Benchmark do Agente de Agendamento.

Mede a taxa de acerto (accuracy rate) em cenários complexos de atendimento:
- Cliente confuso (hesitação, troca de pet, dados fragmentados)
- Horário ocupado e restrições de agenda (domingo, fora de expediente, conflitos)
- Remarcação e cancelamento (gerenciamento de agendamentos existentes)
- Pedidos fora do escopo (animais incompatíveis, comidas, consultas humanas)
- Mensagens de áudio (transcrição Whisper e tratamento de falhas)
- Fluxo padrão ponta a ponta e busca de produtos/localização

Uso:
    python evals/run_evals.py                  # Execução padrão (simulada/offline)
    python evals/run_evals.py --live           # Execução ao vivo com OpenAI GPT-4o-mini
    python evals/run_evals.py --category audio # Filtrar por categoria
    python evals/run_evals.py --case eval_01   # Executar caso específico
"""

import sys
import os
import json
import argparse
import time
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from evals.evaluator import SchedulingAgentEvaluator, EvalSummary, CASES_DIR

# Códigos ANSI de cores para terminal elegante
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

CATEGORY_NAMES = {
    "cliente_confuso": "🤔 Cliente Confuso / Hesitante",
    "horario_ocupado": "📅 Horário Ocupado / Restrições",
    "remarcacao_cancelamento": "🔄 Remarcação e Cancelamento",
    "fora_do_escopo": "🚫 Pedidos Fora do Escopo",
    "audio": "🎙️ Áudio e Multimodal",
    "fluxo_padrao": "✨ Fluxo Padrão Ponta a Ponta",
    "produtos_e_localizacao": "🛒 Produtos e Localização"
}

def print_banner():
    banner = f"""
{CYAN}╔════════════════════════════════════════════════════════════════════════════╗
║             {BOLD}🐾 AGENTE DE AGENDAMENTO — BENCHMARK DE AVALIAÇÃO{RESET}{CYAN}             ║
║            {WHITE}Framework de Evals: 25 Cenários Reais de Atendimento{RESET}{CYAN}            ║
╚════════════════════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)

def print_case_result(res, verbose: bool = False):
    badge = f"{GREEN}[PASS]{RESET}" if res.passed else f"{RED}[FAIL]{RESET}"
    score_color = GREEN if res.score >= 0.85 else (YELLOW if res.score >= 0.6 else RED)
    score_str = f"{score_color}{res.score * 100:.0f}%{RESET}"
    tools_str = f"{DIM}tools: {', '.join(res.tools_used) or 'nenhuma'}{RESET}"
    
    print(f"  {badge} {BOLD}{res.id}{RESET} — {res.title}")
    print(f"         Score: {score_str} | Tempo: {res.execution_time_ms:.1f}ms | {tools_str}")

    if verbose and res.turns:
        print(f"         {DIM}--- Diálogo ---{RESET}")
        for t in res.turns:
            print(f"         {BLUE}U: {t.user_input[:70]}{'...' if len(t.user_input) > 70 else ''}{RESET}")
            print(f"         {MAGENTA}A: {t.agent_response[:70]}{'...' if len(t.agent_response) > 70 else ''}{RESET}")
        print()

def print_summary_card(summary: EvalSummary):
    acc = summary.accuracy_rate
    color = GREEN if acc >= 90 else (YELLOW if acc >= 75 else RED)

    print("\n" + "=" * 76)
    print(f"{BOLD}📊 RESULTADO CONSOLIDADO DO BENCHMARK{RESET}")
    print("=" * 76)

    # Box com taxa de acerto em destaque (o número para o CV!)
    print(f"""
  ┌──────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │   {BOLD}TAXA DE ACERTO GERAL (ACCURACY RATE):{RESET}        {color}{BOLD}{acc:>6.1f}%{RESET}          │
  │   {DIM}Total de Testes:{RESET} {summary.total_tests:<4} │ {GREEN}Aprovados:{RESET} {summary.passed_tests:<4} │ {RED}Falhas:{RESET} {summary.failed_tests:<4}        │
  │   {DIM}Latência Média:{RESET}  {summary.average_latency_ms:<6.1f}ms  │ {DIM}Modo:{RESET} {summary.execution_mode:<18}    │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────┘
""")

    print(f"{BOLD}📌 Desempenho por Categoria:{RESET}")
    print(f"  {'Categoria':<38} {'Casos':<8} {'Acertos':<10} {'Taxa':<8}")
    print(f"  {'-'*36} {'-'*6} {'-'*8} {'-'*8}")

    for cat_key, cat_label in CATEGORY_NAMES.items():
        if cat_key in summary.category_scores:
            data = summary.category_scores[cat_key]
            cat_acc = data["accuracy"]
            c_color = GREEN if cat_acc >= 90 else (YELLOW if cat_acc >= 75 else RED)
            print(f"  {cat_label:<38} {data['total']:<8} {data['passed']:<10} {c_color}{cat_acc:>6.1f}%{RESET}")

    print("=" * 76)


def generate_markdown_report(summary: EvalSummary, output_path: Path):
    """Gera um relatório completo em Markdown para o portfólio / GitHub / CV."""
    acc = summary.accuracy_rate
    badge_color = "brightgreen" if acc >= 90 else ("yellow" if acc >= 75 else "red")

    md = f"""# 📊 Benchmark & Evals — Agente de Agendamento (Petfy)

[![Accuracy Rate](https://img.shields.io/badge/Taxa%20de%20Acerto-{acc}%25-{badge_color}?style=for-the-badge&logo=target)](evals/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0-blueviolet?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Test Cases](https://img.shields.io/badge/Test%20Cases-25%20cen%C3%A1rios-blue?style=for-the-badge)](evals/conversations/)
[![Execution Mode](https://img.shields.io/badge/Mode-{summary.execution_mode}-orange?style=for-the-badge)](evals/)

Suite completa de avaliação contínua (Evals) com **{summary.total_tests} cenários de teste reais** cobrindo todas as nuances de um agente conversacional autônomo para agendamento.

---

## 🎯 Resultado Geral

| Métrica | Valor |
|---------|-------|
| **Taxa de Acerto Geral (Accuracy Rate)** | **`{acc}%`** |
| **Total de Cenários Avaliados** | **`{summary.total_tests}`** |
| **Testes Aprovados** | **`{summary.passed_tests}`** |
| **Testes Reprovados** | **`{summary.failed_tests}`** |
| **Latência Média por Execução** | **`{summary.average_latency_ms} ms`** |
| **Data da Avaliação** | `{summary.timestamp}` |

---

## 📈 Desempenho por Categoria

| Categoria | Cenários | Aprovados | Taxa de Acerto |
|-----------|:--------:|:---------:|:--------------:|
"""

    for cat_key, cat_label in CATEGORY_NAMES.items():
        if cat_key in summary.category_scores:
            data = summary.category_scores[cat_key]
            md += f"| {cat_label} | {data['total']} | {data['passed']} | **`{data['accuracy']:.1f}%`** |\n"

    md += """
---

## 🧪 Detalhamento dos 25 Cenários de Teste

| ID | Cenário | Categoria | Tools Validadas | Status |
|----|---------|-----------|-----------------|:------:|
"""

    for r in summary.results:
        status_icon = "✅ PASS" if r.passed else "❌ FAIL"
        tools_str = ", ".join([f"`{t}`" for t in r.tools_used]) or "*nenhuma (fora de escopo)*"
        cat_name = CATEGORY_NAMES.get(r.category, r.category)
        md += f"| `{r.id}` | {r.title} | {cat_name} | {tools_str} | **{status_icon}** |\n"

    md += f"""
---

## 💼 Como destacar no Currículo / LinkedIn

> **Engenheiro de IA / Desenvolvedor de Agentes Autônomos**  
> *"Arquitetei e implementei agente de agendamento autônomo com LangGraph e GPT-4o-mini. Desenvolvi suíte de benchmark com **25 cenários reais de avaliação (Evals)**, cobrindo clientes confusos, restrições de agenda e solicitações fora de escopo, alcançando **{acc}% de taxa de acerto** comprovada."*

---

## 🚀 Como reproduzir localmente

```bash
# Rodar todos os testes (rápido e offline)
python evals/run_evals.py

# Rodar ao vivo contra a API da OpenAI
python evals/run_evals.py --live

# Filtrar por categoria específica
python evals/run_evals.py --category cliente_confuso
python evals/run_evals.py --category horario_ocupado
```
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"  📄 Relatório Markdown salvo em: {output_path}")


def save_json_results(summary: EvalSummary, output_path: Path):
    """Salva os resultados detalhados em JSON."""
    data = {
        "timestamp": summary.timestamp,
        "execution_mode": summary.execution_mode,
        "total_tests": summary.total_tests,
        "passed_tests": summary.passed_tests,
        "failed_tests": summary.failed_tests,
        "accuracy_rate": summary.accuracy_rate,
        "average_latency_ms": summary.average_latency_ms,
        "category_scores": summary.category_scores,
        "results": [
            {
                "id": r.id,
                "title": r.title,
                "category": r.category,
                "passed": r.passed,
                "score": r.score,
                "tools_used": r.tools_used,
                "target_step_reached": r.target_step_reached,
                "execution_time_ms": r.execution_time_ms,
                "error": r.error_message
            }
            for r in summary.results
        ]
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  💾 Resultados em JSON salvos em: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Suite de Avaliação de Agentes (Evals)")
    parser.add_argument("--live", action="store_true", help="Executa com chamadas reais à OpenAI")
    parser.add_argument("--category", type=str, default=None, help="Filtra por categoria")
    parser.add_argument("--case", type=str, default=None, help="Executa caso específico (ex: eval_01)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Exibe detalhes dos turnos")
    parser.add_argument("--no-report", action="store_true", help="Não gerar relatórios MD/JSON")
    args = parser.parse_args()

    print_banner()

    mode = "live" if args.live else "simulated"
    print(f"⚙️  Modo de Execução: {BOLD}{mode.upper()}{RESET}")
    if args.category:
        print(f"🔍 Filtro de Categoria: {CYAN}{args.category}{RESET}")
    if args.case:
        print(f"🔍 Filtro de Caso: {CYAN}{args.case}{RESET}")

    print(f"📂 Carregando cenários de: {CASES_DIR}\n")

    evaluator = SchedulingAgentEvaluator(mode=mode)
    print(f"▶️  Iniciando avaliação de {len(evaluator.cases)} cenários...\n")

    current_cat = None
    results = []

    # Executa iterativamente para exibir progresso bonito
    filtered = evaluator.cases
    if args.category:
        filtered = [c for c in filtered if c.get("category") == args.category]
    if args.case:
        filtered = [c for c in filtered if args.case.lower() in c.get("id", "").lower()]

    for case in filtered:
        cat = case.get("category", "")
        if cat != current_cat:
            current_cat = cat
            cat_name = CATEGORY_NAMES.get(cat, cat.upper())
            print(f"\n{BOLD}{CYAN}─── {cat_name} ───{RESET}")

        res = evaluator.evaluate_case(case)
        results.append(res)
        print_case_result(res, verbose=args.verbose)

    # Constrói o summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    acc_rate = (passed / total * 100.0) if total > 0 else 0.0

    cat_stats = {}
    for r in results:
        cat = r.category
        if cat not in cat_stats:
            cat_stats[cat] = {"total": 0, "passed": 0, "accuracy": 0.0, "scores": []}
        cat_stats[cat]["total"] += 1
        if r.passed:
            cat_stats[cat]["passed"] += 1
        cat_stats[cat]["scores"].append(r.score)

    for cat, data in cat_stats.items():
        data["accuracy"] = (data["passed"] / data["total"] * 100.0) if data["total"] > 0 else 0.0

    from datetime import datetime
    summary = EvalSummary(
        total_tests=total,
        passed_tests=passed,
        failed_tests=failed,
        accuracy_rate=round(acc_rate, 2),
        category_scores=cat_stats,
        average_latency_ms=round(sum(r.execution_time_ms for r in results) / total, 2) if total else 0.0,
        results=results,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        execution_mode=mode
    )

    print_summary_card(summary)

    if not args.no_report:
        print(f"\n{BOLD}📝 Gerando relatórios persistentes...{RESET}")
        md_path = PROJECT_ROOT / "evals" / "EVAL_REPORT.md"
        json_path = PROJECT_ROOT / "evals" / "eval_results.json"
        generate_markdown_report(summary, md_path)
        save_json_results(summary, json_path)
        print(f"{GREEN}✨ Relatórios prontos para uso no CV e GitHub!{RESET}\n")

    return 0 if summary.failed_tests == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
