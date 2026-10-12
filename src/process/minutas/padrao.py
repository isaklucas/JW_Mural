"""Minutas padrão do final de semana + catálogo de campos.

Uma minuta diz COMO preencher o arquivo modelo (o .docx oficial, com toda a
formatação). Ela não descreve aparência — a aparência vem do modelo:

    {
      "chave": "fds_oradores",
      "formato": 2,
      "nome": "Oradores",
      "sufixo_arquivo": "oradores",
      "cabecalho": [],          # textos novos p/ os parágrafos do topo (vazio = manter os do modelo)
      "tabelas": [              # blocos repetidos para CADA mês do período
        {"nome": "Recebendo",
         "modelo": 0,           # qual tabela do modelo serve de exemplo
         "titulo": "{mes} – Recebendo - Congregação {congregacao_recebendo}",  # "" = manter
         "campos": ["data", "presidente", "orador", "tema_discurso"],  # um por coluna
         "omitir_se_vazio": False,
         "linha_dados": 2}      # linha de exemplo (0 = título do mês, 1 = cabeçalho)
      ]
    }
"""
import copy

FORMATO = 2

CAMPOS = {
    'data': 'Data do sábado',
    'presidente': 'Presidente',
    'orador': 'Orador (vindo)',
    'tema_discurso': 'Tema do discurso (vindo)',
    'titulo_estudo': 'Título do estudo de A Sentinela',
    'leitor_sentinela': 'Leitor de A Sentinela',
    'dirigente': 'Dirigente de A Sentinela',
    'dirigente_leitor': 'Dirigente / Leitor',
    'orador_saindo': 'Orador (indo)',
    'tema_saindo': 'Tema do discurso (indo)',
}

VARIAVEIS_TITULO = {
    'mes': 'Nome do mês',
    'ano': 'Ano',
    'periodo': 'Período (ex.: Novembro–Dezembro 2026)',
    'congregacao': 'Nossa congregação (Configurações)',
    'congregacao_recebendo': 'Congregação — recebendo (do mês)',
    'congregacao_saindo': 'Congregação — indo (do mês)',
}

MINUTA_ORADORES = {
    'chave': 'fds_oradores',
    'formato': FORMATO,
    'nome': 'Oradores (vindo e indo)',
    'sufixo_arquivo': 'oradores',
    'cabecalho': [],
    'tabelas': [
        {
            'nome': 'Recebendo (oradores vindo)',
            'modelo': 0,
            'titulo': '{mes} – Recebendo - Congregação {congregacao_recebendo}',
            'campos': ['data', 'presidente', 'orador', 'tema_discurso'],
            'omitir_se_vazio': False,
            'linha_dados': 2,
        },
        {
            'nome': 'Saindo (oradores indo)',
            'modelo': 2,
            'titulo': '{mes} – Saindo - Congregação {congregacao_saindo}',
            'campos': ['data', 'orador_saindo', 'tema_saindo'],
            'omitir_se_vazio': True,
            'linha_dados': 2,
        },
    ],
}

MINUTA_SENTINELA = {
    'chave': 'fds_sentinela',
    'formato': FORMATO,
    'nome': 'Estudo de A Sentinela',
    'sufixo_arquivo': 'sentinela',
    'cabecalho': [],
    'tabelas': [
        {
            'nome': 'Estudo de A Sentinela',
            'modelo': 0,
            'titulo': '',  # mantém "Estudo de A Sentinela Anunciado o Reino de Jeová" do modelo
            'campos': ['data', 'dirigente_leitor', 'titulo_estudo'],
            'omitir_se_vazio': False,
            'linha_dados': 2,
        },
    ],
}

MINUTAS_PADRAO = {m['chave']: m for m in (MINUTA_ORADORES, MINUTA_SENTINELA)}

# Arquivo modelo padrão de cada minuta, em assets/minutas/ (os documentos oficiais
# de 2026 com os nomes das linhas de exemplo trocados por nomes fictícios).
ARQUIVOS_MODELO = {
    'fds_oradores': 'modelo_fds_oradores.docx',
    'fds_sentinela': 'modelo_fds_sentinela.docx',
}


def minuta_padrao(chave):
    """Cópia independente da minuta padrão (nunca devolve o dict do módulo)."""
    return copy.deepcopy(MINUTAS_PADRAO[chave])


def validar_minuta(minuta, descricao_modelo=None):
    """Lista de erros legíveis; vazia = minuta utilizável.
    Com `descricao_modelo` (render.descrever_modelo) confere também as tabelas."""
    erros = []
    if not isinstance(minuta, dict):
        return ["Minuta não é um objeto."]
    if minuta.get('formato') != FORMATO:
        return ["Minuta em formato antigo."]
    if not minuta.get('chave'):
        erros.append("Minuta sem 'chave'.")
    if not isinstance(minuta.get('cabecalho', []), list):
        erros.append("'cabecalho' deve ser uma lista de textos.")
    tabelas = minuta.get('tabelas')
    if not isinstance(tabelas, list) or not tabelas:
        erros.append("A minuta precisa de ao menos um bloco (tabela).")
        return erros
    modelo_tabelas = (descricao_modelo or {}).get('tabelas')
    for i, t in enumerate(tabelas, start=1):
        nome = t.get('nome') or f"Bloco {i}"
        if not isinstance(t.get('modelo'), int) or t['modelo'] < 0:
            erros.append(f"{nome}: escolha a tabela do modelo.")
            continue
        if modelo_tabelas is not None and t['modelo'] >= len(modelo_tabelas):
            erros.append(f"{nome}: o modelo não tem a tabela {t['modelo'] + 1}.")
        campos = t.get('campos')
        if not isinstance(campos, list):
            erros.append(f"{nome}: 'campos' deve ser uma lista.")
            continue
        for campo in campos:
            if campo and campo not in CAMPOS:
                erros.append(f"{nome}: campo desconhecido '{campo}'.")
    return erros
