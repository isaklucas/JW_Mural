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
                logger.info("Índice criado/verificado com sucesso para ano e semana")
            except Exception as e:
                logger.error(f"Erro ao criar índice: {str(e)}")

    def post(self, nome, batizado):
        try:
            now = datetime.datetime.now().isoformat()
            nome = util.ComandosUteis.TitleCase(nome)
            item = {
                "nome": nome.strip(),
                "batizado": batizado,
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
                else:
                    logger.info(f"Filtro aplicado: {parte}")
            
            return participacoes_ordenadas
            
        except Exception as e:
            logger.error(f"Erro ao contar participações por parte: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}

# Criar uma instância global das operações
db_ops = DatabaseOperations() 