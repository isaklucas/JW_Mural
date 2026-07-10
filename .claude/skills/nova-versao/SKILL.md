---
name: nova-versao
description: Publica uma nova versão do JW Mural para os usuários receberem via auto-update. Bumpa VERSION.txt, builda o instalador (PyInstaller + Inno Setup) e cria a GitHub Release com o Setup_JW_Mural.exe anexado. Use quando o usuário pedir para "versionar", "criar nova versão", "lançar/publicar release", "subir atualização" ou similar.
---

# Publicar nova versão do JW Mural

> **Como o projeto funciona:** a fonte de verdade é `docs/` (comece por
> `docs/AGENTS.md`; build/versionamento em `docs/06-Build-e-Instalador.md`).
> Consulte antes de mexer no pipeline e mantenha atualizado.

Pipeline de release. O app instalado checa `releases/latest` no GitHub a cada boot
(`src/util/updater.py`) e baixa o asset `Setup_JW_Mural.exe` se a tag remota for
numericamente maior que o `VERSION.txt` local. Logo: uma release só chega aos
usuários se (a) a tag for maior e (b) tiver o asset com esse nome exato.

## Passos

1. **Descobrir a versão nova.** Ler `VERSION.txt` (raiz). Se o usuário não disse o
   número, sugerir o próximo (ex.: `1.1` → `1.2`; patch se foi correção, minor se
   foi feature) e confirmar.

2. **Commitar o código pendente primeiro.** O script exige árvore limpa (exceto
   `VERSION.txt`). Se houver mudanças de feature/fix não commitadas, commitá-las com
   mensagem descritiva antes de rodar o script. NÃO bumpar VERSION.txt na mão — o
   script faz isso.

3. **Rodar a pipeline** a partir da raiz do repo:
   ```
   powershell -ExecutionPolicy Bypass -File .claude/skills/nova-versao/release.ps1 -Version <X.Y> -Notes "<resumo das mudanças>"
   ```
   O script faz: preflight → bump `VERSION.txt` → commit `chore: release vX.Y` →
   `build.bat` → `git tag vX.Y` + push do commit e da tag → `gh release create` com
   o instalador anexado. Aborta em qualquer falha antes de publicar.

4. **Confirmar** ao usuário: tag publicada e que os apps oferecerão a atualização no
   próximo boot. Reportar erros com a saída exata do script.

## Notas de release (passar em -Notes)

Resumo curto em PT do que mudou desde a última versão (features/correções). Se
incerto, derivar de `git log <tag-anterior>..HEAD --oneline`.

## Pré-requisitos (checados pelo script; resolver se faltar)

- **GitHub CLI autenticado.** Se faltar: `winget install GitHub.cli`, depois o
  usuário roda `! gh auth login` (login é interativo — não dá para automatizar).
- **Inno Setup 6** em `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`
  (`winget install JRSoftware.InnoSetup`).
- **`.venv`** presente na raiz (usada pelo `build.bat` para o PyInstaller).

## Detalhes fixos (não mudar sem ajustar o updater)

- Asset da release DEVE se chamar `Setup_JW_Mural.exe` (`ASSET_NOME` no updater;
  `OutputBaseFilename` no `JW_Mural.iss`).
- Tag = `v<versão>`; o updater aceita com ou sem `v` e compara numericamente.
- `VERSION.txt` é fonte única: lida pelo app (`src/version.py`) e pelo Inno Setup.
