import json
from pathlib import Path

cases_dir = Path(__file__).parent / "conversations"
cases_dir.mkdir(parents=True, exist_ok=True)

test_cases = [
    # ─── 1. CLIENTE CONFUSO (5 casos) ──────────────────────────
    {
        "id": "eval_01_confuso_hesita_servico",
        "category": "cliente_confuso",
        "title": "Cliente hesita entre serviços e pede recomendação",
        "description": "Cliente diz que o cachorro está sujinho e com pelos embolados, não sabe a diferença dos serviços. O agente lista os serviços, recomenda banho e tosa, e o cliente aceita.",
        "client": {"name": "Mariana Souza", "number": "5511971110001"},
        "turns": [
            {"role": "user", "content": "Oi, sou a Mariana. Queria cuidar do meu cachorrinho mas tô meio perdida, o que vcs fazem aí?"},
            {"role": "user", "content": "Ele é um poodle, tá com pelo embolado e meio sujinho. Quanto fica o banho e tosa?"},
            {"role": "user", "content": "Perfeito, então quero esse de banho e tosa com certeza!"}
        ],
        "expected": {
            "tools_called": ["register_client_tool", "get_services_list_tool", "choose_service_tool"],
            "target_step": "CHOOSE_PET",
            "forbidden_tools": ["cancel_schedule_tool"],
            "criteria": [
                "Agente registrou cliente Mariana",
                "Agente buscou lista de serviços",
                "Agente confirmou o serviço de Banho e Tosa (ID 1)",
                "Transição para etapa CHOOSE_PET"
            ]
        }
    },
    {
        "id": "eval_02_confuso_troca_de_pet",
        "category": "cliente_confuso",
        "title": "Cliente muda de ideia sobre qual pet levar",
        "description": "Cliente começa cadastrando Rex (cão), mas depois muda de ideia e decide agendar para a gatinha Luna.",
        "client": {"name": "Rodrigo Lima", "number": "5511971110002"},
        "turns": [
            {"role": "user", "content": "Olá, meu nome é Rodrigo Lima. Gostaria de agendar uma consulta veterinária."},
            {"role": "user", "content": "Sim, consulta veterinária confirmada!"},
            {"role": "user", "content": "Eu ia levar meu cachorro Rex, mas na verdade a gata Luna que tá espirrando. Ela tem 2 anos, fêmea, sem raça definida, pesa 4kg."},
            {"role": "user", "content": "Isso mesmo, é pra Luna gatinha!"}
        ],
        "expected": {
            "tools_called": ["register_client_tool", "choose_service_tool", "register_pet_tool", "choose_pet_tool"],
            "target_step": "CHOOSE_DATE",
            "forbidden_tools": [],
            "criteria": [
                "Agente registrou cliente Rodrigo",
                "Agente registrou pet do tipo gato (Luna)",
                "Agente associou a gata Luna e não o cão Rex",
                "Avançou para escolha de data"
            ]
        }
    },
    {
        "id": "eval_03_confuso_informacoes_fragmentadas",
        "category": "cliente_confuso",
        "title": "Cliente envia dados fragmentados em várias mensagens",
        "description": "Cliente manda mensagens curtas e picadas com informações incompletas. O agente reúne os dados progressivamente.",
        "client": {"name": "Fernanda Costa", "number": "5511971110003"},
        "turns": [
            {"role": "user", "content": "oie"},
            {"role": "user", "content": "fernanda"},
            {"role": "user", "content": "vacina"},
            {"role": "user", "content": "quero vacinar meu cachorro sim"},
            {"role": "user", "content": "Thor, golden, 3 anos, macho, 30kg, saudável"}
        ],
        "expected": {
            "tools_called": ["register_client_tool", "choose_service_tool", "register_pet_tool"],
            "target_step": "CHOOSE_DATE",
            "forbidden_tools": ["cancel_schedule_tool"],
            "criteria": [
                "Agente tratou mensagens curtas sem quebrar o fluxo",
                "Identificou o nome Fernanda",
                "Identificou serviço de vacinação",
                "Cadastrou o pet Thor com porte grande"
            ]
        }
    },
    {
        "id": "eval_04_confuso_mudanca_de_horario",
        "category": "cliente_confuso",
        "title": "Cliente escolhe horário e muda de ideia imediatamente",
        "description": "Cliente sugere 14:00, mas em seguida percebe compromisso e pede 16:30. Agente deve validar o novo horário.",
        "client": {"name": "Lucas Mendes", "number": "5511971110004"},
        "initial_state": {
            "step": "CHOOSE_DATE",
            "client_info": {"id": 1, "name": "Lucas Mendes", "number": "5511971110004"},
            "schedule_info": {"service_id": 1, "pet_id": 1}
        },
        "turns": [
            {"role": "user", "content": "Pode ser na sexta 2026-11-20 às 14:00?"},
            {"role": "user", "content": "Opa espera! 14h tenho reunião de trabalho, dá pra ser às 16:00 do mesmo dia?"}
        ],
        "expected": {
            "tools_called": ["check_availability_tool", "choose_date_tool"],
            "target_step": "CONFIRM_SCHEDULE",
            "forbidden_tools": [],
            "criteria": [
                "Agente verificou disponibilidade para 16:00",
                "Horário final gravado no estado é 16:00 e não 14:00",
                "Avançou para CONFIRM_SCHEDULE"
            ]
        }
    },
    {
        "id": "eval_05_confuso_pergunta_preco_no_meio",
        "category": "cliente_confuso",
        "title": "Cliente pergunta preço de outro serviço no meio do cadastro do pet",
        "description": "Durante o cadastro do pet para banho, o cliente interrompe perguntando quanto custa consulta veterinária. O agente responde o preço e retoma o agendamento.",
        "client": {"name": "Beatriz Ramos", "number": "5511971110005"},
        "initial_state": {
            "step": "CHOOSE_PET",
            "client_info": {"id": 1, "name": "Beatriz Ramos", "number": "5511971110005"},
            "schedule_info": {"service_id": 1}
        },
        "turns": [
            {"role": "user", "content": "Antes de falar do meu cachorro, quanto custa uma consulta veterinária com vocês?"},
            {"role": "user", "content": "Entendi! Bom, pro banho vai ser o Pipoca, um maltês macho de 2 anos, pequeno, 4kg"}
        ],
        "expected": {
            "tools_called": ["get_services_list_tool", "register_pet_tool", "choose_pet_tool"],
            "target_step": "CHOOSE_DATE",
            "forbidden_tools": [],
            "criteria": [
                "Agente informou o valor da consulta (R$ 60)",
                "Agente retomou a etapa de pet sem perder o serviço de banho",
                "Registrou o Pipoca e avançou para CHOOSE_DATE"
            ]
        }
    },

    # ─── 2. HORÁRIO OCUPADO E RESTRIÇÕES (5 casos) ─────────────
    {
        "id": "eval_06_horario_domingo_fechado",
        "category": "horario_ocupado",
        "title": "Tentativa de agendamento em domingo (clínica fechada)",
        "description": "Cliente tenta marcar atendimento para um domingo (2026-11-15). O agente recusa informando que a clínica não abre aos domingos e sugere dias úteis ou sábado.",
        "client": {"name": "Juliana Dias", "number": "5511972220001"},
        "initial_state": {
            "step": "CHOOSE_DATE",
            "client_info": {"id": 1, "name": "Juliana Dias", "number": "5511972220001"},
            "schedule_info": {"service_id": 2, "pet_id": 1}
        },
        "turns": [
            {"role": "user", "content": "Queria marcar a consulta pro próximo domingo dia 2026-11-15 às 10:00, é possível?"},
            {"role": "user", "content": "Ah entendi que não abre domingo. Pode ser na segunda dia 2026-11-16 às 10:00 então?"}
        ],
        "expected": {
            "tools_called": ["check_availability_tool", "choose_date_tool"],
            "target_step": "CONFIRM_SCHEDULE",
            "forbidden_tools": [],
            "criteria": [
                "Agente verificou que domingo está indisponível ('Clínica fechada neste dia')",
                "Não confirmou data inválida de domingo",
                "Aceitou e gravou a segunda-feira 2026-11-16 às 10:00"
            ]
        }
    },
    {
        "id": "eval_07_horario_fora_do_expediente",
        "category": "horario_ocupado",
        "title": "Horário solicitado fora do expediente (noite/madrugada)",
        "description": "Cliente pede agendamento às 21:00 ou 06:00. Agente informa horário comercial (08:00 às 18:00) e não permite agendar fora.",
        "client": {"name": "Marcelo Neves", "number": "5511972220002"},
        "initial_state": {
            "step": "CHOOSE_DATE",
            "client_info": {"id": 1, "name": "Marcelo Neves", "number": "5511972220002"},
            "schedule_info": {"service_id": 1, "pet_id": 1}
        },
        "turns": [
            {"role": "user", "content": "Vocês atendem à noite? Queria levar meu pet dia 2026-11-18 às 21:00."},
            {"role": "user", "content": "Ok, qual o último horário disponível desse dia então?"},
            {"role": "user", "content": "Pode marcar pras 16:00 então!"}
        ],
        "expected": {
            "tools_called": ["check_availability_tool", "choose_date_tool"],
            "target_step": "CONFIRM_SCHEDULE",
            "forbidden_tools": [],
            "criteria": [
                "Agente informou que 21:00 está fora do horário de funcionamento",
                "Agente manteve o cliente no fluxo",
                "Agendou 16:00 após confirmação"
            ]
        }
    },
    {
        "id": "eval_08_horario_conflito_mesmo_dia",
        "category": "horario_ocupado",
        "title": "Horário já ocupado por outro agendamento e sugestão automática",
        "description": "Cliente solicita horário já reservado (15:00 na data com agendamento ativo). O agente detecta conflito e propõe o próximo horário disponível no mesmo dia.",
        "client": {"name": "Patricia Abravanel", "number": "5511972220003"},
        "initial_state": {
            "step": "CHOOSE_DATE",
            "client_info": {"id": 2, "name": "Patricia", "number": "5511972220003"},
            "schedule_info": {"service_id": 1, "pet_id": 1}
        },
        "turns": [
            {"role": "user", "content": "Gostaria de agendar para 2026-11-20 às 15:00."},
            {"role": "user", "content": "Entendi que 15h já está ocupado. Qual horário vago vc me sugeriu mesmo? Pode ser esse!"}
        ],
        "expected": {
            "tools_called": ["check_availability_tool", "choose_date_tool"],
            "target_step": "CONFIRM_SCHEDULE",
            "forbidden_tools": [],
            "criteria": [
                "check_availability_tool retornou available=False para 15:00",
                "Agente informou que horário estava ocupado",
                "Agente usou o slot alternativo válido"
            ]
        }
    },
    {
        "id": "eval_09_horario_duracao_ultrapassa_expediente",
        "category": "horario_ocupado",
        "title": "Duração do serviço ultrapassa o horário de fechamento",
        "description": "Cliente pede serviço de 60 minutos às 17:30 numa sexta (expediente encerra às 18:00). Agente recusa pois ultrapassa expediente e sugere horário anterior.",
        "client": {"name": "Eduardo Paes", "number": "5511972220004"},
        "initial_state": {
            "step": "CHOOSE_DATE",
            "client_info": {"id": 1, "name": "Eduardo", "number": "5511972220004"},
            "schedule_info": {"service_id": 1, "pet_id": 1}
        },
        "turns": [
            {"role": "user", "content": "Quero banho e tosa (60 min) na sexta 2026-11-20 às 17:30."},
            {"role": "user", "content": "Ah, fecha às 18h né! Pode ser às 16:30 então?"}
        ],
        "expected": {
            "tools_called": ["check_availability_tool", "choose_date_tool"],
            "target_step": "CONFIRM_SCHEDULE",
            "forbidden_tools": [],
            "criteria": [
                "Detectou que serviço ultrapassa o horário de encerramento às 18:00",
                "Recusou o horário das 17:30",
                "Aprovou 16:30 que finaliza exatamente às 17:30"
            ]
        }
    },
    {
        "id": "eval_10_horario_dia_bloqueado",
        "category": "horario_ocupado",
        "title": "Dia bloqueado por feriado ou manutenção da clínica",
        "description": "Cliente tenta marcar consulta em data registrada como feriado/bloqueada. Agente informa bloqueio e propõe dia seguinte.",
        "client": {"name": "Carla Perez", "number": "5511972220005"},
        "initial_state": {
            "step": "CHOOSE_DATE",
            "client_info": {"id": 1, "name": "Carla", "number": "5511972220005"},
            "schedule_info": {"service_id": 2, "pet_id": 1}
        },
        "turns": [
            {"role": "user", "content": "Queria marcar consulta pro dia 2026-12-25 às 10:00."},
            {"role": "user", "content": "Sem problemas! Podemos marcar para dia 2026-12-28 às 10:00 (segunda)?"}
        ],
        "expected": {
            "tools_called": ["check_availability_tool", "choose_date_tool"],
            "target_step": "CONFIRM_SCHEDULE",
            "forbidden_tools": [],
            "criteria": [
                "Agente verificou disponibilidade",
                "Não concluiu no feriado bloqueado",
                "Aprovou a data útil subsequente"
            ]
        }
    },

    # ─── 3. REMARCAÇÃO E CANCELAMENTO (5 casos) ────────────────
    {
        "id": "eval_11_remarcacao_horario_existente",
        "category": "remarcacao_cancelamento",
        "title": "Remarcação de horário de agendamento já existente",
        "description": "Cliente que já possui agendamento pede para mudar o dia e hora. O agente lista os agendamentos existentes e executa edit_schedule_tool.",
        "client": {"name": "Gabriel", "number": "5511999999999"},
        "has_previous_appointments": True,
        "turns": [
            {"role": "user", "content": "Olá! Preciso remarcar o agendamento do Floquinho."},
            {"role": "user", "content": "Quero mudar para dia 2026-11-25 às 14:00, por favor."}
        ],
        "expected": {
            "tools_called": ["get_past_schedules_list_tool", "edit_schedule_tool"],
            "target_step": "MANAGE_SCHEDULE",
            "forbidden_tools": ["cancel_schedule_tool"],
            "criteria": [
                "Agente chamou get_past_schedules_list_tool para identificar o agendamento",
                "Agente chamou edit_schedule_tool com nova data e hora",
                "Não cancelou por engano"
            ]
        }
    },
    {
        "id": "eval_12_cancelamento_agendamento",
        "category": "remarcacao_cancelamento",
        "title": "Cancelamento de agendamento existente com confirmação",
        "description": "Cliente solicita cancelamento de agendamento prévio. Agente lista os agendamentos, obtém o ID e cancela usando cancel_schedule_tool.",
        "client": {"name": "Gabriel", "number": "5511999999999"},
        "has_previous_appointments": True,
        "turns": [
            {"role": "user", "content": "Oi, infelizmente vou ter que viajar e preciso cancelar meu horário agendado."},
            {"role": "user", "content": "Sim, pode cancelar o agendamento número 1."}
        ],
        "expected": {
            "tools_called": ["get_past_schedules_list_tool", "cancel_schedule_tool"],
            "target_step": "MANAGE_SCHEDULE",
            "forbidden_tools": ["edit_schedule_tool"],
            "criteria": [
                "Agente identificou agendamento com get_past_schedules_list_tool",
                "Agente executou cancel_schedule_tool com o appointment_id correto",
                "Confirmou cancelamento com mensagem empática"
            ]
        }
    },
    {
        "id": "eval_13_consulta_historico_agendamentos",
        "category": "remarcacao_cancelamento",
        "title": "Consulta de agendamentos agendados pelo cliente",
        "description": "Cliente pergunta quais horários tem marcados na clínica. Agente chama get_past_schedules_list_tool e informa detalhes.",
        "client": {"name": "Gabriel", "number": "5511999999999"},
        "has_previous_appointments": True,
        "turns": [
            {"role": "user", "content": "Oi Júlia! Não lembro qual dia marquei o banho do Floquinho, pode me lembrar?"}
        ],
        "expected": {
            "tools_called": ["get_past_schedules_list_tool"],
            "target_step": "MANAGE_SCHEDULE",
            "forbidden_tools": ["cancel_schedule_tool", "edit_schedule_tool"],
            "criteria": [
                "Agente chamou get_past_schedules_list_tool",
                "Agente informou a data, horário e serviço do Floquinho",
                "Não modificou nenhum dado"
            ]
        }
    },
    {
        "id": "eval_14_remarcacao_troca_de_servico",
        "category": "remarcacao_cancelamento",
        "title": "Remarcação alterando o serviço agendado",
        "description": "Cliente quer manter a data mas trocar o serviço de banho para consulta veterinária.",
        "client": {"name": "Gabriel", "number": "5511999999999"},
        "has_previous_appointments": True,
        "turns": [
            {"role": "user", "content": "Queria trocar meu agendamento: em vez de banho, preciso de uma consulta veterinária pro Floquinho no mesmo dia."}
        ],
        "expected": {
            "tools_called": ["get_past_schedules_list_tool", "edit_schedule_tool"],
            "target_step": "MANAGE_SCHEDULE",
            "forbidden_tools": [],
            "criteria": [
                "Agente localizou o agendamento anterior",
                "Agente chamou edit_schedule_tool com o service_id atualizado",
                "Confirmou a alteração do tipo de serviço"
            ]
        }
    },
    {
        "id": "eval_15_cancelamento_sem_agendamentos",
        "category": "remarcacao_cancelamento",
        "title": "Tentativa de cancelamento por cliente sem agendamentos",
        "description": "Cliente novo ou sem histórico pede cancelamento. Agente avisa educadamente que não há agendamentos ativos vinculados.",
        "client": {"name": "Thiago Silva", "number": "5511973330001"},
        "has_previous_appointments": False,
        "turns": [
            {"role": "user", "content": "Oi, sou o Thiago Silva. Quero cancelar o agendamento de amanhã."}
        ],
        "expected": {
            "tools_called": [],
            "target_step": "REGISTER_CLIENT",
            "forbidden_tools": ["cancel_schedule_tool", "edit_schedule_tool"],
            "criteria": [
                "Não tentou cancelar agendamento inexistente",
                "Informou educadamente ausência de agendamentos no cadastro",
                "Se ofereceu para criar um novo agendamento"
            ]
        }
    },

    # ─── 4. PEDIDOS FORA DO ESCOPO (5 casos) ───────────────────
    {
        "id": "eval_16_fora_escopo_animal_incompativel",
        "category": "fora_do_escopo",
        "title": "Solicitação de tosa para animal silvestre/incompatível",
        "description": "Cliente pede tosa para uma jiboia ou iguana. O agente informa que o serviço de banho e tosa é exclusivo para cães e não atende répteis.",
        "client": {"name": "Bruno Covas", "number": "5511974440001"},
        "initial_state": {
            "step": "CHOOSE_SERVICE",
            "client_info": {"id": 1, "name": "Bruno", "number": "5511974440001"},
            "schedule_info": {}
        },
        "turns": [
            {"role": "user", "content": "Vocês fazem tosa completa em cobra jiboia?"},
            {"role": "user", "content": "E em cavalo?"}
        ],
        "expected": {
            "tools_called": ["get_services_list_tool"],
            "target_step": "CHOOSE_SERVICE",
            "forbidden_tools": ["choose_service_tool", "confirm_schedule_tool"],
            "criteria": [
                "Agente recusou atendimento de animais não suportados",
                "Explicou que banho e tosa é para cães/gatos suportados",
                "Manteve tom profissional e acolhedor sem alucinar suporte a animais silvestres"
            ]
        }
    },
    {
        "id": "eval_17_fora_escopo_pedido_pizza",
        "category": "fora_do_escopo",
        "title": "Mensagem fora de contexto (pedido de comida/pizza)",
        "description": "Usuário envia pedido de pizza. Agente reforça educadamente que é um assistente veterinário/petshop da Petfy.",
        "client": {"name": "Desconhecido", "number": "5511974440002"},
        "turns": [
            {"role": "user", "content": "Boa noite, me manda duas pizzas grandes de 4 queijos e uma coca 2 litros no endereço Rua das Flores 123"}
        ],
        "expected": {
            "tools_called": [],
            "target_step": "REGISTER_CLIENT",
            "forbidden_tools": ["confirm_schedule_tool", "register_client_tool"],
            "criteria": [
                "Agente não tentou agendar serviço para pizza",
                "Esclareceu identidade como assistente da clínica Petfy",
                "Respondeu com cordialidade e bom humor"
            ]
        }
    },
    {
        "id": "eval_18_fora_escopo_venda_animais",
        "category": "fora_do_escopo",
        "title": "Pergunta sobre compra/venda de filhotes de animais",
        "description": "Cliente pergunta se a clínica vende filhotes de cachorro de raça. Agente esclarece que presta serviços de saúde e estética, não comercializando animais.",
        "client": {"name": "Larissa Manoela", "number": "5511974440003"},
        "turns": [
            {"role": "user", "content": "Oi, vocês têm filhote de Golden Retriever para vender? Quanto tá custando?"}
        ],
        "expected": {
            "tools_called": [],
            "target_step": "REGISTER_CLIENT",
            "forbidden_tools": ["choose_service_tool"],
            "criteria": [
                "Agente informou que a Petfy não vende animais",
                "Explicou os serviços prestados (consultas, vacinas, banho e tosa, produtos)",
                "Convidou para conhecer os serviços de saúde preventiva"
            ]
        }
    },
    {
        "id": "eval_19_fora_escopo_consulta_humana",
        "category": "fora_do_escopo",
        "title": "Relato de sintoma de saúde humana e pedido de receita",
        "description": "Usuário relata sintomas de gripe/dor de garganta humana e pede remédio. Agente recusa expressamente e orienta buscar médico humano.",
        "client": {"name": "Renato Russo", "number": "5511974440004"},
        "turns": [
            {"role": "user", "content": "Estou com muita dor de garganta e febre alta, o veterinário aí pode me receitar um antibiótico pra eu tomar?"}
        ],
        "expected": {
            "tools_called": [],
            "target_step": "REGISTER_CLIENT",
            "forbidden_tools": ["choose_service_tool", "confirm_schedule_tool"],
            "criteria": [
                "Agente recusou atendimento médico para seres humanos",
                "Recomendou procurar UBS ou pronto-socorro humano",
                "Reiterou que o atendimento é estritamente veterinário para animais de estimação"
            ]
        }
    },
    {
        "id": "eval_20_fora_escopo_fiado_gratuito",
        "category": "fora_do_escopo",
        "title": "Tentativa de agendamento gratuito ou fiado sem pagamento",
        "description": "Cliente pede serviço gratuito ou fiado para pagar no mês seguinte. Agente mantém a política de preços da clínica com respeito.",
        "client": {"name": "Seu Madruga", "number": "5511974440005"},
        "turns": [
            {"role": "user", "content": "Oi, sou o Seu Madruga. Posso dar banho no meu cachorro e pagar fiado daqui 14 meses?"}
        ],
        "expected": {
            "tools_called": ["register_client_tool"],
            "target_step": "CHOOSE_SERVICE",
            "forbidden_tools": ["confirm_schedule_tool"],
            "criteria": [
                "Agente manteve postura profissional",
                "Informou que não realiza atendimentos fiados",
                "Apresentou a tabela padrão de serviços e formas de pagamento"
            ]
        }
    },

    # ─── 5. ÁUDIO E MULTIMODAL (3 casos) ───────────────────────
    {
        "id": "eval_21_audio_mensagem_usuario",
        "category": "audio",
        "title": "Mensagem enviada em formato de áudio (transcrição Whisper)",
        "description": "Cliente envia áudio pedindo banho pro Floquinho. Sistema processa transcrição e responde de forma empática.",
        "client": {"name": "Gabriel", "number": "5511999999999"},
        "turns": [
            {
                "role": "user",
                "mode": "audio",
                "content": "Oi Júlia, tudo bem? Tô mandando esse áudio porque tô dirigindo, queria marcar um banho pro Floquinho amanhã às dez da manhã."
            }
        ],
        "expected": {
            "tools_called": ["choose_service_tool", "check_availability_tool"],
            "target_step": "CONFIRM_SCHEDULE",
            "forbidden_tools": [],
            "criteria": [
                "Sistema identificou o modo áudio corretamente",
                "Agente compreendeu a intenção falada do cliente",
                "Deu andamento ao agendamento de forma fluida"
            ]
        }
    },
    {
        "id": "eval_22_audio_resposta_preferencial",
        "category": "audio",
        "title": "Interação com cliente que solicita resposta direta e concisa",
        "description": "Cliente pede áudio ou texto objetivo com horários da semana. Agente responde de acordo com as preferências de tom e canal.",
        "client": {"name": "Vanessa Camargo", "number": "5511975550001"},
        "turns": [
            {
                "role": "user",
                "mode": "text",
                "content": "Olá Júlia! Sou a Vanessa. Quais são os horários disponíveis para consulta nesta quarta-feira 2026-11-18?"
            }
        ],
        "expected": {
            "tools_called": ["register_client_tool", "get_services_list_tool"],
            "target_step": "CHOOSE_SERVICE",
            "forbidden_tools": [],
            "criteria": [
                "Registrou cliente Vanessa",
                "Listou os horários/serviços disponíveis com clareza",
                "Tom acolhedor e informativo"
            ]
        }
    },
    {
        "id": "eval_23_audio_invalido_recuperacao",
        "category": "audio",
        "title": "Recuperação graciosa de áudio inaudível ou corrompido",
        "description": "Mensagem de áudio chega sem dados válidos ou inaudível. Agente avisa com gentileza e pede para o usuário repetir ou digitar.",
        "client": {"name": "Paulo Coelho", "number": "5511975550002"},
        "turns": [
            {
                "role": "user",
                "mode": "audio",
                "content": "[audio_not_processed]"
            },
            {
                "role": "user",
                "mode": "text",
                "content": "Oi, acho que meu áudio falhou! Sou o Paulo e quero agendar vacinação pro meu cão."
            }
        ],
        "expected": {
            "tools_called": ["register_client_tool", "choose_service_tool"],
            "target_step": "CHOOSE_PET",
            "forbidden_tools": [],
            "criteria": [
                "Tratou o áudio não processado sem quebrar o sistema",
                "Respondeu educadamente na mensagem de texto subsequente",
                "Conduziu o cadastro e serviço normalmente"
            ]
        }
    },

    # ─── 6. FLUXO PADRÃO, PRODUTOS E LOCALIZAÇÃO (2 casos) ─────
    {
        "id": "eval_24_fluxo_completo_cliente_novo",
        "category": "fluxo_padrao",
        "title": "Fluxo feliz completo ponta a ponta (novo cliente até confirmação)",
        "description": "Cliente novo chega, se cadastra, escolhe banho e tosa, cadastra o cão Duque, seleciona data livre e confirma o agendamento.",
        "client": {"name": "Helena Rost", "number": "5511976660001"},
        "turns": [
            {"role": "user", "content": "Olá! Gostaria de agendar um serviço pro meu pet. Meu nome é Helena."},
            {"role": "user", "content": "Quero Banho e Tosa de Cachorros."},
            {"role": "user", "content": "O pet é o Duque, um Golden Retriever de 4 anos, porte grande, macho, 32kg, muito dócil."},
            {"role": "user", "content": "Pode ser na segunda 2026-11-16 às 14:00?"},
            {"role": "user", "content": "Sim, tudo certo! Pode confirmar o agendamento."}
        ],
        "expected": {
            "tools_called": [
                "register_client_tool",
                "choose_service_tool",
                "register_pet_tool",
                "choose_pet_tool",
                "check_availability_tool",
                "choose_date_tool",
                "get_schedule_summary_tool",
                "confirm_schedule_tool"
            ],
            "target_step": "CHOOSE_SERVICE",  # após confirmação o estado reseta para CHOOSE_SERVICE
            "forbidden_tools": ["cancel_schedule_tool"],
            "criteria": [
                "Registrou cliente Helena",
                "Selecionou Banho e Tosa (ID 1)",
                "Cadastrou e associou o cão Duque",
                "Verificou disponibilidade para 14:00 em dia útil",
                "Chamou get_schedule_summary_tool antes de confirmar",
                "Executou confirm_schedule_tool criando novo agendamento no banco",
                "Chamou reset_state_node preservando cliente e zerando schedule_info"
            ]
        }
    },
    {
        "id": "eval_25_produtos_e_localizacao",
        "category": "produtos_e_localizacao",
        "title": "Consulta de produtos da loja e envio de localização da clínica",
        "description": "Cliente pergunta se a clínica tem coleira e ração à venda e pede a localização/endereço no WhatsApp.",
        "client": {"name": "Felipe Neto", "number": "5511976660002"},
        "turns": [
            {"role": "user", "content": "Olá, vcs vendem coleira na clínica? Tem em estoque?"},
            {"role": "user", "content": "Ótimo! Onde fica a clínica de vocês? Pode me mandar a localização?"}
        ],
        "expected": {
            "tools_called": ["search_products_tool", "send_location_tool"],
            "target_step": "REGISTER_CLIENT",
            "forbidden_tools": ["confirm_schedule_tool"],
            "criteria": [
                "Agente chamou search_products_tool com o termo 'coleira'",
                "Informou estoque/preço do produto",
                "Chamou send_location_tool enviando o endereço/localização da clínica",
                "Respondeu de forma precisa e prestativa"
            ]
        }
    }
]

for tc in test_cases:
    file_path = cases_dir / f"{tc['id']}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(tc, f, indent=2, ensure_ascii=False)
    print(f"✅ Gerado: {file_path.name}")

print(f"\n🎉 Total de {len(test_cases)} casos de teste gerados com sucesso em {cases_dir}!")
