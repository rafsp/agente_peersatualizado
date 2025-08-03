import os
from github import Github
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

def get_github_client():
    """Inicializa cliente GitHub"""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise ValueError("GITHUB_TOKEN não encontrado no .env")
    return Github(token)

def get_file_extensions_by_analysis(tipo_de_analise: str) -> List[str]:
    """Define extensões de arquivo por tipo de análise"""
    extensoes = {
        'design': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.jsx', '.tsx'],
        'pentest': ['.py', '.js', '.ts', '.php', '.java', '.config', '.yml', '.yaml', '.json', '.xml'],
        'seguranca': ['.py', '.js', '.ts', '.php', '.java', '.config', '.yml', '.yaml', '.dockerfile', '.env.example'],
        'terraform': ['.tf', '.tfvars', '.hcl', '.tfstate'],
        'refatoracao': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.jsx', '.tsx'],
        'escrever_testes': ['.py', '.js', '.ts', '.java', '.test.js', '.spec.js', '.test.py'],
        'agrupamento_design': ['.py', '.js', '.ts', '.java', '.cpp', '.cs'],
        'agrupamento_testes': ['.py', '.js', '.ts', '.java', '.test.js', '.spec.js']
    }
    return extensoes.get(tipo_de_analise, ['.py', '.js', '.ts'])

def should_skip_file(file_path: str) -> bool:
    """Verifica se arquivo deve ser ignorado"""
    skip_patterns = [
        'node_modules/', 'venv/', 'env/', '__pycache__/', '.git/',
        'build/', 'dist/', 'target/', '.idea/', '.vscode/',
        'coverage/', '.nyc_output/', '.pytest_cache/',
        'package-lock.json', 'yarn.lock', '.gitignore',
        '.env', '.env.local', '.env.production'
    ]
    
    file_path_lower = file_path.lower()
    return any(pattern in file_path_lower for pattern in skip_patterns)

def _leitura_recursiva_com_debug(repo, path: str, extensoes: List[str], max_files: int = 50, current_count: int = 0) -> Dict[str, str]:
    """Lê arquivos recursivamente do repositório"""
    arquivos_lidos = {}
    
    if current_count >= max_files:
        print(f"⚠️ Limite de {max_files} arquivos atingido")
        return arquivos_lidos
    
    try:
        print(f"📂 Explorando diretório: {path}")
        contents = repo.get_contents(path)
        
        if not isinstance(contents, list):
            contents = [contents]
            
        # Ordenar conteúdos: arquivos primeiro, depois diretórios
        files = [c for c in contents if c.type == "file"]
        dirs = [c for c in contents if c.type == "dir"]
        
        # Processar arquivos primeiro
        for content in files:
            if len(arquivos_lidos) + current_count >= max_files:
                break
                
            # Verificar se deve pular arquivo
            if should_skip_file(content.path):
                continue
                
            # Verificar extensão
            if any(content.name.endswith(ext) for ext in extensoes):
                try:
                    # Verificar tamanho do arquivo (limite de 1MB)
                    if content.size > 1024 * 1024:  # 1MB
                        print(f"⚠️ Arquivo muito grande ignorado: {content.path} ({content.size} bytes)")
                        continue
                        
                    arquivo_conteudo = content.decoded_content.decode('utf-8')
                    arquivos_lidos[content.path] = arquivo_conteudo
                    print(f"✅ Lido: {content.path} ({content.size} bytes)")
                    
                except UnicodeDecodeError:
                    print(f"⚠️ Erro de encoding ignorado: {content.path}")
                except Exception as e:
                    print(f"⚠️ Erro ao ler {content.path}: {e}")
        
        # Processar diretórios recursivamente
        for content in dirs:
            if len(arquivos_lidos) + current_count >= max_files:
                break
                
            # Verificar se deve pular diretório
            if should_skip_file(content.path + '/'):
                continue
                
            try:
                sub_arquivos = _leitura_recursiva_com_debug(
                    repo, 
                    content.path, 
                    extensoes, 
                    max_files, 
                    current_count + len(arquivos_lidos)
                )
                arquivos_lidos.update(sub_arquivos)
            except Exception as e:
                print(f"⚠️ Erro ao acessar diretório {content.path}: {e}")
                        
    except Exception as e:
        print(f"❌ Erro ao acessar {path}: {e}")
        
    return arquivos_lidos

def main(repo: str, tipo_de_analise: str, branch: str = "main") -> Dict[str, str]:
    """Função principal para leitura do repositório"""
    try:
        print(f"🔍 Iniciando leitura do repositório: {repo}")
        print(f"📂 Tipo de análise: {tipo_de_analise}")
        print(f"🌿 Branch: {branch}")
        
        # Obter cliente GitHub
        github_client = get_github_client()
        
        # Obter repositório
        try:
            repository = github_client.get_repo(repo)
            print(f"✅ Repositório encontrado: {repository.full_name}")
        except Exception as e:
            print(f"❌ Erro ao acessar repositório {repo}: {e}")
            raise ValueError(f"Repositório {repo} não encontrado ou sem acesso")
        
        # Verificar se branch existe
        try:
            if branch != "main":
                repository.get_branch(branch)
                print(f"✅ Branch '{branch}' encontrada")
        except Exception:
            print(f"⚠️ Branch '{branch}' não encontrada, usando branch padrão")
            branch = repository.default_branch
            print(f"🌿 Usando branch padrão: {branch}")
        
        # Obter extensões de arquivo
        extensoes = get_file_extensions_by_analysis(tipo_de_analise)
        print(f"📝 Extensões a serem lidas: {extensoes}")
        
        # Ler arquivos
        print("📖 Iniciando leitura de arquivos...")
        arquivos = _leitura_recursiva_com_debug(repository, "", extensoes, max_files=50)
        
        if not arquivos:
            print("⚠️ Nenhum arquivo encontrado com as extensões especificadas")
            # Tentar com extensões mais básicas
            extensoes_basicas = ['.py', '.js', '.ts', '.java']
            print(f"🔄 Tentando novamente com extensões básicas: {extensoes_basicas}")
            arquivos = _leitura_recursiva_com_debug(repository, "", extensoes_basicas, max_files=20)
        
        print(f"📊 Total de arquivos lidos: {len(arquivos)}")
        
        if arquivos:
            print("📋 Arquivos processados:")
            for arquivo in list(arquivos.keys())[:10]:  # Mostrar apenas os primeiros 10
                print(f"   - {arquivo}")
            if len(arquivos) > 10:
                print(f"   ... e mais {len(arquivos) - 10} arquivos")
        else:
            raise ValueError(f"Nenhum arquivo de código encontrado no repositório {repo}")
        
        return arquivos
        
    except Exception as e:
        print(f"❌ Erro na leitura do repositório: {e}")
        raise

# Função para compatibilidade com diferentes chamadas
def ler_repositorio(repo: str, tipo_analise: str = "design", branch: str = "main") -> Dict[str, str]:
    """Função alternativa para compatibilidade"""
    return main(repo, tipo_analise, branch)