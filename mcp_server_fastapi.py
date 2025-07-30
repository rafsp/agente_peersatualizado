# mcp_server_fastapi.py - Com simulação de fluxo completo

from fastapi import FastAPI, BackgroundTasks
from typing import Optional
import json
import uuid
import time
import asyncio
import threading

# Criar aplicação FastAPI
app = FastAPI(
    title="Agentes Peers - Backend",
    description="Sistema de análise de código com IA",
    version="1.0.0"
)

# Armazenar jobs em memória (temporário)
jobs = {}

def simulate_job_progress(job_id: str):
    """Simula o progresso automático de um job após aprovação"""
    if job_id not in jobs:
        return
    
    # Lista de etapas do processo
    steps = [
        {"status": "refactoring_code", "message": "Aplicando refatorações no código...", "duration": 3},
        {"status": "grouping_commits", "message": "Agrupando commits por tema...", "duration": 2},
        {"status": "writing_unit_tests", "message": "Escrevendo testes unitários...", "duration": 4},
        {"status": "grouping_tests", "message": "Organizando testes em grupos...", "duration": 2},
        {"status": "populating_data", "message": "Preparando dados para commit...", "duration": 2},
        {"status": "committing_to_github", "message": "Enviando mudanças para GitHub...", "duration": 3},
        {"status": "completed", "message": "Análise concluída com sucesso!", "duration": 0}
    ]
    
    progress_per_step = 75 / len(steps)  # 75% restante dividido pelas etapas
    current_progress = 25  # Começa em 25% (após aprovação)
    
    for i, step in enumerate(steps):
        time.sleep(step["duration"])  # Simular tempo de processamento
        
        if job_id not in jobs:  # Job pode ter sido removido
            break
            
        current_progress += progress_per_step
        if step["status"] == "completed":
            current_progress = 100
            
        jobs[job_id].update({
            "status": step["status"],
            "message": step["message"],
            "progress": int(current_progress),
            "last_updated": time.time()
        })
        
        print(f"[{job_id}] {step['status']}: {step['message']} ({int(current_progress)}%)")

@app.get("/")
async def root():
    return {
        "message": "Backend Agentes Peers funcionando!",
        "status": "ok",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Backend está funcionando",
        "environment": "local"
    }

@app.post("/start-analysis")
async def start_analysis_simple(data: dict):
    """Versão otimizada com resposta rápida"""
    try:
        # Extrair dados do request
        repo_name = data.get("repo_name")
        analysis_type = data.get("analysis_type")
        branch_name = data.get("branch_name")
        instrucoes_extras = data.get("instrucoes_extras")
        
        if not repo_name or not analysis_type:
            return {"error": "repo_name e analysis_type são obrigatórios"}
        
        # Criar job simples
        job_id = str(uuid.uuid4())
        
        # Gerar um relatório de exemplo mais realista baseado no tipo
        if analysis_type == "design":
            report = f"""# Relatório de Análise de Design - {repo_name}

## Resumo Executivo
A análise do repositório {repo_name} identificou oportunidades de melhoria na arquitetura e estrutura do código.

## Principais Descobertas

### 1. Estrutura de Arquivos
- ✅ Organização de pastas adequada
- ⚠️ Alguns arquivos poderiam ser reorganizados
- 🔧 Sugestão de refatoração para melhor modularidade

### 2. Padrões de Design
- **Princípios SOLID**: Parcialmente aplicados
- **Padrões GoF**: Opportunity para implementar Strategy e Factory
- **Clean Architecture**: Recomendada separação de camadas

### 3. Qualidade do Código
- **Complexidade**: Moderada
- **Manutenibilidade**: Boa com melhorias pontuais
- **Testabilidade**: Pode ser aprimorada

## Recomendações
1. Implementar injeção de dependências
2. Separar responsabilidades em módulos menores
3. Adicionar interfaces para desacoplamento
4. Melhorar cobertura de testes

## Próximos Passos
Se aprovado, o sistema irá:
1. Aplicar refatorações automáticas
2. Criar PRs organizados por tema
3. Gerar testes automatizados
4. Documentar mudanças

**Status**: Aguardando aprovação para prosseguir com implementação.
"""
        else:  # relatorio_teste_unitario
            report = f"""# Relatório de Testes Unitários - {repo_name}

## Análise de Cobertura Atual
Análise do repositório {repo_name} para identificar gaps de cobertura de testes.

## Situação Atual
- **Cobertura estimada**: 45%
- **Arquivos sem testes**: 12
- **Funções críticas descobertas**: 8
- **Casos de borda identificados**: 15

## Testes Recomendados

### 1. Testes de Unidade
- Funções principais do core business
- Validações de entrada e saída
- Tratamento de erros e exceções

### 2. Testes de Integração
- APIs e endpoints
- Conexões com banco de dados
- Serviços externos

### 3. Testes de Borda
- Valores nulos e vazios
- Limites de entrada
- Cenários de falha

## Estratégia de Implementação
1. **Prioridade Alta**: Funções críticas de negócio
2. **Prioridade Média**: Utilitários e helpers
3. **Prioridade Baixa**: Funções de configuração

## Estimativa
- **Testes a criar**: ~25 arquivos
- **Cobertura esperada**: 85%+
- **Tempo estimado**: 2-3 dias de implementação

**Status**: Aguardando aprovação para iniciar criação dos testes.
"""
        
        jobs[job_id] = {
            "status": "pending_approval",
            "repo_name": repo_name,
            "analysis_type": analysis_type,
            "branch_name": branch_name,
            "instrucoes_extras": instrucoes_extras,
            "created_at": time.time(),
            "report": report,
            "message": "Relatório inicial gerado. Aguardando aprovação...",
            "progress": 10
        }
        
        # Retornar resposta rápida
        return {
            "job_id": job_id,
            "report": report,
            "status": "success"
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Consultar status de um job"""
    job = jobs.get(job_id)
    if not job:
        return {"error": "Job não encontrado"}
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "repo_name": job["repo_name"],
        "analysis_type": job["analysis_type"],
        "message": job.get("message", "Processando..."),
        "progress": job.get("progress", 0)
    }

@app.get("/jobs")
async def list_jobs():
    """Listar todos os jobs"""
    return {
        "total": len(jobs),
        "jobs": jobs
    }

@app.post("/update-job-status")
async def update_job_status(data: dict, background_tasks: BackgroundTasks):
    """Atualizar status de um job"""
    job_id = data.get("job_id")
    action = data.get("action")
    
    if not job_id or not action:
        return {"error": "job_id e action são obrigatórios"}
    
    job = jobs.get(job_id)
    if not job:
        return {"error": "Job não encontrado"}
    
    # Atualizar status baseado na ação
    if action == "approve":
        job["status"] = "approved"
        job["message"] = "Análise aprovada! Iniciando processamento..."
        job["progress"] = 25
        message = "Job aprovado com sucesso!"
        
        # Iniciar simulação de progresso em background
        background_tasks.add_task(simulate_job_progress, job_id)
        
    elif action == "reject":
        job["status"] = "rejected"
        job["message"] = "Análise rejeitada pelo usuário"
        job["progress"] = 0
        message = "Job rejeitado pelo usuário"
    else:
        return {"error": "Ação inválida. Use 'approve' ou 'reject'"}
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "message": message
    }

# Endpoint para testar conectividade
@app.get("/test")
async def test_connection():
    return {
        "message": "Conexão funcionando!",
        "timestamp": time.time(),
        "total_jobs": len(jobs),
        "backend_status": "ready"
    }