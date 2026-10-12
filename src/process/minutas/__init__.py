"""Modo Minutas (SDD 18): documentos Word gerados por código a partir de um layout
guardado como dado (a "minuta"), em vez de preencher placeholders num .docx fixo.

- `periodo`  — datas das reuniões do bimestre e URL da semana no wol.jw.org.
- `padrao`   — minutas padrão (Oradores e Sentinela) e catálogo de campos.
- `render`   — monta o .docx (bytes) a partir de minuta + docx base + dados.

Nada aqui importa `database`: o módulo é puro e testável offline. Quem busca a
minuta/base no banco e grava o resultado é `services.minuta_service`.
"""
