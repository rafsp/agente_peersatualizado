# teste_agente_corrigido.py
import sys
import os
sys.path.append('.')

# IMPORTANTE: Executar fix primeiro
import fix_imports

from agents import agente_revisor
from tools import github_reader, revisor_geral

exec(open('fix_imports.py').read())

print("🧪 TESTE DIRETO DO FLUXO COMPLETO")
print("=" * 50)

# Agora importar com mock ativo
try:
    from agents import agente_revisor
    from tools import github_reader, revisor_geral
    print("✅ Imports realizados com sucesso")
except Exception as e:
    print(f"❌ Erro nos imports: {e}")
    import traceback
    traceback.print_exc()
    exit()

print("🧪 TESTE DIRETO DO FLUXO COMPLETO")
print("=" * 50)

# Teste 1: GitHub Reader diretamente
print("1. Testando GitHub Reader...")
try:
    codigo = github_reader.main(
        nome_repo='rafsp/api-springboot-web-app',
        tipo_de_analise='design'
    )
    print(f"✅ GitHub: {len(codigo)} arquivos, {sum(len(c) for c in codigo.values())} chars")
    print(f"📄 Primeiros arquivos: {list(codigo.keys())[:3]}")
except Exception as e:
    print(f"❌ GitHub falhou: {e}")
    import traceback
    traceback.print_exc()

# Teste 2: Análise LLM diretamente  
print("\n2. Testando OpenAI LLM...")
try:
    # Usar amostra pequena
    codigo_sample = "def hello(): return 'Spring Boot App'"
    
    resultado = revisor_geral.executar_analise_llm(
        tipo_analise='design',
        codigo=codigo_sample,
        analise_extra='Teste direto',
        model_name='gpt-4.1',  # Trocar gpt-4.1 por gpt-4
        max_token_out=500
    )
    print(f"✅ OpenAI: {len(resultado)} chars")
    print(f"Preview: {resultado[:200]}...")
except Exception as e:
    print(f"❌ OpenAI falhou: {e}")
    import traceback
    traceback.print_exc()

# Teste 3: Agente completo
print("\n3. Testando agente completo...")
try:
    resultado = agente_revisor.main(
        tipo_analise='design',
        repositorio='rafsp/api-springboot-web-app'
    )
    print(f"✅ Agente: {len(str(resultado))} chars")
    print(f"Preview: {str(resultado)[:300]}...")
except Exception as e:
    print(f"❌ Agente falhou: {e}")
    import traceback
    traceback.print_exc()