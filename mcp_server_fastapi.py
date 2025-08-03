# mcp_server_fastapi.py - BACKEND COM AGENTES REAIS (SEM SIMULAÇÃO)

import json
import uuid
import time
import asyncio
import threading
from typing import Optional, Literal, Dict, Any
from fastapi import FastAPI, BackgroundTasks, HTTPException, Path
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# IMPORTS DOS AGENTES REAIS - OBRIGATÓRIOS
try:
    from agents import agente_revisor
    from tools import preenchimento, commit_multiplas_branchs
    AGENTS_AVAILABLE = True
    print("✅ Agentes reais carregados com sucesso")
    
    # Verificar dependências críticas
    import openai
    import github
    print("✅ Dependências OpenAI e GitHub disponíveis")
    
    # Verificar variáveis de ambiente
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY não encontrada no .env")
        AGENTS_AVAILABLE = False
    if not os.getenv('GITHUB_TOKEN'):
        print("⚠️  GITHUB_TOKEN não encontrada no .env")
        AGENTS_AVAILABLE = False
        
    if AGENTS_AVAILABLE:
        print("✅ Configuração completa para agentes reais")
    else:
        print("❌ Configuração incompleta - verifique .env")
        
except ImportError as e:
    print(f"❌ ERRO CRÍTICO: Agentes não encontrados: {e}")
    print("❌ Execute: pip install PyGithub openai python-dotenv")
    print("❌ Verifique se os arquivos dos agentes existem:")
    print("   - agents/agente_revisor.py")
    print("   - tools/github_reader.py") 
    print("   - tools/revisor_geral.py")
    AGENTS_AVAILABLE = False
    exit(1)  # PARAR EXECUÇÃO - AGENTES SÃO OBRIGATÓRIOS

# --- Modelos de Dados ---
class StartAnalysisRequest(BaseModel):
    repo_name: str = Field(..., description="Nome do repositório GitHub (formato: owner/repo)")
    analysis_type: Literal["design", "relatorio_teste_unitario"] = Field(..., description="Tipo de análise")
    branch_name: Optional[str] = Field(None, description="Branch específica (opcional)")
    instrucoes_extras: Optional[str] = Field(None, description="Instruções adicionais")

class UpdateJobRequest(BaseModel):
    job_id: str = Field(..., description="ID do job")
    action: Literal["approve", "reject"] = Field(..., description="Ação a ser executada")

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    message: str
    progress: int
    error_details: Optional[str] = None
    last_updated: float

class StartAnalysisResponse(BaseModel):
    job_id: str
    report: str
    status: str

