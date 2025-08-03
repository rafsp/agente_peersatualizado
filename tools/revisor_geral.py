# tools/revisor_geral.py - CORREÇÃO APENAS DO TRATAMENTO DE RESPOSTA
import os
from openai import OpenAI
from typing import Dict

def get_openai_key():
    """Obtém chave OpenAI de forma robusta"""
    # Primeiro tenta variáveis de ambiente
    key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY')
    
    if not key:
        # Só tenta Google Colab se disponível
        try:
            from google.colab import userdata
            key = userdata.get('OPENAI_API_KEY')
        except ImportError:
            # Não está no Colab - normal
            pass
        except Exception:
            # Erro no Colab - continua
            pass
    
    if not key:
        raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
    
    return key

# Inicializar cliente OpenAI
OPENAI_API_KEY = get_openai_key()
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def carregar_prompt(tipo_analise: str) -> str:
    """Carrega o conteúdo do arquivo de prompt correspondente."""
    caminho_prompt = os.path.join(os.path.dirname(__file__), 'prompts', f'{tipo_analise}.md')
    try:
        with open(caminho_prompt, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Prompt padrão caso arquivo não encontrado
        return f"""
Você é um especialista em análise de código para o tipo '{tipo_analise}'.
Analise o código fornecido e forneça um relatório detalhado com:

1. **Principais problemas identificados**
2. **Recomendações de melhoria**  
3. **Boas práticas aplicáveis**
4. **Próximos passos sugeridos**

Seja específico e prático nas suas recomendações.
"""

def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    model_name: str,
    max_token_out: int
) -> str:
    """
    Executa análise usando LLM da OpenAI com tratamento robusto da resposta.
    """
    
    prompt_sistema = carregar_prompt(tipo_analise)

    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {'role': 'user', 'content': codigo},
        {
            'role': 'user', 
            'content': f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra and analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'
        }
    ]

    try:
        print(f"🤖 Fazendo chamada para OpenAI...")
        print(f"📊 Modelo: {model_name}")
        print(f"🔤 Max tokens: {max_token_out}")
        print(f"📝 Tamanho do código: {len(codigo)} caracteres")
        
        response = openai_client.chat.completions.create(
            model=model_name,
            messages=mensagens,
            temperature=0.5,
            max_tokens=max_token_out
        )
        
        print(f"✅ Resposta recebida da OpenAI")
        
        # CORREÇÃO: Tratamento robusto da resposta
        if not response:
            print("❌ Response é None")
            raise RuntimeError("Resposta vazia da API OpenAI")
        
        if not response.choices:
            print("❌ Response.choices está vazio")
            raise RuntimeError("Nenhuma escolha na resposta da OpenAI")
        
        choice = response.choices[0]
        if not choice:
            print("❌ Choice é None")
            raise RuntimeError("Primeira escolha é None")
        
        if not choice.message:
            print("❌ Choice.message é None")
            raise RuntimeError("Mensagem da escolha é None")
        
        conteudo_resposta = choice.message.content
        print(f"📄 Conteudo recebido: {type(conteudo_resposta)}")
        
        # CORREÇÃO PRINCIPAL: Verificar se conteudo_resposta é None antes de fazer strip()
        if conteudo_resposta is None:
            print("❌ conteudo_resposta é None - este é o problema!")
            raise RuntimeError("Conteúdo da resposta é None")
        
        # Agora é seguro fazer strip()
        resultado_final = conteudo_resposta.strip()
        
        if not resultado_final:
            print("⚠️ Resultado final está vazio após strip")
            resultado_final = "Análise concluída, mas resposta vazia. Tente novamente."
        
        print(f"✅ Análise concluída! Resposta: {len(resultado_final)} caracteres")
        return resultado_final
        
    except Exception as e:
        error_msg = f"ERRO: Falha na chamada à API da OpenAI para análise '{tipo_analise}'. Causa: {e}"
        print(error_msg)
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e