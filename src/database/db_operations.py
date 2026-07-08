import datetime
import logging
from .db_connection import db_connection
import util.comandosUteis as util

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseOperations:
    def __init__(self):
        self.db = db_connection.get_connection()
        self.db_type = db_connection.db_type
        
        # Criar índices se for MongoDB
        if self.db_type == 'mongodb':
            try:
                # Criar índice composto para ano e semana
                collection_reunioes = self.db['reunioes']
                collection_reunioes.create_index([("ano", 1), ("semana", 1)], unique=True)
                # Índice para reunioes_final_semana
                collection_fs = self.db['reunioes_final_semana']
                collection_fs.create_index([("ano", 1), ("mes", 1)], unique=True)
                # Índice para designacoes_salao
                collection_salao = self.db['designacoes_salao']
                collection_salao.create_index([("ano", 1), ("mes", 1)], unique=True)
                logger.info("Índices criados/verificados com sucesso")
            except Exception as e:
                logger.error(f"Erro ao criar índices: {str(e)}")

    def post(self, nome, batizado, sexo="Masculino", permissoes=None):
        """
        Adiciona um novo publicador ao banco de dados
        
        Args:
            nome: Nome do publicador
            batizado: Status de batismo (boolean)
            sexo: Sexo do publicador - "Masculino" ou "Feminino" (padrão: "Masculino")
            permissoes: Dicionário com permissões {"parte_escola": bool, "oracao": bool, "leitura_livro": bool}
                       Se None, usa valores padrão (todos True)
        """
        try:
            now = datetime.datetime.now().isoformat()
            nome = util.ComandosUteis.TitleCase(nome)
            
            # Valores padrão para permissões se não fornecidas
            if permissoes is None:
                permissoes = {
                    "parte_escola": True,
                    "oracao": True,
                    "leitura_livro": True,
                    "leitura_sentinela": False,
                    "presidente_final_semana": False
                }
            # Garantir que permissoes de final de semana existem em permissoes existentes
            if "leitura_sentinela" not in permissoes:
                permissoes["leitura_sentinela"] = False
            if "presidente_final_semana" not in permissoes:
                permissoes["presidente_final_semana"] = False
            if "audio_video" not in permissoes:
                permissoes["audio_video"] = False
            if "indicador" not in permissoes:
                permissoes["indicador"] = False
            if "microfone" not in permissoes:
                permissoes["microfone"] = False
            
            item = {
                "nome": nome.strip(),
                "batizado": batizado,
                "Anciao": False,
                "Servo_Ministerial": False,
                "sexo": sexo,
                "permissoes": permissoes,
                "data_inclusao": now,
                "ultima_parte": "",
                "historico": []
            }
            
            logger.info(f"Adicionando novo publicador {nome}")
            
            if self.db_type == 'mongodb':
                self.db.insert_one(item)
            else:
                self.db.put_item(Item=item)
                
        except Exception as e:
            logger.error(f"Erro ao adicionar publicador: {str(e)}")
            raise

    def getAllPub(self):
        try:
            if self.db_type == 'mongodb':
                return list(self.db.find({}, {'_id': 0}))
            else:
                response = self.db.scan()
                return response['Items']
        except Exception as e:
            logger.error(f"Erro ao buscar publicadores: {str(e)}")
            return []

    def delete(self, nome):
        try:
            nome = util.ComandosUteis.TitleCase(nome)
            logger.info(f"Removendo publicador {nome}")
            
            if self.db_type == 'mongodb':
                result = self.db.delete_one({"nome": nome.strip()})
                if result.deleted_count == 0:
                    logger.warning(f"Publicador {nome} não encontrado")
            else:
                self.db.delete_item(Key={"nome": nome.strip()})
                
        except Exception as e:
            logger.error(f"Erro ao remover publicador: {str(e)}")
            raise

    def update_parte(self, nome, parte, semana):
        try:
            # Se houver /, divide os nomes e processa cada um
            if '/' in nome:
                nomes = [n.strip() for n in nome.split('/')]
                for nome_individual in nomes:
                    if nome_individual:  # Verifica se não está vazio
                        self._update_parte_individual(nome_individual, parte, semana)
                return
            else:
                self._update_parte_individual(nome, parte, semana)
                
        except Exception as e:
            logger.error(f"Erro ao atualizar publicador: {str(e)}")
            raise
            
    def _update_parte_individual(self, nome, parte, semana):
        """
        Atualiza a parte de um único publicador
        """
        try:
            nome = util.ComandosUteis.TitleCase(nome)
            logger.info(f"Atualizando publicador {nome}")
            
            # Primeiro verifica se o publicador existe
            if self.db_type == 'mongodb':
                publicador = self.db.find_one({"nome": nome.strip()})
                if not publicador:
                    # Se não existe, chama a função para verificar inclusão
                    from util.janelas import janelas
                    janelas.verificarInclusaoPublicador(nome, parte, semana)
                    return
                    
            ano = datetime.datetime.now().year
            data_participacao = f"{semana} de {ano}"
            
            if self.db_type == 'mongodb':
                result = self.db.update_one(
                    {"nome": nome.strip()},
                    {
                        "$set": {"ultima_parte": data_participacao},
                        "$push": {
                            "historico": {
                                "parte": parte,
                                "data": data_participacao
                            }
                        }
                    }
                )
                if result.matched_count == 0:
                    logger.warning(f"Publicador {nome} não encontrado")
            else:
                self.db.update_item(
                    Key={"nome": nome.strip()},
                    UpdateExpression="set ultima_parte = :p, historico = list_append(if_not_exists(historico, :empty_list), :h)",
                    ExpressionAttributeValues={
                        ":p": data_participacao,
                        ":h": [{"parte": parte, "data": data_participacao}],
                        ":empty_list": []
                    }
                )
                
        except Exception as e:
            logger.error(f"Erro ao atualizar publicador individual: {str(e)}")
            raise

    def limpar_historico_todos(self):
        try:
            logger.info("Limpando histórico de todos os publicadores")
            
            if self.db_type == 'mongodb':
                self.db.update_many(
                    {},
                    {
                        "$set": {
                            "ultima_parte": "",
                            "historico": []
                        }
                    }
                )
            else:
                response = self.db.scan()
                for item in response['Items']:
                    self.db.update_item(
                        Key={"nome": item['nome']},
                        UpdateExpression="set ultima_parte = :p, historico = :empty_list",
                        ExpressionAttributeValues={
                            ":p": "",
                            ":empty_list": []
                        }
                    )
                    
        except Exception as e:
            logger.error(f"Erro ao limpar histórico: {str(e)}")
            raise

    def resetar_todo_historico(self):
        """
        Reseta todo o histórico: limpa o campo historico de todos os publicadores
        e remove todos os registros da tabela de reuniões.
        
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            logger.warning("Iniciando reset completo do histórico - esta operação é irreversível!")
            
            if self.db_type != 'mongodb':
                logger.warning("Reset completo de histórico só está disponível para MongoDB")
                return {
                    "success": False,
                    "message": "Reset completo de histórico só está disponível para MongoDB"
                }
            
            # Limpar histórico de todos os publicadores
            logger.info("Limpando histórico de todos os publicadores...")
            resultado_publicadores = self.db.update_many(
                {},
                {
                    "$set": {
                        "ultima_parte": "",
                        "historico": []
                    }
                }
            )
            logger.info(f"Histórico limpo para {resultado_publicadores.modified_count} publicadores")
            
            # Limpar todas as reuniões
            logger.info("Removendo todas as reuniões...")
            collection_reunioes = self.db['reunioes']
            resultado_reunioes = collection_reunioes.delete_many({})
            logger.info(f"{resultado_reunioes.deleted_count} reuniões removidas")
            
            mensagem = f"Histórico resetado com sucesso! {resultado_publicadores.modified_count} publicadores atualizados e {resultado_reunioes.deleted_count} reuniões removidas."
            
            logger.info(mensagem)
            
            return {
                "success": True,
                "message": mensagem,
                "publicadores_atualizados": resultado_publicadores.modified_count,
                "reunioes_removidas": resultado_reunioes.deleted_count
            }
            
        except Exception as e:
            logger.error(f"Erro ao resetar histórico completo: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"Erro ao resetar histórico: {str(e)}"
            }

    def salvar_reuniao(self, dados_reuniao):
        """
        Salva ou atualiza uma reunião no banco de dados.
        A chave única é a combinação de ano e semana.
        """
        try:
            # Validar campos obrigatórios
            campos_obrigatorios = [
                'ano', 'semana', 'data_reuniao', 'presidente', 'oracao_inicial',
                'tesouro', 'joias_espirituais', 'leitura_biblia', 'escola',
                'nossa_vida_crista', 'estudo_congregacao', 'oracao_final'
            ]
            
            campos_escola = ['primeira_parte', 'segunda_parte', 'terceira_parte', 'quarta_parte']
            campos_nvc = ['primeira_parte', 'segunda_parte']
            
            # Verificar campos principais
            for campo in campos_obrigatorios:
                if campo not in dados_reuniao:
                    raise ValueError(f"Campo obrigatório ausente: {campo}")
            
            # Verificar campos da escola
            for campo in campos_escola:
                if campo not in dados_reuniao['escola']:
                    raise ValueError(f"Campo obrigatório ausente em 'escola': {campo}")
            
            # Verificar campos da nossa vida cristã
            for campo in campos_nvc:
                if campo not in dados_reuniao['nossa_vida_crista']:
                    raise ValueError(f"Campo obrigatório ausente em 'nossa_vida_crista': {campo}")
            
            # Extrair ano e semana dos dados
            ano = dados_reuniao['ano']
            semana = dados_reuniao['semana'].upper()  # Garantir que a semana está em maiúsculo
            
            # Criar filtro para buscar reunião existente
            filtro = {
                "ano": ano,
                "semana": semana
            }
            
            # Preparar dados para atualização/inserção
            dados_atualizados = {
                "$set": {
                    "ano": ano,
                    "semana": semana,
                    "data_reuniao": dados_reuniao['data_reuniao'],  # Mantendo o campo original
                    "presidente": dados_reuniao['presidente'],
                    "oracao_inicial": dados_reuniao['oracao_inicial'],
                    "tesouro": dados_reuniao['tesouro'],
                    "joias_espirituais": dados_reuniao['joias_espirituais'],
                    "leitura_biblia": dados_reuniao['leitura_biblia'],
                    "escola": {
                        "primeira_parte": dados_reuniao['escola']['primeira_parte'],
                        "segunda_parte": dados_reuniao['escola']['segunda_parte'],
                        "terceira_parte": dados_reuniao['escola']['terceira_parte'],
                        "quarta_parte": dados_reuniao['escola']['quarta_parte']
                    },
                    "nossa_vida_crista": {
                        "primeira_parte": dados_reuniao['nossa_vida_crista']['primeira_parte'],
                        "segunda_parte": dados_reuniao['nossa_vida_crista']['segunda_parte']
                    },
                    "estudo_congregacao": dados_reuniao['estudo_congregacao'],
                    "oracao_final": dados_reuniao['oracao_final'],
                    "ultima_atualizacao": datetime.datetime.now().isoformat()
                }
            }
            
            # Log para debug
            logger.info(f"Salvando reunião - Ano: {ano}, Semana: {semana}")
            
            # Atualizar ou inserir (upsert=True)
            collection_reunioes = self.db['reunioes']
            resultado = collection_reunioes.update_one(
                filtro,
                dados_atualizados,
                upsert=True
            )
            
            # Atualizar histórico dos publicadores participantes
            self._atualizar_historico_publicadores(dados_reuniao)
            
            return {
                "success": True,
                "message": "Reunião atualizada" if resultado.matched_count > 0 else "Reunião criada",
                "operacao": "update" if resultado.matched_count > 0 else "insert"
            }
            
        except ValueError as ve:
            logger.error(f"Erro de validação ao salvar reunião: {str(ve)}")
            return {
                "success": False,
                "message": f"Erro de validação: {str(ve)}"
            }
        except Exception as e:
            logger.error(f"Erro ao salvar reunião: {str(e)}")
            return {
                "success": False,
                "message": f"Erro ao salvar reunião: {str(e)}"
            }

    def _atualizar_historico_publicadores(self, dados_reuniao):
        """
        Atualiza o histórico de participação dos publicadores envolvidos na reunião
        """
        try:
            data_participacao = f"Semana {dados_reuniao['semana']} de {dados_reuniao['ano']}"
            
            # Lista de todas as participações
            participacoes = [
                (dados_reuniao['presidente'], "Presidente"),
                (dados_reuniao['oracao_inicial'], "Oração Inicial"),
                (dados_reuniao['tesouro'], "Tesouro"),
                (dados_reuniao['joias_espirituais'], "Joias Espirituais"),
                (dados_reuniao['leitura_biblia'], "Leitura da Bíblia"),
                (dados_reuniao['escola']['primeira_parte'], "Escola - Primeira Parte"),
                (dados_reuniao['escola']['segunda_parte'], "Escola - Segunda Parte"),
                (dados_reuniao['escola']['terceira_parte'], "Escola - Terceira Parte"),
                (dados_reuniao['escola']['quarta_parte'], "Escola - Quarta Parte"),
                (dados_reuniao['nossa_vida_crista']['primeira_parte'], "Nossa Vida Cristã - Primeira Parte"),
                (dados_reuniao['nossa_vida_crista']['segunda_parte'], "Nossa Vida Cristã - Segunda Parte"),
                (dados_reuniao['estudo_congregacao'], "Estudo de Congregação"),
                (dados_reuniao['oracao_final'], "Oração Final")
            ]
            
            # Conjunto para controlar combinações (publicador, parte) já processadas
            # Isso evita que o mesmo publicador faça a mesma parte duas vezes
            combinacoes_processadas = set()
            # Dicionário para registrar todas as partes atribuídas a cada publicador
            participantes_partes = {}
            
            # Processar cada participação
            for nome, parte in participacoes:
                if nome and nome != "não possui":
                    # Se houver /, divide os nomes e processa cada um
                    if '/' in nome:
                        nomes = [n.strip() for n in nome.split('/')]
                        for nome_individual in nomes:
                            if nome_individual:  # Verifica se não está vazio
                                nome_formatado = util.ComandosUteis.TitleCase(nome_individual.strip())
                                
                                # Criar chave única: (publicador, parte)
                                chave = (nome_formatado, parte)
                                
                                # Verificar se esta combinação já foi processada
                                if chave in combinacoes_processadas:
                                    logger.warning(f"DUPLICAÇÃO DETECTADA: {nome_formatado} já foi designado para '{parte}' na mesma reunião. Ignorando duplicação.")
                                    continue
                                
                                # Marcar como processada
                                combinacoes_processadas.add(chave)
                                
                                # Registrar todas as partes deste publicador
                                if nome_formatado in participantes_partes:
                                    participantes_partes[nome_formatado].append(parte)
                                else:
                                    participantes_partes[nome_formatado] = [parte]
                                    
                                # Atualizar histórico
                                self._atualizar_historico_individual(nome_individual, parte, data_participacao)
                    else:
                        nome_formatado = util.ComandosUteis.TitleCase(nome.strip())
                        
                        # Criar chave única: (publicador, parte)
                        chave = (nome_formatado, parte)
                        
                        # Verificar se esta combinação já foi processada
                        if chave in combinacoes_processadas:
                            logger.warning(f"DUPLICAÇÃO DETECTADA: {nome_formatado} já foi designado para '{parte}' na mesma reunião. Ignorando duplicação.")
                            continue
                        
                        # Marcar como processada
                        combinacoes_processadas.add(chave)
                        
                        # Registrar todas as partes deste publicador
                        if nome_formatado in participantes_partes:
                            participantes_partes[nome_formatado].append(parte)
                        else:
                            participantes_partes[nome_formatado] = [parte]
                            
                        # Atualizar histórico
                        self._atualizar_historico_individual(nome, parte, data_participacao)
            
            # Exibir informações sobre publicadores com múltiplas partes
            for nome, partes in participantes_partes.items():
                if len(partes) > 1:
                    logger.info(f"Publicador {nome} designado para múltiplas partes na mesma reunião: {', '.join(partes)}")
                    
        except Exception as e:
            logger.error(f"Erro ao atualizar histórico dos publicadores: {str(e)}")
            raise
            
    def _atualizar_historico_individual(self, nome, parte, data_participacao):
        """
        Atualiza o histórico de um único publicador
        """
        try:
            nome = util.ComandosUteis.TitleCase(nome)
            
            if self.db_type == 'mongodb':
                # Verificar se o publicador existe
                publicador = self.db.find_one({"nome": nome.strip()})
                
                if publicador:
                    # Verificar se já existe um registro idêntico no histórico
                    historico = publicador.get('historico', [])
                    entrada_duplicada = False
                    
                    for entrada in historico:
                        # Verifica se já existe um registro para a mesma parte e mesma data
                        if entrada.get('parte') == parte and entrada.get('data') == data_participacao:
                            entrada_duplicada = True
                            logger.warning(f"Registro duplicado no histórico: {nome} já tem '{parte}' em '{data_participacao}'. Ignorando.")
                            break
                    
                    if not entrada_duplicada:
                        # Só atualiza se não for duplicado
                        result = self.db.update_one(
                            {"nome": nome.strip()},
                            {
                                "$set": {"ultima_parte": data_participacao},
                                "$push": {
                                    "historico": {
                                        "parte": parte,
                                        "data": data_participacao
                                    }
                                }
                            }
                        )
                else:
                    # Se o publicador não existir, tenta criar
                    from util.janelas import janelas
                    janelas.verificarInclusaoPublicador(nome, parte, data_participacao)
            else:
                # Para DynamoDB
                # Primeiro verificar se o publicador existe
                response = self.db.get_item(Key={"nome": nome.strip()})
                item = response.get('Item')
                
                if item:
                    # Verificar duplicação
                    historico = item.get('historico', [])
                    entrada_duplicada = False
                    
                    for entrada in historico:
                        if entrada.get('parte') == parte and entrada.get('data') == data_participacao:
                            entrada_duplicada = True
                            logger.warning(f"Registro duplicado no histórico: {nome} já tem '{parte}' em '{data_participacao}'. Ignorando.")
                            break
                    
                    if not entrada_duplicada:
                        # Atualizar se não for duplicado
                        self.db.update_item(
                            Key={"nome": nome.strip()},
                            UpdateExpression="set ultima_parte = :p, historico = list_append(if_not_exists(historico, :empty_list), :h)",
                            ExpressionAttributeValues={
                                ":p": data_participacao,
                                ":h": [{"parte": parte, "data": data_participacao}],
                                ":empty_list": []
                            }
                        )
                else:
                    # Se o publicador não existir, deve ser criado ou notificado
                    logger.warning(f"Publicador {nome} não encontrado no DynamoDB")
                    # Aqui pode ser adicionada uma lógica para criar o publicador ou notificar
        
        except Exception as e:
            logger.error(f"Erro ao atualizar histórico individual: {str(e)}")
            raise

    def buscar_reuniao(self, ano, semana):
        """
        Busca uma reunião específica pelo ano e semana.
        Tenta diferentes variações de formatação para encontrar a reunião.
        """
        try:
            collection_reunioes = self.db['reunioes']
            # Adicionar log para debug
            logger.info(f"Buscando reunião - Ano: {ano}, Semana: {semana}")
            
            # Normalizar a semana para maiúsculas e remover espaços extras
            semana_normalizada = semana.upper().strip()
            
            # Tentar diferentes variações de formatação
            # No banco pode estar: "9-15 DE JUNHO" ou "9–15 DE JUNHO" ou "9 A 15 DE JUNHO"
            variacoes = [
                semana_normalizada,  # Exatamente como recebido
                semana_normalizada.replace('–', '-'),  # En-dash para hífen simples
                semana_normalizada.replace('-', '–'),  # Hífen simples para en-dash
                semana_normalizada.replace(' A ', '-'),  # " A " para hífen
                semana_normalizada.replace(' A ', '–'),  # " A " para en-dash
            ]
            
            # Remover duplicatas mantendo a ordem
            variacoes = list(dict.fromkeys(variacoes))
            
            reuniao = None
            for variacao in variacoes:
                logger.info(f"Tentando buscar com semana: {variacao}")
                reuniao = collection_reunioes.find_one({
                    "ano": ano,
                    "semana": variacao
                })
                if reuniao:
                    logger.info(f"Reunião encontrada com variação: {variacao}")
                    break
            
            # Log do resultado
            if reuniao:
                reuniao['_id'] = str(reuniao['_id'])  # Converter ObjectId para string
            else:
                logger.warning(f"Nenhuma reunião encontrada para semana: {semana_normalizada} (tentou {len(variacoes)} variações)")
                
            return reuniao
            
        except Exception as e:
            logger.error(f"Erro ao buscar reunião: {str(e)}")
            return None

    def buscar_historico_publicador(self, nome_publicador):
        """
        Busca o histórico de participação de um publicador diretamente do campo 'historico' no documento do publicador.
        Retorna o array de histórico que está armazenado no banco de dados.
        """
        try:
            nome_publicador = util.ComandosUteis.TitleCase(nome_publicador.strip())
            
            # Buscar o publicador no banco de dados
            if self.db_type == 'mongodb':
                publicador = self.db.find_one({"nome": nome_publicador})
            else:
                # Para DynamoDB
                response = self.db.get_item(Key={"nome": nome_publicador})
                publicador = response.get('Item')
            
            if not publicador:
                logger.warning(f"Publicador {nome_publicador} não encontrado")
                return []
            
            # Obter o array de histórico diretamente do documento do publicador
            historico = publicador.get('historico', [])
            
            if not historico:
                logger.info(f"Publicador {nome_publicador} não possui histórico")
                return []
            
            # Retornar o histórico como está no banco (array de objetos com 'parte' e 'data')
            logger.info(f"Histórico encontrado para {nome_publicador}: {len(historico)} registros")
            return historico
            
        except Exception as e:
            logger.error(f"Erro ao buscar histórico do publicador: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def calcular_tempo_sem_fazer(self, nome_publicador, parte):
        """
        Calcula quantas semanas se passaram desde a última vez que o publicador fez uma parte específica.
        
        Args:
            nome_publicador: Nome do publicador
            parte: Nome da parte (ex: "Presidente", "Oração Inicial", etc.)
            
        Returns:
            int: Número de semanas desde a última participação. 
                 Retorna 999 se nunca fez essa parte.
                 Retorna 0 se fez recentemente (na mesma semana).
        """
        try:
            historico = self.buscar_historico_publicador(nome_publicador)
            
            if not historico:
                # Nunca fez nenhuma parte, retornar valor alto para priorizar
                return 999
            
            # Filtrar histórico pela parte específica
            participacoes_parte = [h for h in historico if h.get('parte') == parte]
            
            if not participacoes_parte:
                # Nunca fez essa parte específica
                return 999
            
            # Encontrar a data mais recente dessa parte
            # Formato da data: "Semana X-Y DE MÊS de ANO" ou "X-Y DE MÊS de ANO"
            ultima_data_str = None
            ultima_data_obj = None
            
            for participacao in participacoes_parte:
                data_str = participacao.get('data', '')
                if not data_str:
                    continue
                
                # Tentar parsear a data
                try:
                    # Remover "Semana " se existir
                    data_limpa = data_str.replace("Semana ", "").strip()
                    
                    # Extrair ano
                    if " de " in data_limpa:
                        partes_data = data_limpa.split(" de ")
                        if len(partes_data) >= 2:
                            ano_str = partes_data[-1].strip()
                            try:
                                ano = int(ano_str)
                                
                                # Extrair mês e dias
                                mes_dias = partes_data[0].strip()
                                
                                # Mapeamento de meses
                                meses_pt = {
                                    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
                                    'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
                                    'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
                                }
                                
                                # Procurar o mês na string
                                mes_num = None
                                for mes_nome, mes_valor in meses_pt.items():
                                    if mes_nome.upper() in mes_dias.upper():
                                        mes_num = mes_valor
                                        break
                                
                                if mes_num:
                                    # Extrair o primeiro dia (antes do hífen ou en-dash)
                                    import re
                                    dias_match = re.search(r'(\d+)[\s\-–]+', mes_dias)
                                    if dias_match:
                                        try:
                                            dia = int(dias_match.group(1))
                                            
                                            # Criar data da segunda-feira da semana
                                            data_semana = datetime.datetime(ano, mes_num, dia)
                                            
                                            # Se ainda não temos uma data ou esta é mais recente
                                            if ultima_data_obj is None or data_semana > ultima_data_obj:
                                                ultima_data_obj = data_semana
                                                ultima_data_str = data_str
                                        except (ValueError, IndexError) as e:
                                            logger.warning(f"Erro ao parsear data '{data_str}': {str(e)}")
                                            continue
                                    
                            except ValueError:
                                continue
                                
                except Exception as e:
                    logger.warning(f"Erro ao processar data '{data_str}': {str(e)}")
                    continue
            
            if ultima_data_obj is None:
                # Não conseguiu parsear nenhuma data, retornar valor alto
                return 999
            
            # Calcular semanas desde a última participação
            hoje = datetime.datetime.now()
            diferenca = hoje - ultima_data_obj
            semanas = diferenca.days // 7
            
            # Se for negativo (data futura), retornar 0
            if semanas < 0:
                semanas = 0
            
            logger.debug(f"Publicador {nome_publicador} fez '{parte}' há {semanas} semanas")
            return semanas
            
        except Exception as e:
            logger.error(f"Erro ao calcular tempo sem fazer para {nome_publicador} na parte {parte}: {str(e)}")
            import traceback
            traceback.print_exc()
            # Em caso de erro, retornar valor médio para não priorizar nem despriorizar
            return 50

    def listar_reunioes(self, ano=None, semana=None, limite=50, pagina=1):
        """
        Lista as reuniões com opção de filtro por ano e semana.
        Ordena por data_reuniao em ordem decrescente (mais recente primeiro).
        """
        try:
            collection_reunioes = self.db['reunioes']
            
            # Construir query baseada nos filtros
            query = {}
            if ano is not None:
                query["ano"] = ano
            if semana is not None:
                query["semana"] = semana
            
            # Se não há filtros específicos, usar limite maior para retornar todas as reuniões
            if ano is None and semana is None:
                limite = 10000  # Limite alto para retornar todas as reuniões
            
            # Calcular skip para paginação
            skip = (pagina - 1) * limite
            
            # Buscar reuniões ordenadas por data_reuniao em ordem decrescente (mais recente primeiro)
            # Se não houver data_reuniao, usar ordenação por ano e semana como fallback
            reunioes = collection_reunioes.find(query) \
                                        .sort("data_reuniao", -1) \
                                        .skip(skip) \
                                        .limit(limite)
            
            # Converter ObjectId para string e retornar lista
            resultado = []
            for reuniao in reunioes:
                reuniao['_id'] = str(reuniao['_id'])
                resultado.append(reuniao)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao listar reuniões: {str(e)}")
            return None

    def buscar_reuniao_por_data(self, data_str):
        """Busca uma reunião pela data formatada (ex: '31 de março a 7 de abril')"""
        try:
            # Extrair o mês e dia inicial da string
            partes = data_str.split(' de ')
            dia_inicio = int(partes[0])
            mes = partes[1].split(' a ')[0]
            
            # Converter mês para número
            meses = {
                'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
                'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
                'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
            }
            mes_num = meses[mes.lower()]
            
            # Buscar reuniões do mês
            collection_reunioes = self.db['reunioes']
            reunioes = collection_reunioes.find({
                "$expr": {
                    "$and": [
                        {"$eq": [{"$month": {"$dateFromString": {"dateString": "$data_reuniao"}}}, mes_num]},
                        {"$eq": [{"$dayOfMonth": {"$dateFromString": {"dateString": "$data_reuniao"}}}, dia_inicio]}
                    ]
                }
            })
            
            # Retornar a primeira reunião encontrada
            reuniao = next(reunioes, None)
            if reuniao:
                reuniao['_id'] = str(reuniao['_id'])  # Converter ObjectId para string
            return reuniao
            
        except Exception as e:
            logger.error(f"Erro ao buscar reunião por data: {str(e)}")
            return None

    def update_batismo(self, nome, batizado):
        """
        Atualiza o status de batismo de um publicador
        """
        try:
            collection_publicadores = self.db['publicadores']
            resultado = collection_publicadores.update_one(
                {"nome": nome},
                {"$set": {"batizado": batizado}}
            )
            
            if resultado.matched_count > 0:
                logger.info(f"Status de batismo atualizado para {nome}")
                return True
            else:
                logger.warning(f"Publicador {nome} não encontrado")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao atualizar status de batismo: {str(e)}")
            return False
    
    def update_publicador(self, nome, batizado=None, anciao=None, servo_ministerial=None, 
                         sexo=None, permissoes=None):
        """
        Atualiza os campos de um publicador
        
        Args:
            nome: Nome do publicador
            batizado: Status de batismo (opcional)
            anciao: Status de ancião (opcional)
            servo_ministerial: Status de servo ministerial (opcional)
            sexo: Sexo do publicador - "Masculino" ou "Feminino" (opcional)
            permissoes: Dicionário com permissões {"parte_escola": bool, "oracao": bool, "leitura_livro": bool} (opcional)
        """
        try:
            # Verificar se self.db tem o método find (é uma collection)
            if hasattr(self.db, 'find'):
                # self.db é uma collection, usar diretamente
                collection_publicadores = self.db
            else:
                # self.db pode ser o database, acessar a collection
                collection_publicadores = self.db['publicadores']
            
            # Construir dicionário de atualização apenas com os campos fornecidos
            update_data = {}
            if batizado is not None:
                update_data["batizado"] = batizado
            if anciao is not None:
                update_data["Anciao"] = anciao
            if servo_ministerial is not None:
                update_data["Servo_Ministerial"] = servo_ministerial
            if sexo is not None:
                update_data["sexo"] = sexo
            if permissoes is not None:
                update_data["permissoes"] = permissoes
            
            if not update_data:
                logger.warning("Nenhum campo para atualizar")
                return False
            
            resultado = collection_publicadores.update_one(
                {"nome": nome},
                {"$set": update_data}
            )
            
            if resultado.matched_count > 0:
                logger.info(f"Publicador {nome} atualizado: {update_data}")
                return True
            else:
                logger.warning(f"Publicador {nome} não encontrado")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao atualizar publicador: {str(e)}")
            return False

    def contar_reunioes_por_publicador(self):
        """
        Conta em quantas reuniões cada publicador participou, agrupando por mês
        """
        try:
            print("Iniciando método contar_reunioes_por_publicador...")
            
            if self.db_type != 'mongodb':
                print("Tipo de banco de dados não é MongoDB. Tipo:", self.db_type)
                return {}
                
            collection_reunioes = self.db['reunioes']
            collection_publicadores = self.db['publicadores']
            
            # Buscar todos os publicadores
            publicadores = list(collection_publicadores.find({}, {"nome": 1, "_id": 0}))
            print(f"Publicadores encontrados: {len(publicadores)}")
            
            if not publicadores:
                print("Nenhum publicador encontrado no banco de dados.")
                return {}
                
            nomes_publicadores = [p["nome"] for p in publicadores]
            
            # Buscar todas as reuniões
            reunioes = list(collection_reunioes.find({}))
            print(f"Reuniões encontradas: {len(reunioes)}")
            
            if not reunioes:
                print("Nenhuma reunião encontrada no banco de dados.")
                return {}
            
            # Dicionário para armazenar participações por publicador e mês
            participacoes = {}
            
            # Processar cada reunião
            for i, reuniao in enumerate(reunioes):
                # Obter dados básicos da reunião para debug
                semana = reuniao.get('semana', 'Desconhecida')
                ano = reuniao.get('ano', 'Desconhecido')
                
                print(f"Processando reunião {i+1}/{len(reunioes)}: Semana {semana} de {ano}")
                
                # Obter ano e mês da reunião
                try:
                    data_reuniao = datetime.datetime.fromisoformat(reuniao.get('data_reuniao', ''))
                    ano = data_reuniao.year
                    mes = data_reuniao.month
                    
                    # Criar chave para o mês
                    chave_mes = f"{mes:02d}/{ano}"
                    print(f"  Data da reunião: {data_reuniao}, Chave do mês: {chave_mes}")
                except Exception as e:
                    # Se não conseguir extrair data, usar semana/ano
                    semana = reuniao.get('semana', 'Desconhecida')
                    ano = reuniao.get('ano', 9999)
                    chave_mes = f"{semana}/{ano}"
                    print(f"  Erro ao processar data: {e}, usando chave alternativa: {chave_mes}")
                
                # Lista de todos os participantes nesta reunião
                participantes = []
                
                # Adicionar presidente
                if reuniao.get('presidente') and reuniao.get('presidente') != "não possui":
                    if '/' in reuniao['presidente']:
                        participantes.extend([p.strip() for p in reuniao['presidente'].split('/')])
                    else:
                        participantes.append(reuniao['presidente'])
                
                # Adicionar oração inicial
                if reuniao.get('oracao_inicial') and reuniao.get('oracao_inicial') != "não possui":
                    if '/' in reuniao['oracao_inicial']:
                        participantes.extend([p.strip() for p in reuniao['oracao_inicial'].split('/')])
                    else:
                        participantes.append(reuniao['oracao_inicial'])
                
                # Adicionar tesouro
                if reuniao.get('tesouro') and reuniao.get('tesouro') != "não possui":
                    if '/' in reuniao['tesouro']:
                        participantes.extend([p.strip() for p in reuniao['tesouro'].split('/')])
                    else:
                        participantes.append(reuniao['tesouro'])
                
                # Adicionar joias espirituais
                if reuniao.get('joias_espirituais') and reuniao.get('joias_espirituais') != "não possui":
                    if '/' in reuniao['joias_espirituais']:
                        participantes.extend([p.strip() for p in reuniao['joias_espirituais'].split('/')])
                    else:
                        participantes.append(reuniao['joias_espirituais'])
                
                # Adicionar leitura da bíblia
                if reuniao.get('leitura_biblia') and reuniao.get('leitura_biblia') != "não possui":
                    if '/' in reuniao['leitura_biblia']:
                        participantes.extend([p.strip() for p in reuniao['leitura_biblia'].split('/')])
                    else:
                        participantes.append(reuniao['leitura_biblia'])
                
                # Adicionar escola ministerial
                if 'escola' in reuniao:
                    for parte in ['primeira_parte', 'segunda_parte', 'terceira_parte', 'quarta_parte']:
                        if parte in reuniao['escola'] and reuniao['escola'][parte] and reuniao['escola'][parte] != "não possui":
                            if '/' in reuniao['escola'][parte]:
                                participantes.extend([p.strip() for p in reuniao['escola'][parte].split('/')])
                            else:
                                participantes.append(reuniao['escola'][parte])
                
                # Adicionar nossa vida cristã
                if 'nossa_vida_crista' in reuniao:
                    for parte in ['primeira_parte', 'segunda_parte']:
                        if parte in reuniao['nossa_vida_crista'] and reuniao['nossa_vida_crista'][parte] and reuniao['nossa_vida_crista'][parte] != "não possui":
                            if '/' in reuniao['nossa_vida_crista'][parte]:
                                participantes.extend([p.strip() for p in reuniao['nossa_vida_crista'][parte].split('/')])
                            else:
                                participantes.append(reuniao['nossa_vida_crista'][parte])
                
                # Adicionar estudo de congregação
                if reuniao.get('estudo_congregacao') and reuniao.get('estudo_congregacao') != "não possui":
                    if '/' in reuniao['estudo_congregacao']:
                        participantes.extend([p.strip() for p in reuniao['estudo_congregacao'].split('/')])
                    else:
                        participantes.append(reuniao['estudo_congregacao'])
                
                # Adicionar oração final
                if reuniao.get('oracao_final') and reuniao.get('oracao_final') != "não possui":
                    if '/' in reuniao['oracao_final']:
                        participantes.extend([p.strip() for p in reuniao['oracao_final'].split('/')])
                    else:
                        participantes.append(reuniao['oracao_final'])
                
                # Padronizar nomes e remover duplicatas
                participantes = [util.ComandosUteis.TitleCase(p) for p in participantes]
                participantes = list(set(participantes))  # Remover duplicatas
                
                print(f"  Participantes encontrados: {len(participantes)}")
                
                # Adicionar participação ao contador para cada publicador
                for nome in participantes:
                    if nome in nomes_publicadores:
                        if nome not in participacoes:
                            participacoes[nome] = {}
                        
                        if chave_mes not in participacoes[nome]:
                            participacoes[nome][chave_mes] = 0
                        
                        # Incrementar o contador (cada publicador só conta uma vez por reunião)
                        participacoes[nome][chave_mes] += 1
            
            print(f"Contagem concluída. Publicadores com participações: {len(participacoes)}")
            return participacoes
                
        except Exception as e:
            logger.error(f"Erro ao contar reuniões por publicador: {str(e)}")
            print(f"ERRO ao contar reuniões por publicador: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}

    def contar_participacoes_unicas_por_reuniao(self):
        """
        Conta quantas reuniões cada publicador participou de forma única.
        Cada reunião conta apenas 1x por publicador, mesmo que ele tenha feito múltiplas partes.
        
        Returns:
            tuple: (total_reunioes, dict) onde dict é {nome_publicador: quantidade_reunioes} ordenado por quantidade
        """
        try:
            if self.db_type != 'mongodb':
                logger.warning("Tipo de banco de dados não é MongoDB. Tipo: " + str(self.db_type))
                return (0, {})
            
            # Acessar collection de reuniões (mesma lógica usada em outros métodos)
            collection_reunioes = self.db['reunioes']
            
            # Buscar todas as reuniões
            reunioes = list(collection_reunioes.find({}))
            total_reunioes = len(reunioes)
            
            logger.info(f"Total de reuniões encontradas: {total_reunioes}")
            
            if not reunioes:
                logger.info("Nenhuma reunião encontrada no banco de dados.")
                return (0, {})
            
            # Dicionário para armazenar participações únicas por publicador
            # {nome_publicador: set de reuniões onde participou}
            participacoes_unicas = {}
            
            # Processar cada reunião
            for i, reuniao in enumerate(reunioes):
                # Identificador único da reunião (ano + semana)
                ano = reuniao.get('ano', '')
                semana = reuniao.get('semana', '')
                id_reuniao = f"{ano}_{semana}"
                
                # Lista de todos os participantes nesta reunião
                participantes = []
                
                # Adicionar presidente
                if reuniao.get('presidente') and reuniao.get('presidente') != "não possui":
                    if '/' in reuniao['presidente']:
                        participantes.extend([p.strip() for p in reuniao['presidente'].split('/')])
                    else:
                        participantes.append(reuniao['presidente'])
                
                # Adicionar oração inicial
                if reuniao.get('oracao_inicial') and reuniao.get('oracao_inicial') != "não possui":
                    if '/' in reuniao['oracao_inicial']:
                        participantes.extend([p.strip() for p in reuniao['oracao_inicial'].split('/')])
                    else:
                        participantes.append(reuniao['oracao_inicial'])
                
                # Adicionar tesouro
                if reuniao.get('tesouro') and reuniao.get('tesouro') != "não possui":
                    if '/' in reuniao['tesouro']:
                        participantes.extend([p.strip() for p in reuniao['tesouro'].split('/')])
                    else:
                        participantes.append(reuniao['tesouro'])
                
                # Adicionar joias espirituais
                if reuniao.get('joias_espirituais') and reuniao.get('joias_espirituais') != "não possui":
                    if '/' in reuniao['joias_espirituais']:
                        participantes.extend([p.strip() for p in reuniao['joias_espirituais'].split('/')])
                    else:
                        participantes.append(reuniao['joias_espirituais'])
                
                # Adicionar leitura da bíblia
                if reuniao.get('leitura_biblia') and reuniao.get('leitura_biblia') != "não possui":
                    if '/' in reuniao['leitura_biblia']:
                        participantes.extend([p.strip() for p in reuniao['leitura_biblia'].split('/')])
                    else:
                        participantes.append(reuniao['leitura_biblia'])
                
                # Adicionar escola ministerial
                if 'escola' in reuniao:
                    for parte in ['primeira_parte', 'segunda_parte', 'terceira_parte', 'quarta_parte']:
                        if parte in reuniao['escola'] and reuniao['escola'][parte] and reuniao['escola'][parte] != "não possui":
                            if '/' in reuniao['escola'][parte]:
                                participantes.extend([p.strip() for p in reuniao['escola'][parte].split('/')])
                            else:
                                participantes.append(reuniao['escola'][parte])
                
                # Adicionar nossa vida cristã
                if 'nossa_vida_crista' in reuniao:
                    for parte in ['primeira_parte', 'segunda_parte']:
                        if parte in reuniao['nossa_vida_crista'] and reuniao['nossa_vida_crista'][parte] and reuniao['nossa_vida_crista'][parte] != "não possui":
                            if '/' in reuniao['nossa_vida_crista'][parte]:
                                participantes.extend([p.strip() for p in reuniao['nossa_vida_crista'][parte].split('/')])
                            else:
                                participantes.append(reuniao['nossa_vida_crista'][parte])
                
                # Adicionar estudo de congregação
                if reuniao.get('estudo_congregacao') and reuniao.get('estudo_congregacao') != "não possui":
                    if '/' in reuniao['estudo_congregacao']:
                        participantes.extend([p.strip() for p in reuniao['estudo_congregacao'].split('/')])
                    else:
                        participantes.append(reuniao['estudo_congregacao'])
                
                # Adicionar oração final
                if reuniao.get('oracao_final') and reuniao.get('oracao_final') != "não possui":
                    if '/' in reuniao['oracao_final']:
                        participantes.extend([p.strip() for p in reuniao['oracao_final'].split('/')])
                    else:
                        participantes.append(reuniao['oracao_final'])
                
                # Padronizar nomes e remover duplicatas (cada publicador conta 1x por reunião)
                participantes_unicos = set([util.ComandosUteis.TitleCase(p) for p in participantes if p.strip()])
                
                # Adicionar participação única para cada publicador nesta reunião
                for nome in participantes_unicos:
                    if nome not in participacoes_unicas:
                        participacoes_unicas[nome] = set()
                    participacoes_unicas[nome].add(id_reuniao)
            
            # Converter sets para contagem
            resultado = {nome: len(reunioes_participadas) for nome, reunioes_participadas in participacoes_unicas.items()}
            
            # Ordenar por quantidade (decrescente)
            resultado_ordenado = dict(sorted(resultado.items(), key=lambda x: x[1], reverse=True))
            
            logger.info(f"Contagem concluída. Publicadores com participações únicas: {len(resultado_ordenado)}")
            
            return (total_reunioes, resultado_ordenado)
            
        except Exception as e:
            logger.error(f"Erro ao contar participações únicas por reunião: {str(e)}")
            import traceback
            traceback.print_exc()
            return (0, {})

    def contar_participacoes_por_parte(self, parte=None):
        """
        Conta as participações de cada publicador, opcionalmente filtradas por parte específica.
        
        Args:
            parte (str, optional): Nome da parte para filtrar. 
                Se None, conta todas as participações.
                Se "__EXCLUIR_ORACOES__", conta todas exceto orações (Oração Inicial e Oração Final).
                Se "__EXCLUIR_FINAL_SEMANA__", conta todas exceto Leitura Sentinela (partes de Final de Semana).
            
        Returns:
            dict: Dicionário com {nome_publicador: quantidade} ordenado por quantidade (decrescente)
        """
        try:
            if self.db_type != 'mongodb':
                logger.warning("Tipo de banco de dados não é MongoDB. Tipo: " + str(self.db_type))
                return {}
            
            # self.db é a collection de publicadores (retornada por get_connection())
            # No pymongo, uma collection tem a propriedade 'database' para acessar o database
            # Mas também podemos usar self.db diretamente já que é a collection de publicadores
            
            # Verificar se self.db tem o método find (é uma collection)
            if hasattr(self.db, 'find'):
                # self.db é uma collection, usar diretamente
                collection_publicadores = self.db
            else:
                # self.db pode ser o database, acessar a collection
                collection_publicadores = self.db['publicadores']
            
            # Buscar todos os publicadores
            publicadores = list(collection_publicadores.find({}, {"nome": 1, "historico": 1, "_id": 0}))
            
            logger.info(f"Publicadores encontrados na busca: {len(publicadores)}")
            
            if not publicadores:
                logger.warning("Nenhum publicador encontrado no banco de dados.")
                # Tentar buscar sem filtro de campos para ver se há dados
                total = collection_publicadores.count_documents({})
                logger.info(f"Total de documentos na collection: {total}")
                return {}
            
            # Dicionário para armazenar contagem de participações
            participacoes = {}
            
            # Lista de partes de oração para excluir
            partes_oracao = ["Oração Inicial", "Oração Final"]
            
            # Processar cada publicador
            for publicador in publicadores:
                nome = publicador.get('nome', '')
                historico = publicador.get('historico', [])
                
                if not nome:
                    continue
                
                # Se parte especificada, filtrar histórico por essa parte
                if parte:
                    if parte == "__EXCLUIR_ORACOES__":
                        # Excluir orações: contar todas as participações exceto orações
                        participacoes_parte = [h for h in historico if h.get('parte') not in partes_oracao]
                        quantidade = len(participacoes_parte)
                    elif parte == "__EXCLUIR_FINAL_SEMANA__":
                        # Excluir Final de Semana: contar todas exceto Leitura Sentinela e Presidente Final Semana
                        partes_final_semana = ["Leitura Sentinela", "Presidente Final Semana"]
                        participacoes_parte = [h for h in historico if h.get('parte') not in partes_final_semana]
                        quantidade = len(participacoes_parte)
                    else:
                        # Filtrar apenas as participações da parte especificada
                        participacoes_parte = [h for h in historico if h.get('parte') == parte]
                        quantidade = len(participacoes_parte)
                else:
                    # Contar todas as participações
                    quantidade = len(historico)
                
                # Adicionar ao dicionário se houver participações
                if quantidade > 0:
                    participacoes[nome] = quantidade
            
            # Ordenar por quantidade (decrescente)
            participacoes_ordenadas = dict(sorted(participacoes.items(), key=lambda x: x[1], reverse=True))
            
            logger.info(f"Contagem concluída. Publicadores com participações: {len(participacoes_ordenadas)}")
            if parte:
                if parte == "__EXCLUIR_ORACOES__":
                    logger.info(f"Filtro aplicado: Todas as Partes Menos Oração")
                elif parte == "__EXCLUIR_FINAL_SEMANA__":
                    logger.info(f"Filtro aplicado: Todas as Partes Menos Final de Semana")
                else:
                    logger.info(f"Filtro aplicado: {parte}")
            
            return participacoes_ordenadas
            
        except Exception as e:
            logger.error(f"Erro ao contar participações por parte: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}

    def _filtrar_publicadores_por_parte_meio(self, parte, publicadores):
        """Aplica os mesmos filtros de selecionar_publicador_para_parte. Retorna lista de dicts publicador."""
        if parte == "Presidente":
            return [p for p in publicadores if p.get("Anciao", False)]
        if parte == "Oração Inicial":
            return [
                p for p in publicadores
                if (p.get("Anciao", False) or p.get("Servo_Ministerial", False) or p.get("permissoes", {}).get("oracao", False))
            ]
        if parte in ["Tesouro", "Joias Espirituais"]:
            return [p for p in publicadores if (p.get("Anciao", False) or p.get("Servo_Ministerial", False))]
        if parte == "Leitura da Bíblia":
            return [
                p for p in publicadores
                if (p.get("sexo") == "Masculino" and p.get("permissoes", {}).get("leitura_livro", False)
                   and not p.get("Anciao", False) and not p.get("Servo_Ministerial", False))
            ]
        if parte in ["Escola - Primeira Parte", "Escola - Segunda Parte", "Escola - Quarta Parte"]:
            return [
                p for p in publicadores
                if (p.get("permissoes", {}).get("parte_escola", False) and not p.get("Anciao", False) and not p.get("Servo_Ministerial", False))
            ]
        if parte == "Escola - Terceira Parte":
            return [
                p for p in publicadores
                if (p.get("sexo") == "Masculino" and p.get("permissoes", {}).get("parte_escola", False) and not p.get("Anciao", False))
            ]
        if parte in ["Nossa Vida Cristã - Primeira Parte", "Nossa Vida Cristã - Segunda Parte"]:
            return [p for p in publicadores if p.get("Anciao", False)]
        if parte == "Estudo de Congregação":
            return [p for p in publicadores if p.get("Anciao", False)]
        return list(publicadores)

    def listar_candidatos_ordenados_por_menos_partecipacoes_meio(self, parte):
        """
        Lista candidatos elegíveis para a parte (meio de semana), ordenados por quem fez MENOS
        participações nessa parte. Usado para seleção automática com distribuição em ciclo.
        """
        try:
            if self.db_type == 'mongodb':
                publicadores = list(self.db.find({}, {"nome": 1, "Anciao": 1, "Servo_Ministerial": 1, "sexo": 1, "permissoes": 1, "_id": 0}))
            else:
                publicadores = list(self.db.scan().get('Items', []))
            if not publicadores:
                return []
            filtrados = self._filtrar_publicadores_por_parte_meio(parte, publicadores)
            nomes = [p.get('nome', '').strip() for p in filtrados if p.get('nome')]
            com_contagem = [(n, self.contar_participacoes_parte(n, parte)) for n in nomes]
            com_contagem.sort(key=lambda x: x[1])
            return [n for n, _ in com_contagem]
        except Exception as e:
            logger.error(f"Erro ao listar candidatos meio por menos participações '{parte}': {str(e)}")
            return []

    def listar_ajudantes_estudo_ordenados_por_menos_partecipacoes(self):
        """Lista publicadores masculinos com permissão de leitura, ordenados por menos participações em Estudo de Congregação (ajudante)."""
        try:
            if self.db_type == 'mongodb':
                publicadores = list(self.db.find({}, {"nome": 1, "sexo": 1, "permissoes": 1, "_id": 0}))
            else:
                publicadores = list(self.db.scan().get('Items', []))
            ajudantes = [
                p for p in publicadores
                if (p.get("sexo") == "Masculino" and p.get("permissoes", {}).get("leitura_livro", False))
            ]
            nomes = [p.get('nome', '').strip() for p in ajudantes if p.get('nome')]
            com_contagem = [(n, self.contar_participacoes_parte(n, "Estudo de Congregação")) for n in nomes]
            com_contagem.sort(key=lambda x: x[1])
            return [n for n, _ in com_contagem]
        except Exception as e:
            logger.error(f"Erro ao listar ajudantes estudo: {str(e)}")
            return []

    def obter_sexo_publicador(self, nome):
        """Retorna o sexo do publicador ('Masculino' ou 'Feminino') ou None se não encontrado."""
        if not nome or not nome.strip():
            return None
        try:
            if self.db_type == 'mongodb':
                p = self.db.find_one({"nome": nome.strip()}, {"sexo": 1})
            else:
                r = self.db.get_item(Key={"nome": nome.strip()}, ProjectionExpression="sexo")
                p = r.get('Item')
            return p.get('sexo') if p else None
        except Exception as e:
            logger.error(f"Erro ao obter sexo de '{nome}': {str(e)}")
            return None

    def selecionar_publicador_para_parte(self, parte, semana, publicadores_ja_selecionados=None, publicadores_selecionados_global=None):
        """
        Seleciona automaticamente um publicador para uma parte específica baseado em critérios.
        
        Args:
            parte: Nome da parte (ex: "Presidente", "Oração Inicial", etc.)
            semana: String da semana (para logging)
            publicadores_ja_selecionados: Lista de nomes já selecionados nesta reunião (para evitar duplicação)
            publicadores_selecionados_global: Lista de nomes já selecionados em todas as semanas anteriores
            
        Returns:
            str: Nome do publicador selecionado ou "não possui" se nenhum atender critérios
        """
        try:
            if publicadores_ja_selecionados is None:
                publicadores_ja_selecionados = []
            if publicadores_selecionados_global is None:
                publicadores_selecionados_global = []
            
            # Buscar todos os publicadores
            if self.db_type == 'mongodb':
                publicadores = list(self.db.find({}, {"nome": 1, "Anciao": 1, "Servo_Ministerial": 1, 
                                                      "sexo": 1, "permissoes": 1, "_id": 0}))
            else:
                # Para DynamoDB
                response = self.db.scan()
                publicadores = response.get('Items', [])
            
            if not publicadores:
                logger.warning("Nenhum publicador encontrado no banco de dados")
                return "não possui"
            
            # 1. Aplicar filtros específicos por parte (reutiliza lógica do meio de semana)
            publicadores_filtrados = self._filtrar_publicadores_por_parte_meio(parte, publicadores)
            
            if not publicadores_filtrados:
                logger.warning(f"Nenhum publicador encontrado que atenda os critérios para '{parte}'")
                return "não possui"
            
            # 2. Remover os que estão em publicadores_selecionados_global (já selecionados nas semanas anteriores)
            if publicadores_selecionados_global:
                publicadores_candidatos = [p for p in publicadores_filtrados 
                                         if p.get('nome') not in publicadores_selecionados_global]
            else:
                publicadores_candidatos = publicadores_filtrados
            
            # 3. Se lista vazia após remover, permitir reutilização (usar todos os filtrados)
            if not publicadores_candidatos:
                logger.warning(f"Lista vazia após remover selecionados. Permitindo reutilização para '{parte}'")
                publicadores_candidatos = publicadores_filtrados
            
            # 4. Filtrar também os já selecionados nesta reunião específica
            publicadores_candidatos = [p for p in publicadores_candidatos 
                                     if p.get('nome') not in publicadores_ja_selecionados]
            
            # 5. Se ainda vazio, permitir reutilização mesmo nesta reunião
            if not publicadores_candidatos:
                logger.warning(f"Lista vazia após remover selecionados desta reunião. Permitindo reutilização para '{parte}'")
                publicadores_candidatos = publicadores_filtrados
            
            # 6. Calcular tempo sem fazer para cada candidato e ordenar
            publicadores_com_tempo = []
            for pub in publicadores_candidatos:
                tempo = self.calcular_tempo_sem_fazer(pub.get('nome'), parte)
                publicadores_com_tempo.append((pub, tempo))
            
            # 7. Ordenar por tempo sem fazer (maior = mais tempo sem fazer = maior prioridade)
            publicadores_com_tempo.sort(key=lambda x: x[1], reverse=True)
            
            # 8. Selecionar o primeiro (que tem mais tempo sem fazer)
            if not publicadores_com_tempo:
                logger.warning(f"Nenhum publicador disponível para '{parte}'")
                return "não possui"
            
            publicador_selecionado = publicadores_com_tempo[0][0]
            nome_selecionado = publicador_selecionado.get('nome')
            
            logger.info(f"Selecionado '{nome_selecionado}' para '{parte}' (tempo sem fazer: {publicadores_com_tempo[0][1]} semanas)")
            return nome_selecionado
            
        except Exception as e:
            logger.error(f"Erro ao selecionar publicador para parte '{parte}': {str(e)}")
            import traceback
            traceback.print_exc()
            return "não possui"
    
    def selecionar_dois_publicadores_escola(self, parte, semana, publicadores_ja_selecionados=None, publicadores_selecionados_global=None):
        """
        Seleciona dois publicadores para partes da escola (mesmo sexo, permissão de parte da escola).
        
        Args:
            parte: Nome da parte da escola
            semana: String da semana
            publicadores_ja_selecionados: Lista de nomes já selecionados nesta reunião
            publicadores_selecionados_global: Lista de nomes já selecionados em todas as semanas anteriores
            
        Returns:
            str: "Publicador1 / Publicador2" ou "não possui"
        """
        try:
            if publicadores_ja_selecionados is None:
                publicadores_ja_selecionados = []
            if publicadores_selecionados_global is None:
                publicadores_selecionados_global = []
            
            # Buscar todos os publicadores
            if self.db_type == 'mongodb':
                publicadores = list(self.db.find({}, {"nome": 1, "Anciao": 1, "Servo_Ministerial": 1, 
                                                      "sexo": 1, "permissoes": 1, "_id": 0}))
            else:
                # Para DynamoDB
                response = self.db.scan()
                publicadores = response.get('Items', [])
            
            # 1. Filtrar por critérios: permissão de parte da escola, NÃO Ancião, NÃO Servo Ministerial
            publicadores_filtrados = [
                p for p in publicadores 
                if (p.get("permissoes", {}).get("parte_escola", False) and
                    not p.get("Anciao", False) and
                    not p.get("Servo_Ministerial", False))
            ]
            
            if not publicadores_filtrados:
                logger.warning(f"Nenhum publicador encontrado que atenda os critérios para '{parte}'")
                return "não possui"
            
            # 2. Remover os que estão em publicadores_selecionados_global
            if publicadores_selecionados_global:
                publicadores_candidatos = [p for p in publicadores_filtrados 
                                         if p.get('nome') not in publicadores_selecionados_global]
            else:
                publicadores_candidatos = publicadores_filtrados
            
            # 3. Se lista vazia após remover, permitir reutilização
            if not publicadores_candidatos:
                logger.warning(f"Lista vazia após remover selecionados. Permitindo reutilização para '{parte}'")
                publicadores_candidatos = publicadores_filtrados
            
            # 4. Filtrar também os já selecionados nesta reunião específica
            publicadores_candidatos = [p for p in publicadores_candidatos 
                                     if p.get('nome') not in publicadores_ja_selecionados]
            
            # 5. Se ainda vazio, permitir reutilização mesmo nesta reunião
            if not publicadores_candidatos:
                logger.warning(f"Lista vazia após remover selecionados desta reunião. Permitindo reutilização para '{parte}'")
                publicadores_candidatos = publicadores_filtrados
            
            if len(publicadores_candidatos) < 2:
                logger.warning(f"Não há publicadores suficientes para '{parte}' (precisa 2, encontrado {len(publicadores_candidatos)})")
                return "não possui"
            
            # 6. Calcular tempo sem fazer para cada um
            publicadores_com_tempo = []
            for pub in publicadores_candidatos:
                tempo = self.calcular_tempo_sem_fazer(pub.get('nome'), parte)
                publicadores_com_tempo.append((pub, tempo))
            
            # 7. Ordenar por tempo sem fazer
            publicadores_com_tempo.sort(key=lambda x: x[1], reverse=True)
            
            # 8. Selecionar o primeiro
            primeiro = publicadores_com_tempo[0][0]
            sexo_primeiro = primeiro.get('sexo')
            
            # 9. Selecionar o segundo do mesmo sexo
            segundo_candidatos = [
                (p, t) for p, t in publicadores_com_tempo[1:] 
                if p.get('sexo') == sexo_primeiro and p.get('nome') != primeiro.get('nome')
            ]
            
            if not segundo_candidatos:
                logger.warning(f"Não há segundo publicador do mesmo sexo ({sexo_primeiro}) para '{parte}'")
                return primeiro.get('nome')  # Retornar apenas o primeiro
            
            # 10. Ordenar segundo por tempo sem fazer
            segundo_candidatos.sort(key=lambda x: x[1], reverse=True)
            segundo = segundo_candidatos[0][0]
            
            resultado = f"{primeiro.get('nome')} / {segundo.get('nome')}"
            logger.info(f"Selecionados para '{parte}': {resultado}")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao selecionar dois publicadores para '{parte}': {str(e)}")
            import traceback
            traceback.print_exc()
            return "não possui"
    
    def selecionar_estudo_congregacao(self, semana, publicadores_ja_selecionados=None, publicadores_selecionados_global=None):
        """
        Seleciona publicadores para Estudo de Congregação: Ancião (principal) / Publicador masculino com permissão de leitura (ajudante).
        
        Args:
            semana: String da semana
            publicadores_ja_selecionados: Lista de nomes já selecionados nesta reunião
            publicadores_selecionados_global: Lista de nomes já selecionados em todas as semanas anteriores
            
        Returns:
            str: "Ancião / Ajudante" ou "não possui"
        """
        try:
            if publicadores_ja_selecionados is None:
                publicadores_ja_selecionados = []
            if publicadores_selecionados_global is None:
                publicadores_selecionados_global = []
            
            # Buscar todos os publicadores
            if self.db_type == 'mongodb':
                publicadores = list(self.db.find({}, {"nome": 1, "Anciao": 1, "Servo_Ministerial": 1, 
                                                      "sexo": 1, "permissoes": 1, "_id": 0}))
            else:
                # Para DynamoDB
                response = self.db.scan()
                publicadores = response.get('Items', [])
            
            # 1. Filtrar anciões
            ancioes_filtrados = [p for p in publicadores if p.get("Anciao", False)]
            
            if not ancioes_filtrados:
                logger.warning("Nenhum ancião encontrado para Estudo de Congregação")
                return "não possui"
            
            # 2. Remover os que estão em publicadores_selecionados_global
            if publicadores_selecionados_global:
                ancioes_candidatos = [p for p in ancioes_filtrados 
                                    if p.get('nome') not in publicadores_selecionados_global]
            else:
                ancioes_candidatos = ancioes_filtrados
            
            # 3. Se lista vazia após remover, permitir reutilização
            if not ancioes_candidatos:
                logger.warning("Lista vazia de anciões após remover selecionados. Permitindo reutilização...")
                ancioes_candidatos = ancioes_filtrados
            
            # 4. Filtrar também os já selecionados nesta reunião específica
            ancioes_candidatos = [p for p in ancioes_candidatos 
                                if p.get('nome') not in publicadores_ja_selecionados]
            
            # 5. Se ainda vazio, permitir reutilização mesmo nesta reunião
            if not ancioes_candidatos:
                logger.warning("Lista vazia de anciões após remover selecionados desta reunião. Permitindo reutilização...")
                ancioes_candidatos = ancioes_filtrados
            
            # 6. Calcular tempo sem fazer para anciões
            ancioes_com_tempo = []
            for pub in ancioes_candidatos:
                tempo = self.calcular_tempo_sem_fazer(pub.get('nome'), "Estudo de Congregação")
                ancioes_com_tempo.append((pub, tempo))
            
            ancioes_com_tempo.sort(key=lambda x: x[1], reverse=True)
            principal = ancioes_com_tempo[0][0]
            
            # 7. Selecionar ajudante (Masculino com permissão de leitura)
            ajudantes_filtrados = [
                p for p in publicadores 
                if (p.get("sexo") == "Masculino" and
                    p.get("permissoes", {}).get("leitura_livro", False) and
                    p.get('nome') != principal.get('nome'))
            ]
            
            if not ajudantes_filtrados:
                logger.warning("Nenhum ajudante encontrado para Estudo de Congregação")
                return principal.get('nome')  # Retornar apenas o principal
            
            # 8. Remover os que estão em publicadores_selecionados_global
            if publicadores_selecionados_global:
                ajudantes_candidatos = [p for p in ajudantes_filtrados 
                                      if p.get('nome') not in publicadores_selecionados_global]
            else:
                ajudantes_candidatos = ajudantes_filtrados
            
            # 9. Se lista vazia após remover, permitir reutilização
            if not ajudantes_candidatos:
                logger.warning("Lista vazia de ajudantes após remover selecionados. Permitindo reutilização...")
                ajudantes_candidatos = ajudantes_filtrados
            
            # 10. Filtrar também os já selecionados nesta reunião específica
            ajudantes_candidatos = [p for p in ajudantes_candidatos 
                                  if p.get('nome') not in publicadores_ja_selecionados]
            
            # 11. Se ainda vazio, permitir reutilização mesmo nesta reunião
            if not ajudantes_candidatos:
                logger.warning("Lista vazia de ajudantes após remover selecionados desta reunião. Permitindo reutilização...")
                ajudantes_candidatos = ajudantes_filtrados
            
            # 12. Calcular tempo sem fazer para ajudantes
            ajudantes_com_tempo = []
            for pub in ajudantes_candidatos:
                tempo = self.calcular_tempo_sem_fazer(pub.get('nome'), "Estudo de Congregação")
                ajudantes_com_tempo.append((pub, tempo))
            
            ajudantes_com_tempo.sort(key=lambda x: x[1], reverse=True)
            ajudante = ajudantes_com_tempo[0][0]
            
            resultado = f"{principal.get('nome')} / {ajudante.get('nome')}"
            logger.info(f"Selecionados para Estudo de Congregação: {resultado}")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao selecionar publicadores para Estudo de Congregação: {str(e)}")
            import traceback
            traceback.print_exc()
            return "não possui"

    def selecionar_publicador_leitura_sentinela(self, semana, publicadores_ja_selecionados=None):
        """
        Seleciona automaticamente um publicador para Leitura da Sentinela.
        Critério: permissoes.leitura_sentinela = True. Prioriza quem está há mais tempo sem fazer.
        """
        try:
            if publicadores_ja_selecionados is None:
                publicadores_ja_selecionados = []
            
            if self.db_type == 'mongodb':
                publicadores = list(self.db.find({}, {"nome": 1, "permissoes": 1, "_id": 0}))
            else:
                response = self.db.scan()
                publicadores = response.get('Items', [])
            
            publicadores_filtrados = [
                p for p in publicadores
                if p.get("permissoes", {}).get("leitura_sentinela", False)
            ]
            
            if not publicadores_filtrados:
                logger.warning("Nenhum publicador com permissão de leitura da Sentinela")
                return ""
            
            publicadores_candidatos = [
                p for p in publicadores_filtrados
                if p.get('nome') not in publicadores_ja_selecionados
            ]
            if not publicadores_candidatos:
                publicadores_candidatos = publicadores_filtrados
            
            publicadores_com_tempo = []
            for pub in publicadores_candidatos:
                tempo = self.calcular_tempo_sem_fazer(pub.get('nome'), "Leitura Sentinela")
                publicadores_com_tempo.append((pub, tempo))
            
            publicadores_com_tempo.sort(key=lambda x: x[1], reverse=True)
            return publicadores_com_tempo[0][0].get('nome', '')
        except Exception as e:
            logger.error(f"Erro ao selecionar publicador para Leitura Sentinela: {str(e)}")
            return ""

    def selecionar_publicador_presidente_final_semana(self, semana, publicadores_ja_selecionados=None):
        """
        Seleciona automaticamente um publicador para Presidente da reunião de Final de Semana.
        Critério: permissoes.presidente_final_semana = True. Prioriza quem está há mais tempo sem fazer.
        """
        try:
            if publicadores_ja_selecionados is None:
                publicadores_ja_selecionados = []
            
            if self.db_type == 'mongodb':
                publicadores = list(self.db.find({}, {"nome": 1, "permissoes": 1, "_id": 0}))
            else:
                response = self.db.scan()
                publicadores = response.get('Items', [])
            
            publicadores_filtrados = [
                p for p in publicadores
                if p.get("permissoes", {}).get("presidente_final_semana", False)
            ]
            
            if not publicadores_filtrados:
                logger.warning("Nenhum publicador com permissão de Presidente Final de Semana")
                return ""
            
            publicadores_candidatos = [
                p for p in publicadores_filtrados
                if p.get('nome') not in publicadores_ja_selecionados
            ]
            if not publicadores_candidatos:
                publicadores_candidatos = publicadores_filtrados
            
            publicadores_com_tempo = []
            for pub in publicadores_candidatos:
                tempo = self.calcular_tempo_sem_fazer(pub.get('nome'), "Presidente Final Semana")
                publicadores_com_tempo.append((pub, tempo))
            
            publicadores_com_tempo.sort(key=lambda x: x[1], reverse=True)
            return publicadores_com_tempo[0][0].get('nome', '')
        except Exception as e:
            logger.error(f"Erro ao selecionar publicador para Presidente Final Semana: {str(e)}")
            return ""

    def listar_publicadores_por_permissao(self, permissao):
        """
        Retorna lista de nomes de publicadores que possuem a permissão informada.
        Usado para autocomplete em campos de Presidente e Leitor Final de Semana.
        """
        try:
            if self.db_type == 'mongodb':
                publicadores = list(self.db.find({}, {"nome": 1, "permissoes": 1, "_id": 0}))
            else:
                response = self.db.scan()
                publicadores = response.get('Items', [])
            
            nomes = [
                p.get('nome', '') for p in publicadores
                if p.get("permissoes", {}).get(permissao, False) and p.get('nome')
            ]
            return sorted(nomes)
        except Exception as e:
            logger.error(f"Erro ao listar publicadores por permissão {permissao}: {str(e)}")
            return []

    def contar_participacoes_parte(self, nome_publicador, parte):
        """
        Retorna quantas vezes o publicador fez determinada parte (conta no histórico).
        Ex.: contar_participacoes_parte("João", "Leitura Sentinela") -> 3
        """
        try:
            historico = self.buscar_historico_publicador(nome_publicador)
            if not historico:
                return 0
            return len([h for h in historico if h.get('parte') == parte])
        except Exception as e:
            logger.error(f"Erro ao contar participações de {nome_publicador} na parte {parte}: {str(e)}")
            return 0

    def listar_ordenados_por_menos_partecipacoes(self, permissao, nome_parte_historico):
        """
        Lista publicadores com a permissão informada, ordenados do que fez MENOS
        participações na parte (nome_parte_historico) ao que fez mais.
        Usado para distribuir Leitor Sentinela e Presidente Final de Semana (um por semana).
        """
        try:
            nomes = self.listar_publicadores_por_permissao(permissao)
            if not nomes:
                return []
            com_contagem = [(nome, self.contar_participacoes_parte(nome, nome_parte_historico)) for nome in nomes]
            com_contagem.sort(key=lambda x: x[1])
            return [nome for nome, _ in com_contagem]
        except Exception as e:
            logger.error(f"Erro ao listar ordenados por menos participações: {str(e)}")
            return []

    def listar_ancios(self):
        """
        Retorna lista de nomes de publicadores que são anciãos (Anciao == True).
        Usado para o modal de Dirigente de Sentinela.
        """
        try:
            if self.db_type == 'mongodb':
                publicadores = list(self.db.find({"Anciao": True}, {"nome": 1, "_id": 0}))
            else:
                response = self.db.scan()
                publicadores = [p for p in response.get('Items', []) if p.get("Anciao", False)]
            nomes = [p.get('nome', '') for p in publicadores if p.get('nome')]
            return sorted(nomes)
        except Exception as e:
            logger.error(f"Erro ao listar anciãos: {str(e)}")
            return []

    def listar_ancios_e_servos(self):
        """
        Retorna lista de nomes de publicadores que são anciãos (Anciao == True)
        ou servos ministeriais (Servo_Ministerial == True). Sem duplicatas.
        Usado para candidatos a Presidente Final de Semana e autocomplete do campo Presidente.
        """
        try:
            if self.db_type == 'mongodb':
                publicadores = list(self.db.find(
                    {"$or": [{"Anciao": True}, {"Servo_Ministerial": True}]},
                    {"nome": 1, "_id": 0}
                ))
            else:
                response = self.db.scan()
                publicadores = [
                    p for p in response.get('Items', [])
                    if p.get("Anciao", False) or p.get("Servo_Ministerial", False)
                ]
            nomes = list({p.get('nome', '') for p in publicadores if p.get('nome')})
            return sorted(nomes)
        except Exception as e:
            logger.error(f"Erro ao listar anciãos e servos: {str(e)}")
            return []

    def listar_presidentes_final_semana_ordenados_por_menos_partecipacoes(self):
        """
        Lista anciãos e servos ministeriais ordenados do que fez MENOS
        participações em 'Presidente Final Semana' ao que fez mais.
        Usado para seleção automática de presidente (um por semana, com ciclo).
        """
        try:
            nomes = self.listar_ancios_e_servos()
            if not nomes:
                return []
            com_contagem = [
                (nome, self.contar_participacoes_parte(nome, "Presidente Final Semana"))
                for nome in nomes
            ]
            com_contagem.sort(key=lambda x: x[1])
            return [nome for nome, _ in com_contagem]
        except Exception as e:
            logger.error(f"Erro ao listar presidentes final semana ordenados: {str(e)}")
            return []

    def salvar_reuniao_final_semana(self, dados):
        """Salva ou atualiza uma reunião de final de semana em reunioes_final_semana."""
        try:
            if self.db_type != 'mongodb':
                return {"success": False, "message": "Reunião final de semana suportada apenas em MongoDB"}
            
            collection = self.db['reunioes_final_semana']
            ano = dados.get('ano')
            mes = dados.get('mes')
            filtro = {"ano": ano, "mes": mes}
            
            dados_doc = {
                **dados,
                "ultima_atualizacao": datetime.datetime.now().isoformat()
            }
            
            collection.update_one(filtro, {"$set": dados_doc}, upsert=True)
            
            meses_pt = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            nome_mes = meses_pt.get(mes, str(mes))
            for i, semana in enumerate(dados.get('semanas', [])):
                periodo = (semana.get('semana') or '').strip()
                data_part = f"{periodo} de {ano}" if periodo else f"Semana {i + 1} de {nome_mes} de {ano}"
                presidente = semana.get('presidente', '')
                if presidente:
                    self._atualizar_historico_individual(presidente, "Presidente Final Semana", data_part)
                leitor = semana.get('leitor_sentinela', '')
                if leitor:
                    self._atualizar_historico_individual(leitor, "Leitura Sentinela", data_part)
            
            return {"success": True, "message": "Reunião salva"}
        except Exception as e:
            logger.error(f"Erro ao salvar reunião final de semana: {str(e)}")
            return {"success": False, "message": str(e)}

    def listar_reunioes_final_semana(self, ano=None, mes=None, limite=50):
        """Lista reuniões de final de semana com filtros opcionais."""
        try:
            if self.db_type != 'mongodb':
                return []
            
            collection = self.db['reunioes_final_semana']
            query = {}
            if ano is not None:
                query["ano"] = ano
            if mes is not None:
                query["mes"] = mes
            
            reunioes = list(collection.find(query).sort("data_criacao", -1).limit(limite))
            for r in reunioes:
                r.pop('_id', None)
            return reunioes
        except Exception as e:
            logger.error(f"Erro ao listar reuniões final de semana: {str(e)}")
            return []

    def buscar_reuniao_final_semana(self, ano, mes):
        """Busca uma reunião de final de semana por ano e mês."""
        try:
            if self.db_type != 'mongodb':
                return None
            collection = self.db['reunioes_final_semana']
            doc = collection.find_one({"ano": ano, "mes": mes})
            if doc:
                doc.pop('_id', None)
            return doc
        except Exception as e:
            logger.error(f"Erro ao buscar reunião final de semana: {str(e)}")
            return None

    def _obter_db_e_collections_mongodb(self):
        """Retorna (database, collection_publicadores) para MongoDB. Compatível com self.db sendo collection ou database."""
        if hasattr(self.db, 'database'):
            db = self.db.database
            collection_publicadores = self.db
        else:
            db = self.db
            collection_publicadores = self.db['publicadores']
        return db, collection_publicadores

    def excluir_reuniao_final_semana(self, ano, mes):
        """
        Exclui uma reunião de final de semana (ano, mes) e remove do histórico
        de cada publicador as entradas correspondentes (Leitura Sentinela e Presidente Final Semana).
        """
        try:
            if self.db_type != 'mongodb':
                return {"success": False, "message": "Reunião final de semana suportada apenas em MongoDB"}
            try:
                ano = int(ano)
                mes = int(mes)
            except (TypeError, ValueError):
                return {"success": False, "message": "Ano e mês devem ser números válidos"}
            # Mesma referência de collection que buscar_reuniao_final_semana
            collection_fs = self.db['reunioes_final_semana']
            reuniao = collection_fs.find_one({"ano": ano, "mes": mes})
            if not reuniao:
                return {"success": False, "message": "Reunião não encontrada"}
            _, collection_publicadores = self._obter_db_e_collections_mongodb()
            meses_pt = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            nome_mes = meses_pt.get(mes, str(mes))
            datas_remover = []
            for i, s in enumerate(reuniao.get('semanas', [])):
                periodo = (s.get('semana') or '').strip()
                if periodo:
                    datas_remover.append(f"{periodo} de {ano}")
                datas_remover.append(f"Semana {i + 1} de {nome_mes} de {ano}")
            datas_remover = list(set(datas_remover))
            partes_final_semana = ["Leitura Sentinela", "Presidente Final Semana"]
            publicadores = list(collection_publicadores.find({}, {"nome": 1, "historico": 1}))
            for pub in publicadores:
                historico = pub.get("historico", [])
                novo_historico = [
                    h for h in historico
                    if not (h.get("parte") in partes_final_semana and h.get("data") in datas_remover)
                ]
                if len(novo_historico) != len(historico):
                    ultima = novo_historico[-1]["data"] if novo_historico else ""
                    collection_publicadores.update_one(
                        {"nome": pub["nome"]},
                        {"$set": {"historico": novo_historico, "ultima_parte": ultima}}
                    )
            result = collection_fs.delete_one({"ano": ano, "mes": mes})
            if result.deleted_count == 0:
                return {"success": False, "message": "Falha ao excluir reunião"}
            return {"success": True, "message": "Reunião excluída e histórico dos publicadores atualizado."}
        except Exception as e:
            logger.error(f"Erro ao excluir reunião final de semana: {str(e)}")
            return {"success": False, "message": str(e)}

    def listar_candidatos_salao_ordenados(self, papel):
        """
        Lista publicadores masculinos com a permissão de salão ativa (papel),
        ordenados por quem fez menos participações nessa função.
        papel: 'audio_video', 'microfone' ou 'indicador'
        """
        try:
            if self.db_type == 'mongodb':
                publicadores = list(self.db.find({}, {"nome": 1, "sexo": 1, "permissoes": 1, "_id": 0}))
            else:
                publicadores = self.db.scan().get('Items', [])
            filtrados = [
                p for p in publicadores
                if p.get("sexo") == "Masculino" and p.get("permissoes", {}).get(papel, False)
            ]
            nomes = [p.get('nome', '').strip() for p in filtrados if p.get('nome')]
            partes_map = {
                "audio_video": ["Salão - Áudio", "Salão - Vídeo"],
                "microfone":   ["Salão - Microfone"],
                "indicador":   ["Salão - Indicador"],
            }
            partes = partes_map.get(papel, [papel])
            com_contagem = [
                (n, sum(self.contar_participacoes_parte(n, p) for p in partes))
                for n in nomes
            ]
            com_contagem.sort(key=lambda x: x[1])
            return [n for n, _ in com_contagem]
        except Exception as e:
            logger.error(f"Erro ao listar candidatos salão '{papel}': {str(e)}")
            return []

    def salvar_designacoes_salao(self, dados):
        """Salva ou atualiza designações de salão em designacoes_salao."""
        try:
            if self.db_type != 'mongodb':
                return {"success": False, "message": "Suportado apenas em MongoDB"}
            db, _ = self._obter_db_e_collections_mongodb()
            collection = db['designacoes_salao']
            ano = dados.get('ano')
            mes = dados.get('mes')
            dados_doc = {**dados, "ultima_atualizacao": datetime.datetime.now().isoformat()}
            collection.update_one({"ano": ano, "mes": mes}, {"$set": dados_doc}, upsert=True)
            meses_pt = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            nome_mes = meses_pt.get(mes, str(mes))
            for i, semana in enumerate(dados.get('semanas', [])):
                data_part = semana.get('data', f"Semana {i + 1} de {nome_mes} de {ano}")
                if semana.get('audio'):
                    self._atualizar_historico_individual(semana['audio'], "Salão - Áudio", data_part)
                if semana.get('video'):
                    self._atualizar_historico_individual(semana['video'], "Salão - Vídeo", data_part)
                for nome in (semana.get('microfone') or '').split('/'):
                    nome = nome.strip()
                    if nome:
                        self._atualizar_historico_individual(nome, "Salão - Microfone", data_part)
                for nome in (semana.get('indicadores') or '').split('/'):
                    nome = nome.strip()
                    if nome:
                        self._atualizar_historico_individual(nome, "Salão - Indicador", data_part)
            return {"success": True, "message": "Designações salvas"}
        except Exception as e:
            logger.error(f"Erro ao salvar designações salão: {str(e)}")
            return {"success": False, "message": str(e)}

    def listar_designacoes_salao(self):
        """Retorna todos os meses salvos em designacoes_salao, ordenados por ano/mês."""
        try:
            if self.db_type != 'mongodb':
                return []
            db, _ = self._obter_db_e_collections_mongodb()
            collection = db['designacoes_salao']
            docs = list(collection.find({}, {"_id": 0}).sort([("ano", 1), ("mes", 1)]))
            return docs
        except Exception as e:
            logger.error(f"Erro ao listar designações salão: {str(e)}")
            return []

    def buscar_designacoes_salao(self, ano, mes):
        """Busca designações de salão por ano e mês."""
        try:
            if self.db_type != 'mongodb':
                return None
            db, _ = self._obter_db_e_collections_mongodb()
            collection = db['designacoes_salao']
            doc = collection.find_one({"ano": ano, "mes": mes})
            if doc:
                doc.pop('_id', None)
            return doc
        except Exception as e:
            logger.error(f"Erro ao buscar designações salão: {str(e)}")
            return None

    def excluir_designacoes_salao(self, ano, mes):
        """Exclui designações de salão e remove entradas do histórico dos publicadores."""
        try:
            if self.db_type != 'mongodb':
                return {"success": False, "message": "Suportado apenas em MongoDB"}
            try:
                ano = int(ano)
                mes = int(mes)
            except (TypeError, ValueError):
                return {"success": False, "message": "Ano e mês devem ser números válidos"}
            db, collection_publicadores = self._obter_db_e_collections_mongodb()
            collection = db['designacoes_salao']
            doc = collection.find_one({"ano": ano, "mes": mes})
            if not doc:
                return {"success": False, "message": "Designações não encontradas"}
            datas = list({s.get('data', '') for s in doc.get('semanas', []) if s.get('data')})
            partes_salao = ["Salão - Áudio", "Salão - Vídeo", "Salão - Microfone", "Salão - Indicador"]
            publicadores = list(collection_publicadores.find({}, {"nome": 1, "historico": 1}))
            for pub in publicadores:
                historico = pub.get("historico", [])
                novo = [h for h in historico if not (h.get("parte") in partes_salao and h.get("data") in datas)]
                if len(novo) != len(historico):
                    ultima = novo[-1]["data"] if novo else ""
                    collection_publicadores.update_one(
                        {"nome": pub["nome"]},
                        {"$set": {"historico": novo, "ultima_parte": ultima}}
                    )
            result = collection.delete_one({"ano": ano, "mes": mes})
            if result.deleted_count == 0:
                return {"success": False, "message": "Falha ao excluir"}
            return {"success": True, "message": "Designações excluídas e histórico atualizado."}
        except Exception as e:
            logger.error(f"Erro ao excluir designações salão: {str(e)}")
            return {"success": False, "message": str(e)}

    def contar_designacoes_salao_por_publicador(self):
        """Retorna {nome: {audio, video, microfone, indicadores, total}} para todos os publicadores."""
        try:
            if self.db_type != 'mongodb':
                return {}
            if hasattr(self.db, 'find'):
                collection_publicadores = self.db
            else:
                collection_publicadores = self.db['publicadores']
            publicadores = list(collection_publicadores.find({}, {"nome": 1, "historico": 1, "_id": 0}))
            result = {}
            for pub in publicadores:
                nome = pub.get('nome', '')
                if not nome:
                    continue
                hist = pub.get('historico', [])
                audio = sum(1 for h in hist if h.get('parte') == 'Salão - Áudio')
                video = sum(1 for h in hist if h.get('parte') == 'Salão - Vídeo')
                mic   = sum(1 for h in hist if h.get('parte') == 'Salão - Microfone')
                ind   = sum(1 for h in hist if h.get('parte') == 'Salão - Indicador')
                if audio + video + mic + ind > 0:
                    result[nome] = {"audio": audio, "video": video, "microfone": mic,
                                    "indicadores": ind, "total": audio + video + mic + ind}
            return result
        except Exception as e:
            logger.error(f"Erro ao contar designações salão por publicador: {str(e)}")
            return {}


# Criar uma instância global das operações
db_ops = DatabaseOperations()