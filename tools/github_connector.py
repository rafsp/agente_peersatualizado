# tools/github_connector.py - VERSÃO SEM GOOGLE COLAB
import os
from github import Github
from github.Auth import Token

def get_github_token():
    """Obtém token do GitHub apenas de variáveis de ambiente"""
    # Tenta múltiplas variáveis de ambiente
    token = (
        os.getenv('GITHUB_TOKEN') or 
        os.getenv('github_token') or 
        os.getenv('GH_TOKEN') or
        os.getenv('GITHUB_ACCESS_TOKEN')
    )
    
    if not token:
        raise ValueError(
            "❌ Token do GitHub não encontrado!\n"
            "📝 Configure uma das seguintes variáveis de ambiente:\n"
            "   - GITHUB_TOKEN=seu_token_aqui\n"
            "   - github_token=seu_token_aqui\n"
            "   - GH_TOKEN=seu_token_aqui\n"
            "\n💡 Adicione no arquivo .env:\n"
            "   GITHUB_TOKEN=ghp_seu_token_aqui\n"
            "\n🔗 Para criar um token: https://github.com/settings/tokens"
        )
    
    print("✅ Token GitHub encontrado nas variáveis de ambiente")
    return token

def connection(repositorio: str):
    """Conecta ao repositório GitHub"""
    try:
        print(f"🔗 Conectando ao GitHub para repositório: {repositorio}")
        GITHUB_TOKEN = get_github_token()
        auth = Token(GITHUB_TOKEN)
        g = Github(auth=auth)
        repo = g.get_repo(repositorio)
        print(f"✅ Conectado com sucesso ao repositório: {repo.full_name}")
        return repo
    except Exception as e:
        print(f"❌ Erro ao conectar ao repositório '{repositorio}': {e}")
        raise