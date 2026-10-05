# Painel diário de produtividade — plano de implementação

> **Para agentes implementadores:** SUBSKILL OBRIGATÓRIA: use `superpowers:subagent-driven-development` (recomendado) ou `superpowers:executing-plans` para executar este plano tarefa por tarefa. As etapas usam caixas de seleção.

**Objetivo:** Criar uma base privada no Google Drive e um site privado, atualizado após cada registro diário enviado pelo usuário na conversa, com indicadores de produção, fila, relações entre processos e palavras-chave.

**Arquitetura:** Uma planilha privada no Drive será a fonte canônica. O assistente preserva e estrutura cada mensagem diária, atualiza a planilha e prepara um snapshot privado; código Python do repositório público gera os gráficos e a página estática para publicação privada. A planilha e o snapshot publicado permanecem fora do GitHub.

**Tecnologias:** Python, pandas, Pydantic, Plotly, HTML/CSS/JavaScript, Google Sheets, publicação privada de site e pytest.

**Especificação:** `docs/superpowers/specs/2026-10-05-daily-productivity-dashboard-design.md`

## Restrições globais

- Manter os dados canônicos em planilha privada do Google Drive.
- Manter o repositório público sem registros, identificadores de processos, valores de produção ou snapshots privados.
- Publicar o site com acesso privado e atualizar a publicação depois de cada registro diário.
- Gerar gráficos quantitativos com Python.
- Preservar mensagens originais, histórico cumulativo e correções rastreáveis.
- Representar ausências como lacunas ou “sem dado”; não converter ausência em zero.
- Manter pesos de carga identificados como experimentais; não apresentá-los como horas.
- Tratar IC como etapa do fluxo; previsão = emissão + 60 dias; resposta real substitui a previsão.
- Calcular as faixas de envelhecimento em dias: <150, 150–164, 165–179, 180–239 e ≥240.
- Calcular projeções de prazo apenas quando houver datas confiáveis.
- Associar processos com tipo de vínculo e evidência; diferenciar vínculo confirmado de pendente.
- Exibir o cartão de palavras-chave imediatamente acima do cartão da divergência.
- Carregar os valores da divergência do Drive; não fixá-los no código público.

## Foco de revisão

- Mensagem com várias atividades, data ou quantidade ausente: preservar o original e deixar campos ausentes sem estimativa. Fixar em teste de atividade.
- Série mensal com lacuna ou versões divergentes: preservar a lacuna e a proveniência dos valores. Fixar em teste de migração e métricas.
- Idade da fila exatamente nos limites de faixa: classificar sem erro de fronteira. Fixar em teste de métricas.
- IC sem resposta, resposta prevista no 60º dia ou resposta real: substituir previsão pela data efetiva quando houver resposta. Fixar em teste de métricas.
- Relação por CAR ou texto sem evidência: registrar o tipo de evidência disponível e manter sem suporte como pendente. Fixar em teste de relações.

---

### Tarefa 1: Modelos de atividade, processo e snapshot

**Arquivos:**
- Criar: `app_produtividade_diaria/models.py`
- Criar: `app_produtividade_diaria/tests/test_models.py`

**Interfaces:**
- Produz: `ActivityRecord`, `ProcessRelation`, `HistoricalSeries` e `DashboardSnapshot`, validados com Pydantic.
- `ActivityRecord`: id, id da mensagem original, data da atividade, instante de registro com fuso, categoria, descrição, processos associados, resultado, quantidade/unidade opcionais, palavras-chave e estado de revisão.
- `ProcessRelation`: processo A, processo B, tipo, evidência, origem, data de registro e confirmação.
- `DashboardSnapshot`: listas tipadas de atividades, séries históricas, processos, relações e palavras-chave.

- [ ] **Passo 1: escrever os testes que falham**
  - `test_activity_record_keeps_missing_quantity_empty`: quantidade e unidade não informadas permanecem ausentes.
  - `test_activity_record_preserves_source_message`: cada atividade referencia a mensagem original.
  - `test_relation_requires_evidence_or_pending_state`: vínculo sem evidência fica pendente.
  - `test_snapshot_accepts_private_discrepancy_values`: valores vêm do snapshot e não de constantes.

