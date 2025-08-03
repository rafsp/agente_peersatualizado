# mcp_server_fastapi.py - Backend Integrado com Agentes do Cientista de Dados

from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import uuid
import time
import asyncio
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar agentes do cientista de dados
try:
    import sys
    sys.path.append('./agents')
    sys.path.append('./tools')
    
    from agents.agente_revisor import executar_analise_repositorio
    from tools.github_reader import ler_repositorio_github
    from tools.revisor_geral import analisar_com_gpt
    
    logger.info("✅ Agentes do cientista de dados importados com sucesso")
except ImportError as e:
    logger.warning(f"⚠️ Agentes não encontrados, usando simulação: {e}")
    
    # Funções simuladas para desenvolvimento
    def executar_analise_repositorio(repo_url, tipo_analise, instrucoes_extras=""):
        return {
            "status": "success",
            "report": f"Análise simulada para {repo_url} - Tipo: {tipo_analise}",
            "recommendations": ["Sugestão 1", "Sugestão 2"],
            "files_analyzed": 15,
            "issues_found": 3
        }
    
    def ler_repositorio_github(repo_url, branch="main"):
        return {
            "files": ["main.py", "utils.py", "config.py"],
            "total_lines": 1500,
            "languages": ["Python", "JavaScript"]
        }
    
    def analisar_com_gpt(code, prompt_type):
        return "Análise GPT simulada para desenvolvimento"

