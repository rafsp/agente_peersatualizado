# mcp_server_fastapi.py - VERSÃO CORRIGIDA
import json
import uuid
import time
import threading
from fastapi import FastAPI, BackgroundTasks, HTTPException, Path
from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any

# Imports dos agentes (mantenha os seus imports originais)
try:
    from agents import agente_revisor
    from tools import preenchimento, commit_multiplas_branchs
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Agentes não disponíveis: {e}")
    AGENTS_AVAILABLE = False

# --- Modelos de Dados com Pydantic ---
class StartAnalysisPayload(BaseModel):
    repo_name: str
    analysis_type: Literal["design", "relatorio_teste_unitario"]
    branch_name: Optional[str] = None
    instrucoes_extras: Optional[str] = None

class UpdateJobPayload(BaseModel):
    job_id: str
    action: Literal["approve", "reject"]

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    message: Optional[str] = None
    progress: Optional[int] = None
    error_details: Optional[str] = None
    last_updated: Optional[float] = None
    report: Optional[str] = None  # ✅ Adicionar campo report

class StartAnalysisResponse(BaseModel):
    job_id: str
    report: str

# --- Configuração do FastAPI ---
app = FastAPI(
    title="Agentes Peers - Backend",
    description="Sistema de análise de código com IA multi-agentes",
    version="1.0.0"
)

# Armazenamento em memória para jobs
jobs: Dict[str, Dict[str, Any]] = {}

# WORKFLOW_REGISTRY corrigido e completo
WORKFLOW_REGISTRY = {
    "design": {
        "description": "Analisa o design, refatora o código e agrupa os commits",
        "steps": [
            {
                "status": "refactoring_code",
                "message": "Refatorando código...",
                "agent_function": "agente_revisor.main" if AGENTS_AVAILABLE else None,
                "params": {"tipo_analise": "refatoracao"},
                "duration": 5
            },
            {
                "status": "grouping_commits", 
                "message": "Agrupando commits por tema...",
                "agent_function": "agente_revisor.main" if AGENTS_AVAILABLE else None,
                "params": {"tipo_analise": "agrupamento_design"},
                "duration": 3
            }
        ]
    },
    "relatorio_teste_unitario": {
        "description": "Cria testes unitários com base no relatório e os agrupa",
        "steps": [
            {
                "status": "writing_unit_tests",
                "message": "Escrevendo testes unitários...", 
                "agent_function": "agente_revisor.main" if AGENTS_AVAILABLE else None,
                "params": {"tipo_analise": "escrever_testes"},
                "duration": 6
            },
            {
                "status": "grouping_tests",
                "message": "Agrupando testes em grupos...",
                "agent_function": "agente_revisor.main" if AGENTS_AVAILABLE else None, 
                "params": {"tipo_analise": "agrupamento_testes"},
                "duration": 2
            }
        ]
    }
}

def simulate_job_progress(job_id: str):
    """Simula o progresso automático de um job após aprovação"""
    try:
        if job_id not in jobs:
            print(f"[{job_id}] Job não encontrado para simulação")
            return
        
        job_info = jobs[job_id]
        original_analysis_type = job_info['data']['original_analysis_type']
        workflow = WORKFLOW_REGISTRY.get(original_analysis_type)
        
        if not workflow:
            raise ValueError(f"Workflow não definido para: {original_analysis_type}")
        
        print(f"[{job_id}] 🚀 Iniciando workflow para {original_analysis_type}")
        
        # Simular etapas do workflow
        total_steps = len(workflow['steps']) + 2  # +2 para populating_data e committing_to_github
        progress_per_step = 75 / total_steps  # 75% restante dividido pelas etapas
        current_progress = 25  # Começa em 25% (após aprovação)
        
        # Executar steps definidos no workflow
        for i, step in enumerate(workflow['steps']):
            if job_id not in jobs:  # Job pode ter sido removido
                return
                
            # Atualizar status do job
            job_info['status'] = step['status']
            job_info['message'] = step['message']
            current_progress += progress_per_step
            job_info['progress'] = int(current_progress)
            job_info['last_updated'] = time.time()
            
            print(f"[{job_id}] {step['status']}: {step['message']} ({int(current_progress)}%)")
            
            # Simular tempo de processamento
            time.sleep(step.get('duration', 2))
        
        # Etapas finais
        final_steps = [
            {"status": "populating_data", "message": "Preparando dados para commit...", "duration": 2},
            {"status": "committing_to_github", "message": "Enviando mudanças para GitHub...", "duration": 3}
        ]
        
        for step in final_steps:
            if job_id not in jobs:
                return
                
            job_info['status'] = step['status']
            job_info['message'] = step['message']
            current_progress += progress_per_step
            job_info['progress'] = int(current_progress)
            job_info['last_updated'] = time.time()
            
            print(f"[{job_id}] {step['status']}: {step['message']} ({int(current_progress)}%)")
            time.sleep(step['duration'])
        
        # Finalização
        if job_id in jobs:
            job_info['status'] = 'completed'
            job_info['message'] = 'Análise concluída com sucesso!'
            job_info['progress'] = 100
            job_info['last_updated'] = time.time()
            print(f"[{job_id}] ✅ Processo concluído com sucesso!")
            
    except Exception as e:
        print(f"[{job_id}] ❌ ERRO: {e}")
        if job_id in jobs:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['error_details'] = str(e)
            jobs[job_id]['message'] = f'Erro durante processamento: {str(e)}'
            jobs[job_id]['last_updated'] = time.time()

