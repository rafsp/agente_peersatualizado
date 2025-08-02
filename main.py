# main.py - Servidor principal integrado
import os
import sys
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Tentar carregar o backend integrado primeiro
try:
    if os.path.exists("mcp_server_fastapi_integrado.py"):
        from mcp_server_fastapi_integrado import app
        backend_type = "INTEGRADO"
        print("✅ Backend integrado carregado")
    else:
        from mcp_server_fastapi import app
        backend_type = "ORIGINAL"
        print("⚠️ Backend original carregado")
        
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
    sys.exit(1)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print("\n" + "=" * 60)
    print("🚀 BACKEND AGENTES PEERS")
    print("=" * 60)
    print(f"🌐 Servidor: http://{host}:{port}")
    print(f"📚 Docs: http://{host}:{port}/docs")
    print(f"🔧 Tipo: {backend_type}")
    print("=" * 60)
    
    if backend_type == "INTEGRADO":
        print("🎉 BACKEND INTEGRADO ATIVO!")
        print("💡 Agentes reais serão usados se disponíveis")
    else:
        print("⚠️ USANDO BACKEND ORIGINAL")
        print("💡 Crie mcp_server_fastapi_integrado.py para integração")
    
    print("=" * 60)
    print("🛑 Ctrl+C para parar")
    print("=" * 60)
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado")
    except Exception as e:
        print(f"❌ Erro: {e}")