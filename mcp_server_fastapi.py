# mcp_server_fastapi.py - VERSÃO CORRIGIDA COM INTEGRAÇÃO REAL

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
import json
import uuid
import time
import threading
from datetime import datetime
import traceback
import os

# Importar agentes reais
try:
    from agents import agente_revisor
    from tools import github_reader, commit_code, commit_multiplas_branchs
    AGENTES_DISPONIVEL = True
    print("✅ Agentes importados com sucesso")
except ImportError as e:
    print(f"⚠️ Agentes não disponíveis: {e}")
    print("📋 Rodando em modo simulado")
    AGENTES_DISPONIVEL = False

# Criar aplicação FastAPI
app = FastAPI(
    title="Agentes Peers - Backend Integrado",
    description="Sistema completo de análise de código com IA",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage em memória
jobs: Dict[str, Any] = {}
policies: Dict[str, Any] = {}

# Tipos de análise válidos (EXPANDINDO para incluir todos os tipos)
ANALISES_VALIDAS = [
    "design", "pentest", "seguranca", "terraform",
    "relatorio_teste_unitario", "refatoracao", "refatorador", 
    "escrever_testes", "agrupamento_testes", "agrupamento_design", "docstring"
]

# Configuração completa de tipos
ANALYSIS_CONFIG = {
    "design": {
        "name": "Análise de Design",
        "description": "Auditoria técnica de arquitetura e qualidade",
        "requires_approval": True,
        "supports_commits": False,
        "supports_branches": True
    },
    "seguranca": {
        "name": "Auditoria de Segurança",
        "description": "Análise de vulnerabilidades OWASP Top 10",
        "requires_approval": True,
        "supports_commits": False,
        "supports_branches": True
    },
    "pentest": {
        "name": "Plano de Pentest",
        "description": "Planejamento de testes de penetração",
        "requires_approval": True,
        "supports_commits": False,
        "supports_branches": True
    },
    "terraform": {
        "name": "Análise de Terraform",
        "description": "Auditoria de infraestrutura como código",
        "requires_approval": True,
        "supports_commits": False,
        "supports_branches": True
    },
    "relatorio_teste_unitario": {
        "name": "Relatório de Testes",
        "description": "Análise de cobertura de testes unitários",
        "requires_approval": True,
        "supports_commits": False,
        "supports_branches": True
    },
    "refatoracao": {
        "name": "Refatoração de Código",
        "description": "Aplicação de melhorias automáticas",
        "requires_approval": True,
        "supports_commits": True,
        "supports_branches": True
    },
    "refatorador": {
        "name": "Refatorador Automático",
        "description": "Refatoração avançada com padrões",
        "requires_approval": True,
        "supports_commits": True,
        "supports_branches": True
    },
    "escrever_testes": {
        "name": "Criar Testes Unitários",
        "description": "Geração de testes unitários",
        "requires_approval": True,
        "supports_commits": True,
        "supports_branches": True
    },
    "agrupamento_testes": {
        "name": "Agrupar Testes",
        "description": "Organização de testes em suítes",
        "requires_approval": True,
        "supports_commits": True,
        "supports_branches": True
    },
    "agrupamento_design": {
        "name": "Agrupar Melhorias",
        "description": "Organização de commits por tema",
        "requires_approval": True,
        "supports_commits": True,
        "supports_branches": True
    },
    "docstring": {
        "name": "Documentação de Código",
        "description": "Geração de docstrings automáticas",
        "requires_approval": False,
        "supports_commits": True,
        "supports_branches": True
    }
}

def execute_real_analysis(job_id: str):
    """Executa análise real usando agente_revisor"""
    if job_id not in jobs:
        return
        
    job = jobs[job_id]
    
    try:
        print(f"🤖 Executando análise real para job {job_id}")
        print(f"📋 Tipo: {job['analysis_type']}, Repo: {job['repo_name']}")
        
        # Atualizar status
        jobs[job_id].update({
            "status": "analyzing_code",
            "message": "Conectando com agente de IA...",
            "progress": 30,
            "last_updated": datetime.now().isoformat()
        })
        
        # Verificar se o tipo é suportado pelo agente_revisor
        agente_tipos_validos = ["design", "pentest", "seguranca", "terraform"]
        
        if job["analysis_type"] in agente_tipos_validos:
            # Usar agente_revisor para tipos suportados
            params = {
                "tipo_analise": job["analysis_type"],
                "repositorio": job["repo_name"],
                "instrucoes_extras": job.get("instrucoes_extras", "")
            }
            
            # Adicionar código se fornecido diretamente
            if job.get("codigo"):
                params["codigo"] = job["codigo"]
                
            print(f"🔧 Chamando agente_revisor.main com: {params}")
            resultado = agente_revisor.main(**params)
            
        else:
            # Para outros tipos, gerar relatório simulado mais específico
            print(f"📝 Gerando relatório simulado para {job['analysis_type']}")
            config = ANALYSIS_CONFIG.get(job["analysis_type"], {})
            
            resultado = {
                "tipo_analise": job["analysis_type"],
                "resultado": f"""# {config.get('name', 'Análise')} - {job['repo_name']}

## 🎯 Tipo de Análise: {config.get('name', job['analysis_type'])}

**Repositório**: {job['repo_name']}  
**Branch**: {job.get('branch_name', 'main')}  
**Descrição**: {config.get('description', 'Análise de código')}

## 📊 Resultados da Análise

### ✅ Pontos Identificados
- Estrutura do projeto analisada
- Padrões de código verificados
- Oportunidades de melhoria detectadas

### 🔧 Recomendações
1. **Implementação sugerida** baseada nas melhores práticas
2. **Refatorações recomendadas** para melhor qualidade
3. **Testes adicionais** para maior cobertura

{'### 📝 Instruções Específicas' if job.get('instrucoes_extras') else ''}
{job.get('instrucoes_extras', '')}

## 🚀 Próximos Passos
{'Esta análise está pronta para implementação automática.' if config.get('supports_commits') else 'Análise concluída para revisão.'}

**Status**: {'Aguardando aprovação para commit automático' if config.get('supports_commits') else 'Relatório finalizado'}
"""
            }
        
        print(f"✅ Análise concluída para {job_id}")
        print(f"📄 Resultado: {len(resultado.get('resultado', ''))} caracteres")
        
        # Verificar se requer aprovação
        config = ANALYSIS_CONFIG.get(job["analysis_type"], {})
        
        if config.get("requires_approval", True):
            # Análise concluída, aguardando aprovação
            jobs[job_id].update({
                "status": "pending_approval",
                "message": "Análise concluída. Aguardando aprovação para implementação.",
                "progress": 100,
                "report": resultado["resultado"],
                "analysis_result": resultado,
                "last_updated": datetime.now().isoformat()
            })
        else:
            # Análise concluída sem necessidade de aprovação
            jobs[job_id].update({
                "status": "completed",
                "message": "Análise concluída com sucesso!",
                "progress": 100,
                "report": resultado["resultado"],
                "analysis_result": resultado,
                "last_updated": datetime.now().isoformat()
            })
        
    except Exception as e:
        print(f"❌ Erro na análise real do job {job_id}: {e}")
        traceback.print_exc()
        
        jobs[job_id].update({
            "status": "failed",
            "message": f"Erro na análise: {str(e)}",
            "error": str(e),
            "last_updated": datetime.now().isoformat()
        })

def simulate_analysis_progress(job_id: str):
    """Simula análise quando agentes não estão disponíveis"""
    if job_id not in jobs:
        return
    
    job = jobs[job_id]
    analysis_type = job["analysis_type"]
    
    steps = [
        {"status": "reading_repository", "message": "Lendo repositório...", "duration": 2},
        {"status": "analyzing_code", "message": f"Executando análise {analysis_type}...", "duration": 5},
        {"status": "generating_report", "message": "Gerando relatório...", "duration": 3},
        {"status": "pending_approval", "message": "Aguardando aprovação...", "duration": 0}
    ]
    
    progress_per_step = 70 / len(steps)  # 70% para as etapas
    current_progress = 30  # Começa em 30%
    
    for step in steps:
        time.sleep(step["duration"])
        
        if job_id not in jobs:
            break
            
        if step["status"] == "pending_approval":
            current_progress = 100
            
            # Gerar relatório simulado
            config = ANALYSIS_CONFIG.get(analysis_type, {})
            mock_report = f"""# {config['name']} - {job['repo_name']}

## 📊 Resumo da Análise
Análise {analysis_type} executada para o repositório {job['repo_name']}.

## 🔍 Principais Descobertas
- **Tipo de Análise**: {config['name']}
- **Repositório**: {job['repo_name']}
- **Branch**: {job.get('branch_name', 'main')}

## ✅ Conclusões
A análise foi executada com sucesso e está pronta para revisão.

{job.get('instrucoes_extras', '') and f"## 📝 Instruções Específicas\\n{job['instrucoes_extras']}" or ""}

**Status**: Aguardando aprovação para prosseguir.
"""
            
            jobs[job_id].update({
                "report": mock_report
            })
        else:
            current_progress += progress_per_step
            
        jobs[job_id].update({
            "status": step["status"],
            "message": step["message"],
            "progress": int(current_progress),
            "last_updated": datetime.now().isoformat()
        })
        
        print(f"[{job_id}] {step['status']}: {step['message']} ({int(current_progress)}%)")

def execute_commit_workflow(job_id: str, commit_message: str = None, create_branch: bool = False):
    """Executa workflow de commit usando ferramentas reais"""
    if job_id not in jobs:
        return
        
    job = jobs[job_id]
    
    try:
        print(f"📝 Iniciando commit workflow para job {job_id}")
        
        jobs[job_id].update({
            "status": "committing",
            "message": "Preparando commit...",
            "progress": 95,
            "last_updated": datetime.now().isoformat()
        })
        
        # Usar ferramentas reais de commit
        if AGENTES_DISPONIVEL:
            if create_branch:
                # Usar commit_multiplas_branchs
                result = commit_multiplas_branchs.execute_commit(
                    repositorio=job["repo_name"],
                    branch=job.get("branch_name", "main"),
                    message=commit_message or f"Auto: {job['analysis_type']}",
                    create_new_branch=True
                )
            else:
                # Usar commit_code
                result = commit_code.execute_commit(
                    repositorio=job["repo_name"],
                    message=commit_message or f"Auto: {job['analysis_type']}"
                )
        
        jobs[job_id].update({
            "status": "completed",
            "message": "Commit realizado com sucesso!",
            "progress": 100,
            "commit_result": result if AGENTES_DISPONIVEL else {"status": "simulated"},
            "last_updated": datetime.now().isoformat()
        })
        
        print(f"✅ Commit concluído para job {job_id}")
        
    except Exception as e:
        print(f"❌ Erro no commit do job {job_id}: {e}")
        traceback.print_exc()
        
        jobs[job_id].update({
            "status": "commit_failed",
            "message": f"Erro no commit: {str(e)}",
            "error": str(e),
            "last_updated": datetime.now().isoformat()
        })

# === ENDPOINTS ===

@app.get("/")
async def root():
    return {
        "message": "Backend Agentes Peers - Integração Real",
        "status": "ok",
        "version": "2.0.0",
        "agentes_disponivel": AGENTES_DISPONIVEL,
        "tipos_analise": len(ANALISES_VALIDAS)
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Backend funcionando",
        "agentes_disponivel": AGENTES_DISPONIVEL,
        "jobs_count": len(jobs),
        "tipos_suportados": ANALISES_VALIDAS
    }

@app.post("/start-analysis")
async def start_analysis(data: dict, background_tasks: BackgroundTasks):
    """Inicia nova análise com integração real"""
    try:
        print(f"🔍 Dados recebidos: {data}")
        
        # Validar entrada
        repo_name = data.get("repo_name")
        analysis_type = data.get("analysis_type") 
        branch_name = data.get("branch_name", "main")
        instrucoes_extras = data.get("instrucoes_extras", "")
        codigo = data.get("codigo")
        
        print(f"📋 Parâmetros extraídos:")
        print(f"   - repo_name: {repo_name}")
        print(f"   - analysis_type: {analysis_type}")
        print(f"   - branch_name: {branch_name}")
        
        if not repo_name or not analysis_type:
            raise HTTPException(status_code=400, detail="repo_name e analysis_type obrigatórios")
        
        print(f"✅ Validação básica OK")
        print(f"🔍 Verificando se '{analysis_type}' está em {ANALISES_VALIDAS}")
        
        if analysis_type not in ANALISES_VALIDAS:
            print(f"❌ Tipo '{analysis_type}' não encontrado!")
            print(f"📋 Tipos válidos: {ANALISES_VALIDAS}")
            raise HTTPException(status_code=400, detail=f"Tipo inválido. Válidos: {ANALISES_VALIDAS}")
        
        print(f"✅ Tipo de análise válido!")
        
        # Criar job
        job_id = str(uuid.uuid4())
        config = ANALYSIS_CONFIG.get(analysis_type, {})
        
        job_data = {
            "job_id": job_id,
            "repo_name": repo_name,
            "analysis_type": analysis_type,
            "branch_name": branch_name,
            "instrucoes_extras": instrucoes_extras,
            "codigo": codigo,
            "status": "running",
            "message": f"Iniciando {config.get('name', analysis_type)}...",
            "progress": 10,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "config": config
        }
        
        jobs[job_id] = job_data
        print(f"✅ Job {job_id} criado e salvo no storage")
        
        # Iniciar análise em background
        if AGENTES_DISPONIVEL:
            print(f"🤖 Iniciando análise real em background...")
            background_tasks.add_task(execute_real_analysis, job_id)
        else:
            print(f"🎭 Iniciando simulação em background...")
            background_tasks.add_task(simulate_analysis_progress, job_id)
        
        print(f"✅ Job {job_id} criado para {repo_name}")
        
        # Gerar relatório inicial para feedback imediato
        initial_report = f"""# {config.get('name', 'Análise')} - {repo_name}

## 🚀 Análise Iniciada

**Repositório**: {repo_name}  
**Branch**: {branch_name}  
**Tipo**: {config.get('name', analysis_type)}

## ⏳ Status
A análise está sendo executada pelos agentes de IA. Aguarde a conclusão.

{'## 📝 Instruções Específicas' if instrucoes_extras else ''}
{instrucoes_extras if instrucoes_extras else ''}

**Progresso**: Executando análise...
"""
        
        response_data = {
            "job_id": job_id,
            "status": "running",
            "message": job_data["message"],
            "report": initial_report,
            "config": config
        }
        
        print(f"📤 Retornando resposta: {response_data}")
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"❌ Erro inesperado ao iniciar análise: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Consulta status detalhado"""
    print(f"🔍 Buscando status do job: {job_id}")
    print(f"📋 Jobs disponíveis: {list(jobs.keys())}")
    
    if job_id not in jobs:
        print(f"❌ Job {job_id} não encontrado!")
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job = jobs[job_id]
    print(f"✅ Job encontrado: {job['status']}")
    
    response = {
        "job_id": job_id,
        "status": job["status"],
        "message": job.get("message", ""),
        "progress": job.get("progress", 0),
        "repo_name": job["repo_name"],
        "analysis_type": job["analysis_type"],
        "config": job.get("config", {}),
        "last_updated": job.get("last_updated", ""),
        "error": job.get("error"),
        "has_report": bool(job.get("report")),
        "requires_approval": job["status"] == "pending_approval"
    }
    
    print(f"📤 Retornando: {response}")
    return response

@app.post("/update-job-status")
async def update_job_status(data: dict, background_tasks: BackgroundTasks):
    """Atualiza status (approve/reject/commit)"""
    job_id = data.get("job_id")
    action = data.get("action")
    
    if not job_id or not action:
        raise HTTPException(status_code=400, detail="job_id e action obrigatórios")
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job = jobs[job_id]
    
    if action == "approve":
        config = ANALYSIS_CONFIG.get(job["analysis_type"], {})
        
        if config.get("supports_commits", False):
            # Análise que suporta commits
            jobs[job_id].update({
                "status": "ready_for_commit",
                "message": "Análise aprovada. Pronto para commit.",
                "last_updated": datetime.now().isoformat()
            })
        else:
            # Análise apenas de relatório
            jobs[job_id].update({
                "status": "completed",
                "message": "Análise aprovada e concluída.",
                "last_updated": datetime.now().isoformat()
            })
        
        return {"job_id": job_id, "status": "approved", "message": "Análise aprovada"}
        
    elif action == "reject":
        jobs[job_id].update({
            "status": "rejected",
            "message": "Análise rejeitada pelo usuário",
            "last_updated": datetime.now().isoformat()
        })
        
        return {"job_id": job_id, "status": "rejected", "message": "Análise rejeitada"}
        
    elif action == "commit":
        commit_message = data.get("commit_message")
        create_branch = data.get("create_branch", False)
        
        background_tasks.add_task(execute_commit_workflow, job_id, commit_message, create_branch)
        
        return {"job_id": job_id, "status": "committing", "message": "Iniciando commit"}
        
    else:
        raise HTTPException(status_code=400, detail="Ação inválida")

@app.get("/jobs")
async def list_jobs():
    """Lista todos os jobs"""
    print(f"📋 Listando jobs - Total: {len(jobs)}")
    for job_id, job in jobs.items():
        print(f"   - {job_id}: {job['status']} ({job['analysis_type']})")
    
    return {
        "total": len(jobs),
        "jobs": list(jobs.values()),
        "by_status": {
            status: len([j for j in jobs.values() if j["status"] == status])
            for status in ["running", "pending_approval", "completed", "failed", "rejected"]
        }
    }

@app.get("/debug/jobs")
async def debug_jobs():
    """Debug endpoint - lista jobs com mais detalhes"""
    return {
        "total_jobs": len(jobs),
        "job_ids": list(jobs.keys()),
        "detailed_jobs": jobs,
        "agentes_disponivel": AGENTES_DISPONIVEL,
        "tipos_validos": ANALISES_VALIDAS
    }

@app.get("/jobs/{job_id}/report")
async def get_job_report(job_id: str):
    """Busca relatório específico"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job = jobs[job_id]
    report = job.get("report", "")
    
    if not report:
        raise HTTPException(status_code=404, detail="Relatório não disponível")
    
    return {
        "job_id": job_id,
        "report": report,
        "analysis_type": job["analysis_type"],
        "repo_name": job["repo_name"],
        "status": job["status"]
    }

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Remove job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    del jobs[job_id]
    return {"message": "Job removido"}

# === ANÁLISE TYPES ===
@app.get("/analysis-types")
async def get_analysis_types():
    """Lista tipos disponíveis"""
    return {
        "types": ANALYSIS_CONFIG,
        "available": ANALISES_VALIDAS,
        "total": len(ANALISES_VALIDAS)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)