def run_workflow_task_REAL(job_id: str):
    """Executa o workflow real com os agentes (quando disponíveis)"""
    if not AGENTS_AVAILABLE:
        print(f"[{job_id}] Agentes não disponíveis, usando simulação")
        simulate_job_progress(job_id)
        return
    
    try:
        print(f"[{job_id}] 🚀 Iniciando workflow REAL...")
        job_info = jobs[job_id]
        original_analysis_type = job_info['data']['original_analysis_type']
        workflow = WORKFLOW_REGISTRY.get(original_analysis_type)
        
        if not workflow:
            raise ValueError(f"Nenhum workflow definido para: {original_analysis_type}")
        
        # Extrair dados do job
        print(f"[{job_id}] 📊 Dados extraídos:")
        print(f"[{job_id}]   - Repositório: {job_info['data']['repo_name']}")
        print(f"[{job_id}]   - Branch: {job_info['data']['branch_name']}")
        print(f"[{job_id}]   - Tipo: {original_analysis_type}")
        print(f"[{job_id}]   - Tem relatório: {bool(job_info['data'].get('analysis_report'))}")
        print(f"[{job_id}]   - Tem instruções: {bool(job_info['data'].get('instrucoes_extras'))}")
        
        resultado_refatoracao, resultado_agrupamento = None, None
        previous_step_result = None
        
        # Executar cada step do workflow
        for i, step in enumerate(workflow['steps']):
            if job_id not in jobs:
                return
                
            # ✅ CORREÇÃO: Usar 'status' ao invés de 'status_update'
            job_info['status'] = step['status']
            job_info['message'] = step['message']
            job_info['last_updated'] = time.time()
            
            print(f"[{job_id}] ... Executando passo: {job_info['status']}")
            
            # Preparar parâmetros para o agente
            agent_params = step['params'].copy()
            
            if i == 0:
                # Primeira etapa: combinar relatório com instruções extras
                relatorio_gerado = job_info['data']['analysis_report']
                instrucoes_usuario = job_info['data'].get('instrucoes_extras')
                
                instrucoes_completas = relatorio_gerado
                if instrucoes_usuario:
                    instrucoes_completas += f"\n\n--- INSTRUÇÕES ADICIONAIS DO USUÁRIO ---\n{instrucoes_usuario}"
                
                agent_params.update({
                    'repositorio': job_info['data']['repo_name'],
                    'nome_branch': job_info['data']['branch_name'],
                    'instrucoes_extras': instrucoes_completas
                })
            else:
                # Etapas subsequentes: usar resultado anterior
                agent_params['codigo'] = str(previous_step_result)
            
            # Executar função do agente
            if step['agent_function']:
                agent_response = agente_revisor.main(**agent_params)
                
                # ✅ CORREÇÃO: agente_revisor.main() retorna {"tipo_analise": X, "resultado": Y}
                # onde "resultado" é uma string, não um dicionário
                resultado_bruto = agent_response['resultado']
                
                # Tentar extrair JSON da string (pode vir com ```json``` ou não)
                if isinstance(resultado_bruto, str):
                    json_string = resultado_bruto.replace("```json", '').replace("```", '').strip()
                    try:
                        previous_step_result = json.loads(json_string)
                    except json.JSONDecodeError:
                        # Se não conseguir fazer parse, usar como string mesmo
                        previous_step_result = resultado_bruto
                else:
                    previous_step_result = resultado_bruto
                
                if i == 0:
                    resultado_refatoracao = previous_step_result
                else:
                    resultado_agrupamento = previous_step_result
        
        # Etapas finais de processamento
        job_info['status'] = 'populating_data'
        job_info['message'] = 'Preparando dados para commit...'
        job_info['last_updated'] = time.time()
        print(f"[{job_id}] ... Etapa de preenchimento...")
        
        dados_preenchidos = preenchimento.main(
            json_agrupado=resultado_agrupamento, 
            json_inicial=resultado_refatoracao
        )
        
        print(f"[{job_id}] ... Etapa de transformação...")
        
        # ✅ CORREÇÃO: Verificar se dados_preenchidos é dict antes de processar
        if isinstance(dados_preenchidos, str):
            # Se for string, tentar converter para JSON
            try:
                dados_preenchidos = json.loads(dados_preenchidos)
            except json.JSONDecodeError:
                print(f"[{job_id}] ⚠️ Não foi possível converter dados_preenchidos para JSON")
                dados_preenchidos = {"resumo_geral": "Erro na conversão de dados"}
        
        dados_finais_formatados = {
            "resumo_geral": dados_preenchidos.get("resumo_geral", "") if isinstance(dados_preenchidos, dict) else "",
            "grupos": []
        }
        
        if isinstance(dados_preenchidos, dict):
            for nome_grupo, detalhes_pr in dados_preenchidos.items():
                if nome_grupo == "resumo_geral":
                    continue
                    
                # ✅ CORREÇÃO: Verificar se detalhes_pr é dict antes de usar .get()
                if isinstance(detalhes_pr, dict):
                    dados_finais_formatados["grupos"].append({
                        "branch_sugerida": nome_grupo,
                        "titulo_pr": detalhes_pr.get("resumo_do_pr", ""),
                        "resumo_do_pr": detalhes_pr.get("descricao_do_pr", ""),
                        "conjunto_de_mudancas": detalhes_pr.get("conjunto_de_mudancas", [])
                    })
                else:
                    # Se detalhes_pr não é dict, criar estrutura básica
                    dados_finais_formatados["grupos"].append({
                        "branch_sugerida": nome_grupo,
                        "titulo_pr": f"Mudanças em {nome_grupo}",
                        "resumo_do_pr": str(detalhes_pr) if detalhes_pr else "",
                        "conjunto_de_mudancas": []
                    })
        
        if not dados_finais_formatados.get("grupos"):
            print(f"[{job_id}] ⚠️ Nenhum grupo foi criado, criando grupo padrão")
            dados_finais_formatados["grupos"].append({
                "branch_sugerida": "refactoring",
                "titulo_pr": "Refatoração automática",
                "resumo_do_pr": "Aplicação de melhorias no código baseadas na análise",
                "conjunto_de_mudancas": []
            })

        job_info['status'] = 'committing_to_github'
        job_info['message'] = 'Enviando mudanças para GitHub...'
        job_info['last_updated'] = time.time()
        print(f"[{job_id}] ... Etapa de commit para o GitHub...")
        
        # ✅ USAR FUNÇÃO SEGURA PARA COMMIT
        # Importar a função segura (você pode colocar este código diretamente aqui)
        def safe_commit_to_github_inline():
            try:
                print(f"[{job_id}] 🔍 Validando acesso ao repositório {job_info['data']['repo_name']}...")
                
                # Importar dentro da função para evitar problemas de dependência
                try:
                    from tools import github_connector, commit_multiplas_branchs
                except ImportError as e:
                    print(f"[{job_id}] ❌ Módulos GitHub não disponíveis: {e}")
                    return False
                
                # Validação rápida de acesso ao repositório
                try:
                    print(f"[{job_id}] 📋 Testando conexão com {job_info['data']['repo_name']}...")
                    repo = github_connector.connection(repositorio=job_info['data']['repo_name'])
                    
                    # ✅ CORREÇÃO: repo já é o objeto Repository, não precisa de .get_repo()
                    print(f"[{job_id}] ✅ Repositório acessível: {repo.full_name}")
                    
                    # Verificar se a branch existe
                    branch_to_check = job_info['data']['branch_name'] or 'main'
                    try:
                        ref = repo.get_git_ref(f"heads/{branch_to_check}")
                        print(f"[{job_id}] ✅ Branch '{branch_to_check}' encontrada")
                    except Exception as branch_error:
                        if "404" in str(branch_error):
                            print(f"[{job_id}] ⚠️ Branch '{branch_to_check}' não encontrada, tentando 'master'...")
                            try:
                                ref = repo.get_git_ref("heads/master")
                                print(f"[{job_id}] ✅ Branch 'master' encontrada")
                            except Exception:
                                print(f"[{job_id}] ❌ Nem 'main' nem 'master' encontradas")
                                return False
                        else:
                            raise branch_error
                            
                except Exception as github_error:
                    error_msg = str(github_error)
                    print(f"[{job_id}] ❌ Erro GitHub: {error_msg}")
                    
                    if "404" in error_msg:
                        print(f"[{job_id}] ❌ Repositório não encontrado ou sem acesso")
                        return False
                    elif "403" in error_msg:
                        print(f"[{job_id}] ❌ Token do GitHub sem permissões")
                        return False
                    else:
                        print(f"[{job_id}] ❌ Erro inesperado do GitHub")
                        return False
                
                # Se chegou aqui, tentar o commit
                print(f"[{job_id}] 🚀 Iniciando commit para GitHub...")
                
                # ✅ CORREÇÃO: Usar a branch correta detectada na validação
                branch_to_use = job_info['data']['branch_name'] or 'main'
                
                # Verificar qual branch realmente existe
                detected_branch = None
                try:
                    repo.get_git_ref(f"heads/{branch_to_use}")
                    detected_branch = branch_to_use
                    print(f"[{job_id}] 📋 Usando branch: {detected_branch}")
                except Exception:
                    try:
                        repo.get_git_ref("heads/master")
                        detected_branch = 'master'
                        print(f"[{job_id}] 📋 Branch 'main' não encontrada, usando 'master'")
                    except Exception:
                        try:
                            repo.get_git_ref("heads/main")
                            detected_branch = 'main'
                            print(f"[{job_id}] 📋 Usando branch padrão 'main'")
                        except Exception:
                            print(f"[{job_id}] ❌ Nenhuma branch padrão encontrada")
                            return False
                
                # Criar uma cópia dos dados com a branch correta
                dados_para_commit = dados_finais_formatados.copy()
                
                # Chamar commit com a branch detectada
                commit_multiplas_branchs.processar_e_subir_mudancas_agrupadas(
                    nome_repo=job_info['data']['repo_name'],
                    dados_agrupados=dados_para_commit,
                    base_branch=detected_branch  # ✅ Usar branch detectada
                )
                
                print(f"[{job_id}] ✅ Commit realizado com sucesso!")
                return True
                
            except Exception as commit_error:
                error_msg = str(commit_error)
                print(f"[{job_id}] ❌ Erro durante commit: {error_msg}")
                return False
        
        # Tentar commit seguro
        commit_success = safe_commit_to_github_inline()
        
        if commit_success:
            job_info['message'] = 'Análise concluída e mudanças enviadas para GitHub!'
        else:
            job_info['message'] = 'Análise concluída. Commit não realizado devido a problemas de acesso ao GitHub.'
            job_info['error_details'] = 'Verifique se o repositório existe e se o token GitHub tem permissões adequadas.'
        
        job_info['status'] = 'completed'
        job_info['message'] = 'Processo concluído com sucesso!'
        job_info['progress'] = 100
        job_info['last_updated'] = time.time()
        print(f"[{job_id}] ✅ Processo concluído com sucesso!")
        
    except Exception as e:
        print(f"[{job_id}] ❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        
        if job_id in jobs:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['error_details'] = str(e)
            jobs[job_id]['message'] = f'Erro durante processamento: {str(e)}'
            jobs[job_id]['last_updated'] = time.time()

# --- ENDPOINTS DA API ---

@app.get("/")
async def root():
    return {
        "message": "Backend Agentes Peers funcionando!",
        "status": "online",
        "agents_available": AGENTS_AVAILABLE,
        "workflows": list(WORKFLOW_REGISTRY.keys())
    }

@app.post("/start-analysis", response_model=StartAnalysisResponse, tags=["Jobs"])
def start_analysis(payload: StartAnalysisPayload):
    """Inicia um novo job de análise de código e retorna um relatório para aprovação."""
    try:
        print(f"🚀 Iniciando análise: {payload.repo_name} ({payload.analysis_type})")
        
        # Gerar relatório inicial
        if AGENTS_AVAILABLE:
            print(f"📡 Chamando agente_revisor.main() com parâmetros:")
            print(f"  - tipo_analise: {payload.analysis_type}")
            print(f"  - repositorio: {payload.repo_name}")
            print(f"  - nome_branch: {payload.branch_name}")
            print(f"  - instrucoes_extras: {payload.instrucoes_extras}")
            
            resposta = agente_revisor.main(
                tipo_analise=payload.analysis_type,
                repositorio=payload.repo_name,
                nome_branch=payload.branch_name,
                instrucoes_extras=payload.instrucoes_extras
            )
            
            print(f"📄 Resposta do agente recebida:")
            print(f"  - Tipo: {type(resposta)}")
            print(f"  - Keys: {resposta.keys() if isinstance(resposta, dict) else 'N/A'}")
            
            # ✅ CORREÇÃO: agente_revisor.main() retorna {"tipo_analise": X, "resultado": Y}
            if isinstance(resposta, dict) and 'resultado' in resposta:
                report = resposta['resultado']
                print(f"✅ Relatório extraído com sucesso ({len(report)} caracteres)")
            else:
                print(f"❌ Estrutura inesperada na resposta do agente")
                report = str(resposta)
        else:
            # Relatório simulado para desenvolvimento
            report = f"""
# Relatório de Análise - {payload.analysis_type.upper()}

## Repositório: {payload.repo_name}
## Branch: {payload.branch_name or 'main'}

### Resumo da Análise
Este é um relatório simulado para o repositório {payload.repo_name}.

### Problemas Identificados
1. **Arquitetura**: Necessário refatorar algumas classes
2. **Testes**: Faltam testes unitários em alguns módulos
3. **Documentação**: Código precisa de mais comentários

### Recomendações
- Aplicar padrões de design
- Implementar testes automatizados
- Melhorar documentação

**Status**: Aguardando aprovação para continuar com as correções.
            """
            print("🎭 Usando relatório simulado (agentes não disponíveis)")
        
        # Criar job
        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            'status': 'pending_approval',
            'message': 'Aguardando aprovação do usuário',
            'progress': 25,
            'data': {
                'repo_name': payload.repo_name,
                'branch_name': payload.branch_name,
                'original_analysis_type': payload.analysis_type,
                'analysis_report': report,
                'instrucoes_extras': payload.instrucoes_extras
            },
            'created_at': time.time(),
            'last_updated': time.time()
        }
        
        print(f"✅ Job criado: {job_id}")
        print(f"📊 Relatório tem {len(report)} caracteres")
        
        return StartAnalysisResponse(job_id=job_id, report=report)
        
    except Exception as e:
        print(f"❌ Erro ao gerar análise: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Falha ao gerar o relatório de análise: {e}")

