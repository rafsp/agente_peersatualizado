#!/usr/bin/env python3
"""
Script de configuração do Backend Agentes Peers
Execute: python setup.py
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Exibe banner do sistema"""
    print("=" * 60)
    print("🚀 SETUP - BACKEND AGENTES PEERS")
    print("=" * 60)
    print("Sistema de análise de código com IA multi-agentes")
    print("Integração: ChatGPT + GitHub + FastAPI")
    print("=" * 60)

def check_python_version():
    """Verifica versão do Python"""
    print("🐍 Verificando versão do Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ é necessário!")
        print(f"   Versão atual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} OK")
    return True

def install_dependencies():
    """Instala dependências do requirements.txt"""
    print("\n📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def setup_env_file():
    """Configura arquivo .env"""
    print("\n⚙️ Configurando arquivo .env...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("⚠️ Arquivo .env já existe!")
        response = input("Deseja sobrescrever? (s/N): ").lower()
        if response != 's':
            print("📝 Mantendo arquivo .env existente.")
            return True
    
    if not env_example.exists():
        print("❌ Arquivo .env.example não encontrado!")
        return False
    
    # Copiar .env.example para .env
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Arquivo .env criado!")
    print("📝 IMPORTANTE: Edite o arquivo .env e adicione suas chaves API:")
    print("   - OPENAI_API_KEY (obtenha em: https://platform.openai.com/api-keys)")
    print("   - GITHUB_TOKEN (obtenha em: https://github.com/settings/personal-access-tokens)")
    
    return True

def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando estrutura de diretórios...")
    
    dirs_to_create = [
        "logs",
        "data",
        "tools/prompt",
        "agents"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Diretório criado: {dir_path}")
    
    return True

def test_setup():
    """Testa a configuração básica"""
    print("\n🧪 Testando configuração...")
    
    try:
        # Testar importações básicas
        import fastapi
        import openai
        import github
        from dotenv import load_dotenv
        
        print("✅ Importações básicas OK")
        
        # Testar carregamento de .env
        load_dotenv()
        
        openai_key = os.getenv('OPENAI_API_KEY')
        github_token = os.getenv('GITHUB_TOKEN')
        
        if openai_key and openai_key.startswith('sk-'):
            print("✅ OPENAI_API_KEY configurada")
        else:
            print("⚠️ OPENAI_API_KEY não configurada ou inválida")
        
        if github_token and (github_token.startswith('ghp_') or github_token.startswith('github_pat_')):
            print("✅ GITHUB_TOKEN configurada")
        else:
            print("⚠️ GITHUB_TOKEN não configurada ou inválida")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def show_next_steps():
    """Mostra próximos passos"""
    print("\n" + "=" * 60)
    print("🎉 SETUP CONCLUÍDO!")
    print("=" * 60)
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. ✏️ Edite o arquivo .env com suas chaves API")
    print("2. 🚀 Execute o backend: python mcp_server_fastapi.py")
    print("3. 🌐 Execute o frontend: cd frontend && npm run dev")
    print("4. 📖 Acesse a documentação: http://localhost:8000/docs")
    print("\n💡 DICAS:")
    print("• Mantenha o arquivo .env seguro (nunca commite no Git)")
    print("• Use gpt-4o-mini para economizar créditos da OpenAI")
    print("• Configure rate limits se necessário")
    print("\n🆘 SUPORTE:")
    print("• Documentação: README.md")
    print("• Issues: GitHub do projeto")
    print("=" * 60)

def main():
    """Função principal"""
    print_banner()
    
    # Verificações e setup
    steps = [
        ("Verificar Python", check_python_version),
        ("Instalar dependências", install_dependencies),
        ("Configurar .env", setup_env_file),
        ("Criar diretórios", create_directories),
        ("Testar configuração", test_setup),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Falha em: {step_name}")
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
        sys.exit(1)