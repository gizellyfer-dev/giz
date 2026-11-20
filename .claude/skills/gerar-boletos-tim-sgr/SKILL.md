---
name: "gerar-boletos-tim-sgr"
description: "Gerar 2ª via (boleto) de faturas TIM vencidas no Portal de Parcelamentos/SGR, abrindo cada PDF numa aba, mantendo um mapa nome-do-PDF → cliente/fatura e renomeando os PDFs baixados. Use quando a usuária pedir para gerar boletos, 2ª via ou recibos SGR dos clientes em aberto (aba Faturas · Radar da Plataforma Mobile ou planilha)."
---

# Gerar boletos TIM (Portal SGR / Parcelamentos)

Use quando a usuária pedir para gerar boletos (2ª via) das faturas TIM em aberto de clientes da fila de cobrança. Fluxo feito com Claude in Chrome na aba do Portal de Parcelamentos (portalparcelamento.timbrasil.com.br/pparcelamentos/appSgr/...).

## De onde vem a fila
Normalmente da aba **Faturas · Radar** da Plataforma Mobile (`https://claude.ai/artifact/Wi1Cpdb1t435rshHuFRVRL`), coleção `registros`, documentos `lote-1` a `lote-4` (campo `itens`). Cada item: `cnpj`, `nome`, `status`, `faturas[]` com `custCode`, `numero`, `vencimento` (aaaa-mm-dd), `valor`, `desativado`. Se a consulta tiver mais de um ou dois dias, rode antes a skill `consulta-faturas-tim` para atualizar.

Fila = itens `em_aberto`, faturas com `desativado=false` e `vencimento < hoje`. Uma geração por fatura. Ordene por cliente/CustCode/vencimento e salve a fila em CSV.

## Regras da usuária
- Só gerar boleto de faturas JÁ VENCIDAS (vencimento < hoje). Fatura ainda não vencida: pular.
- Cliente com linha "Cliente Desativado": NÃO gerar boleto.
- Ir só até a tela de impressão: ao confirmar, o PDF abre em outra aba; deixar a aba aberta e seguir. A usuária baixa os PDFs e fecha as abas.
- NUNCA usar SMS/E-MAIL (enviam ao cliente). Só "IMPRESSÃO ONLINE".
- Login/senha/token: a usuária digita. Se o Chrome bloquear a aba, avisar e esperar ela logar de novo.
- A cada ~20 boletos, parar e pedir que ela baixe e feche as abas de PDF (muitas abas travam o portal e incham o contexto).

## Ledger (obrigatório)
CSV (separador ;): `arquivo_pdf;cliente;cnpj;custcode;fatura;valor;vencimento`. O nome do PDF é `GeraSGR_<Nº Sequência do recibo>_<aaaammddhhmmss>.pdf` e aparece como título da aba nova (o "Tab Context" que volta de cada ação já lista as abas). Entregar o CSV com SendUserFile a cada checkpoint e no final.

## Entrar no portal
1. Pelo PAC (aba do grupo do Claude): clicar em **PORTALPARCELAMENTO** — a aba nova entra no grupo.
2. Tela "Selecione o Contexto": marcar **TIM** e **Selecionar**. Sem isso o fluxo quebra.
3. Depois disso dá para ir direto por URL: `.../appSgr/gerarConsultar/filtroPesquisa.xhtml` (esperar ~8 s a página assentar).

## Fluxo por fatura (método que funcionou em 19/11/2026)
IDs da tela de busca: campo CustCode `form1:codcliGSM`, select do motivo `form1:motivoGSM_input` (valor `2` = Segunda Via de Conta), botão `form1:btBuscarGSM`.

1. **CustCode com digitação real.** Focar o campo via JS (`value=''; focus()`) e usar `computer type`. Preencher `value` só por JS faz o portal responder "Código do cliente inválido. Por favor, informe apenas números e pontos."
2. Motivo por JS: `select.value='2'` + evento `change`. Buscar: `click()` no botão (pode ser por JS). Esperar ~8 s → `selecionarFatura.xhtml`.
3. **Escolher a fatura pela linha mais interna**: `tr` que contém o número da fatura E não contém outro `tr` (a tabela é aninhada; pegar o primeiro `tr` que "contém" o número seleciona a linha errada — aconteceu). Clicar `.ui-radiobutton-box` dessa linha, conferir que só 1 rádio está marcado e clicar o botão "Confirmar" (JS serve).
4. `selMetodoEnvio.xhtml`: marcar o 1º rádio (IMPRESSÃO ONLINE) clicando `.ui-radiobutton-box`, conferir `[true,false,false]`, Confirmar.
5. `confirmaRecibo.xhtml`: conferir no texto `Fatura: <número>` e `Cliente: <CustCode> ` (com espaço no fim, para não casar com CustCode maior). Se não bater, sair para a home e NÃO confirmar.
6. **O Confirmar final tem de ser clique real** (por JS o PDF não abre). Rolar ao fim (`scrollTo(0, scrollHeight)`) e clicar ≈(651,551) no viewport 1536x682. Esperar ~8 s; a aba `GeraSGR_...pdf` aparece.

Tudo cabe num único `browser_batch` por fatura (~45 s). Mantenha as checagens: elas evitaram um boleto da fatura errada.

## Renomear os PDFs baixados
Se houver acesso aos arquivos do computador (Claude Code), dá para renomear em `%USERPROFILE%\Downloads` com o ledger: `CLIENTE - CustCode X - Fatura Y - venc dd-mm-aaaa - R$ valor.pdf` (trocar `\/:*?"<>|` por `-`). Arquivo aberto em outro programa dá "em uso": pedir para fechar e repetir. Sem acesso a arquivos, entregar o ledger para ela renomear.

## Aprendizados da tarde de 19/11/2026
- CustCode sem teclado: motivo por JS, esperar ~3 s, depois `e.focus(); e.select(); document.execCommand('insertText', false, cc); e.blur()`, esperar 1 s e `click()` no Buscar por JS. Funciona mesmo com a usuária usando outra aba. Já `value=` com eventos sintéticos dá "inválido".
- Num batch, `throw` dentro do javascript_tool interrompe o resto: use isso para travar o Confirmar final quando a conferência falhar.
- Com muitas abas de PDF abertas e a usuária usando outra aba, o Chrome congela ou troca o ID da aba do portal ("renderer frozen", "not in tab group"). Faça um boleto por batch, confira o ID com tabs_context e peça para deixar a aba do portal na frente e baixar/fechar os PDFs.
- A usuária prefere baixar os PDFs ela mesma: não clicar no ícone de download (abre "Salvar como").

## Problema em aberto (19/11/2026)
Depois de a usuária relogar no PAC no meio do lote, o portal passou a voltar para "Seja bem-vindo ao Portal SGR" ao confirmar o método de envio — com qualquer cliente, mesmo com cliques reais do Claude e após novo login e seleção de contexto. Com a usuária clicando à mão funcionava. Causa não descoberta. Se acontecer: parar, avisar, e pedir para observar (read_network_requests) a usuária fazendo um boleto para comparar.
