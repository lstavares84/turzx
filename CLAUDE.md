<!-- CLAUDE.md | GAMMA TUS-35 | versão 1.0.0 | 07/11/2026 15:55 (-03) | criação original (Claude, para Lucas Tavares). Fonte: documento de transferência do projeto de 07/11/2026. -->

# Instruções para agentes de IA

Este repositório é o GAMMA TUS-35, tema de monitoramento para a tela USB TURZX / Turing de 3,5". Antes de mudar qualquer coisa, leia o [README](README.md), a [arquitetura](docs/arquitetura.md), o [desenvolvimento](docs/desenvolvimento.md), as [decisões e lições](docs/decisoes-e-licoes.md) e o [roteiro](docs/roteiro.md).

## Comunicação com o Lucas

- Responder só em português do Brasil, com acentuação correta, inclusive em arquivos, comentários e logs.
- Nunca usar o travessão longo em nenhum texto, código, comentário ou commit. Use vírgula, dois-pontos ou hífen.
- Data e hora no início de cada interação; data e hora (`dd/mm/aaaa HH:MM:SS`, America/Sao_Paulo) em toda linha de log ou saída.
- Código e prompts em blocos de código. Em revisões de arquivo, comentário de controle de versão no topo (nome, versão, data e hora, autoria).
- Emoji ⚠️ antes de toda ação manual que o Lucas precise fazer.
- Citar as fontes e declarar quando o conteúdo é criação original.
- Ao escrever um prompt para outra plataforma, indicar modelo, nível de esforço e um nome sugerido para o chat.
- Respostas curtas e diretas, sem abuso de listas e negrito.
- Nunca pedir, receber ou manipular tokens ou senhas.

## Regras de trabalho

- Não inventar fatos sobre o hardware. Faltando informação, pedir a saída de um comando somente leitura.
- Mostrar toda modificação visual ou de código do tema na matriz de prévias em PNG (4 versões x 3 estados), gerada por `construir/matriz_previas.py`.
- Quando a sessão roda no PC do Lucas (existe `~/turing-smart-screen-linux`), toda edição termina assim: autoteste e matriz verdes, envio à tela (com autorização, pelo `construir/aplicar-na-tela.sh delta`, o estilo em uso), commit e push. Enviar a versão para a tela física (`construir/aplicar-na-tela.sh`, `instalar-gamma.sh` ou qualquer instalação) só com autorização explícita do Lucas no chat, a cada envio: perguntar e esperar um sim claro.
- Seguir os critérios de pronto de [docs/desenvolvimento.md](docs/desenvolvimento.md): autoteste verde, prévias sem problema de layout, instalação do zero com usuário comum, SemVer e CHANGELOG atualizados.
- Pacotes enxutos: nada que não seja essencial entra nos ZIPs.
- ZIPs são artefatos de lançamento, não vão para o Git.
