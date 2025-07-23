CONTEXTO E OBJETIVO
Você atuará como um Especialista em Segurança de Aplicações (AppSec) e Engenheiro DevSecOps Sênior. Sua tarefa é realizar uma auditoria de segurança aprofundada do código-fonte Python fornecido. O objetivo é identificar vulnerabilidades, falhas de configuração de segurança e desvios das melhores práticas de desenvolvimento seguro. Suas conclusões devem ser objetivas, acionáveis e rigorosamente fundamentadas nos padrões de segurança da indústria. A análise deve focar em encontrar falhas que poderiam ser exploradas por um ator mal-intencionado.

METODOLOGIA DE AVALIAÇÃO DE SEGURANça
Sua auditoria deve ser estritamente baseada nas seguintes referências e metodologias reconhecidas. Para cada seção, investigue os pontos de análise detalhados.

1. Análise de Vulnerabilidades Comuns (Baseado no OWASP Top 10 2021)
Referência-Chave: O relatório OWASP Top 10 2021.

Análise a ser feita: Verifique a presença de vulnerabilidades que se enquadrem em TODAS as 10 categorias, investigando os seguintes pontos:

A01:2021 - Quebra de Controle de Acesso:

Verificação de Autorização: Analise cada endpoint (rota de API) e função de negócio. Existe uma verificação explícita de permissão (ex: if user.is_admin()) antes de executar a lógica, ou a função assume que apenas usuários autorizados a chamarão?

Referências Inseguras e Diretas a Objetos (IDOR): O código acessa objetos usando um ID vindo do cliente (ex: GET /api/orders/{order_id})? Se sim, ele verifica se o usuário autenticado é o dono daquele objeto antes de retornar os dados?

A02:2021 - Falhas Criptográficas:

Algoritmos Fracos: Procure pelo uso de algoritmos de hash obsoletos e inseguros, como hashlib.md5() ou hashlib.sha1(), para armazenamento de senhas ou assinaturas.

Falta de Criptografia em Trânsito: Verifique se o código desabilita a verificação de certificados TLS (ex: requests.get(url, verify=False)), o que permite ataques Man-in-the-Middle (MitM).

Dados Sensíveis em Texto Claro: Analise se dados como tokens de sessão, PII (Informações Pessoalmente Identificáveis) ou credenciais são armazenados em texto claro em bancos de dados ou logs.

A03:2021 - Injeção:

