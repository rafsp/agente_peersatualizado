import os
from openai import OpenAI
from typing import Dict
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar cliente OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    # Tentar obter de outras formas para compatibilidade
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
if not OPENAI_API_KEY:
    raise ValueError(
        "❌ A chave da API da OpenAI não foi encontrada!\n"
        "Configure a variável de ambiente OPENAI_API_KEY ou adicione no arquivo .env:\n"
        "OPENAI_API_KEY=sua_chave_aqui"
    )

print(f"✅ OpenAI API configurada (chave: {OPENAI_API_KEY[:10]}...)")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def carregar_prompt(tipo_analise: str) -> str:
    """Carrega o conteúdo do arquivo de prompt correspondente."""
    # Ajustar caminho para funcionar tanto no desenvolvimento quanto em produção
    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_prompt = os.path.join(base_dir, 'prompt', f'{tipo_analise}.md')
    
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"✅ Prompt carregado: {caminho_prompt}")
            return content
    except FileNotFoundError:
        print(f"❌ Arquivo de prompt não encontrado: {caminho_prompt}")
        # Tentar caminho alternativo (para compatibilidade)
        caminho_alternativo = os.path.join(base_dir, 'prompts', f'{tipo_analise}.md')
        try:
            with open(caminho_alternativo, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ Prompt carregado (caminho alternativo): {caminho_alternativo}")
                return content
        except FileNotFoundError:
            raise ValueError(f"Arquivo de prompt para '{tipo_analise}' não encontrado em:\n- {caminho_prompt}\n- {caminho_alternativo}")

def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str = "",
    model_name: str = "gpt-4.1",  # Modelo mais econômico por padrão
    max_token_out: int = 3000
) -> str:
    """
    Executa análise de código usando a API do ChatGPT
    
    Args:
        tipo_analise: Tipo de análise (design, pentest, seguranca, terraform)
        codigo: Código fonte para analisar
        analise_extra: Instruções extras do usuário
        model_name: Modelo da OpenAI a usar
        max_token_out: Máximo de tokens na resposta
    
    Returns:
        Resultado da análise em formato markdown
    """
    
    print(f"🔍 Iniciando análise {tipo_analise} com modelo {model_name}")
    
    try:
        # Carregar prompt do sistema
        prompt_sistema = carregar_prompt(tipo_analise)
        
        # Preparar mensagens
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": f"CÓDIGO PARA ANÁLISE:\n\n{codigo}"}
        ]
        
        # Adicionar instruções extras se fornecidas
        if analise_extra and analise_extra.strip():
            mensagens.append({
                "role": "user", 
                "content": f"INSTRUÇÕES EXTRAS DO USUÁRIO:\n{analise_extra}"
            })
        else:
            mensagens.append({
                "role": "user",
                "content": "Nenhuma instrução extra fornecida pelo usuário."
            })
        
        print(f"📤 Enviando requisição para OpenAI...")
        print(f"📊 Tokens estimados: ~{len(codigo)//4} (código) + {len(prompt_sistema)//4} (prompt)")
        
        # Fazer chamada para a API
        response = openai_client.chat.completions.create(
            model=model_name,
            messages=mensagens,
            temperature=0.3,  # Reduzir para respostas mais consistentes
            max_tokens=max_token_out,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        # Extrair resposta
        conteudo_resposta = response.choices[0].message.content.strip()
        
        # Log de sucesso
        tokens_usados = response.usage.total_tokens if response.usage else "N/A"
        print(f"✅ Análise concluída! Tokens usados: {tokens_usados}")
        print(f"📝 Tamanho da resposta: {len(conteudo_resposta)} caracteres")
        
        return conteudo_resposta
        
    except Exception as e:
        error_msg = f"Erro ao comunicar com a OpenAI para análise '{tipo_analise}': {str(e)}"
        print(f"❌ {error_msg}")
        
        # Fornecer informações de debug úteis
        if "rate_limit" in str(e).lower():
            error_msg += "\n💡 Dica: Aguarde alguns minutos antes de tentar novamente (rate limit)."
        elif "insufficient_quota" in str(e).lower():
            error_msg += "\n💡 Dica: Verifique se há créditos suficientes na sua conta OpenAI."
        elif "invalid_api_key" in str(e).lower():
            error_msg += "\n💡 Dica: Verifique se a chave OPENAI_API_KEY está correta."
        
        raise RuntimeError(error_msg) from e

def test_openai_connection():
    """Testa a conexão com a API da OpenAI"""
    try:
        print("🧪 Testando conexão com OpenAI...")
        response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
        print("✅ Conexão com OpenAI funcionando!")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão com OpenAI: {e}")
        return False

if __name__ == "__main__":
    # Teste básico quando executado diretamente
    print("🚀 Testando configuração do revisor geral...")
    
    if test_openai_connection():
        print("✅ Tudo configurado corretamente!")
    else:
        print("❌ Há problemas na configuração. Verifique a chave da API.")
    
    # Listar prompts disponíveis
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(base_dir, 'prompt')
    if os.path.exists(prompt_dir):
        prompts = [f.replace('.md', '') for f in os.listdir(prompt_dir) if f.endswith('.md')]
        print(f"📋 Prompts disponíveis: {prompts}")
    else:
        print("⚠️ Diretório de prompts não encontrado")