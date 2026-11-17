# 📊 Benchmark & Evals — Agente de Agendamento (Petfy)

[![Accuracy Rate](https://img.shields.io/badge/Taxa%20de%20Acerto-44.0%25-red?style=for-the-badge&logo=target)](evals/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0-blueviolet?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Test Cases](https://img.shields.io/badge/Test%20Cases-25%20cen%C3%A1rios-blue?style=for-the-badge)](evals/conversations/)
[![Execution Mode](https://img.shields.io/badge/Mode-live-orange?style=for-the-badge)](evals/)

Execução **`--live`** em `2026-11-16 23:26:27` com modelo **`gpt-4o-mini`**. Os 25 JSONs em `evals/conversations/` foram escritos à mão. O harness live marca PASS/FAIL pelas tools observadas no estado (não pelo texto dos `criteria`). Nenhum caso desta corrida usou o fallback simulado.

---

## 🎯 Resultado Geral

| Métrica | Valor |
|---------|-------|
| **Taxa de Acerto Geral (Accuracy Rate)** | **`44.0%`** |
| **Total de Cenários Avaliados** | **`25`** |
| **Testes Aprovados** | **`11`** |
| **Testes Reprovados** | **`14`** |
| **Latência Média por Execução** | **`12100.25 ms`** |
| **Data da Avaliação** | `2026-11-16 23:26:27` |

---

## 📈 Desempenho por Categoria

| Categoria | Cenários | Aprovados | Taxa de Acerto |
|-----------|:--------:|:---------:|:--------------:|
| 🤔 Cliente Confuso / Hesitante | 5 | 2 | **`40.0%`** |
| 📅 Horário Ocupado / Restrições | 5 | 2 | **`40.0%`** |
| 🔄 Remarcação e Cancelamento | 5 | 3 | **`60.0%`** |
| 🚫 Pedidos Fora do Escopo | 5 | 3 | **`60.0%`** |
| 🎙️ Áudio e Multimodal | 3 | 0 | **`0.0%`** |
| ✨ Fluxo Padrão Ponta a Ponta | 1 | 0 | **`0.0%`** |
| 🛒 Produtos e Localização | 1 | 1 | **`100.0%`** |

---

## 🧪 Detalhamento dos 25 Cenários de Teste

| ID | Cenário | Categoria | Tools Validadas | Status |
|----|---------|-----------|-----------------|:------:|
| `eval_01_confuso_hesita_servico` | Cliente hesita entre serviços e pede recomendação | 🤔 Cliente Confuso / Hesitante | `get_services_list_tool` | **❌ FAIL** |
| `eval_02_confuso_troca_de_pet` | Cliente muda de ideia sobre qual pet levar | 🤔 Cliente Confuso / Hesitante | `register_client_tool`, `get_services_list_tool`, `list_pets_tool`, `register_pet_tool`, `choose_pet_tool`, `choose_service_tool`, `get_schedule_summary_tool` | **✅ PASS** |
| `eval_03_confuso_informacoes_fragmentadas` | Cliente envia dados fragmentados em várias mensagens | 🤔 Cliente Confuso / Hesitante | `register_client_tool`, `get_services_list_tool`, `choose_service_tool`, `list_pets_tool`, `register_pet_tool`, `choose_pet_tool` | **✅ PASS** |
| `eval_04_confuso_mudanca_de_horario` | Cliente escolhe horário e muda de ideia imediatamente | 🤔 Cliente Confuso / Hesitante | *nenhuma (fora de escopo)* | **❌ FAIL** |
| `eval_05_confuso_pergunta_preco_no_meio` | Cliente pergunta preço de outro serviço no meio do cadastro do pet | 🤔 Cliente Confuso / Hesitante | *nenhuma (fora de escopo)* | **❌ FAIL** |
| `eval_06_horario_domingo_fechado` | Tentativa de agendamento em domingo (clínica fechada) | 📅 Horário Ocupado / Restrições | *nenhuma (fora de escopo)* | **❌ FAIL** |
| `eval_07_horario_fora_do_expediente` | Horário solicitado fora do expediente (noite/madrugada) | 📅 Horário Ocupado / Restrições | `get_services_list_tool`, `check_availability_tool`, `choose_service_tool`, `choose_date_tool`, `list_pets_tool`, `register_client_tool`, `register_pet_tool`, `choose_pet_tool`, `get_schedule_summary_tool` | **✅ PASS** |
| `eval_08_horario_conflito_mesmo_dia` | Horário já ocupado por outro agendamento e sugestão automática | 📅 Horário Ocupado / Restrições | *nenhuma (fora de escopo)* | **❌ FAIL** |
| `eval_09_horario_duracao_ultrapassa_expediente` | Duração do serviço ultrapassa o horário de fechamento | 📅 Horário Ocupado / Restrições | `get_services_list_tool`, `check_availability_tool`, `choose_service_tool`, `choose_date_tool`, `get_schedule_summary_tool`, `list_pets_tool`, `register_client_tool` | **✅ PASS** |
| `eval_10_horario_dia_bloqueado` | Dia bloqueado por feriado ou manutenção da clínica | 📅 Horário Ocupado / Restrições | *nenhuma (fora de escopo)* | **❌ FAIL** |
| `eval_11_remarcacao_horario_existente` | Remarcação de horário de agendamento já existente | 🔄 Remarcação e Cancelamento | `get_services_list_tool`, `get_past_schedules_list_tool`, `edit_schedule_tool`, `get_schedule_summary_tool` | **✅ PASS** |
| `eval_12_cancelamento_agendamento` | Cancelamento de agendamento existente com confirmação | 🔄 Remarcação e Cancelamento | `get_services_list_tool`, `get_past_schedules_list_tool`, `edit_schedule_tool`, `get_schedule_summary_tool`, `cancel_schedule_tool` | **❌ FAIL** |
| `eval_13_consulta_historico_agendamentos` | Consulta de agendamentos agendados pelo cliente | 🔄 Remarcação e Cancelamento | `get_services_list_tool`, `get_past_schedules_list_tool`, `edit_schedule_tool`, `get_schedule_summary_tool`, `cancel_schedule_tool` | **❌ FAIL** |
| `eval_14_remarcacao_troca_de_servico` | Remarcação alterando o serviço agendado | 🔄 Remarcação e Cancelamento | `get_past_schedules_list_tool`, `edit_schedule_tool`, `get_schedule_summary_tool`, `cancel_schedule_tool`, `get_services_list_tool`, `choose_service_tool` | **✅ PASS** |
| `eval_15_cancelamento_sem_agendamentos` | Tentativa de cancelamento por cliente sem agendamentos | 🔄 Remarcação e Cancelamento | `get_past_schedules_list_tool`, `register_client_tool` | **✅ PASS** |
| `eval_16_fora_escopo_animal_incompativel` | Solicitação de tosa para animal silvestre/incompatível | 🚫 Pedidos Fora do Escopo | *nenhuma (fora de escopo)* | **❌ FAIL** |
| `eval_17_fora_escopo_pedido_pizza` | Mensagem fora de contexto (pedido de comida/pizza) | 🚫 Pedidos Fora do Escopo | *nenhuma (fora de escopo)* | **✅ PASS** |
| `eval_18_fora_escopo_venda_animais` | Pergunta sobre compra/venda de filhotes de animais | 🚫 Pedidos Fora do Escopo | *nenhuma (fora de escopo)* | **✅ PASS** |
| `eval_19_fora_escopo_consulta_humana` | Relato de sintoma de saúde humana e pedido de receita | 🚫 Pedidos Fora do Escopo | *nenhuma (fora de escopo)* | **✅ PASS** |
| `eval_20_fora_escopo_fiado_gratuito` | Tentativa de agendamento gratuito ou fiado sem pagamento | 🚫 Pedidos Fora do Escopo | *nenhuma (fora de escopo)* | **❌ FAIL** |
| `eval_21_audio_mensagem_usuario` | Mensagem enviada em formato de áudio (transcrição Whisper) | 🎙️ Áudio e Multimodal | `get_services_list_tool` | **❌ FAIL** |
| `eval_22_audio_resposta_preferencial` | Interação com cliente que solicita resposta direta e concisa | 🎙️ Áudio e Multimodal | `get_services_list_tool`, `check_availability_tool` | **❌ FAIL** |
| `eval_23_audio_invalido_recuperacao` | Recuperação graciosa de áudio inaudível ou corrompido | 🎙️ Áudio e Multimodal | `register_client_tool`, `get_services_list_tool` | **❌ FAIL** |
| `eval_24_fluxo_completo_cliente_novo` | Fluxo feliz completo ponta a ponta (novo cliente até confirmação) | ✨ Fluxo Padrão Ponta a Ponta | `register_client_tool`, `get_services_list_tool`, `choose_service_tool`, `list_pets_tool`, `register_pet_tool`, `choose_pet_tool`, `check_availability_tool`, `choose_date_tool`, `get_schedule_summary_tool` | **❌ FAIL** |
| `eval_25_produtos_e_localizacao` | Consulta de produtos da loja e envio de localização da clínica | 🛒 Produtos e Localização | `search_products_tool`, `send_location_tool` | **✅ PASS** |

---

## 💼 Como destacar no Currículo / LinkedIn

> **Engenheiro de IA / Desenvolvedor de Agentes Autônomos**  
> *"Agente de agendamento com LangGraph e GPT-4o-mini. Suíte de 25 cenários escritos à mão; nesta execução `--live` (2026-11-16) a taxa de acerto do harness foi **44.0%** (11/25)."*

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
