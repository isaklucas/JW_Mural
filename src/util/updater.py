"""Auto-atualização via GitHub Releases.

Fluxo: ao abrir o app, verifica se há release mais recente no GitHub. Se
houver, baixa o instalador (Setup_JW_Mural.exe), lança-o e fecha o app para
que o Inno Setup substitua os arquivos em uso.

Nunca deve quebrar o startup: toda falha de rede/parse é engolida e tratada
como "sem atualização".
"""
import logging
import os
import re
import subprocess
import sys
import tempfile

import requests

logger = logging.getLogger(__name__)

# Repositório público onde os releases são publicados.
GITHUB_REPO = "isaklucas/JW_Mural"
API_LATEST = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
ASSET_NOME = "Setup_JW_Mural.exe"
TIMEOUT = 5  # segundos


def _parse_version(s):
    """Normaliza uma string de versão em tupla comparável de inteiros.

    Aceita 'v1.2.3', '1.2', '1.0.0'. Partes não numéricas são ignoradas.
    Ex.: 'v1.2' -> (1, 2)
    """
    if not s:
        return (0,)
    nums = re.findall(r"\d+", str(s))
    if not nums:
        return (0,)
    return tuple(int(n) for n in nums)


def _versao_maior(remota, local):
    """True se `remota` for estritamente maior que `local`."""
    a = _parse_version(remota)
    b = _parse_version(local)
    # Igualar comprimentos com zeros à direita para comparar corretamente.
    tamanho = max(len(a), len(b))
    a = a + (0,) * (tamanho - len(a))
    b = b + (0,) * (tamanho - len(b))
    return a > b


def verificar_atualizacao():
    """Consulta o GitHub e retorna dict da nova versão ou None.

    Retorno: {"versao": str, "url": str, "notas": str} se houver versão maior
    que a instalada; None caso contrário ou em qualquer falha.
    """
    try:
        from version import __version__ as versao_atual
    except Exception:
        try:
            from src.version import __version__ as versao_atual
        except Exception:
            logger.warning("Não foi possível ler a versão atual; pulando update.")
            return None

    try:
        resp = requests.get(
            API_LATEST,
            timeout=TIMEOUT,
            headers={"Accept": "application/vnd.github+json"},
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.info(f"Verificação de atualização falhou (ignorado): {e}")
        return None

    tag = data.get("tag_name") or data.get("name")
    if not tag:
        return None

    if not _versao_maior(tag, versao_atual):
        logger.info(f"App atualizado (local {versao_atual}, remoto {tag}).")
        return None

    # Localizar o asset do instalador.
    url = None
    for asset in data.get("assets", []):
        if asset.get("name", "").lower() == ASSET_NOME.lower():
            url = asset.get("browser_download_url")
            break
    if not url:
        logger.warning(f"Release {tag} sem asset '{ASSET_NOME}'.")
        return None

    logger.info(f"Nova versão disponível: {tag}")
    return {
        "versao": str(tag).lstrip("vV"),
        "url": url,
        "notas": data.get("body") or "",
    }


def baixar_instalador(url, on_progress=None):
    """Baixa o instalador para %TEMP% e retorna o caminho local.

    on_progress(baixado, total) é chamado durante o download (total pode ser 0
    se o servidor não informar Content-Length). Lança exceção em falha.
    """
    destino = os.path.join(tempfile.gettempdir(), ASSET_NOME)
    with requests.get(url, stream=True, timeout=30) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        baixado = 0
        with open(destino, "wb") as f:
            for chunk in r.iter_content(chunk_size=64 * 1024):
                if chunk:
                    f.write(chunk)
                    baixado += len(chunk)
                    if on_progress:
                        try:
                            on_progress(baixado, total)
                        except Exception:
                            pass
    logger.info(f"Instalador baixado em {destino} ({baixado} bytes).")
    return destino


def lancar_instalador_e_sair(caminho):
    """Lança o instalador (elevado) e encerra o processo atual.

    O instalador exige admin (PrivilegesRequired=admin), então elevamos via
    ShellExecute 'runas'. Passamos /FORCECLOSEAPPLICATIONS para o Inno usar o
    Restart Manager e fechar qualquer instância que ainda segure arquivos em
    {app}, sem exibir diálogo. Não usamos AppMutex (causava loop). Encerramos o
    app logo em seguida para liberar os arquivos.
    """
    params = "/FORCECLOSEAPPLICATIONS"
    logger.info(f"Lançando instalador: {caminho} {params}")
    lancado = False
    try:
        import ctypes
        # SW_SHOWNORMAL=1; retorno > 32 indica sucesso.
        rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", caminho, params, None, 1)
        lancado = int(rc) > 32
        if not lancado:
            logger.warning(f"ShellExecuteW retornou {rc}; tentando fallback.")
    except Exception as e:
        logger.warning(f"Falha ao elevar instalador ({e}); tentando fallback.")

    if not lancado:
        try:
            subprocess.Popen([caminho, params], close_fds=True)
        except Exception:
            os.startfile(caminho)  # noqa: S606

    # Encerrar o app para liberar os arquivos.
    os._exit(0)
