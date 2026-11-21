<!-- README | espelho do GitHub | versão 1.0.0 | 07/11/2026 17:25 (-03) | criação original (Claude, para Lucas Tavares) -->
# Espelho do GitHub no HDD de 12TB

Mantém um clone de cada repositório do GitHub em `/mnt/12TB_3.5/github/<dono>/<repo>` e sincroniza a cada 10 minutos (timer do systemd de usuário). Não faz parte do tema da tela e não entra nos ZIPs.

| Situação do repositório | O que o script faz |
|---|---|
| não existe no disco | clona |
| atrás do GitHub | avança (`merge --ff-only`) |
| à frente (commits locais) | envia (`push`) |
| mudanças sem commit, divergência, HEAD solto ou ramo sem upstream | não mexe e registra AVISO |

Nunca faz merge com conflito, rebase, reset nem push forçado. Sincroniza só o ramo que está em uso em cada clone. Se o disco não estiver montado, não faz nada.

## Instalar

Pré-requisito: `gh` instalado e com login (`gh auth login`), feito pelo próprio usuário.

```bash
pc/espelho-github/instalar.sh
```

Configuração em `~/.config/espelho-github.conf`. Log em `~/.local/state/espelho-github/sincronizar.log`, com data e hora em cada linha. Para sincronizar na hora: `systemctl --user start espelho-github.service`.