- [ ] **Passo 2: executar os testes e confirmar falha**
  - Executar: `python -m pytest app_produtividade_diaria/tests/test_models.py -q`
  - Esperado: falha porque os modelos ainda não existem.

- [ ] **Passo 3: implementar os modelos**
  - Definir modelos e enums para categoria e estado de revisão em `models.py`.
  - Tratar datas com `datetime` timezone-aware e campos desconhecidos como opcionais.
  - Não colocar valores históricos reais em defaults, fixtures ou constantes.

- [ ] **Passo 4: executar os testes**
  - Executar o mesmo comando.
  - Esperado: todos os testes de modelos passam.

- [ ] **Passo 5: commit**
  - Commit: `feat: define productivity dashboard data models`.

### Tarefa 2: Preparar a base privada e migrar as séries históricas

**Arquivos:**
- Criar: `app_produtividade_diaria/migrate_history.py`
- Criar: `app_produtividade_diaria/tests/test_migrate_history.py`
- Criar fora do repositório: workbook de importação e planilha nativa do Google Drive

**Interfaces:**
- `select_history_tabs(source_path: Path) -> list[str]`: seleciona `sei`, `Dados_Painel_vFinal`, `Produtividade`, `Produtividade_IC` e `Gestao_Fila`.
- `prepare_history_workbook(source_path: Path, output_path: Path) -> MigrationReport`: cria uma cópia de trabalho com as abas selecionadas e valida os cabeçalhos.

- [ ] **Passo 1: escrever os testes que falham**
  - `test_select_history_tabs_uses_approved_list`: seleciona apenas as cinco abas acordadas, mantendo a ordem.
  - `test_migration_preserves_month_gaps`: meses sem dados continuam vazios.
  - `test_migration_keeps_both_conflicting_series`: valores divergentes permanecem associados às suas versões e fontes.
  - `test_source_workbook_is_unchanged`: a preparação não altera o arquivo original.

- [ ] **Passo 2: executar os testes e confirmar falha**
  - Executar: `python -m pytest app_produtividade_diaria/tests/test_migrate_history.py -q`
  - Esperado: falha porque o migrador ainda não existe.

- [ ] **Passo 3: implementar a preparação local**
  - Usar leitura de workbook para copiar apenas as cinco abas definidas e produzir `MigrationReport` com nomes, cabeçalhos e contagens.
  - Usar fixtures sintéticas nos testes; manter os dados reais apenas no arquivo privado de origem e no Drive.

- [ ] **Passo 4: executar os testes**
  - Executar o mesmo comando.
  - Esperado: abas, lacunas, versões divergentes e arquivo original validados.

- [ ] **Passo 5: criar e conferir a planilha privada**
  - Converter o workbook de preparação para planilha nativa do Google Drive conforme o fluxo de Sheets.
  - Adicionar abas vazias `Mensagens`, `Atividades`, `Relacoes`, `Palavras-chave` e `Auditoria`.
  - Ler de volta metadados e cabeçalhos; confirmar que o ID da nova planilha difere do arquivo original e que o original permanece intacto.

- [ ] **Passo 6: commit**
  - Commit: `feat: prepare historical productivity data migration`.
  - Não adicionar workbook, planilha exportada ou dados reais ao commit.

### Tarefa 3: Validar atividades estruturadas para atualização diária

**Arquivos:**
- Criar: `app_produtividade_diaria/activity.py`
- Criar: `app_produtividade_diaria/tests/test_activity.py`

**Interfaces:**
- `validate_activity_batch(message_id: str, raw_message: str, activity_date: date, rows: list[dict]) -> list[ActivityRecord]`.
- O assistente interpreta a mensagem e envia linhas estruturadas; a função valida e preserva a mensagem original, sem chamar outro modelo ou inferir valores.

- [ ] **Passo 1: escrever os testes que falham**
  - `test_one_message_can_create_multiple_activity_rows`: cada item distinto gera uma linha com o mesmo id de mensagem.
  - `test_missing_date_uses_supplied_activity_date`: usa a data informada pelo fluxo de atualização.
  - `test_missing_quantity_is_not_estimated`: quantidade ausente permanece vazia.
  - `test_recorded_at_uses_sao_paulo_timezone`: o instante do registro mantém o fuso America/Sao_Paulo.
  - `test_raw_message_is_retained_verbatim`: texto de origem não é reescrito.

