# debug_files.py - Script para debug direto

import os
import sys
import importlib.util

def debug_directory():
    """Debug completo do diretório atual"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 Diretório atual: {current_dir}")
    
    # Listar TODOS os arquivos
    print("\n📋 TODOS os arquivos no diretório:")
    all_files = os.listdir(current_dir)
    for i, file in enumerate(all_files, 1):
        file_path = os.path.join(current_dir, file)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            print(f"  {i:2d}. {file} ({size} bytes)")
        else:
            print(f"  {i:2d}. {file}/ (pasta)")
    
    # Focar apenas nos arquivos Python
    print("\n🐍 Arquivos Python encontrados:")
    python_files = [f for f in all_files if f.endswith('.py')]
    for i, file in enumerate(python_files, 1):
        print(f"  {i}. {file}")
    
    # Verificar cada arquivo Python em busca da função main
    print("\n🔍 Verificando função main() em cada arquivo Python:")
    for file in python_files:
        if file in ['mcp_server_fastapi.py', 'main.py', 'debug_files.py']:
            continue
            
        print(f"\n📄 Analisando: {file}")
        file_path = os.path.join(current_dir, file)
        
        try:
            # Ler o conteúdo do arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se tem função main
            if 'def main(' in content:
                print(f"  ✅ Função main() encontrada!")
                
                # Extrair a linha da definição da função
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    if 'def main(' in line:
                        print(f"  📋 Linha {line_num}: {line.strip()}")
                        
                        # Tentar ver os parâmetros
                        if 'tipo_analise' in line:
                            print(f"  ✅ Parâmetro 'tipo_analise' encontrado!")
                        if 'repositorio' in line:
                            print(f"  ✅ Parâmetro 'repositorio' encontrado!")
                
                # Tentar importar o módulo
                module_name = file[:-3]  # Remove .py
                print(f"  🔄 Tentando importar módulo: {module_name}")
                
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, 'main'):
                        print(f"  ✅ Módulo importado com sucesso!")
                        print(f"  📦 Função main() disponível: {hasattr(module, 'main')}")
                        
                        # Verificar assinatura
                        import inspect
                        sig = inspect.signature(module.main)
                        params = list(sig.parameters.keys())
                        print(f"  📋 Parâmetros: {params}")
                        
                        return module_name, file_path
                    
                except Exception as e:
                    print(f"  ❌ Erro ao importar: {e}")
            else:
                print(f"  ❌ Função main() não encontrada")
                
        except Exception as e:
            print(f"  ❌ Erro ao ler arquivo: {e}")
    
    return None, None

def verificar_dependencias():
    """Verificar dependências necessárias"""
    print("\n🔧 Verificando dependências:")
    
    dependencias = [
        'fastapi',
        'uvicorn', 
        'pydantic',
        'github',  # PyGithub
        'openai',
        'google.colab'  # Para teste_git_hub
    ]
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} - FALTANDO")

if __name__ == "__main__":
    print("🔍 DEBUG COMPLETO DO DIRETÓRIO\n")
    debug_directory()
    verificar_dependencias()
    
    print(f"\n📍 Para resolver:")
    print(f"1. Identifique qual arquivo tem a função main() com tipo_analise e repositorio")
    print(f"2. Me informe o nome exato do arquivo")
    print(f"3. Vou adaptar o backend para usar esse arquivo específico")