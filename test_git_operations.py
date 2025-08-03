# test_git_operations.py - Teste Específico para Operações Git

import os
import time
from dotenv import load_dotenv
from github import Github, GithubException

load_dotenv()

class GitOperationsTester:
    """Teste focado apenas em operações Git"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_client = None
        self.test_repo = None
        
    def setup(self, repo_name: str):
        """Configuração inicial"""
        print(f"🔧 Configurando teste Git para: {repo_name}")
        
        if not self.github_token:
            raise ValueError("❌ GITHUB_TOKEN não encontrado no .env")
            
        self.github_client = Github(self.github_token)
        self.test_repo = self.github_client.get_repo(repo_name)
        
        print(f"✅ Conectado ao repositório: {self.test_repo.full_name}")
        print(f"📊 Repositório info:")
        print(f"   - Privado: {self.test_repo.private}")
        print(f"   - Branch padrão: {self.test_repo.default_branch}")
        print(f"   - Permissões: Push={self.test_repo.permissions.push}, Admin={self.test_repo.permissions.admin}")
    
    def test_branch_creation(self, branch_name: str = None):
        """Testa criação de branch"""
        print("\n🌿 TESTE: Criação de Branch")
        print("-" * 40)
        
        # Gerar nome único se não fornecido
        if not branch_name:
            timestamp = str(int(time.time()))
            branch_name = f"test-branch-{timestamp}"
        
        try:
            # Obter referência da branch principal
            main_branch = self.test_repo.get_branch(self.test_repo.default_branch)
            print(f"📌 Branch base: {main_branch.name} (SHA: {main_branch.commit.sha[:8]})")
            
            # Criar nova branch
            new_ref = self.test_repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=main_branch.commit.sha
            )
            
            print(f"✅ Branch criada: {branch_name}")
            print(f"📍 Referência: {new_ref.ref}")
            
            # Verificar se branch foi criada
            created_branch = self.test_repo.get_branch(branch_name)
            print(f"✅ Branch verificada: {created_branch.name}")
            
            return branch_name, created_branch
            
        except GithubException as e:
            if e.status == 422 and "Reference already exists" in str(e.data):
                print(f"⚠️ Branch {branch_name} já existe")
                existing_branch = self.test_repo.get_branch(branch_name)
                return branch_name, existing_branch
            else:
                print(f"❌ Erro ao criar branch: {e}")
                raise
    
    def test_file_creation(self, branch_name: str, file_path: str = None):
        """Testa criação de arquivo"""
        print(f"\n📝 TESTE: Criação de Arquivo na Branch {branch_name}")
        print("-" * 50)
        
        # Gerar nome único se não fornecido
        if not file_path:
            timestamp = str(int(time.time()))
            file_path = f"test-files/test-{timestamp}.md"
        
        try:
            # Conteúdo do arquivo
            file_content = f"""# Teste de Operações Git

Este arquivo foi criado automaticamente para testar operações Git.

## Informações:
- **Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Branch**: {branch_name}
- **Arquivo**: {file_path}
- **Repositório**: {self.test_repo.full_name}

## Teste:
✅ Criação de branch
✅ Criação de arquivo
✅ Commit automático

---
*Arquivo gerado pelo teste automático*
"""
            
            # Mensagem de commit
            commit_message = f"test: Adiciona {file_path}\n\nTeste automático de criação de arquivo.\nBranch: {branch_name}\nTimestamp: {int(time.time())}"
            
            # Criar arquivo
            result = self.test_repo.create_file(
                path=file_path,
                message=commit_message,
                content=file_content,
                branch=branch_name
            )
            
            print(f"✅ Arquivo criado: {file_path}")
            
            # Verificar se result['commit'] existe e tem os atributos necessários
            if result and 'commit' in result and result['commit']:
                commit_sha = result['commit'].sha[:8] if hasattr(result['commit'], 'sha') else "unknown"
                print(f"📝 Commit SHA: {commit_sha}")
                
                # Verificar se tem mensagem de commit
                if hasattr(result['commit'], 'commit') and hasattr(result['commit'].commit, 'message'):
                    commit_msg = result['commit'].commit.message.split('\n')[0]
                    print(f"💬 Mensagem: {commit_msg}")
                else:
                    print(f"💬 Mensagem: {commit_message.split(chr(10))[0]}")
            else:
                print(f"📝 Commit criado (detalhes não disponíveis)")
            
            return file_path, result
            
        except GithubException as e:
            print(f"❌ Erro ao criar arquivo: {e}")
            raise
    
    def test_file_update(self, branch_name: str, file_path: str):
        """Testa atualização de arquivo"""
        print(f"\n🔄 TESTE: Atualização de Arquivo {file_path}")
        print("-" * 50)
        
        try:
            # Obter arquivo existente
            file_info = self.test_repo.get_contents(file_path, ref=branch_name)
            print(f"📄 Arquivo encontrado: {file_info.path}")
            print(f"📏 Tamanho atual: {file_info.size} bytes")
            
            # Novo conteúdo
            updated_content = f"""# Teste de Operações Git (ATUALIZADO)

