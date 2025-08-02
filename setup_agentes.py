# setup_agentes.py - Script para configurar e testar os agentes reais
import os
import sys
from pathlib import Path

def verificar_estrutura_agentes():
    """Verifica se a estrutura dos agentes está correta"""
    print("🔍 Verificando estrutura dos agentes...")
    
    # Arquivos obrigatórios
    arquivos_necessarios = [
        "agents/__init__.py",
        "agents/agente_revisor.py", 
        "tools/__init__.py",
        "tools/revisor_geral.py",
        "tools/github_reader.py"
    ]
    
    arquivos_encontrados = []
    arquivos_faltando = []
    
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            arquivos_encontrados.append(arquivo)
            print(f"✅ {arquivo}")
        else:
            arquivos_faltando.append(arquivo)
            print(f"❌ {arquivo}")
    
    print(f"\n📊 Resultado: {len(arquivos_encontrados)}/{len(arquivos_necessarios)} arquivos encontrados")
    
    if arquivos_faltando:
        print(f"\n⚠️ Arquivos faltando:")
        for arquivo in arquivos_faltando:
            print(f"   - {arquivo}")
        return False
    
    return True

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    print("\n🔍 Verificando dependências...")
    
    dependencias = [
        "openai",
        "PyGithub", 
        "requests",
        "fastapi",
        "uvicorn"
    ]
    
    dependencias_ok = []
    dependencias_faltando = []
    
    for dep in dependencias:
        try:
            __import__(dep.lower().replace("-", "_"))
            dependencias_ok.append(dep)
            print(f"✅ {dep}")
        except ImportError:
            dependencias_faltando.append(dep)
            print(f"❌ {dep}")
    
    print(f"\n📊 Resultado: {len(dependencias_ok)}/{len(dependencias)} dependências OK")
    
    if dependencias_faltando:
        print(f"\n⚠️ Para instalar as dependências faltando:")
        print(f"pip install {' '.join(dependencias_faltando)}")
        return False
    
    return True

def verificar_variaveis_ambiente():
    """Verifica as variáveis de ambiente necessárias"""
    print("\n🔍 Verificando variáveis de ambiente...")
    
    # Para desenvolvimento local, pode usar um arquivo .env
    variaveis = [
        "OPENAI_API_KEY"
    ]
    
    variaveis_ok = []
    variaveis_faltando = []
    
    for var in variaveis:
        if os.getenv(var):
            variaveis_ok.append(var)
            print(f"✅ {var}")
        else:
            variaveis_faltando.append(var)
            print(f"❌ {var}")
    
    if variaveis_faltando:
        print(f"\n⚠️ Variáveis de ambiente faltando:")
        for var in variaveis_faltando:
            print(f"   - {var}")
        print("\n💡 Dicas:")
        print("   1. Crie um arquivo .env na raiz do projeto")
        print("   2. Adicione: OPENAI_API_KEY=sua_chave_aqui")
        print("   3. Ou exporte: export OPENAI_API_KEY=sua_chave_aqui")
        return False
    
    return True

def testar_importacao_agentes():
    """Testa se os agentes podem ser importados"""
    print("\n🔍 Testando importação dos agentes...")
    
    try:
        sys.path.append(os.getcwd())
        from agents import agente_revisor
        print("✅ agente_revisor importado com sucesso")
        
        # Testar se a função principal existe
        if hasattr(agente_revisor, 'main'):
            print("✅ Função 'main' encontrada")
        else:
            print("❌ Função 'main' não encontrada")
            return False
            
        # Testar se executar_analise existe (backup)
        if hasattr(agente_revisor, 'executar_analise'):
            print("✅ Função 'executar_analise' encontrada")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar agentes: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def criar_arquivo_env_exemplo():
    """Cria um arquivo .env.example"""
    print("\n📝 Criando arquivo .env.example...")
    
    conteudo_env = """# Configurações do Backend Agentes Peers
# Copie este arquivo para .env e preencha os valores

# OpenAI API Key (obrigatório para análises reais)
OPENAI_API_KEY=sk-sua_chave_openai_aqui

# Configurações do servidor
HOST=127.0.0.1
PORT=8000
DEBUG=true
ENVIRONMENT=development

# GitHub (opcional - para funcionalidades avançadas)
GITHUB_TOKEN=ghp_seu_token_github_aqui
"""
    
    with open(".env.example", "w", encoding="utf-8") as f:
        f.write(conteudo_env)
    
    print("✅ Arquivo .env.example criado")
    print("💡 Copie para .env e configure suas chaves")

def criar_init_files():
    """Cria arquivos __init__.py se não existirem"""
    print("\n📝 Verificando arquivos __init__.py...")
    
    diretorios = ["agents", "tools"]
    
    for diretorio in diretorios:
        init_file = f"{diretorio}/__init__.py"
        if not os.path.exists(init_file):
            os.makedirs(diretorio, exist_ok=True)
            with open(init_file, "w") as f:
                f.write(f"# {diretorio} module\n")
            print(f"✅ Criado {init_file}")
        else:
            print(f"✅ {init_file} já existe")

def main():
    """Função principal do setup"""
    print("🚀 SETUP DOS AGENTES PEERS")
    print("=" * 50)
    
    # Verificações
    estrutura_ok = verificar_estrutura_agentes()
    dependencias_ok = verificar_dependencias()
    variaveis_ok = verificar_variaveis_ambiente()
    
    # Criação de arquivos auxiliares
    criar_init_files()
    criar_arquivo_env_exemplo()
    
    # Teste final
    if estrutura_ok and dependencias_ok:
        agentes_ok = testar_importacao_agentes()
    else:
        agentes_ok = False
    
    print("\n" + "=" * 50)
    print("📋 RESUMO DO SETUP")
    print("=" * 50)
    
    print(f"📁 Estrutura de arquivos: {'✅ OK' if estrutura_ok else '❌ Problemas'}")
    print(f"📦 Dependências Python: {'✅ OK' if dependencias_ok else '❌ Problemas'}")
    print(f"🔑 Variáveis de ambiente: {'✅ OK' if variaveis_ok else '❌ Problemas'}")
    print(f"🤖 Importação agentes: {'✅ OK' if agentes_ok else '❌ Problemas'}")
    
    if estrutura_ok and dependencias_ok and variaveis_ok and agentes_ok:
        print("\n🎉 SETUP COMPLETO! Os agentes reais estão prontos para uso.")
        print("💡 Execute: python main.py para iniciar o backend integrado")
    else:
        print("\n⚠️ SETUP INCOMPLETO. Resolva os problemas acima.")
        print("\n📋 PRÓXIMOS PASSOS:")
        
        if not dependencias_ok:
            print("1. Instale as dependências faltando")
        if not variaveis_ok:
            print("2. Configure as variáveis de ambiente (.env)")
        if not estrutura_ok:
            print("3. Verifique se todos os arquivos dos agentes estão presentes")
        if not agentes_ok:
            print("4. Teste a importação dos agentes novamente")

if __name__ == "__main__":
    main()