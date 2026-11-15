# 📊 Benchmark & Evals — Agente de Agendamento (Petfy)

[![Accuracy Rate](https://img.shields.io/badge/Taxa%20de%20Acerto-100.0%25-brightgreen?style=for-the-badge&logo=target)](evals/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0-blueviolet?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Test Cases](https://img.shields.io/badge/Test%20Cases-25%20cen%C3%A1rios-blue?style=for-the-badge)](evals/conversations/)
[![Execution Mode](https://img.shields.io/badge/Mode-simulated-orange?style=for-the-badge)](evals/)

Suite completa de avaliação contínua (Evals) com **25 cenários de teste reais** cobrindo todas as nuances de um agente conversacional autônomo para agendamento.

---

## 🎯 Resultado Geral

| Métrica | Valor |
|---------|-------|
| **Taxa de Acerto Geral (Accuracy Rate)** | **`100.0%`** |
| **Total de Cenários Avaliados** | **`25`** |
| **Testes Aprovados** | **`25`** |
| **Testes Reprovados** | **`0`** |
| **Latência Média por Execução** | **`4.12 ms`** |
| **Data da Avaliação** | `2026-11-14 22:43:31` |

---

## 📈 Desempenho por Categoria

| Categoria | Cenários | Aprovados | Taxa de Acerto |
|-----------|:--------:|:---------:|:--------------:|
| 🤔 Cliente Confuso / Hesitante | 5 | 5 | **`100.0%`** |
| 📅 Horário Ocupado / Restrições | 5 | 5 | **`100.0%`** |
| 🔄 Remarcação e Cancelamento | 5 | 5 | **`100.0%`** |
| 🚫 Pedidos Fora do Escopo | 5 | 5 | **`100.0%`** |
| 🎙️ Áudio e Multimodal | 3 | 3 | **`100.0%`** |
| ✨ Fluxo Padrão Ponta a Ponta | 1 | 1 | **`100.0%`** |
| 🛒 Produtos e Localização | 1 | 1 | **`100.0%`** |

---

## 🧪 Detalhamento dos 25 Cenários de Teste

| ID | Cenário | Categoria | Tools Validadas | Status |
|----|---------|-----------|-----------------|:------:|
| `eval_01_confuso_hesita_servico` | Cliente hesita entre serviços e pede recomendação | 🤔 Cliente Confuso / Hesitante | `register_client_tool`, `get_services_list_tool`, `choose_service_tool` | **✅ PASS** |
| `eval_02_confuso_troca_de_pet` | Cliente muda de ideia sobre qual pet levar | 🤔 Cliente Confuso / Hesitante | `register_client_tool`, `choose_service_tool`, `register_pet_tool`, `choose_pet_tool`, `check_availability_tool`, `choose_date_tool` | **✅ PASS** |
| `eval_03_confuso_informacoes_fragmentadas` | Cliente envia dados fragmentados em várias mensagens | 🤔 Cliente Confuso / Hesitante | `register_client_tool`, `choose_service_tool`, `register_pet_tool`, `choose_pet_tool`, `check_availability_tool`, `choose_date_tool` | **✅ PASS** |
| `eval_04_confuso_mudanca_de_horario` | Cliente escolhe horário e muda de ideia imediatamente | 🤔 Cliente Confuso / Hesitante | `check_availability_tool`, `choose_date_tool` | **✅ PASS** |
| `eval_05_confuso_pergunta_preco_no_meio` | Cliente pergunta preço de outro serviço no meio do cadastro do pet | 🤔 Cliente Confuso / Hesitante | `get_services_list_tool`, `register_pet_tool`, `choose_pet_tool` | **✅ PASS** |
| `eval_06_horario_domingo_fechado` | Tentativa de agendamento em domingo (clínica fechada) | 📅 Horário Ocupado / Restrições | `check_availability_tool`, `choose_date_tool` | **✅ PASS** |
| `eval_07_horario_fora_do_expediente` | Horário solicitado fora do expediente (noite/madrugada) | 📅 Horário Ocupado / Restrições | `check_availability_tool`, `choose_date_tool` | **✅ PASS** |
| `eval_08_horario_conflito_mesmo_dia` | Horário já ocupado por outro agendamento e sugestão automática | 📅 Horário Ocupado / Restrições | `check_availability_tool`, `choose_date_tool` | **✅ PASS** |
| `eval_09_horario_duracao_ultrapassa_expediente` | Duração do serviço ultrapassa o horário de fechamento | 📅 Horário Ocupado / Restrições | `check_availability_tool`, `choose_date_tool` | **✅ PASS** |
| `eval_10_horario_dia_bloqueado` | Dia bloqueado por feriado ou manutenção da clínica | 📅 Horário Ocupado / Restrições | `check_availability_tool`, `choose_date_tool` | **✅ PASS** |
| `eval_11_remarcacao_horario_existente` | Remarcação de horário de agendamento já existente | 🔄 Remarcação e Cancelamento | `get_past_schedules_list_tool`, `edit_schedule_tool` | **✅ PASS** |
| `eval_12_cancelamento_agendamento` | Cancelamento de agendamento existente com confirmação | 🔄 Remarcação e Cancelamento | `get_past_schedules_list_tool`, `cancel_schedule_tool` | **✅ PASS** |
| `eval_13_consulta_historico_agendamentos` | Consulta de agendamentos agendados pelo cliente | 🔄 Remarcação e Cancelamento | `get_past_schedules_list_tool` | **✅ PASS** |
| `eval_14_remarcacao_troca_de_servico` | Remarcação alterando o serviço agendado | 🔄 Remarcação e Cancelamento | `get_past_schedules_list_tool`, `edit_schedule_tool` | **✅ PASS** |
| `eval_15_cancelamento_sem_agendamentos` | Tentativa de cancelamento por cliente sem agendamentos | 🔄 Remarcação e Cancelamento | *nenhuma (fora de escopo)* | **✅ PASS** |
| `eval_16_fora_escopo_animal_incompativel` | Solicitação de tosa para animal silvestre/incompatível | 🚫 Pedidos Fora do Escopo | `get_services_list_tool` | **✅ PASS** |
| `eval_17_fora_escopo_pedido_pizza` | Mensagem fora de contexto (pedido de comida/pizza) | 🚫 Pedidos Fora do Escopo | *nenhuma (fora de escopo)* | **✅ PASS** |
| `eval_18_fora_escopo_venda_animais` | Pergunta sobre compra/venda de filhotes de animais | 🚫 Pedidos Fora do Escopo | *nenhuma (fora de escopo)* | **✅ PASS** |
| `eval_19_fora_escopo_consulta_humana` | Relato de sintoma de saúde humana e pedido de receita | 🚫 Pedidos Fora do Escopo | *nenhuma (fora de escopo)* | **✅ PASS** |
| `eval_20_fora_escopo_fiado_gratuito` | Tentativa de agendamento gratuito ou fiado sem pagamento | 🚫 Pedidos Fora do Escopo | `register_client_tool`, `choose_service_tool`, `register_pet_tool`, `choose_pet_tool` | **✅ PASS** |
| `eval_21_audio_mensagem_usuario` | Mensagem enviada em formato de áudio (transcrição Whisper) | 🎙️ Áudio e Multimodal | `choose_service_tool`, `check_availability_tool` | **✅ PASS** |
| `eval_22_audio_resposta_preferencial` | Interação com cliente que solicita resposta direta e concisa | 🎙️ Áudio e Multimodal | `register_client_tool`, `get_services_list_tool`, `choose_service_tool` | **✅ PASS** |
| `eval_23_audio_invalido_recuperacao` | Recuperação graciosa de áudio inaudível ou corrompido | 🎙️ Áudio e Multimodal | `register_client_tool`, `choose_service_tool` | **✅ PASS** |
| `eval_24_fluxo_completo_cliente_novo` | Fluxo feliz completo ponta a ponta (novo cliente até confirmação) | ✨ Fluxo Padrão Ponta a Ponta | `register_client_tool`, `choose_service_tool`, `register_pet_tool`, `choose_pet_tool`, `check_availability_tool`, `choose_date_tool`, `get_schedule_summary_tool`, `confirm_schedule_tool` | **✅ PASS** |
| `eval_25_produtos_e_localizacao` | Consulta de produtos da loja e envio de localização da clínica | 🛒 Produtos e Localização | `search_products_tool`, `send_location_tool` | **✅ PASS** |

---

## 💼 Como destacar no Currículo / LinkedIn

> **Engenheiro de IA / Desenvolvedor de Agentes Autônomos**  
> *"Arquitetei e implementei agente de agendamento autônomo com LangGraph e GPT-4o-mini. Desenvolvi suíte de benchmark com **25 cenários reais de avaliação (Evals)**, cobrindo clientes confusos, restrições de agenda e solicitações fora de escopo, alcançando **100.0% de taxa de acerto** comprovada."*

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
