#!/usr/bin/env python3
"""
Script de configuração específico para Windows - Backend Agentes Peers
Execute: python setup_windows.py
"""

import os
import sys
import subprocess
from pathlib import Path
import platform

def print_banner():
    """Exibe banner do sistema"""
    print("=" * 60)
    print("🚀 SETUP WINDOWS - BACKEND AGENTES PEERS")
    print("=" * 60)
    print("Sistema de análise de código com IA multi-agentes")
    print("Otimizado para Windows")
    print("=" * 60)

def check_windows():
    """Verifica se está no Windows"""
    if platform.system() != "Windows":
        print("⚠️ Este script é otimizado para Windows.")
        print("Para outros sistemas, use: python setup.py")
        response = input("Continuar mesmo assim? (s/N): ").lower()
        return response == 's'
    return True

def check_python_version():
    """Verifica versão do Python"""
    print("🐍 Verificando versão do Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ é necessário!")
        print(f"   Versão atual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} OK")
    
    # Verificar se está em venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Ambiente virtual detectado")
    else:
        print("⚠️ Recomendamos usar um ambiente virtual")
        print("   Execute: python -m venv venv && venv\\Scripts\\activate")
    
    return True

def upgrade_pip():
    """Atualiza pip, setuptools e wheel"""
    print("\n🔧 Atualizando ferramentas de build...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "--upgrade", "pip", "setuptools", "wheel"
        ])
        print("✅ Ferramentas atualizadas!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Aviso na atualização: {e}")
        return True  # Continuar mesmo com aviso

def install_dependencies_safe():
    """Instala dependências de forma segura no Windows"""
    print("\n📦 Instalando dependências (modo seguro para Windows)...")
    
    # Lista de pacotes essenciais em ordem de instalação
    essential_packages = [
        "typing-extensions>=4.5.0",
        "anyio>=3.7.0,<5.0.0",
        "h11>=0.14.0,<1.0.0",
        "httpx>=0.24.0,<1.0.0",
        "starlette>=0.27.0,<1.0.0",
        "fastapi>=0.100.0,<1.0.0",
        "uvicorn[standard]>=0.20.0,<1.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "requests>=2.25.0,<3.0.0",
        "openai>=1.10.0,<2.0.0",
        "PyGithub>=1.59.0,<3.0.0",
        "python-multipart>=0.0.5,<1.0.0",
        "Deprecated>=1.2.0,<2.0.0"
    ]
    
    # Tentar instalar usando binários pré-compilados
    print("🔄 Tentativa 1: Instalação com binários pré-compilados...")
    try:
        cmd = [sys.executable, "-m", "pip", "install", "--only-binary=:all:"] + essential_packages
        subprocess.check_call(cmd)
        print("✅ Dependências instaladas com sucesso (binários)!")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Falha na instalação com binários, tentando método alternativo...")
    
    # Tentar instalar sem pydantic-core problemático
    print("🔄 Tentativa 2: Instalação sem compilação...")
    try:
        # Instalar pydantic mais recente que tem binários
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic>=2.5.0", "--only-binary=pydantic"])
        
        # Instalar outros pacotes
        for package in essential_packages:
            if not package.startswith("pydantic"):  # Já instalamos
                print(f"   Instalando: {package}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        print("✅ Dependências instaladas com sucesso (método alternativo)!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na instalação: {e}")
        return False

def create_minimal_requirements():
    """Cria requirements.txt mínimo se a instalação falhar"""
    print("\n📝 Criando requirements.txt mínimo...")
    
    minimal_content = """# Requirements mínimos para Windows
fastapi
uvicorn[standard]
pydantic
python-dotenv
requests
openai
PyGithub
python-multipart
"""
    
    with open("requirements_minimal.txt", "w") as f:
        f.write(minimal_content)
    
    print("✅ Arquivo requirements_minimal.txt criado!")
    print("💡 Se houver problemas, tente: pip install -r requirements_minimal.txt")

def setup_env_file():
    """Configura arquivo .env"""
    print("\n⚙️ Configurando arquivo .env...")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️ Arquivo .env já existe!")
        response = input("Deseja sobrescrever? (s/N): ").lower()
        if response != 's':
            print("📝 Mantendo arquivo .env existente.")
            return True
    
    # Criar .env básico
    env_content = """# Configurações do Backend Agentes Peers
# IMPORTANTE: Preencha com suas chaves reais!

# OpenAI API Key (obtenha em: https://platform.openai.com/api-keys)
OPENAI_API_KEY=sua_chave_openai_aqui

# GitHub Token (obtenha em: https://github.com/settings/personal-access-tokens)
GITHUB_TOKEN=seu_token_github_aqui

# Configurações opcionais
DEFAULT_MODEL=gpt-4.1
PORT=8000
ENVIRONMENT=development
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env criado!")
    print("📝 IMPORTANTE: Edite o arquivo .env e adicione suas chaves API")
    
    return True

def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando estrutura de diretórios...")
    
    dirs_to_create = [
        "logs",
        "data", 
        "tools",
        "tools/prompt",
        "agents"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Diretório: {dir_path}")
    
    return True

def test_imports():
    """Testa importações básicas"""
    print("\n🧪 Testando importações...")
    
    test_modules = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("openai", "OpenAI"), 
        ("github", "PyGithub"),
        ("dotenv", "python-dotenv"),
        ("requests", "Requests")
    ]
    
    success_count = 0
    for module, name in test_modules:
        try:
            __import__(module)
            print(f"✅ {name}")
            success_count += 1
        except ImportError:
            print(f"❌ {name} - falha na importação")
    
    if success_count >= 4:  # Pelo menos os essenciais
        print(f"✅ {success_count}/{len(test_modules)} módulos OK")
        return True
    else:
        print(f"⚠️ Apenas {success_count}/{len(test_modules)} módulos funcionando")
        return False

def show_next_steps():
    """Mostra próximos passos"""
    print("\n" + "=" * 60)
    print("🎉 SETUP WINDOWS CONCLUÍDO!")
    print("=" * 60)
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. ✏️ Edite o arquivo .env com suas chaves API:")
    print("   • OPENAI_API_KEY=sk-proj-...")
    print("   • GITHUB_TOKEN=ghp_...")
    print("\n2. 🚀 Inicie o backend:")
    print("   python start_backend.py")
    print("\n3. 🌐 Inicie o frontend em outro terminal:")
    print("   cd frontend")
    print("   npm install")
    print("   npm run dev")
    print("\n💡 DICAS PARA WINDOWS:")
    print("• Use PowerShell ou Command Prompt como Administrator")
    print("• Se houver erros de SSL, execute: pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org <package>")
    print("• Para problemas de encoding: set PYTHONIOENCODING=utf-8")
    print("\n🆘 EM CASO DE PROBLEMAS:")
    print("• Tente: pip install -r requirements_minimal.txt")
    print("• Verifique antivírus (pode bloquear instalações)")
    print("• Use ambiente virtual: python -m venv venv")
    print("=" * 60)

def main():
    """Função principal"""
    print_banner()
    
    # Verificar se é Windows
    if not check_windows():
        return False
    
    # Verificações e setup
    steps = [
        ("Verificar Python", check_python_version),
        ("Atualizar pip", upgrade_pip),
        ("Instalar dependências", install_dependencies_safe),
        ("Configurar .env", setup_env_file),
        ("Criar diretórios", create_directories),
        ("Testar importações", test_imports),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Falha em: {step_name}")
            if step_name == "Instalar dependências":
                create_minimal_requirements()
                print("💡 Arquivo requirements_minimal.txt criado como fallback")
            else:
                print("🛑 Setup interrompido. Corrija os erros e tente novamente.")
                return False
    
    show_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup cancelado pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print("💡 Tente executar como Administrador")
        sys.exit(1)