@app.post("/update-job-status", tags=["Jobs"])
def update_job_status(payload: UpdateJobPayload, background_tasks: BackgroundTasks):
    """Atualiza o status do job (aprovar/rejeitar)."""
    job = jobs.get(payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job ID não encontrado")
    
    if job['status'] != 'pending_approval':
        raise HTTPException(
            status_code=400, 
            detail=f"O job não pode ser modificado. Status atual: {job['status']}"
        )
    
    if payload.action == 'approve':
        job['status'] = 'workflow_started'
        job['message'] = 'Processamento iniciado'
        job['last_updated'] = time.time()
        
        # Escolher entre workflow real ou simulado
        if AGENTS_AVAILABLE:
            background_tasks.add_task(run_workflow_task_REAL, payload.job_id)
        else:
            background_tasks.add_task(simulate_job_progress, payload.job_id)
        
        return {
            "job_id": payload.job_id,
            "status": "workflow_started",
            "message": "Processo de refatoração iniciado."
        }
    
    elif payload.action == 'reject':
        job['status'] = 'rejected'
        job['message'] = 'Processo encerrado pelo usuário'
        job['last_updated'] = time.time()
        
        return {
            "job_id": payload.job_id,
            "status": "rejected",
            "message": "Processo encerrado a pedido do usuário."
        }

@app.get("/status/{job_id}", response_model=JobStatusResponse, tags=["Jobs"])
def get_status(job_id: str = Path(..., title="O ID do Job a ser verificado")):
    """Verifica o status de um job específico."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job ID não encontrado")
    
    # ✅ CORREÇÃO: Incluir o relatório na resposta do status
    response_data = {
        "job_id": job_id,
        "status": job['status'],
        "message": job.get('message'),
        "progress": job.get('progress'),
        "error_details": job.get('error_details'),
        "last_updated": job.get('last_updated')
    }
    
    # Adicionar relatório se disponível
    if 'data' in job and 'analysis_report' in job['data']:
        response_data["report"] = job['data']['analysis_report']
    
    return response_data

@app.get("/jobs", tags=["Jobs"])
def list_jobs():
    """Lista todos os jobs."""
    return {
        "jobs": [
            {
                "job_id": job_id,
                "status": job_data['status'],
                "message": job_data.get('message'),
                "progress": job_data.get('progress'),
                "repo_name": job_data['data']['repo_name'],
                "analysis_type": job_data['data']['original_analysis_type'],
                "branch_name": job_data['data'].get('branch_name'),
                "created_at": job_data.get('created_at'),
                "last_updated": job_data.get('last_updated'),
                "report": job_data['data'].get('analysis_report'),  # ✅ Incluir relatório
                "instructions": job_data['data'].get('instrucoes_extras')  # ✅ Incluir instruções
            }
            for job_id, job_data in jobs.items()
        ]
    }

@app.delete("/jobs/{job_id}", tags=["Jobs"])  
def delete_job(job_id: str):
    """Remove um job específico."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job ID não encontrado")
    
    del jobs[job_id]
    return {"message": f"Job {job_id} removido com sucesso"}

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Backend está funcionando",
        "agents_available": AGENTS_AVAILABLE,
        "active_jobs": len(jobs)
    }

