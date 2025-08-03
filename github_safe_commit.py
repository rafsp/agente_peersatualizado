# github_safe_commit.py - Função segura para commit
import json
from github import GithubException
from typing import Dict, Any, Optional

def safe_commit_to_github(
    job_id: str,
    repo_name: str,
    branch_name: Optional[str],
    dados_agrupados: Dict[str, Any],
    job_info: Dict[str, Any]
) -> bool:
    """
    Função segura para fazer commit no GitHub com tratamento de erros robusto.
    
    Returns:
        bool: True se commit foi bem-sucedido, False se houve erro mas job deve continuar
    """
    try:
        print(f"[{job_id}] 🔍 Validando acesso ao repositório {repo_name}...")
        
        # Importar dentro da função para evitar problemas de dependência
        try:
            from tools import github_connector, commit_multiplas_branchs
        except ImportError as e:
            print(f"[{job_id}] ❌ Módulos GitHub não disponíveis: {e}")
            job_info['status'] = 'completed'
            job_info['message'] = 'Análise concluída. Módulos GitHub não disponíveis para commit.'
            job_info['error_details'] = f'Import Error: {str(e)}'
            return False
        
        # Validação rápida de acesso ao repositório
        try:
            print(f"[{job_id}] 📋 Testando conexão com {repo_name}...")
            repo = github_connector.connection(repositorio=repo_name)
            
            # Verificar se conseguimos acessar o repositório
            repo_info = repo.get_repo()
            print(f"[{job_id}] ✅ Repositório acessível: {repo_info.full_name}")
            
            # Verificar se a branch existe
            branch_to_check = branch_name or 'main'
            try:
                ref = repo.get_git_ref(f"heads/{branch_to_check}")
                print(f"[{job_id}] ✅ Branch '{branch_to_check}' encontrada")
            except GithubException as branch_error:
                if "404" in str(branch_error):
                    print(f"[{job_id}] ⚠️ Branch '{branch_to_check}' não encontrada, tentando 'master'...")
                    try:
                        ref = repo.get_git_ref("heads/master")
                        print(f"[{job_id}] ✅ Branch 'master' encontrada")
                    except GithubException:
                        print(f"[{job_id}] ❌ Nem 'main' nem 'master' encontradas")
                        job_info['status'] = 'completed'
                        job_info['message'] = f'Análise concluída. Branch {branch_to_check} não encontrada no repositório.'
                        job_info['error_details'] = f'Branch Error: {str(branch_error)}'
                        return False
                else:
                    raise branch_error
                    
        except GithubException as github_error:
            error_code = getattr(github_error, 'status', 0)
            error_msg = str(github_error)
            
            print(f"[{job_id}] ❌ Erro GitHub ({error_code}): {error_msg}")
            
            if error_code == 404:
                job_info['status'] = 'completed'
                job_info['message'] = f'Análise concluída. Repositório {repo_name} não encontrado ou sem acesso de leitura.'
                job_info['error_details'] = f'GitHub 404: {error_msg}'
                return False
            elif error_code == 403:
                job_info['status'] = 'completed'
                job_info['message'] = f'Análise concluída. Token do GitHub sem permissões para acessar {repo_name}.'
                job_info['error_details'] = f'GitHub 403: {error_msg}'
                return False
            else:
                # Para outros erros, tentar continuar mas reportar o problema
                print(f"[{job_id}] ⚠️ Erro inesperado do GitHub, continuando sem commit...")
                job_info['status'] = 'completed'
                job_info['message'] = f'Análise concluída. Erro inesperado do GitHub durante validação.'
                job_info['error_details'] = f'GitHub Error {error_code}: {error_msg}'
                return False
                
        except Exception as validation_error:
            print(f"[{job_id}] ❌ Erro na validação: {validation_error}")
            job_info['status'] = 'completed'
            job_info['message'] = 'Análise concluída. Erro durante validação do repositório.'
            job_info['error_details'] = f'Validation Error: {str(validation_error)}'
            return False
        
        # Se chegou aqui, a validação passou - tentar o commit
        print(f"[{job_id}] 🚀 Iniciando commit para GitHub...")
        
        try:
            commit_multiplas_branchs.processar_e_subir_mudancas_agrupadas(
                nome_repo=repo_name,
                dados_agrupados=dados_agrupados
            )
            
            print(f"[{job_id}] ✅ Commit realizado com sucesso!")
            job_info['status'] = 'completed'
            job_info['message'] = 'Análise concluída e mudanças enviadas para GitHub com sucesso!'
            return True
            
        except GithubException as commit_error:
            error_code = getattr(commit_error, 'status', 0)
            error_msg = str(commit_error)
            
            print(f"[{job_id}] ❌ Erro durante commit ({error_code}): {error_msg}")
            
            if error_code == 404:
                job_info['status'] = 'completed'
                job_info['message'] = 'Análise concluída. Erro 404 durante commit - branch ou repositório não encontrado.'
                job_info['error_details'] = f'Commit 404: {error_msg}'
            elif error_code == 403:
                job_info['status'] = 'completed'
                job_info['message'] = 'Análise concluída. Sem permissão de escrita no repositório.'
                job_info['error_details'] = f'Commit 403: {error_msg}'
            elif error_code == 422:
                job_info['status'] = 'completed'
                job_info['message'] = 'Análise concluída. Erro de validação durante commit (possivelmente PR já existe).'
                job_info['error_details'] = f'Commit 422: {error_msg}'
            else:
                job_info['status'] = 'completed'
                job_info['message'] = f'Análise concluída. Erro durante commit ao GitHub.'
                job_info['error_details'] = f'Commit Error {error_code}: {error_msg}'
            
            return False
            
        except Exception as general_commit_error:
            print(f"[{job_id}] ❌ Erro geral durante commit: {general_commit_error}")
            job_info['status'] = 'completed'
            job_info['message'] = 'Análise concluída. Erro inesperado durante commit.'
            job_info['error_details'] = f'General Commit Error: {str(general_commit_error)}'
            return False
            
    except Exception as unexpected_error:
        print(f"[{job_id}] ❌ Erro inesperado na função de commit: {unexpected_error}")
        job_info['status'] = 'failed'
        job_info['message'] = 'Erro inesperado durante processamento de commit.'
        job_info['error_details'] = f'Unexpected Error: {str(unexpected_error)}'
        return False