- [ ] **Passo 2: executar os testes e confirmar falha**
  - Executar: `python -m pytest app_produtividade_diaria/tests/test_activity.py -q`
  - Esperado: falha porque a validação ainda não existe.

- [ ] **Passo 3: implementar validação e serialização**
  - Validar cada linha com os modelos da Tarefa 1.
  - Manter resultado, quantidade, unidade, processo e palavras-chave ausentes como ausentes.
  - Retornar erro explícito para ids ou datas inválidas, sem descartar silenciosamente a mensagem.

- [ ] **Passo 4: executar os testes**
  - Executar o mesmo comando.
  - Esperado: todos os casos de atividade passam.

- [ ] **Passo 5: commit**
  - Commit: `feat: validate daily activity records`.

### Tarefa 4: Calcular produção, fila, IC e produtividade temporal

**Arquivos:**
- Criar: `app_produtividade_diaria/metrics.py`
- Criar: `app_produtividade_diaria/tests/test_metrics.py`

**Interfaces:**
- `build_daily_productivity(activities: pd.DataFrame, dates: pd.DataFrame) -> pd.DataFrame`: manifestações e carga por dia ativo, dia útil de calendário e dia corrido.
- `build_monthly_flow(history: pd.DataFrame) -> pd.DataFrame`: entradas, conclusões, saldo e estoque sem preencher lacunas.
- `classify_queue_age(days: int | None) -> str`: retorna uma das cinco faixas especificadas ou “sem dado”.
- `build_deadline_horizon(processes: pd.DataFrame, as_of: date) -> pd.DataFrame`: identifica prazos confiáveis a vencer em 15, 30 ou 60 dias.
- `build_ic_timeline(ics: pd.DataFrame) -> pd.DataFrame`: calcula retorno previsto em emissão + 60 dias e substitui previsão pela data real quando disponível.

- [ ] **Passo 1: escrever os testes que falham**
  - `test_daily_rates_use_active_weekday_and_calendar_denominators`: mantém os três denominadores distintos.
  - `test_missing_month_remains_missing`: mês ausente não vira zero.
  - `test_queue_age_boundary_values`: cobre 149, 150, 164, 165, 179, 180, 239 e 240 dias.
  - `test_deadline_horizon_ignores_missing_due_date`: prazo ausente resulta em “sem dado”.
  - `test_actual_ic_response_replaces_plus_60_forecast`: retorno real substitui a previsão.

- [ ] **Passo 2: executar os testes e confirmar falha**
  - Executar: `python -m pytest app_produtividade_diaria/tests/test_metrics.py -q`
  - Esperado: falha porque as funções ainda não existem.

- [ ] **Passo 3: implementar os cálculos**
  - Usar pandas para preservar índices mensais ausentes e separar medidas de fluxo, estoque e produtividade temporal.
  - Aplicar os limites de faixa exatamente como descritos na especificação.
  - Calcular horizontes de prazo somente a partir de datas válidas.

- [ ] **Passo 4: executar os testes**
  - Executar o mesmo comando.
  - Esperado: denominadores, lacunas, faixas, horizontes e ICs validados.

- [ ] **Passo 5: commit**
  - Commit: `feat: calculate productivity and queue metrics`.

### Tarefa 5: Construir vínculos e grafo de processos

**Arquivos:**
- Criar: `app_produtividade_diaria/relationships.py`
- Criar: `app_produtividade_diaria/tests/test_relationships.py`

**Interfaces:**
- `build_process_relations(processes: pd.DataFrame, declared: list[ProcessRelation]) -> list[ProcessRelation]`: combina vínculos declarados com associações de mesmo CAR.
- `build_process_graph(relations: list[ProcessRelation]) -> dict`: produz nós e arestas para a visualização.

