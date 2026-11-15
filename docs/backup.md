<!-- docs/backup.md | versão 1.0.0 | 15/11/2026 15:35 (-03) | criação original (Claude, para Lucas Tavares). Fonte: código do GAMMA EPSILON (collectors.Backups, viewmodel.backup_vm, estilos/epsilon_telas.py) e as rotinas do repositório lstavares84/debian, pasta discos (LEIA-ME 1.5.0 de 14/11/2026). -->
# Backups na tela (GAMMA EPSILON)

O GAMMA EPSILON mostra as rotinas de backup do PC em duas telas:

- **BACKUPS**, uma das telas da rotação: para cada rotina, o estado (`AGENDADA` ou `RODANDO`), a última execução e a duração, o resultado e a próxima execução.
- **Andamento**, que entra no lugar da rotação enquanto uma rotina roda e sai quando ela termina. Só um alerta vermelho passa na frente dela.

## De onde vêm os dados

Cada rotina é uma unidade do systemd com timer, do sistema ou da sessão do usuário. Elas são configuradas em `backup.rotinas` no `config.yaml` (veja a [configuração](configuracao.md)). O padrão são as três rotinas do repositório `lstavares84/debian`:

| Rótulo | Unidade | Onde roda | O que faz |
|---|---|---|---|
| DISCOS → 12TB | `sincronizar-discos` | sistema (root), todo dia às 03:00 | espelha as pastas do 2TB e do 4TB no 12TB com rsync |
| FOTOS → ARCHER | `sincronizar-sessao` | sessão do usuário, uma vez por dia | copia as Fotos para o NVMe ligado ao Archer |
| GITHUB | `espelhar-github` | sessão do usuário, de hora em hora | GitHub → 4TB → 12TB → GitHub |

Uma unidade que não existe no PC é ignorada. A cada 5 s o tema lê:

1. Do `systemctl show` (com `--user` nas rotinas da sessão): se a rotina está rodando, o início e o fim da última execução, o resultado e, no timer, a próxima execução.
2. Do journal, a última linha `Fim | ...` que as rotinas escrevem ao terminar. Por exemplo `Fim | sincronizadas: 11 | puladas: 0 | com falha: 0` ou, no `espelhar-github`, `Fim | repositórios: 20 | ... | enviados: 0 | ... | erros: 0`. Falha ou erro deixa o resultado com fundo âmbar. O backup não entra na saúde do PC: não conta no N1 nem no N2.
3. Enquanto a rotina roda, o **arquivo de andamento**, descrito abaixo.

Sem o arquivo de andamento, a tela de andamento mostra só há quanto tempo a rotina roda, com uma barra listrada.

## Arquivo de andamento

A rotina grava o andamento num arquivo JSON pequeno enquanto roda. Ele deve ser regravado a cada poucos segundos, sempre por troca atômica (grava num `.tmp` e renomeia). O tema só usa o arquivo se ele tiver sido atualizado nos últimos 90 s e tiver `"estado": "rodando"`.

| Rotina | Onde gravar |
|---|---|
| do sistema (root) | `/run/gamma-backup/<unidade>.json`, com a pasta em modo 755 e o arquivo em 644, para o usuário conseguir ler |
| da sessão do usuário | `$XDG_RUNTIME_DIR/gamma-backup/<unidade>.json` (normalmente `/run/user/1000/gamma-backup/`) |

As pastas podem ser trocadas em `backup.andamento`. Os campos:

```json
{
  "versao": 1,
  "rotina": "sincronizar-discos",
  "estado": "rodando",
  "inicio": 1794722400,
  "atual": 1794722890,
  "pasta": "Fotos",
  "origem": "/mnt/2TB_3.5/Fotos",
  "destino": "/mnt/12TB_3.5/Fotos",
  "indice": 2,
  "total": 11,
  "pct": 42.0,
  "bytes": 12400000000,
  "velocidade": 35200000,
  "restante_s": 751
}
```

| Campo | Significado |
|---|---|
| `estado` | `rodando` enquanto copia; `terminado` no fim (ou apagar o arquivo) |
| `inicio`, `atual` | início da rotina e hora desta gravação, em segundos desde 1970 (`date +%s`) |
| `pasta`, `origem`, `destino` | pasta sendo copiada agora (a tela mostra `pasta`) |
| `indice`, `total` | número da pasta atual e total de pastas da execução |
| `pct` | percentual da pasta atual (o `rsync --info=progress2` informa) |
| `bytes` | bytes já transferidos na pasta atual |
| `velocidade` | bytes por segundo |
| `restante_s` | tempo restante estimado da pasta atual, em segundos |

Campos que a rotina não souber podem faltar: a tela mostra `N/D` no lugar.

## Como uma rotina com rsync pode gravar o arquivo

Esboço para o laço de pastas do `sincronizar-discos.sh` (criação original, ainda não aplicado no repositório `debian`). O `rsync --info=progress2 --no-inc-recursive` escreve linhas como `1,234,567  42%  35.20MB/s  0:12:31`. Com `stdbuf` e `tr '\r' '\n'`, cada atualização vira uma linha:

```bash
AND_DIR=/run/gamma-backup; mkdir -p "$AND_DIR"; chmod 755 "$AND_DIR"
AND="$AND_DIR/sincronizar-discos.json"
andamento() {   # estado pasta indice total pct bytes velocidade restante_s
    printf '{"versao":1,"rotina":"sincronizar-discos","estado":"%s","inicio":%s,"atual":%s,"pasta":"%s","indice":%s,"total":%s,"pct":%s,"bytes":%s,"velocidade":%s,"restante_s":%s}\n' \
        "$1" "$INICIO" "$(date +%s)" "$2" "$3" "$4" "$5" "$6" "$7" "$8" > "$AND.tmp" && chmod 644 "$AND.tmp" && mv "$AND.tmp" "$AND"
}
# dentro do laço, no lugar da chamada ao rsync:
stdbuf -oL rsync "${opcoes[@]}" --info=progress2 --no-inc-recursive "$origem/" "$destino/" 2>"$erros" \
  | stdbuf -oL tr '\r' '\n' | while read -r b p v r _; do
        [[ "$p" == *% ]] || continue
        andamento rodando "$(basename "$origem")" "$i" "${#PARES[@]}" "${p%\%}" "${b//,/}" "0" "0"
    done
rc=${PIPESTATUS[0]}
# no fim da rotina:
andamento terminado "" 0 0 100 0 0 0
```

A velocidade e o tempo restante do exemplo ficam em 0. Para preenchê-los, converta `35.20MB/s` para bytes por segundo e `0:12:31` para segundos.
