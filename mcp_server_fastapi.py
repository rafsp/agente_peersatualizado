# mcp_server_fastapi.py - VERSÃO FINAL COMPLETA E CORRIGIDA

from fastapi import FastAPI, BackgroundTasks, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any, List
import json
import uuid
import time
import threading
import sys
import os
import traceback
import importlib.util
from datetime import datetime

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Adicionar subdiretórios importantes ao path
subdirs = ['agents', 'tools', '.']
for subdir in subdirs:
    path = os.path.join(current_dir, subdir)
    if os.path.exists(path):
        sys.path.insert(0, path)

print(f"📁 Diretório atual: {current_dir}")

# CONFIGURAÇÃO DE CREDENCIAIS E MODELOS
def setup_credentials():
    """Configura credenciais usando .env ou variáveis de ambiente"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Arquivo .env carregado")
    except ImportError:
        print("⚠️ python-dotenv não instalado, usando variáveis de ambiente")
    
    # Verificar se as credenciais estão disponíveis
    openai_key = os.getenv('OPENAI_API_KEY')
    github_token = os.getenv('GITHUB_TOKEN') or os.getenv('github_token') or os.getenv('GITHUB_PAT') or os.getenv('github_pat')
    
    # Configurar modelo padrão
    default_model = os.getenv('DEFAULT_MODEL', 'gpt-4.1')
    
    print(f"🔑 OpenAI API Key: {'✅ Configurada' if openai_key else '❌ Não encontrada'}")
    print(f"🔑 GitHub Token: {'✅ Configurado' if github_token else '❌ Não encontrado'}")
    print(f"🤖 Modelo padrão: {default_model}")
    
    return {
        'openai_available': bool(openai_key),
        'github_available': bool(github_token),
        'default_model': default_model
    }

# Configurar credenciais
credentials_status = setup_credentials()

# IMPORTAÇÃO DO AGENTE REAL
class RealAgentImporter:
    def __init__(self):
        self.agente_principal = None
        self.github_reader = None
        self.revisor_geral = None
        
    def fix_colab_imports(self):
        """Corrige imports específicos do Google Colab de forma mais robusta"""
        print("🔧 Corrigindo imports do Google Colab...")
        
        try:
            import sys
            from unittest.mock import MagicMock
            
            # Criar mock mais robusto para google.colab
            if 'google' not in sys.modules:
                # Mock completo do módulo google
                google_mock = MagicMock()
                
                # Mock específico para userdata
                def get_env_var(key):
                    # Lista extendida de possíveis nomes para tokens GitHub
                    if key.lower() in ['github_token', 'github_pat']:
                        possible_names = [
                            'GITHUB_TOKEN',
                            'github_token', 
                            'GITHUB_PAT',
                            'github_pat',
                            'GH_TOKEN',
                            'gh_token'
                        ]
                        for var_name in possible_names:
                            value = os.getenv(var_name)
                            if value:
                                print(f"✅ Encontrada variável GitHub: {var_name}")
                                return value
                    
                    # Para outras variáveis, tentar variações normais
                    variations = [key, key.upper(), key.lower()]
                    for var_name in variations:
                        value = os.getenv(var_name)
                        if value:
                            print(f"✅ Encontrada variável: {var_name}")
                            return value
                    
                    print(f"⚠️ Variável não encontrada: {key}")
                    return None
                
                # Configurar userdata mock
                userdata_mock = MagicMock()
                userdata_mock.get = get_env_var
                
                # Configurar hierarquia completa
                colab_mock = MagicMock()
                colab_mock.userdata = userdata_mock
                google_mock.colab = colab_mock
                
                # Registrar no sys.modules
                sys.modules['google'] = google_mock
                sys.modules['google.colab'] = colab_mock
                sys.modules['google.colab.userdata'] = userdata_mock
                
                print("✅ Mock completo do Google Colab criado")
                
                # Testar se funcionou
                try:
                    from google.colab import userdata
                    test_token = userdata.get('GITHUB_TOKEN')
                    print(f"🧪 Teste do mock: {'✅ Funcionando' if test_token else '⚠️ Token não encontrado'}")
                except Exception as e:
                    print(f"⚠️ Erro no teste do mock: {e}")
                
        except Exception as e:
            print(f"⚠️ Erro ao criar mock do Colab: {e}")
            
        # Patch adicional para imports problemáticos
        try:
            # Se os módulos tools já foram importados com erro, forçar reload
            import importlib
            
            modules_to_reload = []
            for module_name in sys.modules.keys():
                if module_name.startswith('tools.') or module_name == 'tools':
                    modules_to_reload.append(module_name)
            
            # Remover módulos problemáticos do cache
            for module_name in modules_to_reload:
                if module_name in sys.modules:
                    del sys.modules[module_name]
                    print(f"🔄 Removido do cache: {module_name}")
            
        except Exception as e:
            print(f"⚠️ Erro no patch de imports: {e}")
        
    def import_real_agents(self):
        """Importa os agentes reais do seu projeto"""
        print("🤖 Importando agentes reais...")
        
        # Importar agente principal
        try:
            if os.path.exists(os.path.join(current_dir, 'agents', 'agente_revisor.py')):
                from agents import agente_revisor
                self.agente_principal = agente_revisor
                print("✅ agente_revisor importado com sucesso")
                
                # Verificar função principal
                if hasattr(agente_revisor, 'main'):
                    print("✅ Função main() encontrada")
                else:
                    print("⚠️ Função main() não encontrada")
                    
        except Exception as e:
            print(f"❌ Erro ao importar agente_revisor: {e}")
            
        # Importar github_reader
        try:
            if os.path.exists(os.path.join(current_dir, 'tools', 'github_reader.py')):
                from tools import github_reader
                self.github_reader = github_reader
                print("✅ github_reader importado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao importar github_reader: {e}")
            
        # Importar revisor_geral
        try:
            if os.path.exists(os.path.join(current_dir, 'tools', 'revisor_geral.py')):
                from tools import revisor_geral
                self.revisor_geral = revisor_geral
                openai_key = os.getenv('OPENAI_API_KEY')
                if openai_key:
                    print(f"✅ OpenAI API configurada (chave: {openai_key[:7]}...)")
                print("✅ revisor_geral importado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao importar revisor_geral: {e}")
            
        return self.agente_principal is not None
    
    def execute_real_analysis(self, tipo_analise: str, repositorio: str = None, **kwargs):
        """Executa análise usando o agente real - VERSÃO FINAL CORRIGIDA"""
        if not self.agente_principal:
            raise Exception("Agente principal não disponível")
            
        try:
            print(f"🚀 Executando análise REAL: {tipo_analise}")
            print(f"📂 Repositório: {repositorio}")
            
            # Verificar assinatura da função main() real
            import inspect
            sig = inspect.signature(self.agente_principal.main)
            valid_params = list(sig.parameters.keys())
            print(f"📝 Parâmetros aceitos pela função main(): {valid_params}")
            
            # Preparar apenas parâmetros válidos
            params = {}
            
            # Parâmetros obrigatórios
            if 'tipo_analise' in valid_params:
                params['tipo_analise'] = tipo_analise
            if 'repositorio' in valid_params and repositorio:
                params['repositorio'] = repositorio
                
            # Parâmetros opcionais baseados na assinatura real
            if 'nome_branch' in valid_params and kwargs.get('nome_branch'):
                params['nome_branch'] = kwargs.get('nome_branch')
            if 'codigo' in valid_params and kwargs.get('codigo'):
                params['codigo'] = kwargs.get('codigo')
            if 'instrucoes_extras' in valid_params:
                params['instrucoes_extras'] = kwargs.get('instrucoes_extras', '')
                
            # Parâmetros específicos do modelo (apenas se aceitos)
            if 'model_name' in valid_params:
                params['model_name'] = kwargs.get('model_name', credentials_status.get('default_model', 'gpt-4.1'))
                print(f"📝 Adicionando model_name: {params['model_name']}")
            else:
                print(f"⚠️ Parâmetro model_name não aceito pela função main()")
                
            if 'max_token_out' in valid_params:
                params['max_token_out'] = kwargs.get('max_token_out', 3000)
                print(f"📝 Adicionando max_token_out: {params['max_token_out']}")
            else:
                print(f"⚠️ Parâmetro max_token_out não aceito pela função main()")
            
            print(f"📋 Parâmetros enviados: {list(params.keys())}")
            print(f"📄 Valores: {params}")
            
            # Executar análise real sem logs problemáticos
            print(f"🔄 Iniciando execução da análise...")
            
            resultado = self.agente_principal.main(**params)
            
            # Logs de resultado
            print(f"📤 Resultado recebido do agente:")
            print(f"   Tipo: {type(resultado)}")
            
            if isinstance(resultado, dict):
                print(f"   Chaves: {list(resultado.keys())}")
                if 'resultado' in resultado:
                    resultado_conteudo = resultado['resultado']
                    print(f"   Tamanho do resultado: {len(str(resultado_conteudo))} caracteres")
                    print(f"   Primeiros 200 chars: {str(resultado_conteudo)[:200]}...")
                else:
                    print(f"   Conteúdo completo: {resultado}")
            else:
                print(f"   Conteúdo: {str(resultado)[:200]}...")
            
            print(f"✅ Análise real executada com sucesso")
            
            if isinstance(resultado, dict) and 'resultado' in resultado:
                return resultado['resultado']
            else:
                return str(resultado)
                
        except Exception as e:
            print(f"❌ Erro na análise real: {e}")
            traceback.print_exc()
            
            # Retornar erro detalhado ao invés de falhar silenciosamente
            return f"""# Erro na Análise Real

