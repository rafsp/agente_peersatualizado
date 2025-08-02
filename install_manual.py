#!/usr/bin/env python3
"""
Instalador manual passo a passo - para resolver problemas específicos
Execute: python install_manual.py
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package, description=""):
    """Instala um pacote individual"""
    print(f"\n📦 Instalando: {package}")
    if description:
        print(f"   {description}")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar {package}: {e}")
        return False

def main():
    print("🔧 INSTALAÇÃO MANUAL - AGENTES PEERS")
    print("=" * 50)
    print("Este script instala cada dependência individualmente")
    print("para identificar e resolver problemas específicos.")
    print("=" * 50)
    
    # Lista de pacotes em ordem de prioridade
    packages = [
        ("pip --upgrade", "Atualizador de pacotes"),
        ("setuptools --upgrade", "Ferramentas de build"),
        ("wheel", "Suporte a wheels"),
        ("typing-extensions", "Suporte a tipos"),
        ("anyio", "I/O assíncrono"),
        ("h11", "Protocolo HTTP/1.1"),
        ("httpx", "Cliente HTTP moderno"),
        ("starlette", "Framework web base"),
        ("fastapi", "Framework web principal"),
        ("uvicorn[standard]", "Servidor ASGI"),
        ("python-dotenv", "Carregamento de .env"),
        ("requests", "Cliente HTTP simples"),
        ("openai", "API da OpenAI"),
        ("PyGithub", "API do GitHub"),
        ("python-multipart", "Upload de arquivos"),
        ("deprecated", "Suporte a funcionalidades obsoletas")
    ]
    
    print(f"\n🚀 Iniciando instalação de {len(packages)} pacotes...")
    
    success_count = 0
    failed_packages = []
    
    for package, description in packages:
        if install_package(package, description):
            success_count += 1
        else:
            failed_packages.append(package)
            
            # Perguntar se quer continuar
            print(f"⚠️ Falha ao instalar {package}")
            response = input("Continuar com próximo pacote? (S/n): ").lower()
            if response == 'n':
                break
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DA INSTALAÇÃO")
    print("=" * 50)
    print(f"✅ Sucesso: {success_count}/{len(packages)} pacotes")
    
    if failed_packages:
        print(f"❌ Falhas: {len(failed_packages)} pacotes")
        print("Pacotes com problemas:")
        for pkg in failed_packages:
            print(f"  • {pkg}")
        
        print("\n💡 SOLUÇÕES PARA PACOTES QUE FALHARAM:")
        print("1. Tente instalar versões mais antigas:")
        for pkg in failed_packages:
            simple_name = pkg.split('[')[0].split('=')[0].split('<')[0].split('>')[0]
            print(f"   pip install {simple_name}")
        
        print("\n2. Ou tente com --no-deps (cuidado!):")
        for pkg in failed_packages:
            print(f"   pip install --no-deps {pkg}")
        
        print("\n3. Ou use conda (se disponível):")
        for pkg in failed_packages:
            simple_name = pkg.split('[')[0].split('=')[0].split('<')[0].split('>')[0]
            print(f"   conda install {simple_name}")
    
    # Testar importações
    print("\n🧪 Testando importações básicas...")
    test_imports = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn", 
        "openai": "OpenAI",
        "github": "PyGithub",
        "requests": "Requests",
        "dotenv": "python-dotenv"
    }
    
    working_imports = 0
    for module, name in test_imports.items():
        try:
            __import__(module)
            print(f"✅ {name}")
            working_imports += 1
        except ImportError:
            print(f"❌ {name}")
    
    print(f"\n📊 Importações funcionando: {working_imports}/{len(test_imports)}")
    
    if working_imports >= 4:
        print("🎉 Instalação suficiente para funcionar!")
        
        # Criar .env se não existir
        if not Path(".env").exists():
            print("\n📝 Criando arquivo .env...")
            with open(".env", "w") as f:
                f.write("""# Configure suas chaves API aqui
OPENAI_API_KEY=sua_chave_openai_aqui
GITHUB_TOKEN=seu_token_github_aqui
DEFAULT_MODEL=gpt-4.1
PORT=8000
""")
            print("✅ Arquivo .env criado!")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Edite o arquivo .env com suas chaves")
        print("2. Execute: python start_backend.py")
        
    else:
        print("⚠️ Muitas dependências falharam. Considere:")
        print("1. Usar um ambiente virtual limpo")
        print("2. Atualizar Python para versão mais recente")
        print("3. Instalar Visual Studio Build Tools (Windows)")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Instalação cancelada.")