def validate_github_repository(repo_name: str, branch_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Valida se um repositório GitHub está acessível.
    
    Returns:
        Dict com success (bool), error (str), e detalhes adicionais
    """
    try:
        from tools import github_connector
        
        repo = github_connector.connection(repositorio=repo_name)
        repo_info = repo.get_repo()
        
        # Verificar branch
        branch_to_check = branch_name or 'main'
        try:
            ref = repo.get_git_ref(f"heads/{branch_to_check}")
            branch_exists = True
            actual_branch = branch_to_check
        except GithubException:
            try:
                ref = repo.get_git_ref("heads/master")
                branch_exists = True
                actual_branch = 'master'
            except GithubException:
                branch_exists = False
                actual_branch = None
        
        return {
            "success": True,
            "repo_name": repo_info.full_name,
            "branch_name": actual_branch,
            "branch_exists": branch_exists,
            "default_branch": repo_info.default_branch,
            "private": repo_info.private,
            "permissions": {
                "read": True,  # Se chegamos aqui, temos pelo menos leitura
                "write": repo_info.permissions.push if hasattr(repo_info.permissions, 'push') else None
            }
        }
        
    except GithubException as e:
        error_code = getattr(e, 'status', 0)
        return {
            "success": False,
            "error_code": error_code,
            "error": str(e),
            "repo_name": repo_name,
            "branch_name": branch_name
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "repo_name": repo_name,
            "branch_name": branch_name
        }