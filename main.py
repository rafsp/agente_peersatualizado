# main.py - VERSÃO SIMPLIFICADA
import os
import sys
import uvicorn
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório atual ao path do Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Importar a aplicação FastAPI
    from mcp_server_fastapi import app
    print("✅ Aplicação FastAPI importada com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar aplicação FastAPI: {e}")
    print("📋 Verifique se o arquivo mcp_server_fastapi.py existe e está correto")
    sys.exit(1)

# REMOVER CORS DAQUI - já está no mcp_server_fastapi.py

if __name__ == "__main__":
    # Configuração do servidor
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print("=" * 50)
    print("🚀 BACKEND AGENTES_PEERS")
    print("=" * 50)
    print(f"🌐 Servidor: http://{host}:{port}")
    print(f"📚 Documentação: http://{host}:{port}/docs")
    print(f"❤️  Health Check: http://{host}:{port}/health")
    print(f"🔧 Debug mode: {debug}")
    print("=" * 50)
    print("🛑 Para parar o servidor: Ctrl+C")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if debug else "warning",
            access_log=debug
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)