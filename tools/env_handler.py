# tools/env_handler.py
import os

def get_env_var(key):
    """Obtém variável de ambiente de forma compatível"""
    # Tentar diferentes variações do nome
    variations = [key, key.upper(), key.lower()]
    
    for var_name in variations:
        value = os.getenv(var_name)
        if value:
            return value
    
    # Se não encontrou, retornar None
    return None

# Mock para compatibilidade com Google Colab
class MockUserdata:
    @staticmethod
    def get(key):
        return get_env_var(key)

# Simular google.colab.userdata
userdata = MockUserdata()