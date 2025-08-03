# fix_imports.py - Corrige imports para usar variáveis de ambiente

import os
import re

def fix_file(filepath, replacements):
    """Aplica substituições em um arquivo"""
    if not os.path.exists(filepath):
        print(f"⚠️  Arquivo não encontrado: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    for old, new in replacements:
        content = re.sub(old, new, content, flags=re.MULTILINE)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Atualizado: {filepath}")
    else:
        print(f"ℹ️  Sem mudanças: {filepath}")

# Adicionar imports necessários no início dos arquivos
def add_imports(filepath, imports_to_add):
    """Adiciona imports no início do arquivo se não existirem"""
    if not os.path.exists(filepath):
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar quais imports já existem
    new_imports = []
    for imp in imports_to_add:
        if imp not in content:
            new_imports.append(imp)
    
    if new_imports:
        # Adicionar após outros imports
        import_block = '\n'.join(new_imports)
        
        # Encontrar onde inserir (após últimos imports)
        import_pattern = r'^(from\s+\S+\s+import\s+\S+|import\s+\S+).*$'
        matches = list(re.finditer(import_pattern, content, re.MULTILINE))
        
        if matches:
            last_import_end = matches[-1].end()
            content = content[:last_import_end] + '\n' + import_block + content[last_import_end:]
        else:
            # Adicionar no início
            content = import_block + '\n\n' + content
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Imports adicionados em: {filepath}")

print("🔧 Corrigindo imports e configurações...")
print("-" * 50)

# 1. Corrigir github_connector.py e similares
files_to_fix = [
    'backend/tools/github_connector.py',
    'backend/tools/github_reader.py',
    'backend/tools/requisicao_openai.py',
    'backend/tools/revisor_geral.py'
]

# Substituições para userdata
userdata_replacements = [
    (r'from google\.colab import userdata', 'import os'),
    (r'userdata\.get\([\'"](\w+)[\'"]\)', r'os.getenv("\1")')
]

for file in files_to_fix:
    fix_file(file, userdata_replacements)

# 2. Adicionar load_dotenv onde necessário
dotenv_files = [
    'backend/main.py',
    'backend/app.py'
]

dotenv_imports = [
    'from dotenv import load_dotenv',
    'load_dotenv()  # Carregar variáveis de ambiente'
]

for file in dotenv_files:
    add_imports(file, dotenv_imports[:1])  # Só o import
    # Adicionar load_dotenv() após imports
    if os.path.exists(file):
        with open(file, 'r') as f:
            content = f.read()
        if 'load_dotenv()' not in content:
            # Adicionar após imports
            content = re.sub(
                r'(import.*\n)+',
                r'\g<0>\nload_dotenv()  # Carregar variáveis de ambiente\n',
                content,
                count=1
            )
            with open(file, 'w') as f:
                f.write(content)

# 3. Verificar e criar .env se não existir
env_file = 'backend/.env'
if not os.path.exists(env_file):
    env_content = """# Tokens de API
GITHUB_TOKEN=seu_token_github_aqui
OPENAI_API_KEY=sua_chave_openai_aqui

# Configurações do servidor
HOST=127.0.0.1
PORT=8000
DEBUG=true
ENVIRONMENT=development

# URL do serviço Flask (se usar)
FLASK_SERVICE_URL=http://localhost:5000
"""
    with open(env_file, 'w') as f:
        f.write(env_content)
    print(f"✅ Criado arquivo .env de exemplo")
    print("⚠️  IMPORTANTE: Adicione suas chaves reais no .env!")
else:
    print("ℹ️  Arquivo .env já existe")

print("-" * 50)
print("✅ Correções aplicadas!")
print("\n📝 Próximos passos:")
print("1. Edite backend/.env e adicione suas chaves reais")
print("2. Execute: cd backend && python main.py")
print("3. Acesse: http://localhost:8000/docs")