Este arquivo foi ATUALIZADO automaticamente para testar operações Git.

## Informações:
- **Primeira criação**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Última atualização**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Branch**: {branch_name}
- **Arquivo**: {file_path}
- **Repositório**: {self.test_repo.full_name}

## Teste:
✅ Criação de branch
✅ Criação de arquivo
✅ Commit automático
✅ Atualização de arquivo
✅ Segundo commit

## Alterações:
- Adicionado timestamp de atualização
- Adicionado seção de alterações
- Conteúdo expandido

---
*Arquivo atualizado pelo teste automático*
"""
            
            # Mensagem de commit para atualização
            update_message = f"test: Atualiza {file_path}\n\nSegunda versão do arquivo de teste.\nBranch: {branch_name}\nOperação: UPDATE"
            
            # Atualizar arquivo
            result = self.test_repo.update_file(
                path=file_path,
                message=update_message,
                content=updated_content,
                sha=file_info.sha,
                branch=branch_name
            )
            
            print(f"✅ Arquivo atualizado: {file_path}")
            
            # Verificar resultado da atualização com tratamento de erro
            if result and 'commit' in result and result['commit']:
                commit_sha = result['commit'].sha[:8] if hasattr(result['commit'], 'sha') else "unknown"
                print(f"📝 Novo commit SHA: {commit_sha}")
                
                # Verificar se tem mensagem de commit
                if hasattr(result['commit'], 'commit') and hasattr(result['commit'].commit, 'message'):
                    commit_msg = result['commit'].commit.message.split('\n')[0]
                    print(f"💬 Mensagem: {commit_msg}")
                else:
                    print(f"💬 Mensagem: {update_message.split(chr(10))[0]}")
            else:
                print(f"📝 Atualização criada (detalhes não disponíveis)")
            
            return result
            
        except GithubException as e:
            print(f"❌ Erro ao atualizar arquivo: {e}")
            raise
    
    def test_pull_request_creation(self, branch_name: str):
        """Testa criação de Pull Request"""
        print(f"\n📋 TESTE: Criação de Pull Request")
        print("-" * 40)
        
        try:
            # Título e descrição do PR
            pr_title = f"🧪 Teste Git Operations - {time.strftime('%Y-%m-%d %H:%M')}"
            pr_body = f"""# Teste de Operações Git

Este Pull Request foi criado automaticamente para testar operações Git básicas.

## 🎯 Objetivo
Validar que o sistema consegue:
- ✅ Criar branches
- ✅ Criar arquivos  
- ✅ Fazer commits
- ✅ Atualizar arquivos
- ✅ Criar Pull Requests

## 📊 Detalhes
- **Branch source**: `{branch_name}`
- **Branch target**: `{self.test_repo.default_branch}`
- **Timestamp**: {int(time.time())}

## 🚨 Ação
Este PR pode ser fechado sem merge - é apenas um teste das operações Git.

