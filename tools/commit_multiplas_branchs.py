# tools/commit_multiplas_branchs.py - CORREÇÃO MÍNIMA DO ERRO 404

import json
from github import GithubException
from tools import github_connector

def _processar_uma_branch(
    repo,
    nome_branch: str,
    branch_de_origem: str,
    branch_alvo_do_pr: str,
    mensagem_pr: str,
    descricao_pr: str,
    conjunto_de_mudancas: list
):
    print(f"\n--- Processando o Lote para a Branch: '{nome_branch}' ---")
    
    # 1. Criação da Branch (COM CORREÇÃO DO 404)
    print(f"Criando ou reutilizando a branch '{nome_branch}' a partir de '{branch_de_origem}'...")
    try:
        # CORREÇÃO: Verificar se a branch de origem existe primeiro
        try:
            ref_base = repo.get_git_ref(f"heads/{branch_de_origem}")
        except GithubException as e:
            if e.status == 404:
                print(f"⚠️ Branch '{branch_de_origem}' não encontrada, usando branch padrão")
                branch_de_origem = repo.default_branch
                ref_base = repo.get_git_ref(f"heads/{branch_de_origem}")
            else:
                raise

        # Tentar criar a nova branch
        repo.create_git_ref(ref=f"refs/heads/{nome_branch}", sha=ref_base.object.sha)
        print(f"✅ Branch '{nome_branch}' criada com sucesso.")
    except GithubException as e:
        if e.status == 422 and "Reference already exists" in str(e.data):
            print(f"⚠️ Branch '{nome_branch}' já existe. Os commits serão adicionados a ela.")
        else:
            print(f"❌ Erro ao criar branch: {e}")
            raise

    # 2. Loop de Commits (MANTIDO ORIGINAL COM PEQUENAS MELHORIAS)
    if not conjunto_de_mudancas:
        print("⚠️ Nenhuma mudança para aplicar nesta branch.")
        return

    print("📝 Iniciando a aplicação dos arquivos (um commit por arquivo)...")
    commits_realizados = 0
    
    for mudanca in conjunto_de_mudancas:
        caminho = mudanca.get("caminho_do_arquivo")
        conteudo = mudanca.get("conteudo")
        justificativa = mudanca.get("justificativa", "")

        # CORREÇÃO: Validações mais rigorosas
        if conteudo is None:
            print(f"  [IGNORADO] ⚠️ Arquivo '{caminho}' tem conteúdo nulo (None).")
            continue
        if not caminho:
            print(f"  [IGNORADO] ⚠️ Mudança sem caminho de arquivo.")
            continue
        if conteudo == "":
            print(f"  [IGNORADO] ⚠️ Arquivo '{caminho}' tem conteúdo vazio.")
            continue

        sha_arquivo_existente = None
        try:
            arquivo_existente = repo.get_contents(caminho, ref=nome_branch)
            sha_arquivo_existente = arquivo_existente.sha
        except GithubException as e:
            if e.status != 404:
                print(f"❌ Erro ao verificar arquivo '{caminho}': {e}")
                continue
        
        try:
            assunto_commit = f"feat: {caminho}" if not sha_arquivo_existente else f"refactor: {caminho}"
            commit_message_completo = f"{assunto_commit}\n\n{justificativa}" if justificativa else assunto_commit

            if sha_arquivo_existente:
                repo.update_file(
                    path=caminho, 
                    message=commit_message_completo, 
                    content=conteudo, 
                    sha=sha_arquivo_existente, 
                    branch=nome_branch
                )
                print(f"  ✅ [MODIFICADO] {caminho}")
            else:
                repo.create_file(
                    path=caminho, 
                    message=commit_message_completo, 
                    content=conteudo, 
                    branch=nome_branch
                )
                print(f"  ✅ [CRIADO] {caminho}")
            
            commits_realizados += 1
            
        except GithubException as e:
            print(f"❌ Erro ao commitar arquivo '{caminho}': {e}")
            
    print(f"📊 Aplicação de commits concluída: {commits_realizados}/{len(conjunto_de_mudancas)} arquivos processados")

    # 3. Criação do Pull Request (APENAS SE HOUVE COMMITS)
    if commits_realizados > 0:
        try:
            print(f"\n🔄 Criando Pull Request de '{nome_branch}' para '{branch_alvo_do_pr}'...")
            pr_body = descricao_pr if descricao_pr else mensagem_pr
            pr = repo.create_pull(
                title=mensagem_pr, 
                body=pr_body, 
                head=nome_branch, 
                base=branch_alvo_do_pr
            )
            print(f"🎉 Pull Request criado com sucesso! {pr.html_url}")
        except GithubException as e:
            if e.status == 422 and "A pull request for these commits already exists" in str(e.data.get('message', '')):
                print(f"⚠️ Pull Request para a branch '{nome_branch}' já existe.")
            else:
                print(f"❌ Erro ao criar Pull Request: {e}")
    else:
        print(f"⚠️ Nenhum commit foi realizado, pulando criação de PR")

