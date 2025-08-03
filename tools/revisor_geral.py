import os
from openai import OpenAI
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def carregar_prompt(tipo_analise: str) -> str:
    """Carrega prompt do arquivo correspondente"""
    prompt_path = f"prompts/{tipo_analise}.md"
    
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Prompt padrão se arquivo não existir
        prompts_default = {
            "design": """
Você é um arquiteto de software sênior. Analise o código fornecido focando em:

## Aspectos a Analisar:
1. **Princípios SOLID**
2. **Padrões de Design (GoF)**
3. **Arquitetura geral**
4. **Coesão e acoplamento**
5. **Escalabilidade**

## Formato da Resposta:
- Problemas identificados
- Recomendações específicas
- Código refatorado (quando aplicável)
- Prioridade das mudanças
""",
            "refatoracao": """
Você é um especialista em refatoração. Aplique as seguintes melhorias:

## Objetivos:
1. Aplicar princípios SOLID
2. Remover code smells
3. Melhorar legibilidade
4. Otimizar performance
5. Adicionar documentação

## Entrega:
- Código refatorado completo
- Explicação das mudanças
- Benefícios obtidos
""",
            "escrever_testes": """
Você é um especialista em testes. Crie testes abrangentes para o código:

## Requisitos:
1. Cobertura de casos normais
2. Casos de borda
3. Tratamento de erros
4. Mocks quando necessário
5. Framework pytest

## Estrutura:
- Testes organizados por classe/função
- Nomes descritivos
- AAA pattern (Arrange, Act, Assert)
""",
            "pentest": """
Você é um especialista em segurança ofensiva. Analise o código em busca de:

## Vulnerabilidades:
1. Injeção de código (SQL, XSS, etc.)
2. Autenticação e autorização
3. Exposição de dados sensíveis
4. Configurações inseguras
5. Dependências vulneráveis

## Relatório:
- Vulnerabilidades encontradas
- Nível de risco
- Exploração possível
- Correções recomendadas
""",
            "seguranca": """
Você é um especialista em segurança defensiva. Analise o código focando em:

## Aspectos de Segurança:
1. Validação de entrada
2. Sanitização de dados
3. Controle de acesso
4. Criptografia
5. Logs de segurança

## Relatório:
- Problemas de segurança
- Boas práticas não seguidas
- Melhorias recomendadas
- Código corrigido
""",
            "terraform": """
Você é um especialista em Terraform e Infrastructure as Code. Analise o código focando em:

## Aspectos Terraform:
1. Boas práticas de IaC
2. Segurança de recursos
3. Organização de módulos
4. Estado e versionamento
5. Eficiência de custos

## Relatório:
- Problemas identificados
- Melhorias de segurança
- Otimizações de custo
- Código corrigido
""",
            "agrupamento_design": """
Você é um especialista em organização de código. Agrupe as mudanças de design em commits lógicos:

## Objetivo:
Organizar mudanças em grupos temáticos para commits mais limpos

## Agrupamentos sugeridos:
1. Refatorações de arquitetura
2. Aplicação de padrões
3. Melhorias de performance
4. Documentação

## Saída:
- Grupos de mudanças
- Mensagens de commit sugeridas
- Ordem de aplicação
""",
            "agrupamento_testes": """
Você é um especialista em organização de testes. Agrupe os testes em estrutura lógica:

## Objetivo:
Organizar testes em grupos coerentes e estrutura clara

## Agrupamentos:
1. Testes unitários por módulo
2. Testes de integração
3. Testes de borda
4. Fixtures e mocks

## Saída:
- Estrutura de pastas
- Organização por funcionalidade
- Configuração de testes
"""
        }
        
        return prompts_default.get(tipo_analise, f"""
Você é um especialista em análise de código. 
Analise o código fornecido com foco em: {tipo_analise}

Forneça um relatório detalhado com:
1. Problemas identificados
2. Recomendações de melhoria
3. Boas práticas sugeridas
4. Código refatorado (se aplicável)
""")

def executar_analise_llm(tipo_analise: str,
                        codigo: str,
                        analise_extra: str = "",
                        model_name: str = "gpt-4",  # Mudei para gpt-4 padrão
                        max_token_out: int = 3000) -> str:
    """Executa análise usando OpenAI v1.0+"""
    
    try:
        # Inicializar cliente OpenAI v1.0+
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada no .env")
        
        client = OpenAI(api_key=api_key)
        
        # Verificar modelo disponível
        models_available = ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo-preview"]
        if model_name not in models_available:
            print(f"⚠️ Modelo {model_name} não reconhecido, usando gpt-4")
            model_name = "gpt-4"
        
        # Carregar prompt
        prompt_base = carregar_prompt(tipo_analise)
        
        # Construir prompt completo
        prompt_completo = f"""
{prompt_base}

INSTRUÇÕES EXTRAS DO USUÁRIO:
{analise_extra}

CÓDIGO PARA ANÁLISE:
```
{codigo}
```

Por favor, forneça uma análise detalhada seguindo as diretrizes acima.
"""
        
        print(f"🤖 Enviando para OpenAI (modelo: {model_name})")
        print(f"📄 Tamanho do código: {len(codigo)} caracteres")
        print(f"🎯 Tipo de análise: {tipo_analise}")
        
        # Fazer chamada para OpenAI usando a nova API v1.0+
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system", 
                    "content": "Você é um especialista sênior em análise de código, arquitetura de software e segurança. Forneça análises detalhadas e práticas."
                },
                {
                    "role": "user", 
                    "content": prompt_completo
                }
            ],
            max_tokens=max_token_out,
            temperature=0.3
        )
        
        resultado = response.choices[0].message.content
        print("✅ Análise concluída com sucesso")
        print(f"📊 Tamanho do resultado: {len(resultado)} caracteres")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Erro na análise LLM: {e}")
        
        # Tentar com modelo alternativo em caso de erro
        if "gpt-4" in model_name and "gpt-4" != model_name:
            print("🔄 Tentando novamente com gpt-4...")
            return executar_analise_llm(tipo_analise, codigo, analise_extra, "gpt-4", max_token_out)
        elif model_name == "gpt-4":
            print("🔄 Tentando novamente com gpt-3.5-turbo...")
            return executar_analise_llm(tipo_analise, codigo, analise_extra, "gpt-3.5-turbo", max_token_out)
        else:
            raise

# Função para compatibilidade com código legado
def main(*args, **kwargs):
    """Função para compatibilidade"""
    return executar_analise_llm(*args, **kwargs)