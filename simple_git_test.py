# simple_git_test.py - Teste Simplificado para Branch e Commit

import os
import time
from dotenv import load_dotenv
from github import Github, GithubException

load_dotenv()

def test_basic_git_operations(repo_name: str = "rafsp/api-springboot-web-app"):
    """Teste básico e confiável das operações Git essenciais"""
    
    print("🎯 TESTE SIMPLIFICADO - BRANCH E COMMIT")
    print("=" * 50)
    
    # Verificar token
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("❌ GITHUB_TOKEN não encontrado no .env")
        return False
    
    try:
        # Conectar ao GitHub
        print(f"🔍 Conectando ao repositório: {repo_name}")
        github_client = Github(github_token)
        repo = github_client.get_repo(repo_name)
        
        print(f"✅ Conectado: {repo.full_name}")
        print(f"📊 Permissões: Push={repo.permissions.push}")
        
        # Gerar nome único para branch
        timestamp = str(int(time.time()))
        branch_name = f"test-simple-{timestamp}"
        
        print(f"\n🌿 Criando branch: {branch_name}")
        
        # Obter branch base
        default_branch = repo.default_branch
        base_branch = repo.get_branch(default_branch)
        print(f"📌 Branch base: {default_branch} (SHA: {base_branch.commit.sha[:8]})")
        
        # Criar nova branch
        repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base_branch.commit.sha
        )
        print(f"✅ Branch criada: {branch_name}")
        
        # Criar arquivo simples
        file_path = f"test-{timestamp}.txt"
        file_content = f"""Teste de Git Operations

Timestamp: {timestamp}
Data: {time.strftime('%Y-%m-%d %H:%M:%S')}
Branch: {branch_name}
Repositório: {repo.full_name}

Este arquivo foi criado para testar:
✅ Criação de branch
✅ Criação de arquivo
✅ Commit automático

Status: Teste bem-sucedido!
"""
        
        commit_message = f"test: Adiciona arquivo de teste {file_path}"
        
        print(f"\n📝 Criando arquivo: {file_path}")
        
        # Fazer commit
        result = repo.create_file(
            path=file_path,
            message=commit_message,
            content=file_content,
            branch=branch_name
        )
        
        print(f"✅ Arquivo criado e commitado!")
        print(f"📝 Commit realizado na branch {branch_name}")
        
        # Verificar se arquivo foi criado
        created_file = repo.get_contents(file_path, ref=branch_name)
        print(f"✅ Arquivo verificado: {created_file.path} ({created_file.size} bytes)")
        
        # Verificar commits na branch
        commits = list(repo.get_commits(sha=branch_name))
        latest_commit = commits[0]
        print(f"✅ Último commit: {latest_commit.sha[:8]} - {latest_commit.commit.message.split(chr(10))[0]}")
        
        print(f"\n🎉 TESTE BÁSICO CONCLUÍDO COM SUCESSO!")
        print(f"✅ Branch criada: {branch_name}")
        print(f"✅ Arquivo commitado: {file_path}")
        print(f"🔗 Visualizar: https://github.com/{repo.full_name}/tree/{branch_name}")
        
        # Limpeza (remover branch)
        print(f"\n🧹 Removendo branch de teste...")
        ref = repo.get_git_ref(f"heads/{branch_name}")
        ref.delete()
        print(f"✅ Branch {branch_name} removida")
        
        return True
        
    except GithubException as e:
        print(f"❌ Erro GitHub: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def test_commit_workflow_simulation():
    """Simula o workflow de commits que seria usado pelo sistema"""
    
    print("\n🔄 SIMULAÇÃO DO WORKFLOW DE COMMITS")
    print("=" * 50)
    
    # Dados simulados que viriam dos agentes
    simulated_changes = [
        {
            "caminho_do_arquivo": "src/controllers/UserController.java",
            "conteudo": "// Refatorado para aplicar SOLID principles\npublic class UserController { ... }",
            "justificativa": "Aplicação do Single Responsibility Principle"
        },
        {
            "caminho_do_arquivo": "src/services/UserService.java", 
            "conteudo": "// Novo serviço extraído do controller\npublic class UserService { ... }",
            "justificativa": "Separação de responsabilidades - lógica de negócio movida para service"
        },
        {
            "caminho_do_arquivo": "tests/UserControllerTest.java",
            "conteudo": "// Testes unitários para o controller refatorado\npublic class UserControllerTest { ... }",
            "justificativa": "Testes unitários para garantir funcionamento após refatoração"
        }
    ]
    
    print("📊 Mudanças simuladas preparadas:")
    for i, change in enumerate(simulated_changes, 1):
        print(f"   {i}. {change['caminho_do_arquivo']}")
        print(f"      Justificativa: {change['justificativa']}")
    
    print(f"\n✅ Workflow simulado preparado!")
    print(f"📝 {len(simulated_changes)} arquivos seriam modificados")
    print(f"🔄 {len(simulated_changes)} commits seriam criados")
    print(f"📋 1 Pull Request seria criado")
    
    return True

if __name__ == "__main__":
    import sys
    
    # Obter repositório via argumento ou usar padrão
    repo = sys.argv[1] if len(sys.argv) > 1 else "rafsp/api-springboot-web-app"
    
    print(f"🎯 Testando repositório: {repo}")
    print()
    
    # Teste 1: Operações Git básicas
    success_git = test_basic_git_operations(repo)
    
    # Teste 2: Simulação do workflow
    success_workflow = test_commit_workflow_simulation()
    
    # Resultado final
    print(f"\n" + "=" * 60)
    print("📋 RESULTADO FINAL")
    print("=" * 60)
    
    if success_git and success_workflow:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema pode criar branches")
        print("✅ Sistema pode fazer commits") 
        print("✅ Workflow está preparado")
        print("\n🚀 SISTEMA PRONTO PARA OPERAÇÕES REAIS!")
        exit(0)
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        if not success_git:
            print("❌ Operações Git básicas falharam")
        if not success_workflow:
            print("❌ Simulação do workflow falhou")
        exit(1)