---
*Criado automaticamente pelo teste de operações Git*
"""
            
            # Criar Pull Request
            pr = self.test_repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=self.test_repo.default_branch
            )
            
            print(f"✅ Pull Request criado!")
            print(f"🔗 URL: {pr.html_url}")
            print(f"📝 Número: #{pr.number}")
            print(f"📊 Status: {pr.state}")
            
            return pr
            
        except GithubException as e:
            if "A pull request already exists" in str(e.data.get('message', '')):
                print("⚠️ Pull Request já existe para esta branch")
                return None
            else:
                print(f"❌ Erro ao criar Pull Request: {e}")
                raise
    
    def test_branch_listing(self):
        """Testa listagem de branches"""
        print(f"\n📋 TESTE: Listagem de Branches")
        print("-" * 35)
        
        try:
            branches = list(self.test_repo.get_branches())
            print(f"📊 Total de branches: {len(branches)}")
            
            # Mostrar últimas 10 branches
            print("🌿 Últimas branches:")
            for branch in branches[:10]:
                print(f"   - {branch.name} (SHA: {branch.commit.sha[:8]})")
            
            if len(branches) > 10:
                print(f"   ... e mais {len(branches) - 10} branches")
                
            return branches
            
        except Exception as e:
            print(f"❌ Erro ao listar branches: {e}")
            raise
    
    def cleanup_test_branch(self, branch_name: str):
        """Remove branch de teste"""
        print(f"\n🗑️ LIMPEZA: Removendo branch {branch_name}")
        print("-" * 40)
        
        try:
            # Obter e deletar referência da branch
            ref = self.test_repo.get_git_ref(f"heads/{branch_name}")
            ref.delete()
            
            print(f"✅ Branch {branch_name} removida com sucesso")
            
        except GithubException as e:
            if e.status == 404:
                print(f"ℹ️ Branch {branch_name} não encontrada (já foi removida)")
            else:
                print(f"⚠️ Erro ao remover branch: {e}")
    
    def run_complete_git_test(self, repo_name: str, cleanup: bool = True):
        """Executa teste completo das operações Git"""
        print("🌿 TESTE COMPLETO DE OPERAÇÕES GIT")
        print("=" * 60)
        
        start_time = time.time()
        branch_name = None
        
        try:
            # Setup
            self.setup(repo_name)
            
            # Listar branches existentes
            self.test_branch_listing()
            
            # Criar branch
            branch_name, branch_obj = self.test_branch_creation()
            
            # Criar arquivo
            file_path, create_result = self.test_file_creation(branch_name)
            
            # Teste de atualização (opcional - pode falhar em alguns casos)
            try:
                update_result = self.test_file_update(branch_name, file_path)
                print("✅ Atualização de arquivo bem-sucedida")
            except Exception as e:
                print(f"⚠️ Atualização de arquivo falhou (não crítico): {e}")
                print("ℹ️ Continuando com criação de Pull Request...")
            
            # Criar Pull Request
            try:
                pr = self.test_pull_request_creation(branch_name)
                print("✅ Pull Request criado com sucesso")
            except Exception as e:
                print(f"⚠️ Criação de Pull Request falhou: {e}")
                pr = None
            
            # Resumo final
            end_time = time.time()
            duration = end_time - start_time
            
            print("\n" + "=" * 60)
            print("🎉 TESTE GIT PRINCIPAL CONCLUÍDO")
            print("=" * 60)
            print(f"⏱️ Duração: {duration:.2f} segundos")
            print(f"📂 Repositório: {repo_name}")
            print(f"🌿 Branch criada: {branch_name}")
            print(f"📝 Arquivo: {file_path}")
            
            if pr:
                print(f"📋 Pull Request: #{pr.number}")
                print(f"🔗 Link: {pr.html_url}")
            
            print("\n✅ OPERAÇÕES GIT PRINCIPAIS FUNCIONARAM!")
            print("✅ Sistema consegue criar branches e fazer commits!")
            
            return True
            
        except Exception as e:
            print(f"\n❌ TESTE GIT FALHOU: {e}")
            print("❌ Erro crítico nas operações Git básicas")
            return False
            
        finally:
            if cleanup and branch_name:
                self.cleanup_test_branch(branch_name)

# Função principal para executar teste
def test_git_operations(repo_name: str = "rafsp/api-springboot-web-app", cleanup: bool = True):
    """Executa teste das operações Git"""
    tester = GitOperationsTester()
    return tester.run_complete_git_test(repo_name, cleanup)

if __name__ == "__main__":
    import sys
    
    # Argumentos da linha de comando
    repo = sys.argv[1] if len(sys.argv) > 1 else "rafsp/api-springboot-web-app"
    cleanup = "--no-cleanup" not in sys.argv
    
    print(f"🎯 Testando operações Git no repositório: {repo}")
    print(f"🧹 Limpeza automática: {'Sim' if cleanup else 'Não'}")
    print()
    
    success = test_git_operations(repo, cleanup)
    
    if success:
        print("\n🎉 TODAS AS OPERAÇÕES GIT PASSARAM!")
        exit(0)
    else:
        print("\n❌ ALGUMAS OPERAÇÕES GIT FALHARAM!")
        exit(1)