**Tipo de Análise**: {tipo_analise}
**Repositório**: {repositorio}
**Erro**: {str(e)}

## Detalhes do Problema

Ocorreu um erro ao executar a análise real. Possíveis causas:

1. **Credenciais**: Verificar se OPENAI_API_KEY e GITHUB_TOKEN estão configurados
2. **Dependências**: Verificar se todas as bibliotecas estão instaladas
3. **Permissões**: Verificar se o repositório é acessível
4. **Rede**: Verificar conectividade com APIs externas

## Status das Credenciais
- OpenAI API: {'✅' if credentials_status['openai_available'] else '❌ Não configurada'}
- GitHub Token: {'✅' if credentials_status['github_available'] else '❌ Não configurado'}

## Como Resolver

1. Crie um arquivo `.env` no diretório do backend:
```
OPENAI_API_KEY=sua_chave_openai_aqui
GITHUB_TOKEN=seu_token_github_aqui
```

2. Ou configure as variáveis de ambiente:
```bash
export OPENAI_API_KEY="sua_chave_aqui"
export GITHUB_TOKEN="seu_token_aqui"
```

3. Reinstale dependências se necessário:
```bash
pip install openai PyGithub python-dotenv
```

**Erro técnico**: {str(e)}
"""
    
    def get_status(self):
        """Retorna status dos agentes"""
        return {
            "agente_principal_disponivel": self.agente_principal is not None,
            "github_reader_disponivel": self.github_reader is not None,
            "revisor_geral_disponivel": self.revisor_geral is not None,
            "credenciais": credentials_status,
            "modulo_principal": self.agente_principal.__name__ if self.agente_principal else None
        }

# Inicializar importador de agentes reais
real_agent = RealAgentImporter()
real_agent.fix_colab_imports()  # Corrigir imports do Colab primeiro
AGENTES_DISPONVEIS = real_agent.import_real_agents()

print(f"🎯 Status dos agentes reais: {real_agent.get_status()}")

# --- Modelos Pydantic ---
class StartAnalysisPayload(BaseModel):
    repo_name: str
    analysis_type: Literal[
        "design", "relatorio_teste_unitario", "escrever_testes", 
        "pentest", "seguranca", "terraform", "refatoracao", 
        "refatorador", "agrupamento_testes", "agrupamento_design", 
        "docstring"
    ]
    branch_name: Optional[str] = "main"
    instrucoes_extras: Optional[str] = ""

class UpdateJobPayload(BaseModel):
    job_id: str
    action: Literal["approve", "reject"]

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    repo_name: Optional[str] = None
    analysis_type: Optional[str] = None
    message: Optional[str] = None
    progress: Optional[int] = None
    error_details: Optional[str] = None
    created_at: Optional[float] = None
    last_updated: Optional[float] = None

class StartAnalysisResponse(BaseModel):
    job_id: str
    status: str
    message: str
    report: str
    config: Dict[str, Any]

# --- Configuração FastAPI ---
app = FastAPI(
    title="Agentes Peers - Backend com Agentes Reais",
    description="Sistema real de análise de código usando agentes especializados",
    version="2.2.0",
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
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage de jobs
jobs: Dict[str, Dict[str, Any]] = {}

# Mapeamento de tipos de análise para compatibilidade
# Baseado em: analises_validas = ["design", "pentest", "seguranca", "terraform"]
ANALYSIS_TYPE_MAPPING = {
    'design': 'design',
    'security': 'seguranca',
    'pentest': 'pentest', 
    'terraform': 'terraform',
    'relatorio_teste_unitario': 'design',  # Mapear para design como fallback
    'escrever_testes': 'design',  # Mapear para design como fallback
    'seguranca': 'seguranca',
    'refatoracao': 'design',
    'docstring': 'design'
}

def execute_real_workflow(job_id: str):
    """Executa workflow usando agentes reais"""
    try:
        print(f"🤖 [{job_id}] Iniciando workflow com agentes REAIS...")
        
        job = jobs[job_id]
        analysis_type = job['data']['original_analysis_type']
        repo_name = job['data']['repo_name']
        branch_name = job['data']['branch_name']
        instrucoes_extras = job['data']['instrucoes_extras']
        
        # Mapear tipo de análise
        mapped_type = ANALYSIS_TYPE_MAPPING.get(analysis_type, analysis_type)
        
        # Atualizar status
        job.update({
            'status': 'processing',
            'progress': 40,
            'message': f'Executando análise real {mapped_type}...',
            'last_updated': time.time()
        })
        
        # Executar análise real completa
        print(f"🔄 [{job_id}] Chamando agente real para {mapped_type}")
        
        final_report = real_agent.execute_real_analysis(
            tipo_analise=mapped_type,
            repositorio=repo_name,
            nome_branch=branch_name,
            instrucoes_extras=instrucoes_extras
        )
        
        # Simular etapas finais
        job.update({
            'status': 'finalizing',
            'progress': 90,
            'message': 'Finalizando relatório...',
            'last_updated': time.time()
        })
        
        time.sleep(2)  # Simular processamento final
        
        # Finalizar
        job.update({
            'status': 'completed',
            'progress': 100,
            'message': 'Análise real concluída com sucesso!',
            'last_updated': time.time(),
            'completed_at': time.time()
        })
        
        job['data']['final_report'] = final_report
        
        print(f"🎉 [{job_id}] Análise real concluída!")
        
    except Exception as e:
        print(f"❌ Erro no workflow real [{job_id}]: {e}")
        traceback.print_exc()
        
        jobs[job_id].update({
            'status': 'failed',
            'error': str(e),
            'message': f"Erro na análise: {e}",
            'last_updated': time.time()
        })

def simulate_workflow(job_id: str):
    """Workflow simulado para quando agentes não estão disponíveis"""
    try:
        print(f"🎭 [{job_id}] Workflow simulado (agentes não disponíveis)")
        
        job = jobs[job_id]
        
        steps = [
            {"status": "connecting_github", "message": "Conectando ao GitHub...", "duration": 2},
            {"status": "reading_code", "message": "Lendo código do repositório...", "duration": 3},
            {"status": "analyzing", "message": "Analisando com IA...", "duration": 4},
            {"status": "generating_report", "message": "Gerando relatório...", "duration": 2},
            {"status": "completed", "message": "Simulação concluída!", "duration": 0}
        ]
        
        current_progress = 25
        progress_per_step = 75 / len(steps)
        
        for step in steps:
            if job_id not in jobs:
                break
                
            time.sleep(step["duration"])
            current_progress += progress_per_step
            
            if step["status"] == "completed":
                current_progress = 100
                
            jobs[job_id].update({
                "status": step["status"],
                "message": step["message"],
                "progress": int(current_progress),
                "last_updated": time.time()
            })
            
        # Relatório simulado
        analysis_type = job['data']['original_analysis_type']
        repo_name = job['data']['repo_name']
        
        simulated_report = f"""# Análise {analysis_type.title()} - Modo Simulação

