import os
from github import Github
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import logging
from dataclasses import dataclass

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

@dataclass
class FileReadResult:
    """Resultado da leitura de arquivos"""
    files: Dict[str, str]
    total_files: int
    skipped_files: int
    errors: List[str]

class GitHubReaderConfig:
    """Configurações do GitHub Reader"""
    MAX_FILES = 50
    MAX_FILE_SIZE_MB = 1
    DEFAULT_BRANCH = "main"
    
    # Extensões por tipo de análise
    EXTENSIONS_MAP = {
        'design': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.jsx', '.tsx', '.ipynb'],
        'pentest': ['.py', '.js', '.ts', '.php', '.java', '.config', '.yml', '.yaml', '.json', '.xml', '.ipynb'],
        'seguranca': ['.py', '.js', '.ts', '.php', '.java', '.config', '.yml', '.yaml', '.dockerfile', '.env.example', '.ipynb'],
        'terraform': ['.tf', '.tfvars', '.hcl', '.tfstate'],
        'refatoracao': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.jsx', '.tsx', '.ipynb'],
        'escrever_testes': ['.py', '.js', '.ts', '.java', '.test.js', '.spec.js', '.test.py'],
        'agrupamento_design': ['.py', '.js', '.ts', '.java', '.cpp', '.cs', '.ipynb'],
        'agrupamento_testes': ['.py', '.js', '.ts', '.java', '.test.js', '.spec.js'],
        'relatorio_teste_unitario': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rb', '.php', '.cs', '.ipynb']
    }
    
    # Padrões de arquivos/diretórios a serem ignorados
    SKIP_PATTERNS = [
        'node_modules/', 'venv/', 'env/', '__pycache__/', '.git/',
        'build/', 'dist/', 'target/', '.idea/', '.vscode/',
        'coverage/', '.nyc_output/', '.pytest_cache/',
        'package-lock.json', 'yarn.lock', '.gitignore',
        '.env', '.env.local', '.env.production'
    ]

