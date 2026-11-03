import datetime
import random
from collections import defaultdict

from database import listar_candidatos_salao_ordenados, listar_designacoes_salao


# Pesos da pontuação (menor pontuação = escolhido). Ver _pontuar.
PESO_FUNCAO = 10.0        # vezes nesta função na janela recente
PESO_TOTAL = 4.0          # vezes em qualquer função do salão na janela recente
PESO_DUPLA = 8.0          # vezes que a dupla já trabalhou junta
PESO_DUPLA_SEGUIDA = 60.0 # mesma dupla da reunião anterior nesta função
PENAL_GAP = {1: 50.0, 2: 15.0, 3: 5.0}       # serviu há N reuniões (qualquer função)
PENAL_GAP_FUNCAO = {1: 40.0, 2: 12.0, 3: 4.0}  # serviu há N reuniões NESTA função
MESES_JANELA = 4          # meses salvos anteriores usados como histórico
RUIDO = 3.0               # aleatoriedade para mesclar empates
PESO_HISTORICO = 0.3      # contagens do histórico valem menos que as da rodada
                          # (evita "compensar" demais quem fez pouco antes)

# Função lógica de cada campo da semana (áudio e vídeo dividem a mesma lista).
FUNCOES = ("audio", "video", "microfone", "indicadores")


def _nomes(valor):
    return [n.strip() for n in (valor or "").split("/") if n.strip()]


def _parse_data(s):
    return datetime.datetime.strptime(s, "%d/%m/%Y").date()


class _Estado:
    """Carga acumulada (histórico recente + o que já foi gerado nesta rodada)."""

    def __init__(self):
        self.cont_funcao = defaultdict(float)  # (nome, funcao) -> qtd
        self.cont_total = defaultdict(float)   # nome -> qtd
        self.ultimo_idx = {}                  # nome -> índice da reunião
        self.ultimo_idx_funcao = {}           # (nome, funcao) -> índice
        self.duplas = defaultdict(int)        # frozenset -> qtd
        self.ultima_dupla = {}                # funcao -> frozenset

    def registrar(self, idx, semana, peso=1.0):
        for funcao in FUNCOES:
            nomes = _nomes(semana.get(funcao))
            for n in nomes:
                self.cont_funcao[(n, funcao)] += peso
                self.cont_total[n] += peso
                self.ultimo_idx[n] = idx
                self.ultimo_idx_funcao[(n, funcao)] = idx
            if len(nomes) == 2:
                par = frozenset(nomes)
                self.duplas[par] += 1
                self.ultima_dupla[funcao] = par
        # Áudio + vídeo também formam uma dupla (evita sempre os mesmos dois juntos)
        av = _nomes(semana.get("audio")) + _nomes(semana.get("video"))
        if len(av) == 2 and av[0] != av[1]:
            par = frozenset(av)
            self.duplas[par] += 1
            self.ultima_dupla["audio_video"] = par


