# mcp_server_fastapi_clean.py - Backend Limpo e Funcional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import uuid
import time
import asyncio
import threading
import os
from datetime import datetime

# Importar agentes existentes
try:
    from agents import agente_revisor
    print("✅ Agente revisor importado com sucesso")
except ImportError as e:
    print(f"⚠️ Erro ao importar agente_revisor: {e}")
    agente_revisor = None

# Configuração da aplicação FastAPI
app = FastAPI(
    title="Agentes Peers - Backend",
    description="Sistema de análise de código com IA multi-agentes",
    version="2.0.0"
)

# Configurar CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenar jobs em memória
jobs: Dict[str, Dict[str, Any]] = {}

# Modelos Pydantic para validação de dados
class StartAnalysisRequest(BaseModel):
    repo_name: str
    analysis_type: str
    branch_name: Optional[str] = None
    instrucoes_extras: Optional[str] = ""

class UpdateJobRequest(BaseModel):
    job_id: str
    action: str

# Mapeamento de tipos de análise
ANALYSIS_TYPE_MAPPING = {
    "design": "design",
    "relatorio_teste_unitario": "design",
    "security": "seguranca",
    "pentest": "pentest",
    "terraform": "terraform"
}

@app.get("/")
async def root():
    return {
        "message": "Backend Agentes Peers funcionando!",
        "status": "ok",
        "version": "2.0.0",
        "chatgpt_integration": "enabled"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Backend está funcionando",
        "environment": "production",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/start-analysis")
async def start_analysis(request: StartAnalysisRequest):
    """Inicia uma análise de código usando IA - EXECUÇÃO DIRETA"""
    try:
        print(f"🚀 Iniciando análise para: {request.repo_name}")
        
        # Validar tipo de análise
        valid_types = ["design", "relatorio_teste_unitario", "security", "pentest", "terraform"]
        if request.analysis_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de análise inválido. Tipos válidos: {valid_types}"
            )
        
        # Criar job
        job_id = str(uuid.uuid4())
        
        # Verificar se agente está disponível
        if not agente_revisor:
            raise HTTPException(status_code=500, detail="Agente revisor não disponível")
        
        try:
            # Executar análise DIRETAMENTE (não em background)
            mapped_analysis_type = ANALYSIS_TYPE_MAPPING.get(request.analysis_type, "design")
            
            print(f"🤖 Executando análise {mapped_analysis_type} para {request.repo_name}")
            
            resultado = agente_revisor.main(
                tipo_analise=mapped_analysis_type,
                repositorio=request.repo_name,
                instrucoes_extras=request.instrucoes_extras or ""
            )
            
            # Extrair resultado real
            real_report = resultado.get("resultado", "Erro: Nenhum resultado gerado")
            
            print(f"✅ Análise concluída! Resultado: {len(real_report)} caracteres")
            
            # Armazenar job com resultado REAL
            jobs[job_id] = {
                "job_id": job_id,
                "repo_name": request.repo_name,
                "analysis_type": request.analysis_type,
                "branch_name": request.branch_name,
                "instrucoes_extras": request.instrucoes_extras,
                "status": "completed",  # Já completado pois análise foi feita
                "message": "Análise com IA concluída com sucesso!",
                "progress": 100,
                "created_at": time.time(),
                "last_updated": time.time(),
                "report": real_report,  # RESULTADO REAL DA IA
                "result": resultado,
                "ai_analysis_completed": True
            }
            
            return {
                "job_id": job_id,
                "report": real_report,  # RETORNAR RESULTADO REAL
                "status": "completed"
            }
            
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
            
            # Template de erro
            error_report = f"""# Erro na Análise - {request.repo_name}

## Status
❌ **Erro**: Falha ao executar análise

## Detalhes
- **Repositório**: {request.repo_name}
- **Tipo**: {request.analysis_type}
- **Erro**: {str(e)}

## Próximos Passos
1. Verifique se o repositório existe e é público
2. Confirme se as chaves API estão configuradas
3. Tente novamente em alguns minutos

**Status**: ❌ Análise falhou
"""
            
            jobs[job_id] = {
                "job_id": job_id,
                "repo_name": request.repo_name,
                "analysis_type": request.analysis_type,
                "status": "failed",
                "message": f"Erro na análise: {str(e)}",
                "progress": 0,
                "created_at": time.time(),
                "last_updated": time.time(),
                "report": error_report,
                "error_details": str(e)
            }
            
            return {
                "job_id": job_id,
                "report": error_report,
                "status": "failed",
                "error": str(e)
            }
        
    except Exception as e:
        print(f"❌ ERRO ao iniciar análise: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Obtém o status de um job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job = jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "message": job.get("message", ""),
        "progress": job.get("progress", 0),
        "repo_name": job.get("repo_name"),
        "analysis_type": job.get("analysis_type"),
        "report": job.get("report", ""),
        "error_details": job.get("error_details"),
        "result": job.get("result"),
        "last_updated": job.get("last_updated")
    }

