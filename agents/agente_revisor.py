from typing import Optional, Dict, Any
import sys
import os

# Adicionar diretório pai ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import github_reader
from tools.revisor_geral import executar_analise_llm

# Configurações padrão
modelo_llm = 'gpt-4o-mini'  # Modelo mais econômico
max_tokens_saida = 3000

# Análises válidas (mapeamento do frontend para backend)
analises_validas = ["design", "pentest", "seguranca", "terraform"]

def code_from_repo(repositorio: str, tipo_analise: str) -> Dict[str, str]:
    """
    Obtém código do repositório GitHub
    
    Args:
        repositorio: Nome do repo no formato "usuario/repo" 
        tipo_analise: Tipo de análise para filtrar arquivos
        
    Returns:
        Dicionário com arquivos do repositório
    """
    try:
        print(f'🔍 Iniciando leitura do repositório: {repositorio}')
        codigo_para_analise = github_reader.main(
            repo=repositorio,
            tipo_de_analise=tipo_analise
        )
        
        if not codigo_para_analise:
            print("⚠️ Nenhum arquivo encontrado no repositório")
            return {}
        
        print(f"✅ {len(codigo_para_analise)} arquivos obtidos do repositório")
        return codigo_para_analise

    except Exception as e:
        error_msg = f"Falha ao executar a análise de '{tipo_analise}' no repo '{repositorio}': {e}"
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg) from e

def validation(tipo_analise: str,
               repositorio: Optional[str] = None,
               codigo: Optional[str] = None) -> str:
    """
    Valida parâmetros e obtém código para análise
    
    Args:
        tipo_analise: Tipo de análise
        repositorio: URL/nome do repositório (opcional)
        codigo: Código direto (opcional)
        
    Returns:
        Código formatado para análise
    """
    # Validar tipo de análise
    if tipo_analise not in analises_validas:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")

    # Validar que pelo menos uma fonte foi fornecida
    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

    # Obter código
    if codigo is None:
        # Obter código do repositório
        arquivos_repo = code_from_repo(tipo_analise=tipo_analise, repositorio=repositorio)
        
        if not arquivos_repo:
            return ""
        
        # Formatar código como dicionário Python para o prompt
        codigo_formatado = "{\n"
        for caminho, conteudo in arquivos_repo.items():
            # Escapar aspas no conteúdo
            conteudo_escaped = conteudo.replace('"""', '\\"\\"\\"').replace("'''", "\\'\\'\\'")
            codigo_formatado += f'    "{caminho}": """{conteudo_escaped}""",\n'
        codigo_formatado += "}"
        
        return codigo_formatado
    else:
        # Usar código fornecido diretamente
        return codigo

def main(tipo_analise: str,
         repositorio: Optional[str] = None,
         codigo: Optional[str] = None,
         instrucoes_extras: str = "",
         model_name: str = modelo_llm,
         max_token_out: int = max_tokens_saida) -> Dict[str, Any]:
    """
    Função principal para executar análise de código
    
    Args:
        tipo_analise: Tipo de análise ('design', 'pentest', 'seguranca', 'terraform')
        repositorio: Nome do repositório (formato: "usuario/repo")
        codigo: Código direto para análise (opcional)
        instrucoes_extras: Instruções adicionais do usuário
        model_name: Modelo da OpenAI a usar
        max_token_out: Máximo de tokens na resposta
        
    Returns:
        Dicionário com resultado da análise
    """
    print(f"🚀 Iniciando análise de {tipo_analise}")
    print(f"📊 Modelo: {model_name} | Max tokens: {max_token_out}")
    
    try:
        # Validar e obter código
        codigo_para_analise = validation(
            tipo_analise=tipo_analise,
            repositorio=repositorio,
            codigo=codigo
        )
        
        if not codigo_para_analise or codigo_para_analise.strip() == "":
            resultado_vazio = "Não foi fornecido nenhum código para análise ou repositório está vazio."
            print(f"⚠️ {resultado_vazio}")
            return {
                "tipo_analise": tipo_analise,
                "repositorio": repositorio,
                "resultado": resultado_vazio,
                "status": "empty"
            }
        
        print(f"📝 Código obtido: {len(codigo_para_analise)} caracteres")
        
        # Executar análise com IA
        print("🤖 Enviando para análise com IA...")
        resultado = executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        
        print("✅ Análise concluída com sucesso!")
        
        return {
            "tipo_analise": tipo_analise,
            "repositorio": repositorio,
            "resultado": resultado,
            "status": "success",
            "model_used": model_name,
            "instructions_extra": instrucoes_extras
        }
        
    except Exception as e:
        error_msg = f"Erro na análise: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            "tipo_analise": tipo_analise,
            "repositorio": repositorio,
            "resultado": f"Erro durante a análise: {error_msg}",
            "status": "error",
            "error_details": str(e)
        }

# Função de compatibilidade (nome antigo)
def executar_analise(*args, **kwargs):
    """Função de compatibilidade - usa main()"""
    return main(*args, **kwargs)

if __name__ == "__main__":
    # Teste básico
    print("🧪 Testando agente revisor...")
    
    # Exemplo de teste com repositório público pequeno
    try:
        resultado = main(
            tipo_analise="design",
            repositorio="octocat/Hello-World",
            instrucoes_extras="Foque na estrutura básica do projeto"
        )
        
        print("📋 Resultado do teste:")
        print(f"Status: {resultado['status']}")
        print(f"Tipo: {resultado['tipo_analise']}")
        if resultado['status'] == 'success':
            print(f"Resultado: {resultado['resultado'][:200]}...")  # Primeiros 200 chars
        else:
            print(f"Erro: {resultado['resultado']}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        print("💡 Verifique se as chaves API estão configuradas em .env")