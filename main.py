# main.py - Arquivo principal do servidor FastAPI
import os
import sys
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
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

# Configurar CORS para permitir conexões do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        "http://localhost:3001", # Caso use porta diferente
        "https://your-frontend-domain.com",  # Adicione seu domínio de produção
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint de health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "Backend está funcionando",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Endpoint de informações do sistema
@app.get("/info")
async def system_info():
    return {
        "platform": sys.platform,
        "python_version": sys.version,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "false").lower() == "true"
    }

if __name__ == "__main__":
    # Configuração do servidor
    host = os.getenv("HOST", "127.0.0.1")  # Usar 127.0.0.1 no Windows
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"  # Debug True por padrão em dev
    
    print("=" * 50)
    print("🚀 BACKEND AGENTES_PEERS")
    print("=" * 50)
    print(f"🌐 Servidor: http://{host}:{port}")
    print(f"📚 Documentação: http://{host}:{port}/docs")
    print(f"❤️  Health Check: http://{host}:{port}/health")
    print(f"🔧 Debug mode: {debug}")
    print(f"🖥️  Platform: {sys.platform}")
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