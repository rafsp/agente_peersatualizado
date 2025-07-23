import re
from github import Github
from github.Auth import Token
from google.colab import userdata

def conection(repositorio: str):
    GITHUB_TOKEN = userdata.get('github_token')
    auth = Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    return g.get_repo(repositorio)


MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"], 
}

def _leitura_recursiva_com_debug(repo, extensoes, path="", arquivos_do_repo=None):

    if arquivos_do_repo is None:
        arquivos_do_repo = {}

    try:
        # Tentando obter o conteúdo do caminho
        conteudos = repo.get_contents(path)

        for conteudo in conteudos:
            if conteudo.type == "dir":
                _leitura_recursiva_com_debug(repo, extensoes, conteudo.path, arquivos_do_repo)
            else:
                # Lógica de decisão de leitura
                ler_o_arquivo = False
                if extensoes is None:
                    ler_o_arquivo = True
                else:
                    if any(conteudo.path.endswith(ext) for ext in extensoes) or conteudo.name in extensoes:
                        ler_o_arquivo = True
                    
                if ler_o_arquivo:
                    try:
                        codigo = conteudo.decoded_content.decode('utf-8')
                        arquivos_do_repo[conteudo.path] = codigo
                    except Exception as e:
                        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")

    except Exception as e:
        print(e)
        
    return arquivos_do_repo


def main(repo, tipo_de_analise: str):

    repositorio_final = conection(repositorio=repo)

    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())

    arquivos_encontrados = _leitura_recursiva_com_debug(repositorio_final, 
                                                        extensoes=extensoes_alvo)
  
    return arquivos_encontrados