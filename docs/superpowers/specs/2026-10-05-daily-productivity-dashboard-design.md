# Painel diário de produtividade — especificação de desenho

Data: 2026-10-05  
Status: desenho validado pelo usuário; implementação ainda não iniciada.

## Objetivo

Permitir que o usuário envie atividades diárias nesta conversa, mantenha um histórico estruturado em uma base privada no Google Drive e consulte um site privado com indicadores de produção, fila e relações entre processos. O repositório público do GitHub contém o código do painel e dos gráficos em Python.

## Decisões e restrições

- A base canônica fica em uma planilha privada do Google Drive.
- O site é uma publicação privada e responsiva, adequada ao uso em computador e celular.
- O repositório público `cassiostrassburger/dashboards` guarda código genérico, sem registros, identificadores de processos ou cópias da base.
- Os gráficos quantitativos são gerados com Python.
- O site recebe uma versão privada dos dados necessários para exibição e é atualizado após cada registro diário processado.
- A série histórica é cumulativa. Correções permanecem rastreáveis; lacunas permanecem como lacunas.
- Pontos de carga são experimentais e não representam horas.
- Informação Complementar (IC) é etapa do fluxo. A previsão de retorno é emissão + 60 dias; quando há resposta, a data real substitui a previsão.
- Nenhuma relação entre processos é apresentada como confirmada sem evidência registrada.

## Fontes e carga inicial

Criar uma nova base no Drive e carregar as abas relevantes do arquivo de produtividade existente:

- `sei`: eventos e manifestações por processo, CAR, tipo e data.
- `Dados_Painel_vFinal`: série canônica usada pelos painéis.
- `Produtividade`: carga e manifestações.
- `Produtividade_IC`: carga refinada e indicadores de IC.
- `Gestao_Fila`: entradas, saídas, saldo, estoque e envelhecimento.

O arquivo de origem permanece preservado. A divergência histórica de janeiro deve ser apresentada pelo site a partir dos valores da base privada, sem hardcode no repositório. O cartão identifica os valores das duas séries, informa qual alimenta os gráficos e mostra a situação da conferência com a fonte primária.

## Estrutura da base

### Registro diário

Cada envio mantém o texto original e a data/hora do registro no fuso America/Sao_Paulo. O conteúdo é desdobrado em uma linha por atividade, ligada ao envio que lhe deu origem.

Campos estruturados: data da atividade, categoria, descrição, processo ou processos quando informados, resultado, quantidade e unidade quando informadas, palavras-chave, status de revisão e referência ao registro original. Informação ausente fica vazia ou marcada como pendente, sem estimativa.

Categorias iniciais: análise de processo, geoespacial, CAR/Reserva Legal, vistoria, redação/revisão, informação complementar, coordenação/reunião e outros. A lista pode ser ampliada conforme os registros reais.

### Processos e relações

A aba `Relacoes` usa uma linha por vínculo, com processo A, processo B, tipo de vínculo, evidência/documento, origem da informação, data de registro e situação da confirmação.

Tipos iniciais: mesmo CAR, mesmo imóvel, mesmo empreendimento, origem/vinculação, complementar, retificação/recurso e outro. Um CAR igual pode sustentar um vínculo do tipo “mesmo CAR”; vínculos de outra natureza precisam de evidência própria. Vínculos pendentes são visualmente distintos dos confirmados.

### Auditoria e palavras-chave

Uma trilha de alterações preserva correções e registros substituídos, com data, motivo e referência à entrada original. A lista de palavras-chave é editável e começa com inventário florestal, fauna, compensação ambiental e Reserva Legal.

## Organização do site

1. **Hoje**: atividades do período selecionado, resultados e filtros por data, categoria e processo.
2. **Produção e fila**: gráficos históricos e indicadores de carga, fluxo, estoque, IC e envelhecimento.
3. **Processos relacionados**: grafo navegável e lista de vínculos com tipo, evidência e confirmação.

No resumo do painel, um cartão **Palavras-chave** exibe etiquetas dos temas cadastrados. Logo abaixo, um cartão visualmente distinto, com título **“Divergência pendente — jan/2026”**, mostra os valores históricos carregados do Drive, destaca a série usada nos gráficos e apresenta o status **“Aguardando conferência da fonte primária”**. O status também é escrito em texto, sem depender apenas de cor.

Filtros gerais: período, processo, categoria, unidade/NAR e tipo de relação. Os indicadores não disponíveis para o filtro escolhido são marcados como “sem dado”.

## Indicadores prioritários

- Manifestações e carga refinada por mês.
- Manifestações e carga por dia ativo, por dia útil de calendário e por dia corrido.
- Entradas, conclusões, saldo e estoque de processos.
- Carga e processos em andamento por etapa e NAR.
- Envelhecimento da fila em dias, com faixas: <150, 150–164, 165–179, 180–239 e ≥240.
- Projeções de prazo/risco em 15, 30 e 60 dias, somente quando houver prazo e datas confiáveis.
- ICs emitidas, retorno previsto em 60 dias, retornos reais e ciclos de retrabalho.
- Distribuição de ICs por tema e relação entre complexidade e carga experimental.

Retrabalho/qualidade aparece como visão complementar quando houver dados suficientes. Geoespacial, inventário, fauna e sensoriamento remoto podem ser categorias ou palavras-chave das atividades. Análises técnicas desses temas e análise de sobrevivência ficam fora do painel diário inicial.

## Fluxo de atualização

1. O usuário envia as atividades concluídas na conversa.
2. O assistente preserva o texto e estrutura as atividades sem completar lacunas por inferência.
3. O assistente atualiza a planilha, registra vínculos de processo somente com base informada e atualiza os indicadores.
4. O código Python gera os gráficos e a publicação privada do site é atualizada.
5. O assistente informa o que foi registrado e sinaliza campos pendentes ou conflitos.

A planilha é a fonte canônica. Se a atualização do site falhar, os dados permanecem registrados no Drive, a página mostra a data da última publicação e a falha é informada para nova tentativa.

## Privacidade e qualidade

- A planilha e a publicação do site mantêm acesso privado ao proprietário.
- O histórico de atividades e relações não é incorporado ao repositório público.
- Nenhum mês sem dado é convertido em zero.
- Toda relação de processo exibe sua evidência e estado de confirmação.
- O cartão da divergência lê os valores da base privada, sem gravá-los no código público.
- O painel separa atividade realizada, etapa do processo e resultado final.
- A importação inicial e cada atualização são verificadas quanto a duplicidade, contagem de linhas, atualização dos gráficos e preservação do histórico.

## Critérios de aceite

- Um envio diário gera registro original preservado e linhas estruturadas correspondentes.
- O site apresenta a atividade no período correto e atualiza os filtros e gráficos afetados.
- Relações entre processos podem ser abertas e verificadas por evidência.
- O cartão de palavras-chave aparece acima do cartão destacado da divergência.
- O cartão da divergência identifica as duas séries, a série usada nos gráficos e o status de conferência.
- Dados ausentes aparecem como “sem dado”; valores e relações sem base não são inventados.
- Os dados permanecem fora do repositório público.
