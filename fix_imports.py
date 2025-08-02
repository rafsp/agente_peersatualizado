# fix_imports.py - MOCK FIRST, IMPORT LATER
import sys
from unittest.mock import MagicMock
import os

# Criar mock ANTES de qualquer import
print("🔧 Criando mock do Google Colab...")

def get_env_var(key):
    variations = [key, key.upper(), key.lower(), 'GITHUB_TOKEN', 'github_token', 'GITHUB_PAT', 'github_pat']
    for var_name in variations:
        value = os.getenv(var_name)
        if value:
            print(f"✅ Encontrada: {var_name}")
            return value
    print(f"⚠️ Não encontrada: {key}")
    return None

# Mock hierarchy
google_mock = MagicMock()
colab_mock = MagicMock()
userdata_mock = MagicMock()
userdata_mock.get = get_env_var
colab_mock.userdata = userdata_mock
google_mock.colab = colab_mock

# Register in sys.modules ANTES de qualquer import
sys.modules['google'] = google_mock
sys.modules['google.colab'] = colab_mock
sys.modules['google.colab.userdata'] = userdata_mock

print("✅ Mock criado com sucesso!")

# Testar mock
try:
    from google.colab import userdata
    test = userdata.get('GITHUB_TOKEN')
    print(f"🧪 Mock funcionando: {'✅' if test else '❌'}")
except Exception as e:
    print(f"❌ Erro no mock: {e}")