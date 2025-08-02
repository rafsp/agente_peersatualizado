# setup_checker.py - Verifica e configura o ambiente dos agentes

import os
import sys
import importlib.util
from pathlib import Path

def main():
    print("🔍 VERIFICADOR DE AMBIENTE - AGENTES PEERS")
    print("=" * 60)
    
    # Obter diretório atual
    current_dir = Path(__file__).parent.absolute()
    print(f"📁 Diretório de trabalho: {current_dir}")
    
    # Verificar estrutura de diretórios
    print("\n📂 ESTRUTURA DE DIRETÓRIOS:")
    check_directory_structure(current_dir)
    
    # Mapear arquivos Python
    print("\n🐍 ARQUIVOS PYTHON ENCONTRADOS:")
    python_files = find_python_files(current_dir)
    
    # Analisar módulos
    print("\n🔍 ANÁLISE DE MÓDULOS:")
    analyze_modules(python_files)
    
    # Verificar dependências
    print("\n📦 VERIFICAÇÃO DE DEPENDÊNCIAS:")
    check_dependencies()
    
    # Sugestões de configuração
    print("\n💡 SUGESTÕES DE CONFIGURAÇÃO:")
    provide_suggestions(current_dir)
    
    print("\n✅ Verificação concluída!")

def check_directory_structure(base_dir):
    """Verifica a estrutura de diretórios"""
    expected_dirs = ['agents', 'tools', 'logs', 'data']
    
    for dir_name in expected_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"  ✅ {dir_name}/ - Encontrado")
            # Listar conteúdo se existir
            contents = list(dir_path.glob("*.py"))
            if contents:
                for file in contents[:3]:  # Mostrar apenas os 3 primeiros
                    print(f"    📄 {file.name}")
                if len(contents) > 3:
                    print(f"    ... e mais {len(contents) - 3} arquivos")
        else:
            print(f"  ❌ {dir_name}/ - Não encontrado")

def find_python_files(base_dir):
    """Encontra todos os arquivos Python"""
    python_files = {}
    
    for file_path in base_dir.rglob("*.py"):
        if not any(part.startswith('.') or part == '__pycache__' for part in file_path.parts):
            relative_path = file_path.relative_to(base_dir)
            module_name = str(relative_path).replace(os.sep, '.').replace('.py', '')
            python_files[module_name] = file_path
            print(f"  📄 {module_name} -> {relative_path}")
    
    return python_files

def analyze_modules(python_files):
    """Analisa módulos em busca de funções principais"""
    potential_main_modules = []
    
    for module_name, file_path in python_files.items():
        if module_name in ['mcp_server_fastapi', 'main', 'setup_checker']:
            continue
            
        try:
            # Ler o arquivo e analisar
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                'module_name': module_name,
                'file_path': file_path,
                'has_main': 'def main(' in content,
                'has_executar_analise': 'def executar_analise(' in content,
                'has_tipo_analise': 'tipo_analise' in content,
                'has_repositorio': 'repositorio' in content,
                'imports_github': 'github' in content.lower(),
                'imports_openai': 'openai' in content.lower(),
                'line_count': len(content.split('\n'))
            }
            
            score = calculate_module_score(analysis)
            analysis['score'] = score
            
            if score > 0:
                potential_main_modules.append(analysis)
                
        except Exception as e:
            print(f"  ⚠️ Erro ao analisar {module_name}: {e}")
    
    # Ordenar por score
    potential_main_modules.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n🎯 MÓDULOS CANDIDATOS A AGENTE PRINCIPAL:")
    for i, module in enumerate(potential_main_modules[:5], 1):
        print(f"  {i}. {module['module_name']} (Score: {module['score']})")
        print(f"     📄 {module['file_path']}")
        print(f"     📋 Características:")
        if module['has_main']:
            print(f"        ✅ Tem função main()")
        if module['has_executar_analise']:
            print(f"        ✅ Tem função executar_analise()")
        if module['has_tipo_analise']:
            print(f"        ✅ Usa parâmetro tipo_analise")
        if module['has_repositorio']:
            print(f"        ✅ Usa parâmetro repositorio")
        print(f"        📏 {module['line_count']} linhas")
        print()

