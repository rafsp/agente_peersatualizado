from agents import agente_revisor

# Teste simples
resultado = agente_revisor.main(
    tipo_analise="design",
    repositorio="rafsp/api-springboot-web-app",
    instrucoes_extras="Focar em arquitetura e SOLID"
)

print("Resultado:", resultado['resultado']['reposta_final'])