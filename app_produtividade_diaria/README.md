# Painel pessoal de produtividade

O código do painel é público. Os dados individuais permanecem na planilha privada do Google Drive e só entram na cópia HTML gerada para uso pessoal.

Para gerar uma cópia estática a partir de um extrato privado revisado:

```bash
python -m app_produtividade_diaria.build_personal_preview private_data/site-data.json painel_produtividade_interativo.html
```

O extrato contém `monthly` em ordem cronológica, `dailyActivities`, `relationships` e as demais séries do painel. Cada atividade usa `activityDate` (AAAA-MM-DD), `category`, `description`, `processIds` (lista), `outcome` e `reviewState`. Cada relação usa `processA`, `processB`, `relationType`, `evidence`, `evidenceReference` e `confirmationState` (`pending` ou `confirmed`). Relações confirmadas exigem evidência e referência; menções textuais sem confirmação ficam em `candidateMentions`.

As abas `Mensagens`, `Atividades`, `Processos` e `Relacoes` da planilha são as fontes operacionais. Ao receber atividades na conversa, preserve a mensagem original, registre as linhas estruturadas no Drive, releia as abas e gere novamente a cópia privada. Este HTML é somente leitura e não atualiza automaticamente a planilha.

Nunca publique `private_data/`, exportações, pacotes gerados nem arquivos `painel_produtividade_*.html` no repositório público.