## Repositório Analisado
**{repo_name}**

## ⚠️ Modo Simulação Ativo

Esta análise foi executada em modo simulação porque:

{real_agent.get_status()}

## Como Ativar Análise Real

1. **Configure credenciais**:
   - OPENAI_API_KEY para análise com IA
   - GITHUB_TOKEN para acesso ao repositório

2. **Verifique dependências**:
   ```bash
   pip install openai PyGithub python-dotenv
   ```

3. **Crie arquivo .env**:
   ```
   OPENAI_API_KEY=sua_chave_openai
   GITHUB_TOKEN=seu_token_github
   ```

4. **Reinicie o backend** e execute nova análise

## Próximos Passos

✅ Configure as credenciais necessárias  
✅ Verifique o endpoint /debug para mais detalhes  
✅ Execute nova análise para usar agentes reais  
"""
        
        jobs[job_id]['data']['final_report'] = simulated_report
        
    except Exception as e:
        print(f"❌ Erro na simulação [{job_id}]: {e}")
        jobs[job_id].update({
            'status': 'failed',
            'error': str(e),
            'message': f"Erro na simulação: {e}",
            'last_updated': time.time()
        })

# --- ENDPOINTS ---

@app.get("/")
async def root():
    """Informações do sistema"""
    status = real_agent.get_status()
    return {
        "message": "Backend Agentes Peers - Com Agentes Reais",
        "version": "2.2.0",
        "agentes_status": status,
        "jobs_count": len(jobs),
        "modo": "AGENTES REAIS" if AGENTES_DISPONVEIS else "SIMULAÇÃO",
        "credenciais_configuradas": credentials_status
    }

@app.get("/health")
async def health_check():
    """Health check com status dos agentes reais"""
    status = real_agent.get_status()
    return {
        "status": "healthy",
        "message": "Sistema funcionando com agentes reais",
        "agentes_reais": status,
        "credenciais": credentials_status,
        "jobs_ativas": len([j for j in jobs.values() if j['status'] not in ['completed', 'failed', 'rejected']]),
        "total_jobs": len(jobs),
        "timestamp": time.time()
    }

@app.post("/start-analysis", response_model=StartAnalysisResponse)
async def start_analysis(payload: StartAnalysisPayload):
    """Inicia análise usando agentes reais"""
    print(f"🚀 [API] Nova análise REAL: {payload.analysis_type} para {payload.repo_name}")
    
    try:
        # Mapear tipo de análise
        mapped_type = ANALYSIS_TYPE_MAPPING.get(payload.analysis_type, payload.analysis_type)
        
        # Verificar se o tipo é válido no agente
        if AGENTES_DISPONVEIS and hasattr(real_agent.agente_principal, 'analises_validas'):
            valid_types = real_agent.agente_principal.analises_validas
            if mapped_type not in valid_types:
                print(f"⚠️ Tipo {mapped_type} não válido. Tipos válidos: {valid_types}")
                mapped_type = 'design'  # Usar design como fallback
                print(f"🔄 Usando tipo fallback: {mapped_type}")
        
        # Gerar relatório inicial usando agente real
        if AGENTES_DISPONVEIS and credentials_status['openai_available'] and credentials_status['github_available']:
            print(f"🤖 Executando análise inicial REAL com {real_agent.agente_principal.__name__}")
            
            try:
                initial_report = real_agent.execute_real_analysis(
                    tipo_analise=mapped_type,
                    repositorio=payload.repo_name,
                    nome_branch=payload.branch_name,
                    instrucoes_extras=f"Análise inicial rápida. {payload.instrucoes_extras}"
                )
                
                print(f"✅ Relatório real gerado com {len(initial_report)} caracteres")
                
            except Exception as e:
                print(f"⚠️ Erro na análise inicial, gerando relatório de erro: {e}")
                initial_report = f"""# Erro na Análise Inicial

