# test_github_commit.py - CRIAR ESTE ARQUIVO PARA TESTAR
"""
Script para testar se a integração com GitHub está funcionando.
Execute: python test_github_commit.py
"""

from tools import commit_multiplas_branchs

def test_simple_github_commit():
    """Testa commit simples no GitHub"""
    
    # Dados de teste mínimos
    test_data = {
        "resumo_geral": "Teste de commit automático",
        "grupos": [
            {
                "branch_sugerida": "test/automated-commit",
                "titulo_pr": "Teste de Commit Automático",
                "resumo_do_pr": "Este é um teste para verificar se o sistema consegue fazer commits no GitHub.",
                "conjunto_de_mudancas": [
                    {
                        "caminho_do_arquivo": "TEST_AUTOMATION.md",
                        "status": "CRIADO",
                        "conteudo": """# Teste de Automação

Este arquivo foi criado automaticamente pelo sistema de agentes.

## Data e Hora
Teste executado em: $(date)

## Objetivo
Verificar se o sistema consegue:
- ✅ Conectar ao GitHub
- ✅ Criar uma nova branch
- ✅ Fazer commit de arquivos
- ✅ Criar Pull Request

## Status
Se você está vendo este arquivo, o teste foi bem-sucedido!
""",
                        "justificativa": "Arquivo de teste criado para verificar a funcionalidade de commit automático."
                    }
                ]
            }
        ]
    }
    
    repo_name = "rafsp/Aula3103_CSHARP"  # Use o mesmo repo que estava testando
    
    print("🧪 Iniciando teste de commit no GitHub...")
    print(f"📁 Repositório: {repo_name}")
    print(f"🌿 Branch: {test_data['grupos'][0]['branch_sugerida']}")
    print(f"📄 Arquivo: {test_data['grupos'][0]['conjunto_de_mudancas'][0]['caminho_do_arquivo']}")
    
    try:
        commit_multiplas_branchs.processar_e_subir_mudancas_agrupadas(
            nome_repo=repo_name,
            dados_agrupados=test_data
        )
        print("✅ Teste concluído! Verifique seu GitHub.")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_github_commit()