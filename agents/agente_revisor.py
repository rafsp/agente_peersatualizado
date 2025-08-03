from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm 

# Configuração dos modelos - usando gpt-4 padrão
modelo_llm = 'gpt-4'  # Mudei de gpt-4.1 para gpt-4
max_tokens_saida = 3000

# Tipos de análise suportados pelos agentes reais
analises_validas = [
    "design", "pentest", "seguranca", "terraform", 
    "refatoracao", "escrever_testes", 
    "agrupamento_design", "agrupamento_testes"
]

def code_from_repo(repositorio: str, tipo_analise: str):
    """Obtém código do repositório GitHub"""
    try:
        print(f'🔍 Iniciando a leitura do repositório: {repositorio}')
        codigo_para_analise = github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)
        return codigo_para_analise
    except Exception as e:
        print(f"❌ Erro ao ler repositório: {e}")
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def validation(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None):
    """Valida parâmetros de entrada"""
    if tipo_analise not in analises_validas:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")

    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

    if codigo is None:
        print(f"📖 Obtendo código do repositório para análise: {tipo_analise}")
        codigo_para_analise = code_from_repo(tipo_analise=tipo_analise, repositorio=repositorio)
    else:
        print(f"📝 Usando código fornecido diretamente")
        codigo_para_analise = codigo

    return codigo_para_analise

def main(tipo_analise: str,
         repositorio: Optional[str] = None,
         nome_branch: Optional[str] = None,  # Compatibilidade com backend
         codigo: Optional[str] = None,
         instrucoes_extras: str = "",
         model_name: str = modelo_llm,
         max_token_out: int = max_tokens_saida) -> Dict[str, Any]:
    """Função principal do agente revisor"""
    
    print(f"🚀 Iniciando análise: {tipo_analise}")
    print(f"📂 Repositório: {repositorio}")
    print(f"🌿 Branch: {nome_branch or 'padrão'}")
    print(f"🤖 Modelo: {model_name}")
    
    try:
        # Validar e obter código
        codigo_para_analise = validation(
            tipo_analise=tipo_analise,
            repositorio=repositorio,
            codigo=codigo
        )
                                       
        if not codigo_para_analise:
            resultado_erro = 'Não foi fornecido nenhum código para análise'
            print(f"⚠️ {resultado_erro}")
            return {
                "tipo_analise": tipo_analise, 
                "resultado": {'reposta_final': resultado_erro}
            }
        else:
            print(f"✅ Código obtido com sucesso ({len(str(codigo_para_analise))} caracteres)")
            
            # Executar análise com IA
            resultado = executar_analise_llm(
                tipo_analise=tipo_analise,
                codigo=str(codigo_para_analise),
                analise_extra=instrucoes_extras,
                model_name=model_name,
                max_token_out=max_token_out
            )
            
            print(f"✅ Análise concluída com sucesso")
            return {
                "tipo_analise": tipo_analise, 
                "resultado": {'reposta_final': resultado}
            }
            
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        raise

# Função de compatibilidade com código legado
def executar_analise(tipo_analise: str, 
                    repositorio: Optional[str] = None, 
                    codigo: Optional[str] = None, 
                    instrucoes_extras: str = "") -> Dict[str, Any]:
    """Função para compatibilidade com código legado"""
    return main(
        tipo_analise=tipo_analise, 
        repositorio=repositorio, 
        codigo=codigo, 
        instrucoes_extras=instrucoes_extras
    )