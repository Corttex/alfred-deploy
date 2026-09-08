import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# Carregar o Cofre de Chaves
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ALFRED CÓRTEX] - %(message)s')

class RouteDecision(BaseModel):
    agent: str = Field(description="Qual agente deve lidar com isso? Escolha entre: 'INFRA' (Servidor/Hetzner), 'WEB' (Pesquisa internet/Tavily), 'DEV' (Código/Arquivos), ou 'CHAT' (Conversa normal)")
    reasoning: str = Field(description="Uma breve explicação do porquê esse agente foi escolhido.")

class AlfredSupervisor:
    def __init__(self):
        logging.info("Inicializando o Córtex Frontal (Roteador de Decisão)...")
        
        # O Cérebro Principal de Roteamento será a Groq (Llama 3) por ser a mais rápida do mundo (quase 0 latência)
        # Perfeita para tomar decisões instantâneas sobre para onde mandar a tarefa.
        self.router_llm = ChatOpenAI(
            openai_api_key=os.getenv("GROQ_API_KEY"),
            openai_api_base="https://api.groq.com/openai/v1",
            model_name="llama3-70b-8192",
            temperature=0.0
        )
        
        # O Roteador Estruturado força a IA a responder num formato JSON garantido (RouteDecision)
        self.structured_router = self.router_llm.with_structured_output(RouteDecision)
        
        self.system_prompt = """
        Você é o ALFRED, um orquestrador de IA avançado (Mente de Colmeia) de acesso estritamente pessoal do Felipe.
        Sua função primária agora é ROTEAMENTO. 
        Analise o pedido do usuário e decida qual dos seus 'Agentes Especialistas' deve ser acionado.
        
        INFRA: Para comandos relacionados a VPS, Servidor, Hetzner, Coolify, Docker, Postgres, RAM, CPU.
        WEB: Para comandos pedindo notícias, cotação, pesquisas na internet, resumo de sites.
        DEV: Para comandos sobre criar arquivos locais, debugar código, escrever scripts.
        CHAT: Para perguntas gerais, filosóficas, cumprimentos ou dicas rápidas.
        
        Lembrete Crítico de Segurança: O Servidor 2.28.26.9 possui instâncias ativas do Coolify. VOCÊ NÃO DEVE TOCAR NELAS a menos que expressamente ordenado.
        """
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", "Pedido do Felipe: {user_input}")
        ])

    def route_command(self, user_input: str) -> RouteDecision:
        """
        Analisa a entrada do usuário e decide para onde rotear.
        """
        logging.info(f"Analisando novo comando: '{user_input}'")
        chain = self.prompt_template | self.structured_router
        
        decision = chain.invoke({"user_input": user_input})
        logging.info(f"Decisão do Córtex: Rota -> {decision.agent} | Motivo: {decision.reasoning}")
        return decision

    def process(self, user_input: str) -> str:
        """
        O Fluxo Principal. Recebe o texto do Mobile/Extensão/Telegram e processa.
        """
        decision = self.route_command(user_input)
        
        # Invocando os Agentes Reais que acabamos de criar
        if decision.agent == "INFRA":
            from agents.agent_infra import get_server_status
            logging.info("Iniciando varredura SSH na Hetzner...")
            resultado = get_server_status()
            return f"🖥️ [AGENTE INFRA]:\n{resultado}\n\n(Motivo: {decision.reasoning})"
        
        elif decision.agent == "WEB":
            from agents.agent_web import search_web
            logging.info("Iniciando Tavily Web Search...")
            resultado = search_web(user_input)
            return f"🌐 [AGENTE WEB]:\n{resultado}\n\n(Motivo: {decision.reasoning})"
        
        elif decision.agent == "DEV":
            from agents.agent_dev import create_project_folder
            logging.info("Iniciando operações locais do Sistema Operacional...")
            # Extração burra de nome de projeto apenas para exemplo imediato. Na versão final, a IA vai extrair.
            if "pasta" in user_input.lower() or "projeto" in user_input.lower():
                resultado = create_project_folder("ALFRED_Novo_Projeto")
                return f"💻 [AGENTE DEV]:\n{resultado}\n\n(Motivo: {decision.reasoning})"
            return f"💻 [AGENTE DEV]: Recebido, mas comando local genérico.\n\n(Motivo: {decision.reasoning})"
            
        else:
            # Rota CHAT (Responde direto)
            # Aqui também chamaríamos a Memória Postgres.
            return f"🧠 [CÓRTEX]: Estou pronto, mestre. \n(Motivo: {decision.reasoning})"

if __name__ == "__main__":
    # Teste Rápido
    supervisor = AlfredSupervisor()
    print("\n--- Teste de Roteamento ALFRED ---")
    print(supervisor.process("Como está o consumo de RAM do meu servidor lá na Hetzner?"))
    print("\n")
    print(supervisor.process("Busque as últimas notícias sobre IA de hoje na web."))
