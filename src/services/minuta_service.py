"""Serviço do Modo Minutas (SDD 18).

Junta as peças: minuta (como preencher) e arquivo modelo (.docx oficial) no banco, renderizador puro em
`process.minutas.render`, gravação do .docx gerado no banco (`documentos_gerados`)
e em `documentosCriados/`, e o histórico em `reunioes_final_semana`.
"""
import datetime
import logging
import os
import re
import sys
from pathlib import Path

from database import db_ops
from process.minutas import padrao, periodo, render

logger = logging.getLogger(__name__)

PASTA_SAIDA = "documentosCriados"
CHAVE_CONGREGACAO = "congregacao"


def _caminho_asset_modelo(chave):
    """Localiza assets/minutas/<arquivo> subindo a partir deste módulo
    (dev: src/services -> raiz; build: services -> pasta do exe; ou _MEIPASS)."""
    nome = padrao.ARQUIVOS_MODELO.get(chave)
    if not nome:
        return None
    candidatos = []
    if getattr(sys, '_MEIPASS', None):
        candidatos.append(Path(sys._MEIPASS))
    candidatos.extend(Path(__file__).resolve().parents)
    for raiz in candidatos:
        caminho = raiz / "assets" / "minutas" / nome
        if caminho.exists():
            return caminho
    return None


def _nome_arquivo_seguro(nome):
    return re.sub(r'[<>:"/\\|?*]+', '-', nome).strip(' .') or "documento"


def agrupar_por_mes(meses_info, semanas):
    """Reconstrói [{ano, mes, congregacao_*, semanas:[...]}] a partir da lista
    plana de semanas (como fica salva no histórico) + metadados dos meses."""
    grupos = []
    for info in meses_info:
        prefixo = f"{info['ano']:04d}-{info['mes']:02d}"
        grupos.append({
            **{k: v for k, v in info.items() if k != 'semanas'},
            'semanas': [s for s in semanas if (s.get('data') or '').startswith(prefixo)],
        })
    return grupos