class GitHubReader:
    """Classe principal para leitura de repositórios GitHub"""
    
    def __init__(self, config: GitHubReaderConfig = None):
        self.config = config or GitHubReaderConfig()
        self._github_client = None
    
    def get_github_client(self) -> Github:
        """Inicializa cliente GitHub (lazy loading)"""
        if self._github_client is None:
            token = os.getenv('GITHUB_TOKEN')
            if not token:
                raise ValueError("GITHUB_TOKEN não encontrado no .env")
            self._github_client = Github(token)
            logger.info("✅ Cliente GitHub inicializado")
        return self._github_client

    def get_file_extensions_by_analysis(self, tipo_de_analise: str) -> List[str]:
        """Define extensões de arquivo por tipo de análise"""
        extensions = self.config.EXTENSIONS_MAP.get(tipo_de_analise.lower())
        if extensions is None:
            logger.warning(f"⚠️ Tipo de análise '{tipo_de_analise}' não encontrado, usando extensões padrão")
            return ['.py', '.js', '.ts']
        return extensions

    def should_skip_file(self, file_path: str) -> bool:
        """Verifica se arquivo deve ser ignorado"""
        file_path_lower = file_path.lower()
        return any(pattern in file_path_lower for pattern in self.config.SKIP_PATTERNS)

    def _read_file_content(self, content) -> Tuple[Optional[str], Optional[str]]:
        """Lê o conteúdo de um arquivo específico
        
        Returns:
            Tuple[conteudo, erro]: (conteúdo do arquivo ou None, mensagem de erro ou None)
        """
        try:
            # Verificar tamanho do arquivo
            max_size_bytes = self.config.MAX_FILE_SIZE_MB * 1024 * 1024
            if content.size > max_size_bytes:
                return None, f"Arquivo muito grande: {content.size} bytes (limite: {max_size_bytes})"
            
            arquivo_conteudo = content.decoded_content.decode('utf-8')
            logger.debug(f"✅ Lido: {content.path} ({content.size} bytes)")
            return arquivo_conteudo, None
            
        except UnicodeDecodeError:
            return None, f"Erro de encoding: {content.path}"
        except Exception as e:
            return None, f"Erro ao ler {content.path}: {str(e)}"

    def _read_directory_recursive(self, repo, path: str, extensoes: List[str], 
                                  result: FileReadResult, current_count: int = 0) -> None:
        """Lê arquivos recursivamente do repositório"""
        
        if current_count >= self.config.MAX_FILES:
            logger.warning(f"⚠️ Limite de {self.config.MAX_FILES} arquivos atingido")
            return
        
        try:
            logger.debug(f"📂 Explorando diretório: {path}")
            contents = repo.get_contents(path)
            
            if not isinstance(contents, list):
                contents = [contents]
                
            # Separar arquivos e diretórios
            files = [c for c in contents if c.type == "file"]
            dirs = [c for c in contents if c.type == "dir"]
            
            # Processar arquivos primeiro
            for content in files:
                if len(result.files) >= self.config.MAX_FILES:
                    break
                    
                # Verificar se deve pular arquivo
                if self.should_skip_file(content.path):
                    result.skipped_files += 1
                    continue
                    
                # Verificar extensão
                if any(content.name.endswith(ext) for ext in extensoes):
                    file_content, error = self._read_file_content(content)
                    
                    if file_content is not None:
                        result.files[content.path] = file_content
                        result.total_files += 1
                        logger.info(f"✅ Arquivo processado: {content.path}")
                    else:
                        result.errors.append(error)
                        result.skipped_files += 1
                        logger.warning(f"⚠️ {error}")
            
            # Processar diretórios recursivamente
            for content in dirs:
                if len(result.files) >= self.config.MAX_FILES:
                    break
                    
                # Verificar se deve pular diretório
                if self.should_skip_file(content.path + '/'):
                    continue
                    
                try:
                    self._read_directory_recursive(
                        repo, content.path, extensoes, result, len(result.files)
                    )
                except Exception as e:
                    error_msg = f"Erro ao acessar diretório {content.path}: {str(e)}"
                    result.errors.append(error_msg)
                    logger.warning(f"⚠️ {error_msg}")
                            
        except Exception as e:
            error_msg = f"Erro ao acessar {path}: {str(e)}"
            result.errors.append(error_msg)
            logger.error(f"❌ {error_msg}")

    def read_repository(self, repo: str, tipo_de_analise: str, branch: str = None) -> FileReadResult:
        """Lê arquivos do repositório especificado
        
        Args:
            repo: Nome do repositório (ex: 'usuario/repo')
            tipo_de_analise: Tipo de análise para definir extensões
            branch: Branch a ser lida (padrão: branch principal do repo)
            
        Returns:
            FileReadResult: Resultado da leitura com arquivos e metadados
        """
        try:
            logger.info(f"🔍 Iniciando leitura do repositório: {repo}")
            logger.info(f"📂 Tipo de análise: {tipo_de_analise}")
            
            # Obter cliente GitHub
            github_client = self.get_github_client()
            
            # Obter repositório
            try:
                repository = github_client.get_repo(repo)
                logger.info(f"✅ Repositório encontrado: {repository.full_name}")
            except Exception as e:
                raise ValueError(f"Repositório {repo} não encontrado ou sem acesso: {str(e)}")
            
            # Definir branch
            if branch is None:
                branch = repository.default_branch
                logger.info(f"🌿 Usando branch padrão: {branch}")
            else:
                # Verificar se branch existe
                try:
                    repository.get_branch(branch)
                    logger.info(f"✅ Branch '{branch}' encontrada")
                except Exception:
                    logger.warning(f"⚠️ Branch '{branch}' não encontrada, usando branch padrão")
                    branch = repository.default_branch
                    logger.info(f"🌿 Usando branch padrão: {branch}")
            
            # Obter extensões de arquivo
            extensoes = self.get_file_extensions_by_analysis(tipo_de_analise)
            logger.info(f"📝 Extensões a serem lidas: {extensoes}")
            
            # Inicializar resultado
            result = FileReadResult(files={}, total_files=0, skipped_files=0, errors=[])
            
            # Ler arquivos
            logger.info("📖 Iniciando leitura de arquivos...")
            self._read_directory_recursive(repository, "", extensoes, result)
            
            # Se não encontrou arquivos, tentar com extensões básicas
            if not result.files:
                logger.warning("⚠️ Nenhum arquivo encontrado com extensões específicas")
                extensoes_basicas = ['.py', '.js', '.ts', '.java', '.ipynb']
                logger.info(f"🔄 Tentando com extensões básicas: {extensoes_basicas}")
                
                result = FileReadResult(files={}, total_files=0, skipped_files=0, errors=[])
                self._read_directory_recursive(repository, "", extensoes_basicas, result)
            
            # Log dos resultados
            logger.info(f"📊 Leitura concluída:")
            logger.info(f"   - Arquivos processados: {result.total_files}")
            logger.info(f"   - Arquivos ignorados: {result.skipped_files}")
            logger.info(f"   - Erros: {len(result.errors)}")
            
            if result.files:
                logger.info("📋 Arquivos encontrados:")
                for i, arquivo in enumerate(list(result.files.keys())[:10]):
                    logger.info(f"   - {arquivo}")
                if len(result.files) > 10:
                    logger.info(f"   ... e mais {len(result.files) - 10} arquivos")
            else:
                raise ValueError(f"Nenhum arquivo de código encontrado no repositório {repo}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na leitura do repositório: {str(e)}")
            raise

# Instância global para compatibilidade
_reader = GitHubReader()

def get_github_client():
    """Função de compatibilidade - Inicializa cliente GitHub"""
    return _reader.get_github_client()

def get_file_extensions_by_analysis(tipo_de_analise: str) -> List[str]:
    """Função de compatibilidade - Define extensões de arquivo por tipo de análise"""
    return _reader.get_file_extensions_by_analysis(tipo_de_analise)

def should_skip_file(file_path: str) -> bool:
    """Função de compatibilidade - Verifica se arquivo deve ser ignorado"""
    return _reader.should_skip_file(file_path)

def main(repo: str, tipo_de_analise: str, branch: str = "main") -> Dict[str, str]:
    """Função principal para leitura do repositório - COMPATIBILIDADE"""
    try:
        result = _reader.read_repository(repo, tipo_de_analise, branch)
        return result.files
    except Exception as e:
        logger.error(f"❌ Erro na função main: {str(e)}")
        raise

def ler_repositorio(repo: str, tipo_analise: str = "design", branch: str = "main") -> Dict[str, str]:
    """Função alternativa para compatibilidade"""
    return main(repo, tipo_analise, branch)