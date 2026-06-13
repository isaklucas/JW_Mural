import datetime
from database import listar_candidatos_salao_ordenados


class DesignacoesSalao:

    @staticmethod
    def pick_one(lista, idx, assigned):
        for j in range(len(lista)):
            k = (idx + j) % len(lista)
            if lista[k] not in assigned:
                return lista[k]
        return lista[idx % len(lista)] if lista else ""

    @staticmethod
    def _round_robin_pairs(lista):
        """
        Gera todos os C(n,2) pares em ordem round-robin (torneio).
        Cada pessoa aparece no máximo 1x por rodada → sem aparições consecutivas longas.
        """
        n = len(lista)
        if n == 0:
            return []
        if n == 1:
            return [(lista[0], lista[0])]

        players = list(range(n))
        if n % 2 == 1:
            players.append(None)  # bye para n ímpar

        half = len(players) // 2
        num_rounds = len(players) - 1
        pairs = []

        for _ in range(num_rounds):
            for i in range(half):
                p1 = players[i]
                p2 = players[len(players) - 1 - i]
                if p1 is not None and p2 is not None:
                    pairs.append((lista[p1], lista[p2]))
            # Rotação: fixa players[0], gira o restante
            players = [players[0]] + [players[-1]] + players[1:-1]

        return pairs

    @staticmethod
    def pick_two(lista, idx, assigned, ultimo_par=None):
        """
        Cicla pelos C(n,2) pares em ordem round-robin.
        ultimo_par: frozenset com os 2 nomes do par anterior — evita repetição consecutiva.
        """
        if not lista:
            return " / "

        all_pairs = DesignacoesSalao._round_robin_pairs(lista)
        np_ = len(all_pairs)

        if np_ == 0:
            return f"{lista[0]} / {lista[0]}"

        # Passo 1: par onde nenhum está em assigned E diferente do último
        for j in range(np_):
            a, b = all_pairs[(idx + j) % np_]
            if a not in assigned and b not in assigned and frozenset([a, b]) != ultimo_par:
                return f"{a} / {b}"

        # Passo 2: relaxa restrição de último par (mas ainda evita assigned)
        for j in range(np_):
            a, b = all_pairs[(idx + j) % np_]
            if a not in assigned and b not in assigned:
                return f"{a} / {b}"

        # Passo 3: relaxa assigned, evita último par
        for j in range(np_):
            a, b = all_pairs[(idx + j) % np_]
            if not (a in assigned and b in assigned) and frozenset([a, b]) != ultimo_par:
                return f"{a} / {b}"

        # Passo 4: relaxa tudo
        for j in range(np_):
            a, b = all_pairs[(idx + j) % np_]
            if not (a in assigned and b in assigned):
                return f"{a} / {b}"

        a, b = all_pairs[idx % np_]
        return f"{a} / {b}"

    @staticmethod
    def add_assigned(nome, assigned):
        for n in (nome or "").split("/"):
            n = n.strip()
            if n:
                assigned.add(n)

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
    def gerar_designacoes(semanas_info):
        """
        Gera designações automáticas para cada data em semanas_info.
        Garante que nenhum irmão tenha duas funções no mesmo dia.
        """
        av  = listar_candidatos_salao_ordenados("audio_video")
        mic = listar_candidatos_salao_ordenados("microfone")
        ind = listar_candidatos_salao_ordenados("indicador")

        result = []
        ultimo_mic = None
        ultimo_ind = None

        for i, s in enumerate(semanas_info):
            assigned = set()

            audio = DesignacoesSalao.pick_one(av, i, assigned)
            DesignacoesSalao.add_assigned(audio, assigned)

            video = DesignacoesSalao.pick_one(av, i + max(len(av) // 2, 1), assigned)
            DesignacoesSalao.add_assigned(video, assigned)

            microfone = DesignacoesSalao.pick_two(mic, i, assigned, ultimo_mic)
            DesignacoesSalao.add_assigned(microfone, assigned)
            ultimo_mic = frozenset(n.strip() for n in microfone.split("/") if n.strip())

            indicadores = DesignacoesSalao.pick_two(ind, i, assigned, ultimo_ind)
            ultimo_ind = frozenset(n.strip() for n in indicadores.split("/") if n.strip())

            result.append({
                **s,
                "audio":       audio,
                "video":       video,
                "microfone":   microfone,
                "indicadores": indicadores,
            })
        return result
