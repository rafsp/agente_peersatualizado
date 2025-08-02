# mcp_server_fastapi_integrado.py - VERSÃO COMPLETA CORRIGIDA
from fastapi import FastAPI, BackgroundTasks, HTTPException
from typing import Optional, Dict, Any
import json
import uuid
import time
import threading
import os

# Imports dos agentes reais
try:
   import sys
   sys.path.append(os.path.dirname(os.path.abspath(__file__)))
   from agents import agente_revisor
   AGENTES_DISPONIVEIS = True
   print("✅ Agentes reais carregados com sucesso!")
except ImportError as e:
   print(f"⚠️ Agentes reais não encontrados: {e}")
   AGENTES_DISPONIVEIS = False

# Criar aplicação FastAPI
app = FastAPI(
   title="Agentes Peers - Backend Integrado",
   description="Sistema de análise de código com IA - Integração com agentes reais",
   version="2.0.0"
)

# Armazenar jobs em memória
jobs = {}

def executar_agente_real(job_id: str, repo_name: str, analysis_type: str, instrucoes_extras: str = ""):
   """Executa a análise real usando os agentes"""
   try:
       print(f"🤖 Executando agente real para job {job_id}")
       print(f"📁 Repositório: {repo_name}")
       print(f"🔍 Tipo: {analysis_type}")
       
       # Atualizar status para iniciando
       if job_id in jobs:
           jobs[job_id].update({
               "status": "workflow_started",
               "message": "Conectando aos agentes de IA...",
               "progress": 30
           })
       
       # Simular etapas de progresso
       time.sleep(2)
       if job_id in jobs:
           jobs[job_id].update({
               "status": "reading_repository",
               "message": "Lendo código do repositório...",
               "progress": 50
           })
       
       time.sleep(2)
       if job_id in jobs:
           jobs[job_id].update({
               "status": "analyzing_code",
               "message": "Agentes analisando o código...",
               "progress": 70
           })
       
       # Chamar o agente real usando executar_analise
       if AGENTES_DISPONIVEIS:
           resultado = agente_revisor.main(
               tipo_analise=analysis_type,
               repositorio=repo_name,
               instrucoes_extras=instrucoes_extras
           )
           
           # Extrair o resultado da análise
           if isinstance(resultado, dict) and 'resultado' in resultado:
               report_content = resultado['resultado']
           else:
               report_content = str(resultado)
               
           # Atualizar com resultado real
           if job_id in jobs:
               jobs[job_id].update({
                   "status": "completed",
                   "message": "Análise real concluída com sucesso!",
                   "progress": 100,
                   "report": f"""# ✅ Análise Real Concluída - {repo_name}

## 🤖 Tipo de Análise
**{jobs[job_id].get('original_type', analysis_type)}** (processado como {analysis_type})

## 📊 Resultado da Análise Real
{report_content}

## 🔍 Detalhes da Execução
- **Agente Utilizado**: agente_revisor.executar_analise()
- **Repositório**: {repo_name}
- **Instruções Extras**: {instrucoes_extras or 'Nenhuma'}
- **Status**: ✅ Análise real executada com sucesso
- **Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S')}

---
**🎉 Esta foi uma análise REAL feita pelos seus agentes de IA!**
""",
                   "real_analysis": True,
                   "last_updated": time.time()
               })
               
           print(f"✅ Análise real concluída para job {job_id}")
           
       else:
           simulate_real_analysis(job_id, repo_name, analysis_type, instrucoes_extras)
           
   except Exception as e:
       print(f"❌ Erro na execução do agente real: {e}")
       import traceback
       traceback.print_exc()
       if job_id in jobs:
           jobs[job_id].update({
               "status": "failed",
               "message": f"Erro na análise real: {str(e)}",
               "progress": 0,
               "error_details": str(e),
               "last_updated": time.time()
           })

def simulate_real_analysis(job_id: str, repo_name: str, analysis_type: str, instrucoes_extras: str = ""):
   """Simula análise quando agentes não estão disponíveis"""
   time.sleep(3)
   if job_id in jobs:
       jobs[job_id].update({
           "status": "completed",
           "message": "Simulação concluída",
           "progress": 100,
           "report": f"""# ⚠️ Análise Simulada - {repo_name}

## 🚨 MODO SIMULAÇÃO ATIVO
Os agentes reais não estão disponíveis.

## 📋 Tipo Solicitado
{analysis_type}

## 🛠️ Para Ativar Análise Real
1. Verifique se a pasta 'agents' existe
2. Verifique se agente_revisor.py está presente
3. Configure OPENAI_API_KEY
4. Reinicie o servidor

**Status**: ⚠️ Simulação - Configure os agentes reais
""",
           "real_analysis": False,
           "last_updated": time.time()
       })