class DesignacoesSalao:

    @staticmethod
    def gerar_datas_meses(dia_semana_idx, dia_fds_idx, meses_list):
        """
        meses_list: [(ano, mes), ...] — meses específicos a gerar
        """
        datas = []
        for (ano, mes) in meses_list:
            d = datetime.date(ano, mes, 1)
            while d.month == mes:
                if dia_semana_idx is not None and d.weekday() == dia_semana_idx:
                    datas.append({"data": d.strftime("%d/%m/%Y"), "tipo": "meio_semana"})
                if dia_fds_idx is not None and d.weekday() == dia_fds_idx:
                    datas.append({"data": d.strftime("%d/%m/%Y"), "tipo": "final_semana"})
                d += datetime.timedelta(days=1)
        datas.sort(key=lambda x: datetime.datetime.strptime(x["data"], "%d/%m/%Y"))
        return datas

    @staticmethod
    def gerar_datas(dia_semana_idx, dia_fds_idx, qntd_meses):
        """
        dia_semana_idx: 0=Seg..4=Sex ou None
        dia_fds_idx: 5=Sáb, 6=Dom ou None
        Retorna lista de {"data": "DD/MM/AAAA", "tipo": "meio_semana"|"final_semana"}
        """
        hoje = datetime.date.today()
        datas = []
        for offset in range(qntd_meses):
            ano = hoje.year + (hoje.month + offset - 1) // 12
            mes = (hoje.month + offset - 1) % 12 + 1
            d = datetime.date(ano, mes, 1)
            while d.month == mes:
                if dia_semana_idx is not None and d.weekday() == dia_semana_idx:
                    datas.append({"data": d.strftime("%d/%m/%Y"), "tipo": "meio_semana"})
                if dia_fds_idx is not None and d.weekday() == dia_fds_idx:
                    datas.append({"data": d.strftime("%d/%m/%Y"), "tipo": "final_semana"})
                d += datetime.timedelta(days=1)
        datas.sort(key=lambda x: datetime.datetime.strptime(x["data"], "%d/%m/%Y"))
        return datas

    @staticmethod
    def _historico_recente(semanas_info, historico=None):
        """
        Semanas já salvas ANTES da primeira data gerada, limitadas aos últimos
        MESES_JANELA meses. Meses sendo (re)gerados são ignorados.
        """
        if historico is None:
            try:
                historico = listar_designacoes_salao() or []
            except Exception:
                historico = []
        if not semanas_info:
            return []
        inicio = min(_parse_data(s["data"]) for s in semanas_info)
        meses_gerados = {(_parse_data(s["data"]).year, _parse_data(s["data"]).month)
                         for s in semanas_info}
        limite = inicio - datetime.timedelta(days=31 * MESES_JANELA)
        semanas = []
        for doc in historico:
            if (doc.get("ano"), doc.get("mes")) in meses_gerados:
                continue
            for s in doc.get("semanas", []):
                try:
                    d = _parse_data(s.get("data", ""))
                except ValueError:
                    continue
                if limite <= d < inicio:
                    semanas.append((d, s))
        semanas.sort(key=lambda x: x[0])
        return [s for _, s in semanas]

    @staticmethod
    def _pontuar(nome, funcao, idx, estado, parceiro=None):
        score = PESO_FUNCAO * estado.cont_funcao[(nome, funcao)]
        score += PESO_TOTAL * estado.cont_total[nome]
        if nome in estado.ultimo_idx:
            score += PENAL_GAP.get(idx - estado.ultimo_idx[nome], 0.0)
        if (nome, funcao) in estado.ultimo_idx_funcao:
            score += PENAL_GAP_FUNCAO.get(idx - estado.ultimo_idx_funcao[(nome, funcao)], 0.0)
        if parceiro:
            par = frozenset([nome, parceiro])
            score += PESO_DUPLA * estado.duplas[par]
            chave = "audio_video" if funcao in ("audio", "video") else funcao
            if estado.ultima_dupla.get(chave) == par:
                score += PESO_DUPLA_SEGUIDA
        return score

    @staticmethod
    def _escolher(candidatos, funcao, idx, estado, ocupados, rng, parceiro=None):
        livres = [n for n in candidatos if n not in ocupados]
        if not livres:
            return ""
        return min(
            livres,
            key=lambda n: DesignacoesSalao._pontuar(n, funcao, idx, estado, parceiro)
            + rng.random() * RUIDO,
        )

    @staticmethod
    def gerar_designacoes(semanas_info, impedimentos=None, historico=None, seed=None):
        """
        Gera designações automáticas para cada data em semanas_info.

        Escolha gulosa por pontuação: favorece quem fez MENOS (na função e no
        total do salão), penaliza quem serviu nas últimas reuniões e duplas que
        já trabalharam juntas. Considera os últimos meses já salvos como histórico.

        Regras fixas: ninguém tem duas funções no mesmo dia; impedimentos
        ({nome: set("DD/MM/AAAA")}) são respeitados.
        historico: lista de docs de designacoes_salao (padrão: lê do banco).
        seed: semente para resultados reprodutíveis (testes).
        """
        impedimentos = impedimentos or {}
        rng = random.Random(seed)
        av = listar_candidatos_salao_ordenados("audio_video") or []
        mic = listar_candidatos_salao_ordenados("microfone") or []
        ind = listar_candidatos_salao_ordenados("indicador") or []

        estado = _Estado()
        anteriores = DesignacoesSalao._historico_recente(semanas_info, historico)
        for i, s in enumerate(anteriores):
            estado.registrar(i, s, PESO_HISTORICO)
        base = len(anteriores)

        def disp(lista, data):
            return [n for n in lista if data not in impedimentos.get(n, set())]

        escolher = DesignacoesSalao._escolher
        result = []
        for k, s in enumerate(semanas_info):
            idx = base + k
            data = s["data"]
            ocupados = set()
            av_f, mic_f, ind_f = disp(av, data), disp(mic, data), disp(ind, data)

            # Áudio/vídeo primeiro: lista menor, mais disputada.
            audio = escolher(av_f, "audio", idx, estado, ocupados, rng)
            ocupados.add(audio)
            video = escolher(av_f, "video", idx, estado, ocupados, rng, parceiro=audio)
            ocupados.add(video)

            duplas = {}
            for funcao, lista in (("microfone", mic_f), ("indicadores", ind_f)):
                a = escolher(lista, funcao, idx, estado, ocupados, rng)
                ocupados.add(a)
                b = escolher(lista, funcao, idx, estado, ocupados, rng, parceiro=a)
                ocupados.add(b)
                duplas[funcao] = " / ".join(n for n in (a, b) if n)

            semana = {
                **s,
                "audio":       audio,
                "video":       video,
                "microfone":   duplas["microfone"],
                "indicadores": duplas["indicadores"],
            }
            estado.registrar(idx, semana)
            result.append(semana)
        return result