# --- Configuração do FastAPI ---
app = FastAPI(
    title="Agentes Peers - Backend com IA Real",
    description="Sistema de análise de código com IA multi-agentes (SEM SIMULAÇÃO)",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "https://your-frontend-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento em memória dos jobs
jobs: Dict[str, Dict[str, Any]] = {}

# --- WORKFLOW REGISTRY COM AGENTES REAIS ---
WORKFLOW_REGISTRY = {
    "design": {
        "description": "Análise de design e refatoração usando agentes reais",
        "agent_analysis_type": "design",  # Tipo para análise inicial
        "steps": [
            {
                "status": "refactoring_code", 
                "message": "Executando refatoração com IA...", 
                "agent_type": "refatoracao",
                "duration": 15
            },
            {
                "status": "grouping_commits", 
                "message": "Organizando commits por tema...", 
                "agent_type": "agrupamento_design",
                "duration": 8
            },
            {
                "status": "populating_data", 
                "message": "Aplicando mudanças no código...", 
                "agent_type": None,  # Usar ferramenta de preenchimento
                "duration": 10
            },
            {
                "status": "committing_to_github", 
                "message": "Criando commits organizados...", 
                "agent_type": None,  # Usar ferramenta de commit
                "duration": 12
            }
        ]
    },
    "relatorio_teste_unitario": {
        "description": "Geração de testes unitários usando agentes reais",
        "agent_analysis_type": "design",  # Análise inicial para entender código
        "steps": [
            {
                "status": "writing_unit_tests", 
                "message": "Gerando testes unitários com IA...", 
                "agent_type": "escrever_testes",
                "duration": 20
            },
            {
                "status": "grouping_tests", 
                "message": "Organizando estrutura de testes...", 
                "agent_type": "agrupamento_testes",
                "duration": 8
            },
            {
                "status": "populating_data", 
                "message": "Aplicando testes no projeto...", 
                "agent_type": None,
                "duration": 10
            },
            {
                "status": "committing_to_github", 
                "message": "Commitando testes organizados...", 
                "agent_type": None,
                "duration": 10
            }
        ]
    }
}

# --- Funções dos Agentes Reais ---

async def execute_real_analysis_step(job_id: str, step: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Executa uma etapa real da análise usando os agentes"""
    try:
        print(f"[{job_id}] Executando etapa: {step['status']}")
        
        if step.get("agent_type"):
            # Executar agente real
            print(f"[{job_id}] Chamando agente: {step['agent_type']}")
            
            resultado = agente_revisor.main(
                tipo_analise=step["agent_type"],
                repositorio=job_data["repo_name"],
                nome_branch=job_data.get("branch_name"),
                instrucoes_extras=job_data.get("instrucoes_extras", "")
            )
            
            print(f"[{job_id}] ✅ Agente executado com sucesso")
            return {
                "status": "success",
                "result": resultado,
                "message": f"Etapa {step['status']} concluída com agente {step['agent_type']}"
            }
            
        else:
            # Executar ferramenta específica
            if step["status"] == "populating_data":
                print(f"[{job_id}] Aplicando mudanças com ferramenta de preenchimento")
                resultado = preenchimento.main()
                
            elif step["status"] == "committing_to_github":
                print(f"[{job_id}] Criando commits com ferramenta de commit")
                resultado = commit_multiplas_branchs.main()
                
            else:
                resultado = {"status": "completed", "message": "Etapa processada"}
            
            print(f"[{job_id}] ✅ Ferramenta executada com sucesso")
            return {
                "status": "success", 
                "result": resultado,
                "message": f"Etapa {step['status']} concluída"
            }
            
    except Exception as e:
        print(f"[{job_id}] ❌ Erro na etapa {step['status']}: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": f"Falha na etapa {step['status']}"
        }

async def execute_full_workflow(job_id: str):
    """Executa workflow completo com agentes reais"""
    if not AGENTS_AVAILABLE:
        print(f"[{job_id}] ❌ Agentes não disponíveis")
        jobs[job_id].update({
            "status": "failed",
            "message": "Agentes não disponíveis - configure .env",
            "progress": 0,
            "last_updated": time.time()
        })
        return
    
    try:
        job = jobs.get(job_id)
        if not job:
            print(f"[{job_id}] ❌ Job não encontrado")
            return
        
        workflow = WORKFLOW_REGISTRY.get(job["analysis_type"])
        if not workflow:
            raise ValueError(f"Workflow não encontrado: {job['analysis_type']}")
        
        print(f"[{job_id}] 🚀 Iniciando workflow: {workflow['description']}")
        
        total_steps = len(workflow["steps"])
        progress_per_step = 75 / total_steps  # 75% restante dividido pelas etapas
        current_progress = 25  # Começa em 25% após aprovação
        
        # Executar cada etapa
        for i, step in enumerate(workflow["steps"]):
            if job_id not in jobs:
                print(f"[{job_id}] ⚠️ Job removido durante execução")
                break
            
            # Atualizar status
            current_progress += progress_per_step
            jobs[job_id].update({
                "status": step["status"],
                "message": step["message"],
                "progress": int(current_progress),
                "last_updated": time.time()
            })
            
            print(f"[{job_id}] {step['status']}: {step['message']} ({int(current_progress)}%)")
            
            # Executar etapa real
            resultado_etapa = await execute_real_analysis_step(job_id, step, job)
            
            if resultado_etapa["status"] == "error":
                # Falha na etapa
                jobs[job_id].update({
                    "status": "failed",
                    "message": f"Falha: {resultado_etapa['message']}",
                    "progress": int(current_progress),
                    "error_details": resultado_etapa.get("error"),
                    "last_updated": time.time()
                })
                print(f"[{job_id}] ❌ Workflow falhou na etapa {step['status']}")
                return
            
            # Simular tempo de processamento real
            await asyncio.sleep(min(step["duration"], 5))  # Máximo 5s por etapa para demo
        
        # Finalizar com sucesso
        if job_id in jobs:
            jobs[job_id].update({
                "status": "completed",
                "message": "Análise concluída com agentes reais!",
                "progress": 100,
                "last_updated": time.time()
            })
            print(f"[{job_id}] ✅ Workflow concluído com sucesso")
        
    except Exception as e:
        print(f"[{job_id}] ❌ Erro no workflow: {e}")
        if job_id in jobs:
            jobs[job_id].update({
                "status": "failed",
                "message": f"Erro na execução: {str(e)}",
                "progress": 0,
                "error_details": str(e),
                "last_updated": time.time()
            })

def generate_initial_report(repo_name: str, analysis_type: str, instrucoes_extras: str = "") -> str:
    """Gera relatório inicial usando agente real"""
    if not AGENTS_AVAILABLE:
        return "❌ Agentes não disponíveis. Configure OPENAI_API_KEY e GITHUB_TOKEN no .env"
    
    try:
        print(f"🤖 Gerando relatório inicial para {repo_name} (tipo: {analysis_type})")
        
        # Usar agente real para análise inicial
        workflow = WORKFLOW_REGISTRY.get(analysis_type)
        agent_type = workflow.get("agent_analysis_type", "design")
        
        resultado = agente_revisor.main(
            tipo_analise=agent_type,
            repositorio=repo_name,
            instrucoes_extras=instrucoes_extras or "Análise inicial para aprovação"
        )
        
        # Extrair relatório do resultado
        if resultado and "resultado" in resultado:
            if isinstance(resultado["resultado"], dict) and "reposta_final" in resultado["resultado"]:
                return resultado["resultado"]["reposta_final"]
            elif isinstance(resultado["resultado"], str):
                return resultado["resultado"]
        
        return "Relatório gerado com sucesso. Código analisado e pronto para processamento."
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório inicial: {e}")
        return f"❌ Erro na análise inicial: {str(e)}\n\nVerifique:\n- OPENAI_API_KEY no .env\n- GITHUB_TOKEN no .env\n- Acesso ao repositório {repo_name}"

# --- Endpoints da API ---

@app.get("/")
async def root():
    return {
        "message": "Backend Agentes Peers com IA Real funcionando!",
        "version": "3.0.0",
        "status": "ok",
        "agents_status": "real_agents" if AGENTS_AVAILABLE else "no_agents",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check():
    status = "healthy" if AGENTS_AVAILABLE else "unhealthy"
    return {
        "status": status,
        "message": "Backend funcionando com agentes reais" if AGENTS_AVAILABLE else "Agentes não disponíveis",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "agents_available": AGENTS_AVAILABLE,
        "openai_configured": bool(os.getenv('OPENAI_API_KEY')),
        "github_configured": bool(os.getenv('GITHUB_TOKEN'))
    }

@app.post("/start-analysis", response_model=StartAnalysisResponse)
async def start_analysis(request: StartAnalysisRequest):
    """Inicia uma nova análise usando agentes reais"""
    try:
        # Validar entrada
        if not request.repo_name.strip():
            raise HTTPException(status_code=400, detail="Nome do repositório é obrigatório")
        
        if not AGENTS_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="Agentes não disponíveis. Configure OPENAI_API_KEY e GITHUB_TOKEN no .env"
            )
        
        # Criar novo job
        job_id = str(uuid.uuid4())
        
        print(f"🎯 Iniciando análise real: {job_id} - {request.analysis_type} - {request.repo_name}")
        
        # Gerar relatório inicial usando agente real
        report = generate_initial_report(
            request.repo_name, 
            request.analysis_type, 
            request.instrucoes_extras
        )
        
        # Criar job no armazenamento
        jobs[job_id] = {
            "job_id": job_id,
            "repo_name": request.repo_name,
            "analysis_type": request.analysis_type,
            "branch_name": request.branch_name,
            "instrucoes_extras": request.instrucoes_extras,
            "status": "pending_approval",
            "message": "Relatório gerado com IA real. Aguardando aprovação...",
            "progress": 10,
            "report": report,
            "created_at": time.time(),
            "last_updated": time.time()
        }
        
        print(f"✅ Análise criada: {job_id} - {request.analysis_type} - {request.repo_name}")
        
        return StartAnalysisResponse(
            job_id=job_id,
            report=report,
            status="pending_approval"
        )
        
    except Exception as e:
        print(f"❌ Erro ao criar análise: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str = Path(..., description="ID do job")):
    """Obtém o status atual de um job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job = jobs[job_id]
    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        message=job["message"],
        progress=job["progress"],
        error_details=job.get("error_details"),
        last_updated=job["last_updated"]
    )

@app.post("/update-job-status")
async def update_job_status(request: UpdateJobRequest, background_tasks: BackgroundTasks):
    """Aprova ou rejeita um job para execução com agentes reais"""
    if request.job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job = jobs[request.job_id]
    
    if request.action == "approve":
        if not AGENTS_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="Agentes não disponíveis para execução"
            )
        
        # Atualizar status para aprovado
        jobs[request.job_id].update({
            "status": "approved",
            "message": "Análise aprovada! Iniciando processamento com agentes reais...",
            "progress": 25,
            "last_updated": time.time()
        })
        
        # Iniciar execução real em background
        background_tasks.add_task(execute_full_workflow, request.job_id)
        
        print(f"✅ Job aprovado para execução real: {request.job_id}")
        
        return {
            "job_id": request.job_id,
            "status": "approved",
            "message": "Análise aprovada e iniciada com agentes reais"
        }
    
    elif request.action == "reject":
        jobs[request.job_id].update({
            "status": "rejected",
            "message": "Análise rejeitada pelo usuário",
            "progress": 0,
            "last_updated": time.time()
        })
        
        print(f"❌ Job rejeitado: {request.job_id}")
        
        return {
            "job_id": request.job_id,
            "status": "rejected",
            "message": "Análise rejeitada"
        }

@app.get("/jobs")
async def list_jobs():
    """Lista todos os jobs"""
    return {
        "jobs": list(jobs.values()),
        "total": len(jobs),
        "agents_available": AGENTS_AVAILABLE
    }

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Remove um job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    del jobs[job_id]
    print(f"🗑️ Job removido: {job_id}")
    return {"message": "Job removido com sucesso"}

# --- Executar Servidor ---
if __name__ == "__main__":
    if not AGENTS_AVAILABLE:
        print("❌ ERRO: Não é possível iniciar sem agentes configurados!")
        print("❌ Configure .env com OPENAI_API_KEY e GITHUB_TOKEN")
        exit(1)
        
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)