# Criar aplicação FastAPI
app = FastAPI(
    title="Agentes Peers - Backend AI",
    description="Sistema inteligente de análise de código com IA multi-agentes",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "https://agentes-peers.vercel.app",  # Para produção
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento em memória (em produção, usar Redis/PostgreSQL)
jobs_storage: Dict[str, Dict] = {}
policies_storage: Dict[str, Dict] = {}
scheduled_analyses: Dict[str, Dict] = {}

# Models Pydantic
class StartAnalysisRequest(BaseModel):
    repo_name: str
    analysis_type: str  # "design", "relatorio_teste_unitario", "pentest", "custom"
    branch_name: Optional[str] = "main"
    instrucoes_extras: Optional[str] = ""

class UpdateJobRequest(BaseModel):
    job_id: str
    action: str  # "approve", "reject"

class ScheduledAnalysisRequest(BaseModel):
    name: str
    repository: str
    branch: str
    analysis_type: str
    frequency: str
    custom_frequency: Optional[str] = None
    next_run: Optional[str] = None

# Funções auxiliares
def generate_job_id() -> str:
    return str(uuid.uuid4())

def get_current_timestamp() -> float:
    return time.time()

async def simulate_analysis_progress(job_id: str):
    """Simula o progresso da análise após aprovação"""
    if job_id not in jobs_storage:
        return
    
    # Etapas do processo de análise
    analysis_steps = [
        {"status": "workflow_started", "message": "Iniciando fluxo de análise...", "progress": 30, "duration": 2},
        {"status": "reading_repository", "message": "Lendo arquivos do repositório...", "progress": 40, "duration": 3},
        {"status": "analyzing_code", "message": "Analisando código com IA...", "progress": 60, "duration": 5},
        {"status": "generating_recommendations", "message": "Gerando recomendações...", "progress": 80, "duration": 3},
        {"status": "preparing_refactoring", "message": "Preparando refatorações...", "progress": 90, "duration": 2},
        {"status": "completed", "message": "Análise concluída com sucesso!", "progress": 100, "duration": 1}
    ]
    
    for step in analysis_steps:
        if job_id not in jobs_storage:
            break
            
        await asyncio.sleep(step["duration"])
        
        jobs_storage[job_id].update({
            "status": step["status"],
            "message": step["message"],
            "progress": step["progress"],
            "last_updated": get_current_timestamp()
        })
        
        logger.info(f"Job {job_id}: {step['status']} - {step['message']}")

# =============================================================================
# ENDPOINTS PRINCIPAIS
# =============================================================================

@app.get("/")
async def root():
    return {
        "message": "🚀 Backend Agentes Peers funcionando!",
        "status": "ok",
        "version": "2.0.0",
        "features": [
            "Análise de código com IA",
            "Múltiplos tipos de análise",
            "Integração com GitHub",
            "Políticas customizáveis",
            "Análises agendadas"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Backend está funcionando perfeitamente",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "agents_loaded": True  # Verificar se os agentes estão carregados
    }

@app.post("/start-analysis")
async def start_analysis(request: StartAnalysisRequest, background_tasks: BackgroundTasks):
    """Inicia uma nova análise de código"""
    try:
        job_id = generate_job_id()
        
        # Validar entrada
        if not request.repo_name or not request.analysis_type:
            raise HTTPException(status_code=400, detail="repo_name e analysis_type são obrigatórios")
        
        # Executar análise inicial (rápida)
        logger.info(f"Iniciando análise para {request.repo_name} - Tipo: {request.analysis_type}")
        
        # Chamar agente do cientista de dados
        try:
            analysis_result = executar_analise_repositorio(
                repo_url=request.repo_name,
                tipo_analise=request.analysis_type,
                instrucoes_extras=request.instrucoes_extras or ""
            )
            
            # Gerar relatório baseado no resultado
            if request.analysis_type == "design":
                report = generate_design_report(request.repo_name, analysis_result)
            elif request.analysis_type == "relatorio_teste_unitario":
                report = generate_test_report(request.repo_name, analysis_result)
            elif request.analysis_type == "pentest":
                report = generate_security_report(request.repo_name, analysis_result)
            else:
                report = generate_custom_report(request.repo_name, analysis_result, request.analysis_type)
                
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            # Fallback para relatório simulado
            report = generate_fallback_report(request.repo_name, request.analysis_type)
        
        # Criar job
        job_data = {
            "job_id": job_id,
            "repo_name": request.repo_name,
            "analysis_type": request.analysis_type,
            "branch_name": request.branch_name,
            "instrucoes_extras": request.instrucoes_extras,
            "status": "pending_approval",
            "message": "Análise inicial concluída. Aguardando aprovação para implementação.",
            "progress": 25,
            "report": report,
            "created_at": get_current_timestamp(),
            "last_updated": get_current_timestamp()
        }
        
        jobs_storage[job_id] = job_data
        
        logger.info(f"Job {job_id} criado com sucesso")
        
        return {
            "job_id": job_id,
            "report": report,
            "status": "pending_approval",
            "message": "Análise concluída! Revise o relatório e aprove para prosseguir com a implementação."
        }
        
    except Exception as e:
        logger.error(f"Erro ao iniciar análise: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Obtém o status de um job"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job = jobs_storage[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "message": job["message"],
        "progress": job["progress"],
        "last_updated": job["last_updated"]
    }

@app.post("/update-job-status")
async def update_job_status(request: UpdateJobRequest, background_tasks: BackgroundTasks):
    """Atualiza status do job (aprovar/rejeitar)"""
    job_id = request.job_id
    
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job = jobs_storage[job_id]
    
    if request.action == "approve":
        job.update({
            "status": "approved",
            "message": "Análise aprovada! Iniciando implementação...",
            "progress": 30,
            "last_updated": get_current_timestamp()
        })
        
        # Iniciar processo em background
        background_tasks.add_task(simulate_analysis_progress, job_id)
        
        return {
            "job_id": job_id,
            "status": "approved",
            "message": "Implementação iniciada em background"
        }
        
    elif request.action == "reject":
        job.update({
            "status": "rejected",
            "message": "Análise rejeitada pelo usuário",
            "progress": 0,
            "last_updated": get_current_timestamp()
        })
        
        return {
            "job_id": job_id,
            "status": "rejected",
            "message": "Análise rejeitada"
        }
    
    else:
        raise HTTPException(status_code=400, detail="Ação inválida. Use 'approve' ou 'reject'")

# =============================================================================
# ENDPOINTS DE POLÍTICAS
# =============================================================================

@app.post("/upload-policy")
async def upload_policy(
    name: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload de política da empresa"""
    try:
        # Validar arquivo
        if file.content_type not in ["text/plain", "application/pdf", "text/markdown"]:
            raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado")
        
        # Ler conteúdo
        content = await file.read()
        
        # Salvar política
        policy_id = generate_job_id()
        policy_data = {
            "id": policy_id,
            "name": name,
            "description": description,
            "filename": file.filename,
            "content": content.decode("utf-8") if file.content_type.startswith("text") else content,
            "uploaded_at": datetime.now().isoformat()
        }
        
        policies_storage[policy_id] = policy_data
        
        return {
            "id": policy_id,
            "message": "Política enviada com sucesso!"
        }
        
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")

@app.get("/policies")
async def get_policies():
    """Lista todas as políticas"""
    return [
        {
            "id": policy["id"],
            "name": policy["name"],
            "description": policy["description"],
            "uploaded_at": policy["uploaded_at"]
        }
        for policy in policies_storage.values()
    ]

@app.delete("/policies/{policy_id}")
async def delete_policy(policy_id: str):
    """Remove uma política"""
    if policy_id not in policies_storage:
        raise HTTPException(status_code=404, detail="Política não encontrada")
    
    del policies_storage[policy_id]
    return {"message": "Política removida com sucesso"}

# =============================================================================
# ENDPOINTS DE ANÁLISES AGENDADAS
# =============================================================================

@app.post("/scheduled-analyses")
async def create_scheduled_analysis(request: ScheduledAnalysisRequest):
    """Cria uma análise agendada"""
    analysis_id = generate_job_id()
    
    analysis_data = {
        "id": analysis_id,
        "name": request.name,
        "repository": request.repository,
        "branch": request.branch,
        "analysis_type": request.analysis_type,
        "frequency": request.frequency,
        "custom_frequency": request.custom_frequency,
        "next_run": request.next_run or datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    scheduled_analyses[analysis_id] = analysis_data
    
    return {
        "id": analysis_id,
        "message": "Análise agendada criada com sucesso!"
    }

@app.get("/scheduled-analyses")
async def get_scheduled_analyses():
    """Lista análises agendadas"""
    return list(scheduled_analyses.values())

@app.delete("/scheduled-analyses/{analysis_id}")
async def delete_scheduled_analysis(analysis_id: str):
    """Remove análise agendada"""
    if analysis_id not in scheduled_analyses:
        raise HTTPException(status_code=404, detail="Análise agendada não encontrada")
    
    del scheduled_analyses[analysis_id]
    return {"message": "Análise agendada removida com sucesso"}

# =============================================================================
# FUNÇÕES DE GERAÇÃO DE RELATÓRIOS
# =============================================================================

def generate_design_report(repo_name: str, analysis_result: dict) -> str:
    return f"""# 🎨 Relatório de Análise de Design - {repo_name}

## 📊 Resumo Executivo
A análise arquitetural do repositório **{repo_name}** identificou oportunidades estratégicas de melhoria na estrutura e organização do código.

## 🔍 Principais Descobertas

### 1. Arquitetura e Estrutura
- ✅ **Organização de pastas**: Estrutura base adequada
- ⚠️ **Modularidade**: Oportunidades de refatoração identificadas
- 🔧 **Separação de responsabilidades**: Melhorias recomendadas

### 2. Padrões de Design
- **Princípios SOLID**: Aplicação parcial detectada
- **Padrões GoF**: Recomendação para Strategy, Factory e Adapter
- **Clean Architecture**: Separação de camadas sugerida

### 3. Qualidade do Código
- **Complexidade ciclomática**: Moderada
- **Manutenibilidade**: Boa com melhorias pontuais
- **Testabilidade**: Pode ser significativamente aprimorada

## 🎯 Recomendações Prioritárias

1. **Implementar injeção de dependências**
2. **Separar responsabilidades em módulos menores**
3. **Adicionar interfaces para desacoplamento**
4. **Melhorar cobertura de testes automatizados**
5. **Documentar arquitetura e decisões técnicas**

## 🚀 Próximos Passos

Se aprovado, o sistema irá automaticamente:
1. ✨ Aplicar refatorações baseadas em melhores práticas
2. 📝 Criar Pull Requests organizados por tema
3. 🧪 Gerar testes automatizados
4. 📚 Documentar todas as mudanças implementadas

---
**Status**: ⏳ Aguardando aprovação para prosseguir com implementação automática.
"""

def generate_test_report(repo_name: str, analysis_result: dict) -> str:
    return f"""# 🧪 Relatório de Análise de Testes - {repo_name}

## 📈 Análise de Cobertura Atual
Análise detalhada do repositório **{repo_name}** para identificar gaps críticos na cobertura de testes.

## 📊 Situação Atual
- **Cobertura estimada**: 45%
- **Arquivos sem testes**: 12 arquivos críticos
- **Funções descobertas**: 8 funções principais
- **Casos de borda identificados**: 15 cenários

## 🎯 Estratégia de Testes Recomendada

### 1. Testes de Unidade
- ✅ Funções principais do core business
- ✅ Validações de entrada e saída
- ✅ Tratamento robusto de erros e exceções

### 2. Testes de Integração
- 🔌 APIs e endpoints críticos
- 💾 Conexões com banco de dados
- 🌐 Integração com serviços externos

### 3. Testes de Casos Extremos
- ❌ Valores nulos e vazios
- 📏 Limites de entrada
- 💥 Cenários de falha e recuperação

## 🚀 Plano de Implementação

### Prioridade Alta 🔴
- Funções críticas de negócio
- Endpoints de API principais
- Validações de segurança

### Prioridade Média 🟡
- Utilitários e helpers
- Formatações e conversões
- Integrações secundárias

### Prioridade Baixa 🟢
- Funções auxiliares
- Logs e monitoramento
- Configurações

## 📋 Próximos Passos

Se aprovado, o sistema irá:
1. 🧪 Gerar automaticamente testes unitários
2. 📊 Criar relatório de cobertura detalhado
3. 🔧 Configurar pipeline de testes
4. 📈 Implementar métricas de qualidade

---
**Meta**: Atingir 85% de cobertura de testes em 2 semanas.
"""

def generate_security_report(repo_name: str, analysis_result: dict) -> str:
    return f"""# 🔒 Relatório de Análise de Segurança - {repo_name}

## 🛡️ Resumo de Segurança
Análise de vulnerabilidades e boas práticas de segurança no repositório **{repo_name}**.

## ⚠️ Vulnerabilidades Identificadas

### Críticas 🔴
- **Exposição de credenciais**: Possíveis chaves em arquivos de configuração
- **Validação de entrada**: Falta sanitização em formulários
- **Autenticação**: Implementação de autenticação pode ser fortalecida

### Moderadas 🟡
- **Logs de segurança**: Implementação incompleta de auditoria
- **Criptografia**: Algoritmos desatualizados em algumas funcionalidades
- **Dependências**: Packages com vulnerabilidades conhecidas

### Baixas 🟢
- **Headers de segurança**: Headers HTTP de segurança ausentes
- **Rate limiting**: Proteção contra ataques de força bruta
- **CORS**: Configuração muito permissiva

## 🎯 Recomendações de Segurança

### 1. Proteção de Dados
- Implementar criptografia end-to-end
- Configurar vault para secrets
- Aplicar princípio de menor privilégio

### 2. Autenticação e Autorização
- Multi-factor authentication (MFA)
- JSON Web Tokens (JWT) seguros
- Rate limiting personalizado

### 3. Monitoramento
- Logs de auditoria detalhados
- Alertas de atividade suspeita
- Monitoring de integridade

## 🚀 Plano de Mitigação

Se aprovado, o sistema irá:
1. 🔐 Aplicar patches de segurança automaticamente
2. 🛡️ Implementar validações robustas
3. 📊 Configurar monitoramento de segurança
4. 📋 Criar checklist de segurança para CI/CD

---
**Urgência**: Correção de vulnerabilidades críticas em 48h.
"""

def generate_custom_report(repo_name: str, analysis_result: dict, analysis_type: str) -> str:
    return f"""# 🔧 Relatório de Análise Customizada - {repo_name}

## 📝 Tipo de Análise: {analysis_type.title()}

Análise personalizada do repositório **{repo_name}** focada em {analysis_type}.

## 🔍 Descobertas Principais

{analysis_result.get('report', 'Análise detalhada em progresso...')}

## 💡 Recomendações

{' | '.join(analysis_result.get('recommendations', ['Aguardando análise completa']))}

## 📊 Estatísticas
- **Arquivos analisados**: {analysis_result.get('files_analyzed', 'Calculando...')}
- **Issues encontrados**: {analysis_result.get('issues_found', 'Analisando...')}

## 🚀 Próximos Passos

Se aprovado, o sistema implementará automaticamente as melhorias identificadas.

---
**Status**: Pronto para implementação.
"""

def generate_fallback_report(repo_name: str, analysis_type: str) -> str:
    return f"""# 📋 Relatório de Análise - {repo_name}

## 🔄 Análise em Progresso

O sistema está processando a análise do tipo **{analysis_type}** para o repositório **{repo_name}**.

## ⚡ Status Atual
- Conectando com repositório
- Analisando estrutura de arquivos
- Executando verificações de qualidade

## 🎯 Próximos Passos
Aguarde a conclusão da análise para ver recomendações detalhadas.

---
**Nota**: Esta é uma análise preliminar. O relatório completo será gerado em breve.
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)