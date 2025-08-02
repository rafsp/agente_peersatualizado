# mcp_server_fastapi.py - VERSÃO INTEGRADA COMPLETA
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
    print("📋 Usando modo simulação até os agentes serem configurados")
    AGENTES_DISPONIVEIS = False

# Criar aplicação FastAPI
app = FastAPI(
    title="Agentes Peers - Backend",
    description="Sistema de análise de código com IA",
    version="2.0.0"
)

# Armazenar jobs em memória (temporário)
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
            resultado = agente_revisor.executar_analise(
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
            # Simulação melhorada
            simulate_job_progress(job_id)
            
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
    agente_status = "✅ Disponíveis" if AGENTES_DISPONIVEIS else "⚠️ Simulação"
    return {
        "message": "Backend Agentes Peers funcionando!",
        "status": "ok",
        "version": "2.0.0",
        "agentes_reais": agente_status,
        "modo": "PRODUÇÃO" if AGENTES_DISPONIVEIS else "SIMULAÇÃO"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Backend está funcionando",
        "agentes_reais_disponiveis": AGENTES_DISPONIVEIS,
        "environment": os.getenv("ENVIRONMENT", "local")
    }

@app.post("/start-analysis")
async def start_analysis_integrado(data: dict, background_tasks: BackgroundTasks):
    """Versão integrada com agentes reais"""
    try:
        # Extrair dados do request
        repo_name = data.get("repo_name")
        analysis_type = data.get("analysis_type")
        branch_name = data.get("branch_name")
        instrucoes_extras = data.get("instrucoes_extras")
        
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
        mapped_type = type_mapping.get(analysis_type_normalized, "design")
        
        # Criar job simples
        job_id = str(uuid.uuid4())
        
        # Gerar um relatório inicial baseado no modo
        if AGENTES_DISPONIVEIS:
            report = f"""# 🚀 Análise Real Iniciada - {repo_name}

## ✅ Modo PRODUÇÃO Ativo
Os agentes de IA reais irão analisar seu código.

## 📊 Configuração
- **Tipo Solicitado**: {analysis_type}
- **Tipo Mapeado**: {mapped_type}
- **Repositório**: {repo_name}
- **Branch**: {branch_name or 'padrão'}
- **Job ID**: {job_id}

## 🎯 Próximos Passos
1. **Aprovação**: Revise e aprove a análise
2. **Execução**: Agente real analisará o código
3. **Resultado**: Relatório detalhado será gerado

**Status**: Aguardando aprovação para iniciar análise real...
"""
        else:
            # Relatório de simulação melhorado
            if analysis_type_normalized == "design" or "design" in analysis_type_normalized:
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
- **Padrões GoF**: Oportunidade para implementar Strategy e Factory
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

**Status**: ⚠️ Modo simulação - Configure agentes reais para análises completas.
"""
            else:  # testes unitários ou outros
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

**Status**: ⚠️ Modo simulação - Configure agentes reais para análises completas.
"""
        
        jobs[job_id] = {
            "status": "pending_approval",
            "repo_name": repo_name,
            "analysis_type": mapped_type,
            "original_type": analysis_type,
            "branch_name": branch_name,
            "instrucoes_extras": instrucoes_extras,
            "created_at": time.time(),
            "report": report,
            "message": f"Relatório inicial gerado. Aguardando aprovação...",
            "progress": 10,
            "real_mode": AGENTES_DISPONIVEIS
        }
        
        modo_texto = "REAL" if AGENTES_DISPONIVEIS else "SIMULAÇÃO"
        print(f"🎯 Nova análise: {job_id} - {repo_name} ({analysis_type} -> {mapped_type}) - Modo: {modo_texto}")
        
        # Retornar resposta rápida
        return {
            "job_id": job_id,
            "report": report,
            "status": "success",
            "mode": modo_texto
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        "real_mode": job.get("real_mode", False)
    }

@app.get("/jobs")
async def list_jobs():
    """Listar todos os jobs"""
    return {
        "total": len(jobs),
        "agentes_reais_disponiveis": AGENTES_DISPONIVEIS,
        "jobs": jobs
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
    
    # Atualizar status baseado na ação
    if action == "approve":
        job["status"] = "approved"
        job["message"] = "Análise aprovada! Iniciando processamento..."
        job["progress"] = 25
        message = "Job aprovado com sucesso!"
        
        # Iniciar execução real ou simulação em background
        if AGENTES_DISPONIVEIS:
            background_tasks.add_task(
                executar_agente_real,
                job_id,
                job["repo_name"], 
                job["analysis_type"],
                job["instrucoes_extras"]
            )
        else:
            background_tasks.add_task(simulate_job_progress, job_id)
        
    elif action == "reject":
        job["status"] = "rejected"
        job["message"] = "Análise rejeitada pelo usuário"
        job["progress"] = 0
        message = "Job rejeitado pelo usuário"
    else:
        raise HTTPException(status_code=400, detail="Ação inválida. Use 'approve' ou 'reject'")
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "message": message
    }

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
        ]
    }

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
        
        resultado = agente_revisor.executar_analise(
            tipo_analise=tipo_analise,
            repositorio=repositorio,
            instrucoes_extras=instrucoes_extras
        )
        
        return {
            "success": True,
            "resultado": resultado,
            "modo": "TESTE_REAL"
        }
        
    except Exception as e:
        return {
            "error": f"Erro ao testar agente: {str(e)}",
            "modo": "ERRO"
        }