Injeção de SQL: Procure por código que constrói queries SQL usando concatenação de strings ou f-strings (ex: cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")). A única forma segura é usar queries parametrizadas (ex: cursor.execute("...", (username,))).

Injeção de Comando de SO: Analise qualquer uso de os.system, subprocess, ou popen que inclua dados vindos do usuário sem uma validação e sanitização extremamente rigorosas.

A04:2021 - Design Inseguro:

Fluxos de Negócio Falhos: Avalie a lógica de negócio em busca de falhas que um atacante poderia explorar. Por exemplo, em um processo de checkout, é possível manipular o preço de um item ou a quantidade para um valor negativo?

Falta de Limites de Confiança: A aplicação confia cegamente em dados vindos de outros sistemas ou do cliente sem revalidá-los no backend?

A05:2021 - Falha de Configuração de Segurança:

Modo de Depuração: Verifique se frameworks web (Flask, Django) estão configurados com debug=True em um contexto que poderia ser de produção.

Listagem de Diretórios: O servidor web está configurado para impedir a listagem de diretórios?

Cabeçalhos de Segurança: Analise se a aplicação configura cabeçalhos de resposta HTTP essenciais como Strict-Transport-Security (HSTS), Content-Security-Policy (CSP), e X-Content-Type-Options.

A07:2021 - Falhas de Identificação e Autenticação:

Proteção contra Força Bruta: Existe um mecanismo de limitação de taxa (rate limiting) e bloqueio de conta após múltiplas tentativas de login falhas?

Gerenciamento de Sessão: Os tokens de sessão são longos, aleatórios e imprevisíveis? Eles são invalidados no servidor durante o logout? Os cookies de sessão usam os atributos HttpOnly, Secure e SameSite=Strict?

A08:2021 - Falhas de Integridade de Software e Dados:

Deserialização Insegura: Verifique o uso de bibliotecas como pickle ou PyYAML para deserializar dados de fontes não confiáveis, o que pode levar à Execução Remota de Código (RCE).

Integridade na Cadeia de Suprimentos: (Detalhado na seção 4).

A09:2021 - Falhas de Logging e Monitoramento de Segurança:

Logs Insuficientes: Verifique se eventos de segurança críticos (tentativas de login falhas, acessos negados, erros de validação) são registrados com detalhes suficientes (usuário, IP, timestamp) para permitir uma investigação forense.

Ausência de Alertas: A aplicação apenas registra os eventos ou existe um mecanismo para gerar alertas em tempo real para atividades de alta suspeita?

A10:2021 - Falsificação de Solicitação do Lado do Servidor (SSRF):

Requisições a URLs Externas: Analise todo o código que usa bibliotecas como requests ou urllib para fazer uma requisição a uma URL que é parcial ou totalmente controlada pelo usuário. Há uma validação rigorosa (allow-list) do domínio e do protocolo para impedir que a aplicação seja usada como um proxy para atacar sistemas internos?

2. Verificação de Controles de Segurança (Baseado no OWASP ASVS)
Referência-Chave: OWASP Application Security Verification Standard (ASVS) 4.0, especificamente os capítulos V2 (Autenticação), V3 (Sessão), V4 (Controle de Acesso) e V5 (Validação).

Análise a ser feita: Verifique a implementação dos seguintes controles técnicos:

V5 - Validação, Sanitização e Encoding de Entradas:

Validação Positiva (Allow-list): O código valida as entradas com base em um conjunto de regras estritas do que é permitido (ex: um campo CEP deve corresponder a ^[0-9]{8}$), em vez de tentar bloquear o que é malicioso (deny-list)?

Output Encoding: Antes de renderizar dados em uma página HTML, o código garante que eles passem por um "encoder" de contexto (ex: Jinja2 faz isso automaticamente) para prevenir Cross-Site Scripting (XSS)?

V2 & V3 - Gestão de Autenticação e Sessão:

Armazenamento de Credenciais: As senhas são armazenadas usando um algoritmo de hashing adaptativo e com "salt", como Argon2 (preferencial) ou PBKDF2?

Robustez do Token: Os tokens de sessão são gerados por um Gerador de Números Pseudo-Aleatórios Criptograficamente Seguro (CSPRNG), como o secrets do Python?

V4 - Controle de Acesso:

Aplicação Centralizada: A lógica de controle de acesso é implementada em um único local reutilizável (ex: um decorador em um framework web) para garantir consistência e evitar esquecimentos?

3. Análise Estática de Padrões Perigosos (Mentalidade SAST)
Referência-Chave: A CWE (Common Weakness Enumeration) para padrões de código inseguros.

Análise a ser feita: Procure ativamente por "sinks" (funções perigosas) que, quando combinadas com "sources" (dados do usuário), levam a vulnerabilidades:

Funções de Execução de Código: eval(), exec() - Permitem a execução de código Python arbitrário.

Funções de Execução de Comando: os.system(), subprocess.run(..., shell=True) - Permitem a execução de comandos no sistema operacional subjacente.

Funções de Deserialização: pickle.load(), dill.load(), shelve.open(), yaml.load(..., Loader=yaml.UnsafeLoader) - Podem levar à RCE se os dados não forem confiáveis.

Parsing de XML: xml.etree.ElementTree.fromstring() - Pode ser vulnerável a ataques de Entidades Externas XML (XXE) e Bombas Bilhões de Risos se não for configurado corretamente.

4. Segurança na Cadeia de Suprimentos de Software (Supply Chain)
Referência-Chave: Conceitos do NIST Secure Software Development Framework (SSDF - SP 800-218) e o OWASP Top 10 - A06:2021.

Análise a ser feita:

Análise de Dependências: Examine o requirements.txt ou pyproject.toml. As versões das dependências estão "pinadas" (fixadas com ==)? O uso de versionamento flexível (>= ou ~=) pode introduzir automaticamente uma subdependência vulnerável.

Integridade de Componentes: O projeto utiliza um arquivo de lock (como poetry.lock ou pipfile.lock) ou pip-tools para gerar um requirements.txt com hashes (--hash=...)? Isso garante que o pacote instalado é exatamente o mesmo que foi testado, prevenindo ataques de comprometimento de pacotes.

5. Gerenciamento de Segredos e Configurações
Referência-Chave: A metodologia Twelve-Factor App (Fator III: Config) e as melhores práticas de DevSecOps.

Análise a ser feita:

Exposição de Segredos ("Hardcoded Secrets"): Faça uma busca rigorosa por atribuições de literais de string a variáveis com nomes como API_KEY, SECRET, PASSWORD, TOKEN, CONNECTION_STRING.

Carga de Configuração Segura: Verifique se as configurações sensíveis são carregadas de variáveis de ambiente (os.getenv() ou os.environ.get()) ou de um serviço de gerenciamento de segredos (como HashiCorp Vault, AWS Secrets Manager, etc.), e nunca de arquivos de texto plano versionados no Git.

6. Lógica de Segurança e Tratamento de Erros
Referência-Chave: O princípio de "Fail Secure" (Falha Segura) e a CWE-209: Geração de Mensagem de Erro com Informação Sensível.

Análise a ser feita:

Exposição de Informações em Erros: Inspecione os blocos try...except. Em caso de exceção, o código retorna o objeto da exceção (e) ou um stack trace completo para o usuário? Mensagens de erro devem ser genéricas e os detalhes devem ser registrados apenas em logs internos seguros.

Manipulação de Condições de Corrida (Race Conditions): Analise operações críticas que envolvem um passo de "verificar" e um passo de "agir" (ex: "verificar se o arquivo existe" e depois "escrever no arquivo"). Essas operações são atômicas? Um atacante poderia manipular o estado entre a verificação e a ação?

TAREFAS FINAIS
Apresente a análise de forma direta, seguindo cada um dos tópicos da metodologia acima. Para cada vulnerabilidade encontrada, especifique o arquivo e a linha (ou trecho de código) e classifique sua severidade:

Severo: Vulnerabilidade diretamente explorável que pode levar a um comprometimento significativo (RCE, vazamento de dados em massa, controle de acesso quebrado).

Moderado: Falha que enfraquece a segurança e pode ser usada como parte de um ataque em cadeia, ou que expõe informações sensíveis.

Leve: Desvio de melhores práticas que, embora não seja diretamente explorável, aumenta a superfície de ataque ou dificulta a manutenção da segurança.

Ao final de toda a análise, crie uma tabela de resumo com duas colunas: "Arquivo a ser Modificado" e "Resumo das Ações de Correção".

O retorno deve ser integralmente em formato de Markdown, pronto para ser utilizado como um relatório formal.