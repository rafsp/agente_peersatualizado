# main.py - Servidor principal
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar a aplicação FastAPI
from mcp_server_fastapi import app

# Configurar CORS para permitir conexões do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Caso use porta diferente
        "https://your-frontend-domain.com",  # Adicione seu domínio de produção
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    # Configuração do servidor
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print("\n" + "=" * 60)
    print("🚀 AGENTES PEERS - BACKEND")
    print("=" * 60)
    print(f"📍 Servidor: http://{host}:{port}")
    print(f"📚 Docs: http://{host}:{port}/docs")
    print(f"🔧 Debug: {debug}")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )