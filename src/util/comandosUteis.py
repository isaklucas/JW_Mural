import unicodedata


class ComandosUteis:

    def TitleCase(texto):
        """Normaliza o nome exibido: colapsa espaços e aplica Title Case.

        Mantém acentos — quem compara/deduplica é o `chave_nome`.
        """
        if texto is None:
            return ""
        texto = " ".join(str(texto).split())
        return texto.lower().title()

    def normalizar_nome(texto):
        """Nome canônico como fica gravado no banco e aparece nos documentos."""
        return ComandosUteis.TitleCase(texto)

    def chave_nome(texto):
        """Chave de deduplicação: sem acento, minúsculo, espaços colapsados.

        "José  da Silva", "jose da silva " e "JOSE DA SILVA" -> "jose da silva".
        Usada só para comparar/localizar publicadores, nunca para exibir.
        """
        nome = ComandosUteis.normalizar_nome(texto)
        decomposto = unicodedata.normalize("NFKD", nome)
        sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
        return sem_acento.lower()
