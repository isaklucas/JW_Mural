# TODO: Auto-Update ao Iniciar

## Objetivo
Notificar usuário quando nova versão estiver disponível, sem exigir verificação manual.

---

## Estratégia: GitHub Releases + verificação no startup

### 1. Infraestrutura (uma vez)

- Criar repositório no GitHub (público ou privado)
- A cada novo build, criar release com tag de versão (ex: `v1.1.0`) e anexar `Setup_JW_Mural.exe`
- GitHub disponibiliza endpoint: `https://api.github.com/repos/USUARIO/REPO/releases/latest`

---

### 2. Versão local

Criar arquivo `assets/version.json` no projeto:

```json
{ "version": "1.0.0" }
```

Incluir no `JW_Mural.iss` como arquivo copiado para `{app}\assets\`.

---

### 3. Verificação no startup — `src/util/update_checker.py`

```python
import requests
import json
from pathlib import Path

GITHUB_REPO = "USUARIO/jw-mural"  # substituir
RELEASES_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

def verificar_atualizacao() -> dict | None:
    """Retorna dict com {'versao': str, 'url': str} se há update, None caso contrário."""
    try:
        local = json.loads((Path(__file__).resolve().parent.parent.parent / "assets/version.json").read_text())
        versao_local = tuple(int(x) for x in local["version"].split("."))

        resp = requests.get(RELEASES_URL, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        versao_remota_str = data["tag_name"].lstrip("v")
        versao_remota = tuple(int(x) for x in versao_remota_str.split("."))

        if versao_remota > versao_local:
            url_download = next(
                (a["browser_download_url"] for a in data.get("assets", []) if a["name"].endswith(".exe")),
                data.get("html_url")
            )
            return {"versao": versao_remota_str, "url": url_download}
    except Exception:
        pass  # silencioso — não bloquear startup por falha de rede
    return None
```

---

### 4. Integração em `src/layout.py`

No final de `ModernApp.__init__`, agendar verificação em background após 3s:

```python
self.root.after(3000, self._checar_atualizacao)
```

Método:

```python
def _checar_atualizacao(self):
    import threading
    import webbrowser
    from util.update_checker import verificar_atualizacao

    def check():
        info = verificar_atualizacao()
        if info:
            self.root.after(0, lambda: self._mostrar_aviso_update(info))

    threading.Thread(target=check, daemon=True).start()

def _mostrar_aviso_update(self, info):
    from ttkbootstrap.dialogs import Messagebox
    resposta = Messagebox.yesno(
        f"Nova versão disponível: v{info['versao']}\n\nDeseja abrir o link de download?",
        "Atualização Disponível",
        parent=self.root
    )
    if resposta in ("Yes", "Sim"):
        import webbrowser
        webbrowser.open(info["url"])
```

---

### 5. Build — ajustes necessários

| Arquivo | Ajuste |
|---|---|
| `assets/version.json` | Atualizar versão a cada release |
| `JW_Mural.iss` | Já inclui `assets\*` — sem mudanças |
| `JW_Mural.spec` | Verificar se `requests` está nos hiddenimports |
| `build.bat` | Opcional: automatizar tag git + criação de release via `gh release create` |

---

### 6. Fluxo completo de release

```
1. Alterar versão em assets/version.json (ex: "1.1.0")
2. Rodar build.bat → gera installer_output\Setup_JW_Mural.exe
3. gh release create v1.1.0 installer_output/Setup_JW_Mural.exe
4. Usuários com app aberto verão aviso na próxima abertura
```

---

## Dependência extra

`requests` já é usado no projeto (webscrapper). Confirmar que PyInstaller empacota corretamente verificando `JW_Mural.spec`.
