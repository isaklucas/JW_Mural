# SDD 18 — Modo Minutas (docx gerado por código + guardado no MongoDB)

**Status:** ✅ Implementado (branch `feature/minutas-final-semana`)
**Prioridade:** P2 (~6-8h)
**Módulos alvo:** `src/process/final_semana.py`, novo `src/process/minutas/`, `src/database/db_operations.py`, `src/services/reuniao_service.py`, `src/views/reunioes_view.py`
**Relacionado:** SDD 06 (placeholders orientados a dados), SDD 09 (testes de docx), SDD 12 (backup)

---

## 0. Revisão (12/10/2026) — modelo oficial + pré-visualização

A 1ª versão montava o docx do zero (estilos de um "docx base"). Resultado **não ficou igual**
ao oficial: perdia a imagem do cabeçalho, as linhas decorativas e a formatação por trecho
(ex.: "Setembro" 14pt preto + "– Saindo…" 12pt azul). Também o editor (JSON de colunas,
larguras, cores) era difícil de entender.

Mudança:

- **O arquivo Word oficial É o modelo** (`minutas_modelo`, Binary). O renderizador mantém o
  cabeçalho intacto e **clona as tabelas do modelo** para cada mês, repetindo a linha de
  exemplo. A troca de texto mapeia caractere a caractere (difflib) para herdar a formatação
  do trecho original.
- **Minuta formato 2** só diz *qual tabela do modelo* usar e *o que vai em cada coluna*.
  Aparência = Word. Minuta formato 1 no banco é substituída pela padrão.
- **Pré-visualização ao vivo** (`process/minutas/preview.py` + `views/preview_docx.py`) à
  direita no assistente e no editor ("Modelo do documento"). Resolve cores de tema/estilo de
  tabela, imagens flutuantes e células mescladas. Aproximação — o .docx final é idêntico ao modelo.
- Modelos padrão em `assets/minutas/modelo_fds_*.docx` (oficiais com nomes trocados por fictícios).

O desenho abaixo (seções 2–3) é o da 1ª versão e fica como histórico.

## 1. Contexto

Hoje o Final de Semana abre `Templates/template_final_semana_{sentinela,oradores}.docx`
e troca placeholders `w1_presidente … w9_tema`. Layout fixo: **9 semanas em 2 tabelas
(5+4)**, coluna SÁBADO vazia, cabeçalho `MES – Recebendo Congregação XXXX` nunca preenchido.

Novos modelos (Downloads, 12/10/2026):

| Arquivo | Estrutura |
|---|---|
| `Reunião de Final de Semana 2026.docx` | Título "Reunião de Final de Semana Oradores Congregação Praias Rasas". Por mês: tabela **Recebendo** (SÁBADO / PRESIDENTE / ORADOR / TEMA, estilo `Grid Table 6 Colorful Accent 5`) + tabela **Saindo – Congregação X** (SÁBADO / ORADOR / TEMA, estilo `Grid Table 4 Accent 5`). Nº de linhas = nº de sábados do mês (4 ou 5). |
| `Reunião de Final de Semana 2026 Anunciando o Reino de Jeová.docx` | Título "Reunião Estudo de A Sentinela / Anunciando o Reino de Jeová". Por mês: tabela 3 col (SÁBADO / DIRIGENTE E LEITOR / ESTUDO), estilo `Table Grid`, células "Dirigente / Leitor". |

São **exemplos preenchidos** (dados de 2024), não templates com placeholder. Diferenças
reais em relação ao atual:

1. **Agrupamento por mês** (tabela por mês, 4-5 linhas) em vez de 5+4 fixo.
2. **Data do sábado preenchida** (`03/08/2024`).
3. **Seção "Saindo"** — oradores da congregação enviados a outra congregação. **Dado novo**,
   não existe em `reunioes_final_semana.semanas[]`.
4. Cabeçalho de mês com nome da congregação (Recebendo/Saindo).

Com template estático, (1) e (3) são inviáveis: o nº de tabelas/linhas varia. → Gerar por código.

## 2. Proposta: "Minuta"

Minuta = **especificação do documento como dado** (JSON no Mongo) + **renderizador**
python-docx que monta o docx do zero a partir de `minuta + semanas`.

### 2.1 Collections

```text
minutas                       # layout (1 doc por tipo; editável/versionável)
{
  _id, chave: "fds_oradores" | "fds_sentinela",
  versao: 3, ativo: true, atualizado_em,
  pagina: { margens_cm: {sup, inf, esq, dir} },
  titulo: ["Reunião de Final de Semana Oradores", "Congregação {congregacao}"],
  agrupar_por: "mes",
  blocos: [
    { tipo: "tabela", titulo: "{mes} – Recebendo - Congregação {congregacao}",
      estilo: "Grid Table 6 Colorful Accent 5",
      colunas: [ {rotulo:"SÁBADO", campo:"data", largura_cm:2.5},
                 {rotulo:"PRESIDENTE", campo:"presidente"},
                 {rotulo:"ORADOR", campo:"orador"},
                 {rotulo:"TEMA: DISCURSO PUBLICO", campo:"tema_discurso"} ] },
    { tipo: "tabela", titulo: "{mes} – Saindo – Congregação {congregacao_destino}",
      estilo: "Grid Table 4 Accent 5", fonte: "saidas",
      colunas: [ {rotulo:"SÁBADO", campo:"data"}, {rotulo:"ORADOR", campo:"orador"},
                 {rotulo:"TEMA: DISCURSO PUBLICO", campo:"tema"} ] }
  ],
  base_docx_id: <ObjectId em minutas_base>   # carrega estilos/fontes
}

minutas_base                  # docx vazio só p/ estilos (Binary, ~30 KB)
{ _id, nome, arquivo: Binary, sha256 }

documentos_gerados            # saída renderizada (Binary)
{ _id, tipo: "fds_oradores", reuniao_id: <reunioes_final_semana._id>,
  minuta_versao: 3, nome_arquivo, criado_em, arquivo: Binary }
```