def processar_e_subir_mudancas_agrupadas(
    nome_repo: str,
    dados_agrupados,
    base_branch: str = "main"
):
    """
    Função principal que orquestra a criação de múltiplas branches e PRs
    (MANTIDA ORIGINAL COM CORREÇÕES MÍNIMAS)
    """
    try:
        if isinstance(dados_agrupados, str):
            dados_agrupados = json.loads(dados_agrupados)

        print("🚀 --- Iniciando o Processo de Pull Requests Empilhados ---")
        repo = github_connector.connection(repositorio=nome_repo)
        print(f"✅ Conectado ao repositório: {repo.full_name}")

        # CORREÇÃO: Verificar se a branch base existe
        branch_anterior = base_branch
        try:
            repo.get_git_ref(f"heads/{base_branch}")
            print(f"✅ Branch base '{base_branch}' encontrada")
        except GithubException as e:
            if e.status == 404:
                print(f"⚠️ Branch '{base_branch}' não encontrada, usando branch padrão")
                branch_anterior = repo.default_branch
                print(f"✅ Usando branch padrão: {branch_anterior}")
            else:
                raise
        
        # Processar grupos (MANTIDO ORIGINAL)
        lista_de_grupos = dados_agrupados.get("grupos", [])
        
        if not lista_de_grupos:
            print("⚠️ Nenhum grupo de mudanças encontrado para processar.")
            return

        print(f"📋 Processando {len(lista_de_grupos)} grupo(s) de mudanças...")

        grupos_processados = 0
        for grupo_atual in lista_de_grupos:
            nome_da_branch_atual = grupo_atual.get("branch_sugerida")
            resumo_do_pr = grupo_atual.get("titulo_pr", "Refatoração Automática")
            descricao_do_pr = grupo_atual.get("resumo_do_pr", "")
            conjunto_de_mudancas = grupo_atual.get("conjunto_de_mudancas", [])

            # Validação básica
            if not nome_da_branch_atual:
                print("⚠️ Um grupo foi ignorado por não ter uma 'branch_sugerida'.")
                continue

            # CORREÇÃO: Verificar se há mudanças válidas
            mudancas_validas = [
                m for m in conjunto_de_mudancas 
                if m.get('conteudo') is not None and m.get('conteudo') != ""
            ]
            
            if not mudancas_validas:
                print(f"⚠️ GRUPO IGNORADO: '{nome_da_branch_atual}' - Sem mudanças válidas para aplicar")
                continue

            print(f"\n📦 Processando grupo: '{nome_da_branch_atual}' ({len(mudancas_validas)} mudanças)")

            try:
                _processar_uma_branch(
                    repo=repo,
                    nome_branch=nome_da_branch_atual,
                    branch_de_origem=branch_anterior,
                    branch_alvo_do_pr=branch_anterior,
                    mensagem_pr=resumo_do_pr,
                    descricao_pr=descricao_do_pr,
                    conjunto_de_mudancas=mudancas_validas  # Usar apenas mudanças válidas
                )
                
                # Atualizar para próximo grupo (empilhamento)
                branch_anterior = nome_da_branch_atual
                grupos_processados += 1
                print(f"✅ Grupo '{nome_da_branch_atual}' processado com sucesso!")
                
            except Exception as e:
                print(f"❌ Erro no grupo '{nome_da_branch_atual}': {e}")
                # Continuar com próximo grupo sem interromper todo o processo
                continue

        print(f"\n🎉 === PROCESSO CONCLUÍDO ===")
        print(f"✅ {grupos_processados}/{len(lista_de_grupos)} grupos processados com sucesso!")

    except Exception as e:
        print(f"❌ ERRO FATAL NO ORQUESTRADOR: {e}")
        raise