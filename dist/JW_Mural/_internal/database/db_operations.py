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
            
            # Processar cada participação
            for nome, parte in participacoes:
                if nome and nome != "não possui":
                    # Se houver /, divide os nomes e processa cada um
                    if '/' in nome:
                        nomes = [n.strip() for n in nome.split('/')]
                        for nome_individual in nomes:
                            if nome_individual:  # Verifica se não está vazio
                                self._atualizar_historico_individual(nome_individual, parte, data_participacao)
                    else:
                        self._atualizar_historico_individual(nome, parte, data_participacao)
                    
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
            logger.error(f"Erro ao atualizar histórico individual: {str(e)}")
            raise

    def buscar_reuniao(self, ano, semana):
        """
        Busca uma reunião específica pelo ano e semana
        """
        try:
            collection_reunioes = self.db['reunioes']
            # Adicionar log para debug
            logger.info(f"Buscando reunião - Ano: {ano}, Semana: {semana}")
            
            # Normalizar a semana substituindo diferentes tipos de traços
            semana_normalizada = semana.upper().replace('-', '–').replace(' A ', '–')
            logger.info(f"Semana normalizada: {semana_normalizada}")
            
            reuniao = collection_reunioes.find_one({
                "ano": ano,
                "semana": semana_normalizada
            })
            
            # Log do resultado
            if reuniao:
                logger.info("Reunião encontrada")
                reuniao['_id'] = str(reuniao['_id'])  # Converter ObjectId para string
            else:
                logger.warning(f"Nenhuma reunião encontrada para semana: {semana_normalizada}")
                
            return reuniao
            
        except Exception as e:
            logger.error(f"Erro ao buscar reunião: {str(e)}")
            return None

    def buscar_historico_publicador(self, nome_publicador):
        """
        Busca o histórico de participação de um publicador nas reuniões
        """
        try:
            nome_publicador = util.ComandosUteis.TitleCase(nome_publicador.strip())
            collection_reunioes = self.db['reunioes']
            
            # Criar query para buscar todas as reuniões onde o publicador participou
            query = {
                "$or": [
                    {"presidente": nome_publicador},
                    {"oracao_inicial": nome_publicador},
                    {"tesouro": nome_publicador},
                    {"joias_espirituais": nome_publicador},
                    {"leitura_biblia": nome_publicador},
                    {"escola.primeira_parte": nome_publicador},
                    {"escola.segunda_parte": nome_publicador},
                    {"escola.terceira_parte": nome_publicador},
                    {"escola.quarta_parte": nome_publicador},
                    {"nossa_vida_crista.primeira_parte": nome_publicador},
                    {"nossa_vida_crista.segunda_parte": nome_publicador},
                    {"estudo_congregacao": nome_publicador},
                    {"oracao_final": nome_publicador}
                ]
            }
            
            # Buscar reuniões e ordenar por data_reuniao decrescente (mais recente primeiro)
            reunioes = collection_reunioes.find(query).sort("data_reuniao", -1)
            
            historico = []
            for reuniao in reunioes:
                participacoes = []
                
                # Verificar cada parte que o publicador participou
                if reuniao['presidente'] == nome_publicador:
                    participacoes.append("Presidente")
                if reuniao['oracao_inicial'] == nome_publicador:
                    participacoes.append("Oração Inicial")
                if reuniao['tesouro'] == nome_publicador:
                    participacoes.append("Tesouro")
                if reuniao['joias_espirituais'] == nome_publicador:
                    participacoes.append("Joias Espirituais")
                if reuniao['leitura_biblia'] == nome_publicador:
                    participacoes.append("Leitura da Bíblia")
                if reuniao['escola']['primeira_parte'] == nome_publicador:
                    participacoes.append("Escola - Primeira Parte")
                if reuniao['escola']['segunda_parte'] == nome_publicador:
                    participacoes.append("Escola - Segunda Parte")
                if reuniao['escola']['terceira_parte'] == nome_publicador:
                    participacoes.append("Escola - Terceira Parte")
                if reuniao['escola']['quarta_parte'] == nome_publicador:
                    participacoes.append("Escola - Quarta Parte")
                if reuniao['nossa_vida_crista']['primeira_parte'] == nome_publicador:
                    participacoes.append("Nossa Vida Cristã - Primeira Parte")
                if reuniao['nossa_vida_crista']['segunda_parte'] == nome_publicador:
                    participacoes.append("Nossa Vida Cristã - Segunda Parte")
                if reuniao['estudo_congregacao'] == nome_publicador:
                    participacoes.append("Estudo de Congregação")
                if reuniao['oracao_final'] == nome_publicador:
                    participacoes.append("Oração Final")
                
                # Formatar data para exibição
                try:
                    # Converter a data da reunião para datetime
                    data = datetime.datetime.fromisoformat(reuniao['data_reuniao'])
                    # Subtrair 4 dias para obter a data real da reunião
                    data_real = data - datetime.timedelta(days=4)
                    # Formatar a data ajustada
                    data_formatada = data_real.strftime("%d/%m/%Y")
                except:
                    # Fallback para o formato antigo se não conseguir converter a data
                    data_formatada = reuniao['semana'] + "/" + str(reuniao['ano'])
                
                # Para cada participação, criar um registro separado
                for parte in participacoes:
                    historico.append({
                        "data": data_formatada,
                        "parte": parte
                    })
            
            return historico
            
        except Exception as e:
            logger.error(f"Erro ao buscar histórico do publicador: {str(e)}")
            return None

    def listar_reunioes(self, ano=None, semana=None, limite=50, pagina=1):
        """
        Lista as reuniões com opção de filtro por ano e semana
        """
        try:
            collection_reunioes = self.db['reunioes']
            
            # Construir query baseada nos filtros
            query = {}
            if ano is not None:
                query["ano"] = ano
            if semana is not None:
                query["semana"] = semana
            
            # Calcular skip para paginação
            skip = (pagina - 1) * limite
            
            # Buscar reuniões com paginação e ordenação
            reunioes = collection_reunioes.find(query) \
                                        .sort([("ano", -1), ("semana", -1)]) \
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

# Criar uma instância global das operações
db_ops = DatabaseOperations() 