def calculate_module_score(analysis):
    """Calcula score de probabilidade de ser o módulo principal"""
    score = 0
    
    # Função main ou executar_analise
    if analysis['has_main'] or analysis['has_executar_analise']:
        score += 10
    
    # Parâmetros esperados
    if analysis['has_tipo_analise']:
        score += 5
    if analysis['has_repositorio']:
        score += 5
    
    # Imports relevantes
    if analysis['imports_github']:
        score += 3
    if analysis['imports_openai']:
        score += 3
    
    # Tamanho do arquivo (módulos principais tendem a ser maiores)
    if analysis['line_count'] > 50:
        score += 2
    if analysis['line_count'] > 100:
        score += 2
    
    # Nome sugere agente principal
    if 'agente' in analysis['module_name'].lower():
        score += 5
    if 'revisor' in analysis['module_name'].lower():
        score += 3
    
    return score

def check_dependencies():
    """Verifica dependências importantes"""
    important_deps = [
        'fastapi',
        'uvicorn', 
        'pydantic',
        'openai',
        'github',  # PyGithub
        'requests'
    ]
    
    for dep in important_deps:
        try:
            importlib.import_module(dep)
            print(f"  ✅ {dep} - Instalado")
        except ImportError:
            print(f"  ❌ {dep} - NÃO instalado")

def provide_suggestions(base_dir):
    """Fornece sugestões de configuração"""
    
    # Verificar se existe agente_revisor.py
    agente_revisor_path = base_dir / 'agents' / 'agente_revisor.py'
    if not agente_revisor_path.exists():
        print(f"  💡 Crie o arquivo agents/agente_revisor.py")
        print(f"     Ou mova seu módulo principal para esse local")
    
    # Verificar se existe .env
    env_path = base_dir / '.env'
    if not env_path.exists():
        print(f"  💡 Crie um arquivo .env com suas credenciais:")
        print(f"     OPENAI_API_KEY=sua_chave_aqui")
        print(f"     GITHUB_TOKEN=seu_token_aqui")
    
    # Sugestão de estrutura
    print(f"  💡 Estrutura recomendada:")
    print(f"     agents/")
    print(f"       └── agente_revisor.py  # Módulo principal")
    print(f"     tools/")
    print(f"       ├── github_reader.py")
    print(f"       └── revisor_geral.py")
    print(f"     mcp_server_fastapi.py   # Backend (já existe)")
    print(f"     main.py                 # Launcher (já existe)")

def create_sample_agente_revisor():
    """Cria um arquivo de exemplo para agente_revisor.py"""
    sample_code = '''# agents/agente_revisor.py - Exemplo básico

def main(tipo_analise: str, repositorio: str = None, 
         nome_branch: str = None, codigo: str = None, 
         instrucoes_extras: str = ""):
    """
    Função principal do agente revisor
    """
    print(f"Executando análise: {tipo_analise}")
    print(f"Repositório: {repositorio}")
    
    # Simular análise
    resultado = f"""
# Análise {tipo_analise.title()}

## Repositório Analisado
{repositorio or 'Código fornecido diretamente'}

## Resultado da Análise
Esta é uma análise de exemplo. 

## Recomendações
1. Implementar análise real baseada no tipo
2. Integrar com ferramentas de análise
3. Retornar insights específicos

## Instruções Extras
{instrucoes_extras}
"""
    
    return {
        "tipo_analise": tipo_analise,
        "resultado": resultado.strip()
    }

# Lista de análises válidas (compatível com o backend)
analises_validas = [
    "design", "pentest", "seguranca", "terraform", 
    "relatorio_teste_unitario", "escrever_testes"
]
'''
    
    return sample_code

if __name__ == "__main__":
    main()
    
    # Oferecer criar arquivo de exemplo
    response = input("\n❓ Deseja criar um arquivo de exemplo agents/agente_revisor.py? (s/n): ")
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        agents_dir = Path(__file__).parent / 'agents'
        agents_dir.mkdir(exist_ok=True)
        
        agente_file = agents_dir / 'agente_revisor.py'
        with open(agente_file, 'w', encoding='utf-8') as f:
            f.write(create_sample_agente_revisor())
        
        print(f"✅ Arquivo criado: {agente_file}")
        print("💡 Agora execute novamente o backend para testar!")