Ocorreu um erro ao executar a análise inicial: {str(e)}

**Verificações necessárias:**
- Credenciais configuradas corretamente
- Repositório acessível 
- Dependências instaladas

O sistema continuará em modo simulação.
"""
        else:
            print(f"📝 Gerando relatório sobre configuração necessária...")
            missing_items = []
            if not AGENTES_DISPONVEIS:
                missing_items.append("❌ Agentes não encontrados")
            if not credentials_status['openai_available']:
                missing_items.append("❌ OPENAI_API_KEY não configurada")
            if not credentials_status['github_available']:
                missing_items.append("❌ GITHUB_TOKEN não configurado")
                
            initial_report = f"""# Configuração Necessária - {payload.analysis_type.title()}

## Repositório: `{payload.repo_name}`

## ⚙️ Status da Configuração

{chr(10).join(missing_items)}

## 🔧 Para Ativar Análise Real

1. **Configure as credenciais** no arquivo `.env`:
```
OPENAI_API_KEY=sua_chave_openai_aqui
GITHUB_TOKEN=seu_token_github_aqui
```

2. **Instale dependências**:
```bash
pip install openai PyGithub python-dotenv
```

3. **Reinicie o backend** e execute nova análise

## 📋 Após Configuração

Quando tudo estiver configurado, este sistema executará:
- ✅ Leitura real do código do repositório GitHub
- ✅ Análise completa usando GPT-4
- ✅ Relatório detalhado e específico para seu código
- ✅ Recomendações práticas e acionáveis