Por que `minutas_base`: python-docx só aplica estilo de tabela (`Grid Table 6 …`) que
**exista** no docx base. O `Document()` padrão não tem os "Grid Table". Solução: guardar um
docx vazio extraído do modelo novo (estilos + tema de cores) e abrir dele com
`Document(BytesIO(base))`. Zero arquivo em `Templates/`.

### 2.2 Renderizador (`src/process/minutas/render.py`)

```python
def renderizar(minuta, base_bytes, contexto, semanas) -> bytes:
    doc = Document(BytesIO(base_bytes)); _limpar_corpo(doc)
    _aplicar_pagina(doc, minuta["pagina"]); _titulo(doc, minuta["titulo"], contexto)
    for mes, grupo in _agrupar(semanas, minuta["agrupar_por"]):
        for bloco in minuta["blocos"]:
            linhas = grupo.saidas if bloco.get("fonte") == "saidas" else grupo.semanas
            if linhas: _tabela(doc, bloco, linhas, {**contexto, "mes": mes})
    buf = BytesIO(); doc.save(buf); return buf.getvalue()
```

Função pura (bytes in → bytes out) → testável com mongomock + comparação de texto (SDD 09).

### 2.3 Fluxo

`reunioes_view` → `reuniao_service.gerar_final_semana(semanas, …)` →
carrega minuta ativa + base → `renderizar` → salva em `documentos_gerados` →
escreve cópia em `documentosCriados/` e abre. Histórico ganha botão **"Reabrir documento"**
(lê Binary do Mongo, sem regenerar).

## 3. Avaliação

| Ponto | Veredito |
|---|---|
| Tamanho | Docx ~35 KB ≪ 16 MB (limite BSON). `Binary` direto, **não precisa GridFS**. 9 semanas/mês × 2 docs ≈ 1 MB/ano. |
| Backup | Entra no backup do Mongo automaticamente (hoje `documentosCriados/` fica fora). Ganho. |
| Multi-máquina (SDD 13) | Documento e layout acessíveis de qualquer PC conectado ao mesmo Mongo. Ganho. |
| Edição de layout | Mudar coluna/título/estilo = editar JSON (ou tela futura), sem Word. Mudar **cor/fonte fina** ainda exige trocar o `minutas_base`. |
| Fidelidade visual | python-docx cobre estilos de tabela, merge da linha de título, negrito, tamanho, margens, largura de colunas. Sombreamento custom por célula exige XML (`w:shd`) — viável. |
| DynamoDB | Item máx. 400 KB — cabe, mas SDD 11 remove Dynamo. Implementar só Mongo. |
| Testes | mongomock suporta `Binary`; renderizador é puro. OK offline. |
| Risco | Minuta mal formada no banco quebra geração → validar schema ao carregar + **minuta padrão embutida no código** como fallback/seed. |

**Conclusão: viável e recomendado.** Resolve o layout variável (mês/Saindo) que template
estático não resolve, e documentos passam a ter histórico no banco.

## 4. Decisões (12/10/2026)

1. **Saindo:** tela separada — assistente em passos: oradores **vindo**, depois oradores **indo**.
2. **Congregação:** fixa em Configurações (`configuracoes.congregacao`); visitante/destino informados por mês.
3. **Período:** de **dois em dois meses** (sábados do bimestre; título do estudo pela semana ISO do wol.jw.org).
4. **Editor de minuta** na UI: sim (`editor_minutas`).
5. **Templates legados:** mantidos como opção ("modo legado") por enquanto.

## 5. Tarefas (após decisões)

- [x] T1 — Extrair `minutas_base` do modelo novo (docx sem corpo, com estilos) → seed.
- [x] T2 — JSON das 2 minutas padrão em `src/process/minutas/padrao.py` + seed em `init_db.py`.
- [x] T3 — `render.py` (agrupamento por mês, tabelas, título mesclado, estilos).
- [x] T4 — `db_operations`: `buscar_minuta_ativa`, `salvar_minuta`, `salvar_documento_gerado`, `buscar_documento_gerado`; expor em `reuniao_service`.
- [x] T5 — Campos "Saindo" no modal `solicitar_dados_usuario` + modelo `semanas[]`.
- [x] T6 — `final_semana.criar_documento_*` passam a usar minuta (legado atrás de flag).
- [x] T7 — Histórico FDS: "Reabrir documento".
- [x] T8 — Testes: `tests/test_minutas_render.py` (puro) + `tests/db/test_minutas.py` (mongomock).
- [x] T9 — Docs: `03-Modulos.md`, `04-Fluxos-Principais.md`, `README_IA.md` (collections novas).