- [ ] **Passo 1: escrever os testes que falham**
  - `test_same_car_creates_only_same_car_relation`: CAR idêntico sustenta somente o vínculo “mesmo CAR”.
  - `test_empty_or_conflicting_car_does_not_create_relation`: CAR ausente ou conflitante não cria aresta confirmada.
  - `test_unsupported_declared_relation_remains_pending`: vínculo declarado sem evidência fica pendente.
  - `test_graph_keeps_evidence_and_confirmation_state`: cada aresta conserva referência e estado.

- [ ] **Passo 2: executar os testes e confirmar falha**
  - Executar: `python -m pytest app_produtividade_diaria/tests/test_relationships.py -q`
  - Esperado: falha porque a construção do grafo ainda não existe.

- [ ] **Passo 3: implementar relações e grafo**
  - Usar identificadores normalizados de processo.
  - Registrar vínculo por CAR com o valor de CAR como evidência; não inferir causalidade, derivação ou dependência.
  - Marcar relações sem evidência como pendentes.

- [ ] **Passo 4: executar os testes**
  - Executar o mesmo comando.
  - Esperado: somente relações sustentadas aparecem como confirmadas.

- [ ] **Passo 5: commit**
  - Commit: `feat: model evidence-backed process relationships`.

### Tarefa 6: Renderizar o painel e os lembretes

**Arquivos:**
- Criar: `app_produtividade_diaria/render.py`
- Criar: `app_produtividade_diaria/templates/index.html`
- Criar: `app_produtividade_diaria/static/dashboard.css`
- Criar: `app_produtividade_diaria/static/dashboard.js`
- Criar: `app_produtividade_diaria/tests/test_render.py`

**Interfaces:**
- `render_dashboard(snapshot: DashboardSnapshot, output_dir: Path) -> Path`: escreve página estática e retorna o caminho de `index.html`.
- `build_chart_payload(snapshot: DashboardSnapshot) -> dict`: prepara séries Plotly e arestas do grafo para a página.

- [ ] **Passo 1: escrever os testes que falham**
  - `test_keyword_card_precedes_discrepancy_card`: verifica a ordem dos cartões no HTML.
  - `test_discrepancy_values_come_from_snapshot`: usa valores sintéticos diferentes por versão e confirma que a página renderiza os valores recebidos.
  - `test_discrepancy_card_shows_source_and_review_status`: mostra qual série alimenta os gráficos e “Aguardando conferência da fonte primária”.
  - `test_relation_graph_exposes_evidence_and_pending_state`: arestas confirmadas e pendentes são distinguíveis e abrem evidência.
  - `test_dashboard_layout_is_mobile_responsive`: exige viewport responsivo e layout fluido.

- [ ] **Passo 2: executar os testes e confirmar falha**
  - Executar: `python -m pytest app_produtividade_diaria/tests/test_render.py -q`
  - Esperado: falha porque o renderer ainda não existe.

- [ ] **Passo 3: implementar a página estática**
  - Agrupar as áreas em Hoje, Produção e fila, e Processos relacionados.
  - Renderizar as séries quantitativas com Plotly.
  - Exibir etiquetas de palavras-chave e, logo abaixo, cartão destacado “Divergência pendente — jan/2026”, com texto e sinal visual acessível.
  - Ler valores da divergência exclusivamente do snapshot privado.

- [ ] **Passo 4: executar os testes**
  - Executar o mesmo comando.
  - Esperado: ordem, valores dinâmicos, evidências, estado pendente e responsividade validados.

- [ ] **Passo 5: commit**
  - Commit: `feat: render private productivity dashboard`.

### Tarefa 7: Empacotar, publicar em privado e documentar atualização diária

**Arquivos:**
- Criar: `app_produtividade_diaria/build.py`
- Criar: `app_produtividade_diaria/.openai/hosting.json`
- Criar: `app_produtividade_diaria/.gitignore`
- Criar: `app_produtividade_diaria/README.md`
- Criar: `app_produtividade_diaria/tests/test_build.py`

**Interfaces:**
- `build_site(input_path: Path, output_dir: Path) -> Path`: valida snapshot, calcula métricas, renderiza a página e retorna o diretório estático.
- CLI: `python -m app_produtividade_diaria.build --input <snapshot-privado.json> --output <dist>`.

