import re
import os
from github import Github
from github.Auth import Token
from dotenv import load_dotenv
from typing import Dict, List, Optional

# Carregar variáveis de ambiente
load_dotenv()

def conection(repositorio: str) -> "Repository":
    """
    Estabelece conexão com o GitHub usando token de acesso
    
    Args:
        repositorio: Nome do repositório no formato "usuario/repo"
    
    Returns:
        Objeto Repository do PyGithub
    """
    # Obter token do GitHub das variáveis de ambiente
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    if not GITHUB_TOKEN:
        GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    
    if not GITHUB_TOKEN:
        raise ValueError(
            "❌ Token do GitHub não encontrado!\n"
            "Configure a variável de ambiente GITHUB_TOKEN ou adicione no arquivo .env:\n"
            "GITHUB_TOKEN=seu_token_aqui\n\n"
            "Para gerar um token: https://github.com/settings/personal-access-tokens/tokens"
        )
    
    try:
        auth = Token(GITHUB_TOKEN)
        g = Github(auth=auth)
        repo = g.get_repo(repositorio)
        
        print(f"✅ Conectado ao repositório: {repositorio}")
        print(f"📊 Repositório: {repo.full_name} | Estrelas: {repo.stargazers_count} | Forks: {repo.forks_count}")
        
        return repo
    except Exception as e:
        raise RuntimeError(f"Erro ao conectar com o repositório '{repositorio}': {str(e)}")