@app.post("/update-job-status")
async def update_job_status(request: UpdateJobRequest):
    """Atualiza o status de um job (aprovar/rejeitar)"""
    job_id = request.job_id
    action = request.action
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job = jobs[job_id]
    
    if action == "approve":
        # Job já está completo, apenas confirmar
        job["status"] = "approved"
        job["message"] = "Análise aprovada pelo usuário"
        job["last_updated"] = time.time()
        
        return {
            "job_id": job_id,
            "status": "approved",
            "message": "Análise aprovada"
        }
        
    elif action == "reject":
        job["status"] = "rejected"
        job["message"] = "Análise rejeitada pelo usuário"
        job["last_updated"] = time.time()
        
        return {
            "job_id": job_id,
            "status": "rejected",
            "message": "Análise rejeitada"
        }
    
    else:
        raise HTTPException(status_code=400, detail="Ação inválida. Use 'approve' ou 'reject'")

@app.get("/jobs")
async def list_jobs():
    """Lista todos os jobs"""
    return {"jobs": list(jobs.values())}

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Remove um job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    del jobs[job_id]
    return {"message": "Job removido com sucesso"}

@app.post("/analyze-direct")
async def analyze_direct(request: StartAnalysisRequest):
    """Análise direta - retorna resultado imediatamente"""
    try:
        print(f"🔥 Análise direta: {request.repo_name}")
        
        if not agente_revisor:
            raise HTTPException(status_code=500, detail="Agente revisor não disponível")
        
        mapped_analysis_type = ANALYSIS_TYPE_MAPPING.get(request.analysis_type, "design")
        
        resultado = agente_revisor.main(
            tipo_analise=mapped_analysis_type,
            repositorio=request.repo_name,
            instrucoes_extras=request.instrucoes_extras or ""
        )
        
        return {
            "status": "completed",
            "repo_name": request.repo_name,
            "analysis_type": request.analysis_type,
            "result": resultado,
            "report": resultado.get("resultado", "Análise concluída")
        }
        
    except Exception as e:
        print(f"❌ Erro na análise direta: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

# Endpoint legado para compatibilidade
@app.post("/executar_analise")
async def executar_analise_legacy(data: dict):
    """Endpoint legado para compatibilidade com Flask"""
    try:
        tipo_analise = data.get('tipo_analise')
        repositorio = data.get('repositorio')
        codigo = data.get('codigo')
        instrucoes_extras = data.get('instrucoes_extras', '')
        
        if not tipo_analise:
            raise HTTPException(status_code=400, detail="tipo_analise é obrigatório")
        if not repositorio and not codigo:
            raise HTTPException(status_code=400, detail="repositorio ou codigo é obrigatório")
        
        if not agente_revisor:
            raise HTTPException(status_code=500, detail="Agente revisor não disponível")
        
        resultado = agente_revisor.main(
            tipo_analise=tipo_analise,
            repositorio=repositorio,
            codigo=codigo,
            instrucoes_extras=instrucoes_extras
        )
        
        return resultado
        
    except Exception as e:
        print(f"❌ Erro na análise legacy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando Backend Agentes Peers (Versão Limpa)...")
    print("📡 Frontend URL: http://localhost:3000")
    print("🔧 Backend URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "mcp_server_fastapi_clean:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )