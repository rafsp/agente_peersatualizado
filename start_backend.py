#!/usr/bin/env python3
"""
Script de inicialização do Backend Agentes Peers
Execute: python start_backend.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_setup():
    """Verifica se o setup está correto"""
    print("🔍 Verificando configuração...")
    
    # Verificar arquivo .env
    if not Path(".env").exists():
        print("❌ Arquivo .env não encontrado!")
        print("💡 Execute: python setup.py")
        return False
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Verificar chaves API
    openai_key = os.getenv('OPENAI_API_KEY')
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not openai_key or not openai_key.startswith('sk-'):
        print("❌ OPENAI_API_KEY não configurada corretamente!")
        print("💡 Edite o arquivo .env")
        return False
    
    if not github_token or not (github_token.startswith('ghp_') or github_token.startswith('github_pat_')):
        print("❌ GITHUB_TOKEN não configurada corretamente!")
        print("💡 Edite o arquivo .env")
        return False
    
    print("✅ Configuração OK!")
    return True

def start_server():
    """Inicia o servidor FastAPI"""
    try:
        print("🚀 Iniciando Backend Agentes Peers...")
        print("=" * 50)
        print("📡 Backend: http://localhost:8000")
        print("📚 Docs: http://localhost:8000/docs")
        print("🔧 Health: http://localhost:8000/health")
        print("=" * 50)
        print("💡 Para parar: Ctrl+C")
        print("")
        
        # Importar e executar o servidor
        import uvicorn
        
        # Usar string de importação para evitar warning e manter rodando
        uvicorn.run(
            "mcp_server_fastapi",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Execute: pip install -r requirements.txt")
        return False
    except KeyboardInterrupt:
        print("\n👋 Servidor encerrado pelo usuário.")
        return True
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False

def main():
    """Função principal"""
    print("🤖 AGENTES PEERS - BACKEND")
    print("Sistema de Análise de Código com IA")
    print("")
    
    # Verificar setup
    if not check_setup():
        print("\n🛑 Corrija os problemas e tente novamente.")
        return False
    
    # Iniciar servidor
    print("🌟 Tudo pronto! Iniciando servidor...")
    return start_server()

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Servidor encerrado pelo usuário.")
        print("Obrigado por usar o Agentes Peers!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)