# Mapeamento atualizado de tipos de análise para extensões
MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars", ".tfstate"],
    "python": [".py", ".pyw", ".pyi"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
    "design": [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cs", ".go", ".rs"],  # Análise geral
    "pentest": [".py", ".js", ".ts", ".php", ".java", ".cs", ".go"],  # Foco em segurança
    "seguranca": [".py", ".js", ".ts", ".php", ".java", ".cs", ".go", ".sql", ".xml", ".json"],  # Segurança ampla
}

def _leitura_recursiva_com_debug(repo, extensoes: Optional[List[str]], path: str = "", arquivos_do_repo: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Lê recursivamente todos os arquivos de um repositório GitHub
    
    Args:
        repo: Objeto Repository do PyGithub
        extensoes: Lista de extensões de arquivo para filtrar (None = todos os arquivos)
        path: Caminho atual (para recursão)
        arquivos_do_repo: Dicionário acumulador de arquivos
    
    Returns:
        Dicionário com caminho do arquivo como chave e conteúdo como valor
    """
    if arquivos_do_repo is None:
        arquivos_do_repo = {}

    try:
        print(f"🔍 Explorando diretório: {path or 'raiz'}")
        conteudos = repo.get_contents(path)
        
        # Contadores para estatísticas
        dirs_found = 0
        files_found = 0
        files_read = 0
        files_skipped = 0

        for conteudo in conteudos:
            if conteudo.type == "dir":
                dirs_found += 1
                # Recursão para subdiretórios
                _leitura_recursiva_com_debug(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                files_found += 1
                
                # Determinar se deve ler o arquivo
                deve_ler_arquivo = False
                
                if extensoes is None:
                    # Ler todos os arquivos se não houver filtro
                    deve_ler_arquivo = True
                else:
                    # Verificar extensão ou nome exato
                    for ext in extensoes:
                        if conteudo.path.endswith(ext) or conteudo.name == ext:
                            deve_ler_arquivo = True
                            break
                
                if deve_ler_arquivo:
                    try:
                        # Verificar tamanho do arquivo (evitar arquivos muito grandes)
                        if conteudo.size > 1024 * 1024:  # 1MB
                            print(f"⚠️ Arquivo muito grande ignorado: {conteudo.path} ({conteudo.size} bytes)")
                            files_skipped += 1
                            continue
                        
                        # Tentar decodificar o conteúdo
                        codigo = conteudo.decoded_content.decode('utf-8')
                        arquivos_do_repo[conteudo.path] = codigo
                        files_read += 1
                        
                        print(f"✅ Lido: {conteudo.path} ({len(codigo)} chars)")
                        
                    except UnicodeDecodeError:
                        print(f"⚠️ Erro de codificação ignorado: {conteudo.path}")
                        files_skipped += 1
                    except Exception as e:
                        print(f"❌ Erro ao ler '{conteudo.path}': {e}")
                        files_skipped += 1
                else:
                    files_skipped += 1
        
        # Log de estatísticas do diretório atual
        if path == "":  # Apenas no diretório raiz
            print(f"📊 Estatísticas finais:")
            print(f"   📁 Diretórios encontrados: {dirs_found}")
            print(f"   📄 Arquivos encontrados: {files_found}")
            print(f"   ✅ Arquivos lidos: {files_read}")
            print(f"   ⏭️ Arquivos ignorados: {files_skipped}")

    except Exception as e:
        print(f"❌ Erro ao explorar '{path}': {e}")
        
    return arquivos_do_repo

def main(repo: str, tipo_de_analise: str) -> Dict[str, str]:
    """
    Função principal para ler arquivos de um repositório GitHub
    
    Args:
        repo: Nome do repositório no formato "usuario/repo"
        tipo_de_analise: Tipo de análise para filtrar arquivos
    
    Returns:
        Dicionário com arquivos lidos (caminho -> conteúdo)
    """
    print(f"🚀 Iniciando leitura do repositório: {repo}")
    print(f"🎯 Tipo de análise: {tipo_de_analise}")
    
    try:
        # Conectar ao repositório
        repositorio_final = conection(repositorio=repo)
        
        # Obter extensões para o tipo de análise
        extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())
        
        if extensoes_alvo:
            print(f"🔍 Filtrando por extensões: {extensoes_alvo}")
        else:
            print(f"⚠️ Tipo de análise '{tipo_de_analise}' não reconhecido. Lendo todos os arquivos.")
            extensoes_alvo = None
        
        # Ler arquivos recursivamente
        arquivos_encontrados = _leitura_recursiva_com_debug(
            repositorio_final, 
            extensoes=extensoes_alvo
        )
        
        print(f"✅ Leitura concluída! {len(arquivos_encontrados)} arquivos processados.")
        
        if not arquivos_encontrados:
            print("⚠️ Nenhum arquivo foi encontrado com os critérios especificados.")
            print("💡 Verifique se o repositório contém arquivos do tipo esperado.")
        
        return arquivos_encontrados
        
    except Exception as e:
        error_msg = f"Falha ao ler repositório '{repo}': {str(e)}"
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg) from e

def listar_repositorios_usuario(usuario: str, limite: int = 10) -> List[str]:
    """
    Lista repositórios públicos de um usuário (útil para testes)
    
    Args:
        usuario: Nome do usuário GitHub
        limite: Número máximo de repositórios para listar
    
    Returns:
        Lista de nomes de repositórios no formato "usuario/repo"
    """
    try:
        GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
        if GITHUB_TOKEN:
            auth = Token(GITHUB_TOKEN)
            g = Github(auth=auth)
        else:
            g = Github()  # Sem autenticação (rate limit menor)
        
        user = g.get_user(usuario)
        repos = user.get_repos(type='public', sort='updated')
        
        repo_list = []
        for i, repo in enumerate(repos):
            if i >= limite:
                break
            repo_list.append(repo.full_name)
        
        return repo_list
        
    except Exception as e:
        print(f"❌ Erro ao listar repositórios: {e}")
        return []

def testar_conexao() -> bool:
    """
    Testa a conexão com a API do GitHub
    
    Returns:
        True se a conexão estiver funcionando
    """
    try:
        print("🧪 Testando conexão com GitHub...")
        
        GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
        if GITHUB_TOKEN:
            auth = Token(GITHUB_TOKEN)
            g = Github(auth=auth)
            user = g.get_user()
            print(f"✅ Conectado como: {user.login}")
            print(f"📊 Rate limit: {g.get_rate_limit().core.remaining}/{g.get_rate_limit().core.limit}")
        else:
            g = Github()
            print("⚠️ Usando acesso sem token (rate limit limitado)")
            print(f"📊 Rate limit: {g.get_rate_limit().core.remaining}/{g.get_rate_limit().core.limit}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

if __name__ == "__main__":
    # Teste básico quando executado diretamente
    print("🚀 Testando GitHub Reader...")
    
    if testar_conexao():
        print("✅ Conexão funcionando!")
        
        # Exemplo de uso
        print("\n📋 Tipos de análise disponíveis:")
        for tipo, exts in MAPEAMENTO_TIPO_EXTENSOES.items():
            print(f"  • {tipo}: {exts}")
        
        # Teste com repositório público pequeno (opcional)
        # arquivos = main("octocat/Hello-World", "python")
        # print(f"Arquivos encontrados: {list(arquivos.keys())}")
        
    else:
        print("❌ Problemas na configuração do GitHub.")
        print("💡 Configure GITHUB_TOKEN nas variáveis de ambiente.")