@app.get("/test-github/{repo_name}")
async def test_github_access(repo_name: str, branch_name: str = "main"):
    """Testa o acesso a um repositório GitHub específico."""
    try:
        if not AGENTS_AVAILABLE:
            return {
                "success": False,
                "error": "Agentes não disponíveis para teste",
                "repo_name": repo_name,
                "branch_name": branch_name
            }
        
        print(f"🔍 Testando acesso ao repositório: {repo_name}")
        
        # Tentar acessar o repositório
        from tools import github_reader
        
        resultado = github_reader.main(
            nome_repo=repo_name,
            tipo_de_analise='design',
            nome_branch=branch_name
        )
        
        if resultado:
            return {
                "success": True,
                "message": "Acesso ao repositório confirmado",
                "repo_name": repo_name,
                "branch_name": branch_name,
                "code_size": len(str(resultado))
            }
        else:
            return {
                "success": False,
                "error": "Repositório retornou dados vazios",
                "repo_name": repo_name,
                "branch_name": branch_name
            }
            
    except Exception as e:
        error_msg = str(e)
        
        if "404" in error_msg:
            return {
                "success": False,
                "error": "Repositório não encontrado ou sem permissão de leitura",
                "repo_name": repo_name,
                "branch_name": branch_name,
                "github_error": error_msg
            }
        elif "403" in error_msg:
            return {
                "success": False,
                "error": "Token do GitHub inválido ou sem permissões",
                "repo_name": repo_name,
                "branch_name": branch_name,
                "github_error": error_msg
            }
        else:
            return {
                "success": False,
                "error": f"Erro ao acessar repositório: {error_msg}",
                "repo_name": repo_name,
                "branch_name": branch_name
            }