class MinutaService:
    # ------------------------------------------------------------ configuração
    def obter_congregacao(self):
        return db_ops.obter_configuracao(CHAVE_CONGREGACAO, "") or ""

    def salvar_congregacao(self, nome):
        return db_ops.salvar_configuracao(CHAVE_CONGREGACAO, (nome or "").strip())

    def listas_de_nomes(self):
        """Sugestões para os campos das telas de preenchimento."""
        import process.final_semana as final_semana
        return {
            'ancios': db_ops.listar_ancios() or [],
            'ancios_servos': db_ops.listar_ancios_e_servos() or [],
            'leitores': db_ops.listar_publicadores_por_permissao("leitura_sentinela") or [],
            'temas': final_semana.FinalSemana._carregar_temas_discursos(),
        }

    # ----------------------------------------------------------------- minutas
    def garantir_padroes(self):
        """Semeia no banco as minutas padrão e os arquivos modelo que ainda não existem.
        Minuta em formato antigo (antes do modelo oficial) é trocada pela padrão."""
        for chave in padrao.MINUTAS_PADRAO:
            atual = db_ops.buscar_minuta(chave)
            if atual is None or atual.get('formato') != padrao.FORMATO:
                db_ops.salvar_minuta(padrao.minuta_padrao(chave))
            if db_ops.buscar_minuta_modelo(chave) is None:
                caminho = _caminho_asset_modelo(chave)
                if caminho:
                    db_ops.salvar_minuta_modelo(chave, caminho.read_bytes(), caminho.name)
                else:
                    logger.warning("Modelo padrão da minuta '%s' não encontrado em assets/minutas.", chave)

    def listar_minutas(self):
        self.garantir_padroes()
        return db_ops.listar_minutas()

    def obter_minuta(self, chave):
        """Minuta do banco; se faltar ou estiver inválida, a padrão (com aviso no log)."""
        self.garantir_padroes()
        minuta = db_ops.buscar_minuta(chave)
        erros = padrao.validar_minuta(minuta) if minuta else ["não encontrada"]
        if erros:
            logger.warning("Minuta '%s' inválida (%s); usando a padrão.", chave, "; ".join(erros))
            return padrao.minuta_padrao(chave)
        return minuta

    def salvar_minuta(self, minuta):
        erros = padrao.validar_minuta(minuta, self.descrever_modelo(minuta.get('chave')))
        if erros:
            return {"success": False, "message": "\n".join(erros)}
        return db_ops.salvar_minuta(minuta)

    def restaurar_padrao(self, chave):
        """Volta a minuta E o arquivo modelo para o padrão."""
        self.restaurar_modelo_padrao(chave)
        return db_ops.salvar_minuta(padrao.minuta_padrao(chave))

    def obter_modelo(self, chave):
        modelo = db_ops.buscar_minuta_modelo(chave)
        if modelo is None:
            caminho = _caminho_asset_modelo(chave)
            modelo = caminho.read_bytes() if caminho else None
        return modelo

    def info_modelo(self, chave):
        return db_ops.info_minuta_modelo(chave) or {}

    def trocar_modelo(self, chave, docx_bytes, nome=""):
        """Passa a usar outro .docx (ex.: o oficial atualizado) como modelo."""
        erro = render.validar_modelo(docx_bytes)
        if erro:
            return {"success": False, "message": erro}
        return db_ops.salvar_minuta_modelo(chave, docx_bytes, nome)

    def restaurar_modelo_padrao(self, chave):
        caminho = _caminho_asset_modelo(chave)
        if not caminho:
            return {"success": False, "message": "Modelo padrão não encontrado."}
        return db_ops.salvar_minuta_modelo(chave, caminho.read_bytes(), caminho.name)

    def descrever_modelo(self, chave):
        """Cabeçalho e tabelas do modelo (para o editor); {} se não houver modelo."""
        try:
            modelo = self.obter_modelo(chave)
            return render.descrever_modelo(modelo) if modelo else {}
        except Exception as e:
            logger.warning("Não foi possível ler o modelo '%s': %s", chave, e)
            return {}

    # -------------------------------------------------------------- geração
    def buscar_programacao(self, ano, mes, qtd_meses=2, auto_presidente=False, auto_leitor=False,
                           idioma="pt"):
        """Monta o período e busca no wol.jw.org o título do estudo de cada semana.
        Roda em thread (sem GUI). Retorna a lista de meses com as semanas."""
        import process.webscrapper as webscrapper
        import process.final_semana as final_semana

        meses = periodo.montar_periodo(ano, mes, qtd_meses)
        congregacao = self.obter_congregacao()
        for m in meses:
            m['congregacao_recebendo'] = congregacao
        todas = [s for m in meses for s in m['semanas']]
        for semana in todas:
            data = datetime.date.fromisoformat(semana['data'])
            url = periodo.url_semana_wol(data, idioma)
            try:
                achados = webscrapper.webscrapper.extrair_titulos_sentinela_meetings(url, 1)
            except Exception as e:
                logger.warning("Falha ao buscar estudo de %s (%s): %s", semana['data'], url, e)
                achados = []
            if achados:
                semana['titulo_estudo'] = achados[0].get('titulo_estudo', '')
        if auto_presidente:
            final_semana.FinalSemana.selecionar_presidente_automaticamente(todas)
        if auto_leitor:
            final_semana.FinalSemana.selecionar_leitor_automaticamente(todas)
        return meses

    def _dados_render(self, meses, dirigente):
        return {'congregacao': self.obter_congregacao(), 'dirigente': dirigente or '', 'meses': meses}

    def renderizar(self, chave, meses, dirigente, minuta=None):
        """(.docx bytes, minuta usada). `minuta` permite renderizar uma ainda não salva."""
        minuta = minuta or self.obter_minuta(chave)
        conteudo = render.renderizar(minuta, self.obter_modelo(chave), self._dados_render(meses, dirigente))
        return conteudo, minuta

    def pacote(self, chave):
        """(minuta, modelo) carregados uma vez — para pré-visualizar muitas vezes sem ir ao banco."""
        return self.obter_minuta(chave), self.obter_modelo(chave)

    def renderizar_pacote(self, pacote, meses, dirigente):
        minuta, modelo = pacote
        return render.renderizar(minuta, modelo, self._dados_render(meses, dirigente))

    def renderizar_exemplo(self, minuta):
        """.docx (bytes) da `minuta` com dados fictícios — pré-visualização do editor."""
        return render.renderizar(
            minuta, self.obter_modelo(minuta['chave']),
            render.dados_de_exemplo(self.obter_congregacao() or "Minha Congregação"),
        )

    def gravar_temporario(self, nome, conteudo):
        """Grava em documentosCriados/ (para abrir no Word) e devolve o caminho."""
        return self._gravar_arquivo(nome, conteudo)

    def _gravar_arquivo(self, nome, conteudo):
        os.makedirs(PASTA_SAIDA, exist_ok=True)
        caminho = os.path.abspath(os.path.join(PASTA_SAIDA, _nome_arquivo_seguro(nome)))
        with open(caminho, "wb") as f:
            f.write(conteudo)
        return caminho

    def reuniao_existente(self, ano, mes):
        return db_ops.buscar_reuniao_final_semana(ano, mes)

    def gerar_final_semana(self, meses, dirigente, nome_base):
        """Gera os documentos de todas as minutas do final de semana, grava no banco
        (documento + histórico) e em documentosCriados/. Devolve os caminhos.

        Se já existe reunião salva para o período (edição/regeração), ela é removida
        antes — senão as participações seriam duplicadas no histórico dos publicadores.
        """
        if not meses:
            raise ValueError("Período sem meses.")
        ano, mes = meses[0]['ano'], meses[0]['mes']
        nome_base = (nome_base or "").strip() or f"Final de Semana {periodo.nome_periodo([(m['ano'], m['mes']) for m in meses])}"

        documentos = []
        for chave in padrao.MINUTAS_PADRAO:
            conteudo, minuta = self.renderizar(chave, meses, dirigente)
            sufixo = minuta.get('sufixo_arquivo') or chave
            nome_arquivo = f"{nome_base}_{sufixo}.docx"
            documentos.append((chave, nome_arquivo, conteudo, minuta.get('versao')))

        if db_ops.buscar_reuniao_final_semana(ano, mes):
            db_ops.excluir_reuniao_final_semana(ano, mes)

        semanas = [s for m in meses for s in m['semanas']]
        dados = {
            'ano': ano,
            'mes': mes,
            'modo': 'minuta',
            'qtd_meses': len(meses),
            'periodo': periodo.nome_periodo([(m['ano'], m['mes']) for m in meses]),
            'nome_arquivo': nome_base,
            'dirigente': dirigente or '',
            'congregacao': self.obter_congregacao(),
            'meses': [{k: v for k, v in m.items() if k != 'semanas'} for m in meses],
            'semanas': semanas,
            'data_criacao': datetime.datetime.now().isoformat(),
        }
        resultado = db_ops.salvar_reuniao_final_semana(dados)
        if not resultado.get('success'):
            raise RuntimeError(f"Erro ao salvar a reunião: {resultado.get('message', '')}")

        caminhos = []
        for chave, nome_arquivo, conteudo, versao in documentos:
            r = db_ops.salvar_documento_gerado(ano, mes, chave, nome_arquivo, conteudo, versao)
            if not r.get('success'):
                logger.warning("Documento '%s' não foi salvo no banco: %s", chave, r.get('message'))
            caminhos.append(self._gravar_arquivo(nome_arquivo, conteudo))
        return caminhos

    # ------------------------------------------------------------ histórico
    def meses_da_reuniao(self, reuniao):
        """Estrutura por mês (para editar/re-renderizar) de uma reunião salva no modo Minutas."""
        return agrupar_por_mes(reuniao.get('meses', []), reuniao.get('semanas', []))

    def listar_documentos(self, ano, mes):
        return db_ops.listar_documentos_gerados(ano, mes)

    def exportar_documento(self, ano, mes, tipo):
        """Grava em documentosCriados/ o .docx guardado no banco; devolve o caminho."""
        doc = db_ops.buscar_documento_gerado(ano, mes, tipo)
        if not doc:
            raise FileNotFoundError("Documento não encontrado no banco.")
        return self._gravar_arquivo(doc.get('nome_arquivo') or f"{tipo}.docx", doc['arquivo'])

    def abrir(self, caminho):
        abrir_arquivo(caminho)


def abrir_arquivo(caminho):
    """Abre o arquivo no programa padrão (Word). Silencioso fora do Windows."""
    try:
        os.startfile(caminho)  # type: ignore[attr-defined]
    except AttributeError:
        logger.info("Arquivo gerado: %s", caminho)
    except OSError as e:
        logger.warning("Não foi possível abrir %s: %s", caminho, e)


minuta_service = MinutaService()
