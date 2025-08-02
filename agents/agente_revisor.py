# agents/agente_revisor.py - Exemplo básico

def main(tipo_analise: str, repositorio: str = None, 
         nome_branch: str = None, codigo: str = None, 
         instrucoes_extras: str = ""):
    """
    Função principal do agente revisor
    """
    print(f"Executando análise: {tipo_analise}")
    print(f"Repositório: {repositorio}")
    
    # Simular análise
    resultado = f"""
# Análise {tipo_analise.title()}

## Repositório Analisado
{repositorio or 'Código fornecido diretamente'}

## Resultado da Análise
Esta é uma análise de exemplo. 

## Recomendações
1. Implementar análise real baseada no tipo
2. Integrar com ferramentas de análise
3. Retornar insights específicos

## Instruções Extras
{instrucoes_extras}
"""
    
    return {
        "tipo_analise": tipo_analise,
        "resultado": resultado.strip()
    }

# Lista de análises válidas (compatível com o backend)
analises_validas = [
    "design", "pentest", "seguranca", "terraform", 
    "relatorio_teste_unitario", "escrever_testes"
]