**Clique em "Aprovar" para continuar (será executado em modo simulação até configuração completa).**
"""
        
        # Criar job
        job_id = str(uuid.uuid4())
        current_time = time.time()
        
        jobs[job_id] = {
            'status': 'pending_approval',
            'progress': 20,
            'message': 'Relatório inicial gerado. Aguardando aprovação...',
            'created_at': current_time,
            'last_updated': current_time,
            'data': {
                'repo_name': payload.repo_name,
                'branch_name': payload.branch_name,
                'original_analysis_type': payload.analysis_type,
                'mapped_analysis_type': mapped_type,
                'analysis_report': initial_report,
                'instrucoes_extras': payload.instrucoes_extras or ""
            }
        }
        
        # Configuração de resposta
        config = {
            "name": f"Análise {payload.analysis_type.title()}",
            "description": f"Análise real de código usando agentes especializados",
            "requires_approval": True,
            "agentes_reais_disponveis": AGENTES_DISPONVEIS,
            "credenciais_configuradas": credentials_status,
            "modo_operacao": "ANÁLISE REAL" if (AGENTES_DISPONVEIS and credentials_status['openai_available'] and credentials_status['github_available']) else "SIMULAÇÃO",
            "tipo_mapeado": mapped_type
        }
        
        response = StartAnalysisResponse(
            job_id=job_id,
            status="pending_approval",
            message="Relatório inicial gerado! Revise e aprove para análise completa.",
            report=initial_report,
            config=config
        )
        
        print(f"✅ Job {job_id} criado com sucesso")
        return response
        
    except Exception as e:
        print(f"❌ Erro ao iniciar análise: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar análise: {str(e)}")

@app.post("/update-job-status")
async def update_job_status(payload: UpdateJobPayload, background_tasks: BackgroundTasks):
    """Aprova ou rejeita análise"""
    print(f"🔄 [API] Atualizando job {payload.job_id}: {payload.action}")
    
    job = jobs.get(payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    if job['status'] != 'pending_approval':
        raise HTTPException(
            status_code=400,
            detail=f"Job não pode ser alterado. Status atual: {job['status']}"
        )
    
    current_time = time.time()
    
    if payload.action == 'approve':
        job.update({
            'status': 'approved',
            'message': 'Análise aprovada! Iniciando processamento completo...',
            'progress': 25,
            'last_updated': current_time
        })
        
        # Escolher tipo de workflow baseado na disponibilidade real
        can_use_real = (AGENTES_DISPONVEIS and 
                       credentials_status['openai_available'] and 
                       credentials_status['github_available'])
        
        if can_use_real:
            background_tasks.add_task(execute_real_workflow, payload.job_id)
            message = "Análise real iniciada com agentes especializados!"
        else:
            background_tasks.add_task(simulate_workflow, payload.job_id)
            message = "Simulação iniciada (configuração incompleta)"
        
        return {
            "job_id": payload.job_id,
            "status": "approved",
            "message": message
        }
    
    elif payload.action == 'reject':
        job.update({
            'status': 'rejected',
            'message': 'Análise cancelada pelo usuário',
            'progress': 0,
            'last_updated': current_time
        })
        
        return {
            "job_id": payload.job_id,
            "status": "rejected",
            "message": "Análise cancelada."
        }

@app.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str = Path(...)):
    """Status detalhado do job"""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    return JobStatusResponse(
        job_id=job_id,
        status=job['status'],
        repo_name=job.get('data', {}).get('repo_name'),
        analysis_type=job.get('data', {}).get('original_analysis_type'),
        message=job.get('message', 'Processando...'),
        progress=job.get('progress', 0),
        error_details=job.get('error'),
        created_at=job.get('created_at'),
        last_updated=job.get('last_updated')
    )

@app.get("/jobs")
async def list_jobs():
    """Lista todos os jobs com informações detalhadas"""
    job_list = []
    for job_id, job in jobs.items():
        job_info = {
            "job_id": job_id,
            "status": job.get('status'),
            "repo_name": job.get('data', {}).get('repo_name'),
            "analysis_type": job.get('data', {}).get('original_analysis_type'),
            "progress": job.get('progress', 0),
            "created_at": job.get('created_at'),
            "last_updated": job.get('last_updated'),
            "message": job.get('message', ''),
            "has_report": bool(job.get('data', {}).get('final_report'))
        }
        job_list.append(job_info)
    
    # Ordenar por criação (mais recentes primeiro)
    job_list.sort(key=lambda x: x.get('created_at', 0), reverse=True)
    
    return {
        "jobs": job_list,
        "total": len(job_list),
        "active_jobs": len([j for j in job_list if j['status'] not in ['completed', 'failed', 'rejected']]),
        "agentes_status": real_agent.get_status(),
        "credenciais": credentials_status
    }

@app.get("/jobs/{job_id}")
async def get_job_details(job_id: str):
    """Obtém detalhes completos de um job específico"""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} não encontrado")
    
    # Retornar todos os detalhes do job
    job_details = {
        "job_id": job_id,
        "status": job.get('status'),
        "progress": job.get('progress', 0),
        "message": job.get('message', ''),
        "created_at": job.get('created_at'),
        "last_updated": job.get('last_updated'),
        "error": job.get('error'),
        "data": job.get('data', {}),
        "final_report": job.get('data', {}).get('final_report', ''),
        "initial_report": job.get('data', {}).get('analysis_report', '')
    }
    
    return job_details

@app.get("/jobs/{job_id}/report")
async def get_job_report(job_id: str):
    """Obtém apenas o relatório de um job"""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} não encontrado")
    
    final_report = job.get('data', {}).get('final_report')
    initial_report = job.get('data', {}).get('analysis_report')
    
    return {
        "job_id": job_id,
        "status": job.get('status'),
        "initial_report": initial_report,
        "final_report": final_report,
        "report_available": bool(final_report or initial_report)
    }

@app.get("/test-direct")
async def test_direct():
    """Teste direto do agente para debug"""
    try:
        print("🧪 [TESTE DIRETO] Iniciando teste do agente...")
        
        result = {"steps": []}
        
        # Teste 1: Verificar mock do Google Colab
        try:
            from google.colab import userdata
            
            # Testar todas as variações de GitHub token
            github_variations = ['GITHUB_TOKEN', 'github_token', 'GITHUB_PAT', 'github_pat', 'GH_TOKEN']
            found_github_tokens = {}
            
            for var in github_variations:
                value = os.getenv(var)
                if value:
                    found_github_tokens[var] = f"ghp_...{value[-4:]}" if value.startswith('ghp_') else f"...{value[-4:]}"
            
            github_token = userdata.get('GITHUB_TOKEN') or userdata.get('github_token') or userdata.get('github_pat')
            openai_key = userdata.get('OPENAI_API_KEY')
            
            result["steps"].append({
                "step": "1_colab_mock",
                "status": "✅ Mock funcionando",
                "github_token": "✅ Encontrado" if github_token else "❌ Não encontrado",
                "openai_key": "✅ Encontrado" if openai_key else "❌ Não encontrado",
                "tokens_encontrados": found_github_tokens,
                "mock_github_result": f"Mock retornou: {'✅' if github_token else '❌'}"
            })
        except Exception as e:
            result["steps"].append({
                "step": "1_colab_mock",
                "status": f"❌ Erro no mock: {str(e)}"
            })
        
        # Teste 2: Importar módulos tools
        try:
            # Forçar reimport dos módulos
            import importlib
            import sys
            
            # Limpar cache se necessário
            modules_to_clear = [m for m in sys.modules.keys() if m.startswith('tools.')]
            for m in modules_to_clear:
                if m in sys.modules:
                    del sys.modules[m]
            
            from tools import github_reader
            from tools import revisor_geral
            
            result["steps"].append({
                "step": "2_import_tools",
                "status": "✅ Módulos tools importados com sucesso"
            })
        except Exception as e:
            result["steps"].append({
                "step": "2_import_tools",
                "status": f"❌ Erro nos imports: {str(e)}",
                "error_details": str(e)
            })
            return result
        
        # Teste 3: Testar GitHub Reader
        try:
            # Primeiro verificar a assinatura correta
            import inspect
            sig = inspect.signature(github_reader.main)
            params = list(sig.parameters.keys())
            result["steps"].append({
                "step": "3a_github_signature",
                "status": "ℹ️ Assinatura encontrada",
                "parametros": params
            })
            
            # Tentar com os parâmetros corretos descobertos
            try:
                if 'nome_repo' in params:
                    codigo_github = github_reader.main(
                        nome_repo='rafsp/api-springboot-web-app',
                        tipo_de_analise='design'
                    )
                else:
                    # Usar os nomes encontrados dinamicamente
                    kwargs = {}
                    if len(params) >= 1:
                        kwargs[params[0]] = 'rafsp/api-springboot-web-app'
                    if len(params) >= 2:
                        kwargs[params[1]] = 'design'
                    
                    codigo_github = github_reader.main(**kwargs)
            except Exception as e:
                # Se falhar com repositório privado, tentar com público
                if "401" in str(e) or "Bad credentials" in str(e):
                    result["steps"].append({
                        "step": "3b_github_retry",
                        "status": "⚠️ Tentando repositório público",
                        "reason": "Credenciais inválidas para repo privado"
                    })
                    
                    # Tentar com repositório público conhecido
                    if 'nome_repo' in params:
                        codigo_github = github_reader.main(
                            nome_repo='octocat/Hello-World',  # Repo público de exemplo
                            tipo_de_analise='design'
                        )
                    else:
                        kwargs[params[0]] = 'octocat/Hello-World'
                        codigo_github = github_reader.main(**kwargs)
                else:
                    raise e
            
            if codigo_github:
                arquivos_count = len(codigo_github)
                total_chars = sum(len(content) for content in codigo_github.values())
                sample_files = list(codigo_github.keys())[:3]
                
                result["steps"].append({
                    "step": "3_github_reader",
                    "status": "✅ GitHub Reader funcionando",
                    "arquivos_encontrados": arquivos_count,
                    "total_caracteres": total_chars,
                    "arquivos_sample": sample_files
                })
            else:
                result["steps"].append({
                    "step": "3_github_reader",
                    "status": "⚠️ GitHub Reader retornou vazio"
                })
                
        except Exception as e:
            result["steps"].append({
                "step": "3_github_reader",
                "status": f"❌ Erro no GitHub Reader: {str(e)}"
            })
        
        # Teste 4: Testar OpenAI (se temos código)
        if len(result["steps"]) >= 3 and "arquivos_encontrados" in result["steps"][2]:
            try:
                # Usar uma amostra pequena para teste
                sample_code = "def hello(): return 'world'"
                
                resultado_llm = revisor_geral.executar_analise_llm(
                    tipo_analise='design',
                    codigo=sample_code,
                    analise_extra='Teste simples',
                    model_name='gpt-4',  # Tentar gpt-4 ao invés de gpt-4.1
                    max_token_out=200
                )
                
                result["steps"].append({
                    "step": "4_openai_test",
                    "status": "✅ OpenAI funcionando",
                    "resultado_tamanho": len(resultado_llm),
                    "resultado_preview": resultado_llm[:100] + "..." if len(resultado_llm) > 100 else resultado_llm
                })
                
            except Exception as e:
                result["steps"].append({
                    "step": "4_openai_test",
                    "status": f"❌ Erro na OpenAI: {str(e)}"
                })
        
        # Teste 5: Agente completo (se tudo funcionou)
        if all("✅" in step.get("status", "") for step in result["steps"]):
            try:
                resultado_agente = real_agent.agente_principal.main(
                    tipo_analise='design',
                    repositorio='rafsp/api-springboot-web-app',
                    instrucoes_extras='Teste completo integrado'
                )
                
                result["steps"].append({
                    "step": "5_agente_completo",
                    "status": "✅ Agente completo funcionando",
                    "resultado_tipo": str(type(resultado_agente)),
                    "resultado_preview": str(resultado_agente)[:200] + "..." if len(str(resultado_agente)) > 200 else str(resultado_agente)
                })
                
            except Exception as e:
                result["steps"].append({
                    "step": "5_agente_completo",
                    "status": f"❌ Erro no agente: {str(e)}"
                })
        
        return result
        
    except Exception as e:
        return {
            "error": f"Erro geral no teste: {str(e)}",
            "status": "failed"
        }

@app.get("/debug")
async def debug_info():
    """Informações detalhadas para debug com jobs ativos"""
    active_jobs = {job_id: job for job_id, job in jobs.items() 
                   if job['status'] not in ['completed', 'failed', 'rejected']}
    
    return {
        "sistema": {
            "diretorio_atual": current_dir,
            "agentes_disponiveis": AGENTES_DISPONVEIS,
            "credenciais": credentials_status
        },
        "agentes": real_agent.get_status(),
        "jobs": {
            "total": len(jobs),
            "ativos": len(active_jobs),
            "ultimos_5_jobs": list(jobs.keys())[-5:] if jobs else [],
            "jobs_ativos": list(active_jobs.keys()),
            "por_status": {
                status: len([j for j in jobs.values() if j['status'] == status])
                for status in set(j['status'] for j in jobs.values())
            } if jobs else {}
        },
        "arquivos": {
            "agente_revisor": os.path.exists(os.path.join(current_dir, 'agents', 'agente_revisor.py')),
            "github_reader": os.path.exists(os.path.join(current_dir, 'tools', 'github_reader.py')),
            "revisor_geral": os.path.exists(os.path.join(current_dir, 'tools', 'revisor_geral.py'))
        },
        "endpoints_disponiveis": [
            "GET /health - Status do sistema",
            "GET /jobs - Lista todos os jobs", 
            "GET /jobs/{job_id} - Detalhes de um job",
            "GET /jobs/{job_id}/report - Relatório de um job",
            "POST /start-analysis - Iniciar análise",
            "POST /update-job-status - Aprovar/rejeitar job"
        ]
    }

@app.get("/analysis-types")
async def get_analysis_types():
    """Tipos de análise disponíveis"""
    return {
        "available_types": list(ANALYSIS_TYPE_MAPPING.keys()),
        "type_mapping": ANALYSIS_TYPE_MAPPING,
        "agentes_status": real_agent.get_status(),
        "modo_operacao": "ANÁLISE REAL" if AGENTES_DISPONVEIS else "SIMULAÇÃO"
    }

# Endpoints de compatibilidade (placeholders)
@app.post("/upload-policy")
async def upload_policy():
    return {"id": str(uuid.uuid4()), "message": "Em desenvolvimento"}

@app.get("/policies")
async def get_policies():
    return []

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Iniciando Backend Agentes Peers - Versão Completa")
    print("=" * 60)
    print(f"📊 Status dos Agentes: {real_agent.get_status()}")
    print(f"🔗 Documentação: http://127.0.0.1:8000/docs")
    print(f"❤️  Health Check: http://127.0.0.1:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )