@echo off
chcp 65001 >nul
echo ============================================================
echo 🚀 SETUP AGENTES PEERS - WINDOWS
echo ============================================================
echo Sistema de análise de código com IA multi-agentes
echo Otimizado para Windows
echo ============================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo 💡 Instale Python em: https://python.org/downloads/
    echo    Marque "Add Python to PATH" durante a instalação
    pause
    exit /b 1
)

echo ✅ Python encontrado!
python --version

REM Verificar se está em ambiente virtual
python -c "import sys; print('✅ Ambiente virtual ativo' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else '⚠️ Ambiente virtual não detectado')"

echo.
echo 🔄 Executando setup otimizado para Windows...
echo.

REM Executar setup Python
python setup_windows.py

if errorlevel 1 (
    echo.
    echo ❌ Setup falhou!
    echo 💡 Possíveis soluções:
    echo    1. Execute como Administrador
    echo    2. Crie ambiente virtual: python -m venv venv
    echo    3. Ative o ambiente: venv\Scripts\activate
    echo    4. Execute novamente: setup_windows.bat
    echo.
    pause
    exit /b 1
)

echo.
echo 🎉 Setup concluído!
echo 📝 Não esqueça de configurar o arquivo .env
echo.
pause