@app.get("/")
async def root():
   agente_status = "✅ Disponíveis" if AGENTES_DISPONIVEIS else "⚠️ Simulação"
   return {
       "message": "Backend Agentes Peers - Versão Integrada",
       "status": "ok",
       "version": "2.0.0",
       "agentes_reais": agente_status,
       "modo": "PRODUÇÃO" if AGENTES_DISPONIVEIS else "SIMULAÇÃO"
   }

@app.get("/health")
async def health_check():
   return {
       "status": "healthy",
       "message": "Backend integrado funcionando",
       "agentes_reais_disponiveis": AGENTES_DISPONIVEIS,
       "environment": os.getenv("ENVIRONMENT", "development")
   }

@app.post("/start-analysis")
async def start_analysis_integrado(data: dict, background_tasks: BackgroundTasks):
   """Inicia análise usando agentes reais ou simulação"""
   try:
       repo_name = data.get("repo_name")
       analysis_type = data.get("analysis_type")
       branch_name = data.get("branch_name", "main")
       instrucoes_extras = data.get("instrucoes_extras", "")
       
       if not repo_name or not analysis_type:
           raise HTTPException(status_code=400, detail="repo_name e analysis_type são obrigatórios")
       
       # Mapear tipos de análise para os agentes reais
       type_mapping = {
           "criar_testes_unitarios": "design",
           "relatorio_teste_unitario": "design", 
           "design": "design",
           "seguranca": "seguranca",
           "pentest": "pentest", 
           "terraform": "terraform"
       }
       
       # Normalizar o tipo de análise
       analysis_type_normalized = analysis_type.lower().replace(" ", "_").replace("-", "_")
       
       # Mapear para o tipo do agente
       mapped_type = type_mapping.get(analysis_type_normalized, "design")
       
       job_id = str(uuid.uuid4())
       modo = "REAL" if AGENTES_DISPONIVEIS else "SIMULAÇÃO"
       
       initial_report = f"""# 🚀 Análise Iniciada - {repo_name}

## 📊 Status Inicial
- **Modo**: {modo}
- **Tipo Solicitado**: {analysis_type}
- **Tipo Mapeado**: {mapped_type}
- **Repositório**: {repo_name}
- **Branch**: {branch_name}
- **Job ID**: {job_id}

## 🎯 Próximos Passos
{'Os agentes de IA reais irão analisar o código do repositório.' if AGENTES_DISPONIVEIS else 'Executando em modo simulação até configurar os agentes reais.'}

**Status**: Aguardando aprovação para prosseguir...
"""
       
       jobs[job_id] = {
           "status": "pending_approval",
           "repo_name": repo_name,
           "analysis_type": mapped_type,  # Usar o tipo mapeado para o agente
           "original_type": analysis_type,  # Manter o original para referência
           "branch_name": branch_name,
           "instrucoes_extras": instrucoes_extras,
           "created_at": time.time(),
           "report": initial_report,
           "message": f"Análise {'real' if AGENTES_DISPONIVEIS else 'simulada'} pronta. Aguardando aprovação...",
           "progress": 10,
           "real_mode": AGENTES_DISPONIVEIS
       }
       
       print(f"🎯 Nova análise criada: {job_id}")
       print(f"📁 Repositório: {repo_name}")
       print(f"🔍 Tipo: {analysis_type} -> {mapped_type}")
       print(f"🤖 Modo: {modo}")
       
       return {
           "job_id": job_id,
           "report": initial_report,
           "status": "success",
           "mode": modo
       }
       
   except HTTPException:
       raise
   except Exception as e:
       print(f"❌ Erro ao criar análise: {e}")
       import traceback
       traceback.print_exc()
       raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
   """Consultar status de um job"""
   job = jobs.get(job_id)
   if not job:
       raise HTTPException(status_code=404, detail="Job não encontrado")
   
   return {
       "job_id": job_id,
       "status": job["status"],
       "repo_name": job["repo_name"],
       "analysis_type": job["analysis_type"],
       "message": job.get("message", "Processando..."),
       "progress": job.get("progress", 0),
       "real_mode": job.get("real_mode", False),
       "error_details": job.get("error_details"),
       "last_updated": job.get("last_updated", job["created_at"])
   }

@app.get("/jobs")
async def list_jobs():
   """Listar todos os jobs"""
   jobs_list = []
   for job_id, job_data in jobs.items():
       jobs_list.append({
           "job_id": job_id,
           "repo_name": job_data["repo_name"],
           "analysis_type": job_data["analysis_type"],
           "original_type": job_data.get("original_type", job_data["analysis_type"]),
           "status": job_data["status"],
           "created_at": job_data["created_at"],
           "progress": job_data.get("progress", 0),
           "real_mode": job_data.get("real_mode", False)
       })
   
   return {
       "total": len(jobs),
       "agentes_reais_disponiveis": AGENTES_DISPONIVEIS,
       "jobs": jobs_list
   }

@app.post("/update-job-status")
async def update_job_status(data: dict, background_tasks: BackgroundTasks):
   """Atualizar status de um job"""
   job_id = data.get("job_id")
   action = data.get("action")
   
   if not job_id or not action:
       raise HTTPException(status_code=400, detail="job_id e action são obrigatórios")
   
   job = jobs.get(job_id)
   if not job:
       raise HTTPException(status_code=404, detail="Job não encontrado")
   
   if action == "approve":
       job["status"] = "approved"
       job["message"] = "Análise aprovada! Iniciando processamento..."
       job["progress"] = 25
       job["last_updated"] = time.time()
       
       # Executar análise real ou simulada em background
       background_tasks.add_task(
           executar_agente_real,
           job_id,
           job["repo_name"],
           job["analysis_type"],
           job["instrucoes_extras"]
       )
       
       message = f"Job aprovado! {'Agentes reais' if AGENTES_DISPONIVEIS else 'Simulação'} iniciados."
       print(f"✅ Job {job_id} aprovado - iniciando {'análise real' if AGENTES_DISPONIVEIS else 'simulação'}")
       
   elif action == "reject":
       job["status"] = "rejected"
       job["message"] = "Análise rejeitada pelo usuário"
       job["progress"] = 0
       job["last_updated"] = time.time()
       message = "Job rejeitado pelo usuário"
       print(f"❌ Job {job_id} rejeitado pelo usuário")
       
   else:
       raise HTTPException(status_code=400, detail="Ação inválida. Use 'approve' ou 'reject'")
   
   return {
       "job_id": job_id,
       "status": job["status"],
       "message": message,
       "mode": "REAL" if AGENTES_DISPONIVEIS else "SIMULAÇÃO"
   }

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
   """Deletar um job"""
   if job_id not in jobs:
       raise HTTPException(status_code=404, detail="Job não encontrado")
   
   del jobs[job_id]
   return {"message": f"Job {job_id} deletado com sucesso"}

@app.get("/agentes/status")
async def get_agentes_status():
   """Verificar status dos agentes"""
   return {
       "agentes_disponiveis": AGENTES_DISPONIVEIS,
       "modo": "PRODUÇÃO" if AGENTES_DISPONIVEIS else "SIMULAÇÃO",
       "tipos_analise_suportados": [
           "design", 
           "relatorio_teste_unitario", 
           "criar_testes_unitarios",
           "seguranca", 
           "pentest", 
           "terraform"
       ],
       "mapeamento_tipos": {
           "criar_testes_unitarios": "design",
           "relatorio_teste_unitario": "design", 
           "design": "design",
           "seguranca": "seguranca",
           "pentest": "pentest", 
           "terraform": "terraform"
       } if AGENTES_DISPONIVEIS else None
   }

# Endpoint de teste para verificar os agentes diretamente
@app.post("/test-agente")
async def test_agente_real(data: dict):
   """Endpoint para testar os agentes diretamente"""
   if not AGENTES_DISPONIVEIS:
       return {
           "error": "Agentes reais não disponíveis",
           "modo": "SIMULAÇÃO",
           "instrucoes": "Configure o módulo 'agents' para ativar análises reais"
       }
   
   try:
       tipo_analise = data.get("tipo_analise", "design")
       repositorio = data.get("repositorio", "test/repo")
       instrucoes_extras = data.get("instrucoes_extras", "")
       
       print(f"🧪 Teste direto do agente: {tipo_analise} - {repositorio}")
       
       resultado = agente_revisor.executar_analise(
           tipo_analise=tipo_analise,
           repositorio=repositorio,
           instrucoes_extras=instrucoes_extras
       )
       
       return {
           "success": True,
           "resultado": resultado,
           "modo": "TESTE_REAL",
           "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
       }
       
   except Exception as e:
       print(f"❌ Erro no teste do agente: {e}")
       import traceback
       traceback.print_exc()
       return {
           "error": f"Erro ao testar agente: {str(e)}",
           "modo": "ERRO",
           "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
       }

# Endpoint adicional para debug
@app.get("/debug/info")
async def debug_info():
   """Informações de debug do sistema"""
   return {
       "agentes_disponiveis": AGENTES_DISPONIVEIS,
       "total_jobs": len(jobs),
       "jobs_por_status": {
           "pending_approval": len([j for j in jobs.values() if j["status"] == "pending_approval"]),
           "approved": len([j for j in jobs.values() if j["status"] == "approved"]),
           "completed": len([j for j in jobs.values() if j["status"] == "completed"]),
           "failed": len([j for j in jobs.values() if j["status"] == "failed"]),
           "rejected": len([j for j in jobs.values() if j["status"] == "rejected"])
       },
       "python_path": sys.path[:3],  # Primeiros 3 caminhos
       "working_directory": os.getcwd(),
       "environment_vars": {
           "OPENAI_API_KEY": "✅ Configurada" if os.getenv("OPENAI_API_KEY") else "❌ Não configurada",
           "DEBUG": os.getenv("DEBUG", "não definida"),
           "ENVIRONMENT": os.getenv("ENVIRONMENT", "não definida")
       }
   }