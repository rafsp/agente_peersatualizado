# agents/agente_revisor.py - VERSÃO UNIFICADA QUE RESOLVE O ERRO
from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm 

# Mantendo o modelo que funciona
modelo_llm = 'gpt-4.1'
max_tokens_saida = 6000  # Aumentado para incluir mais análises

# Lista completa de análises válidas
analises_validas = [
    "design", "pentest", "seguranca", "terraform",
    "refatoracao", "relatorio_teste_unitario", "escrever_testes",
    "agrupamento_testes", "docstring", "agrupamento_design"
]

def code_from_repo(repositorio: str,
                   tipo_analise: str,
                   nome_branch: Optional[str] = None):  # ADICIONADO nome_branch
    try:
        print('Iniciando a leitura do repositório: '+ repositorio)
        
        # Verificar qual versão do github_reader temos
        try:
            # Tenta a versão nova com nome_repo e nome_branch
            codigo_para_analise = github_reader.main(
                nome_repo=repositorio,
                tipo_de_analise=tipo_analise,
                nome_branch=nome_branch
            )
        except TypeError:
            # Fallback para versão antiga com repo
            codigo_para_analise = github_reader.main(
                repo=repositorio,
                tipo_de_analise=tipo_analise
            )
        
        return codigo_para_analise

    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def validation(tipo_analise: str,
               repositorio: Optional[str] = None,
               nome_branch: Optional[str] = None,  # ADICIONADO nome_branch
               codigo: Optional[str] = None):

    if tipo_analise not in analises_validas:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")

    if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

    if codigo is None:
        codigo_para_analise = code_from_repo(
            tipo_analise=tipo_analise,
            repositorio=repositorio,
            nome_branch=nome_branch  # PASSANDO nome_branch
        )
    else:
        codigo_para_analise = codigo

    return codigo_para_analise

def main(tipo_analise: str,
         repositorio: Optional[str] = None,
         nome_branch: Optional[str] = None,  # ADICIONADO nome_branch
         codigo: Optional[str] = None,
         instrucoes_extras: str = "",
         model_name: str = modelo_llm,
         max_token_out: int = max_tokens_saida) -> Dict[str, Any]:

    try:
        print(f"🎯 Executando análise: {tipo_analise}")
        print(f"📊 Modelo: {model_name}")
        
        codigo_para_analise = validation(
            tipo_analise=tipo_analise,
            repositorio=repositorio,
            nome_branch=nome_branch,  # PASSANDO nome_branch
            codigo=codigo
        )
                                       
        if not codigo_para_analise:
            return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
        
        print(f"📝 Código obtido com sucesso")
        
        resultado = executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        
        print(f"✅ Análise concluída")
        
        return {"tipo_analise": tipo_analise, "resultado": resultado}
        
    except Exception as e:
        error_msg = f"Erro na análise '{tipo_analise}': {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "tipo_analise": tipo_analise, 
            "resultado": f"Erro durante a análise: {error_msg}"
        }

# Função para compatibilidade com código existente
def executar_analise(tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None, instrucoes_extras: str = "") -> Dict[str, Any]:
    """Função compatível com código existente que não usa nome_branch"""
    return main(tipo_analise=tipo_analise, repositorio=repositorio, codigo=codigo, instrucoes_extras=instrucoes_extras)