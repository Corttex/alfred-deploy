import asyncio
from datetime import datetime
from models import Task
from agents.monitor_agent import MonitorAgent

async def health_check_routine():
    """
    Rotina infinita que roda a cada 2 horas (7200 segundos).
    O MonitorAgent vai verificar a saúde dos containers via Coolify API ou SSH.
    """
    # Aguarda 10 segundos após o servidor iniciar para o primeiro check
    await asyncio.sleep(10) 
    
    agent = MonitorAgent()
    
    while True:
        print(f"\n[CRONJOB] 🩺 Iniciando verificação de saúde programada às {datetime.now().strftime('%H:%M:%S')}...")
        
        # O prompt que o agente vai seguir sozinho sem intervenção humana
        command = (
            "Verifique o status da infraestrutura. "
            "Use a ferramenta coolify_api_request (GET /api/v1/applications) ou ssh_execute (docker ps). "
            "Avalie se todos os containers importantes estão rodando. "
            "Se houver alertas críticos (Containers parados, RAM explodindo), crie um alerta de emergência. "
            "Se tudo estiver ok, responda apenas: 'Sistemas 100% Nominais e Seguros'."
        )
        
        task = Task(
            id=f"cron-{int(datetime.now().timestamp())}",
            command=command,
            context={"source": "cronjob"}
        )
        
        try:
            result = await agent.run(task)
            
            # Se for crítico, avisa no log (futuramente dispara um Push pro celular/Telegram)
            if "emergência" in result.output.lower() or "crítico" in result.output.lower() or "alerta" in result.output.lower():
                print(f"🚨 [ALERTA DE SISTEMA] 🚨\n{result.output}\n")
            else:
                print(f"✅ [CRONJOB STATUS]: {result.output}")
                
        except Exception as e:
            print(f"⚠️ Erro no Cronjob: {str(e)}")
        
        # Aguarda 2 horas (7200 segundos) para rodar de novo
        await asyncio.sleep(7200)