- [ ] **Passo 1: escrever os testes que falham**
  - `test_build_writes_index_and_private_payload`: saída contém página e dados necessários para exibição.
  - `test_private_snapshot_is_ignored_by_git`: arquivos de snapshot e saída de build não são rastreados no repositório.
  - `test_build_rejects_invalid_snapshot`: erro inclui o campo inválido e mantém o arquivo fonte intacto.

- [ ] **Passo 2: executar os testes e confirmar falha**
  - Executar: `python -m pytest app_produtividade_diaria/tests/test_build.py -q`
  - Esperado: falha porque o comando de build ainda não existe.

- [ ] **Passo 3: implementar build e exclusões**
  - Fazer o build consumir snapshot JSON preparado a partir da planilha privada; não adicionar credenciais Google ao código.
  - Escrever saída apenas em `dist/`; excluir snapshots, exports, arquivos temporários e build local do Git.
  - Documentar no README o fluxo: registrar atividades na planilha, ler de volta, gerar snapshot privado, executar build e atualizar publicação privada.

- [ ] **Passo 4: executar os testes**
  - Executar o mesmo comando.
  - Esperado: saída válida, exclusões aplicadas e dados inválidos rejeitados.

- [ ] **Passo 5: commit**
  - Commit: `feat: package private dashboard site`.

- [ ] **Passo 6: publicar e conferir**
  - Criar uma única publicação privada para a pasta do painel, mantendo acesso somente ao proprietário.
  - Publicar o arquivo estático gerado e verificar o estado final da implantação, URL, acesso privado e cartões na ordem aprovada.
  - Confirmar que o pacote publicado contém os dados de exibição atualizados e o repositório público contém somente código.

### Tarefa 8: Verificação integrada do fluxo diário

**Arquivos:**
- Criar: `app_produtividade_diaria/tests/test_end_to_end.py`
- Modificar: `app_produtividade_diaria/README.md`

**Interfaces:**
- Usa: `validate_activity_batch`, `build_daily_productivity`, `build_monthly_flow`, `build_process_relations`, `render_dashboard` e `build_site`.
- Produz: uma verificação integrada documentada do caminho mensagem → planilha → snapshot privado → site privado.

- [ ] **Passo 1: escrever teste integrado com dados sintéticos**
  - `test_daily_update_renders_activity_metrics_relations_and_reminders`: entrada sintética gera atividade, métricas, aresta com evidência, cartão de palavras-chave e cartão de divergência dinâmico.

- [ ] **Passo 2: executar teste integrado e confirmar falha**
  - Executar: `python -m pytest app_produtividade_diaria/tests/test_end_to_end.py -q`
  - Esperado: falha até que todos os componentes estejam ligados.

- [ ] **Passo 3: integrar interfaces**
  - Conectar validação, cálculos, relações e rendering no caminho de build.
  - Manter atualização da planilha e publicação como operações separadas, para que falha na publicação não reverta um registro salvo.

- [ ] **Passo 4: executar a suíte completa**
  - Executar: `python -m pytest app_produtividade_diaria/tests -q`
  - Esperado: todos os testes passam.

- [ ] **Passo 5: executar uma atualização privada de ponta a ponta**
  - Usar um lote sintético para verificar escrita e leitura da estrutura da planilha e build privado.
  - Confirmar a contagem exata de registros, a atualização do site, ausência de duplicidade, privacidade do site e ausência de dados no GitHub.
  - Documentar a validação no README sem copiar registros reais para o repositório.

- [ ] **Passo 6: commit**
  - Commit: `test: verify daily productivity dashboard workflow`.

---

## Auto-revisão do plano

- Cada parte da especificação tem uma tarefa: fonte histórica (Tarefa 2), mensagens e registros (Tarefas 1 e 3), indicadores (Tarefa 4), relações com evidências (Tarefa 5), cartões e site responsivo (Tarefa 6), privacidade/publicação/atualização (Tarefas 7 e 8).
- Interfaces são definidas uma vez e reutilizadas sem nomes alternativos.
- As cinco classes de falha do foco de revisão têm testes nomeados nas tarefas proprietárias.
- Testes usam dados sintéticos; dados reais permanecem no Drive e em publicação privada.
- A ordem é proporcional: contratos, migração, cálculos, relações, interface, publicação e integração.
