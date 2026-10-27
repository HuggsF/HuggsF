# Hugo Fernandes

**Engenheiro de software back-end** em Recife, com foco em sistemas distribuídos, mensageria e plataformas com IA.
Trabalho com TypeScript, Node.js e Java, e já construí serviços orientados a eventos em produção.

Estou aberto a vagas de **Backend, Platform e AI Engineering** (presencial, híbrido ou remoto).

[LinkedIn](https://www.linkedin.com/in/huggsfmelo) · [hugofmelodev@gmail.com](mailto:hugofmelodev@gmail.com)

---

## Trabalhos selecionados

Cinco projetos, cada um criado para resolver um gargalo clássico de back-end e **medido com carga real**
(Docker Compose em cada um). Os números abaixo vêm das medições que publiquei no LinkedIn.

| Projeto | Problema | Resultado medido |
|---|---|---|
| [csv-stream-importer](https://github.com/HuggsF/csv-stream-importer) | Importar 500 mil linhas de CSV no MySQL sem estourar a memória (Node.js Streams, backpressure, inserts em lote) | Pico de 79 MB de RAM. A abordagem ingênua passa de 590 MB só para ler o arquivo |
| [resilient-pdf-worker](https://github.com/HuggsF/resilient-pdf-worker) | Worker RabbitMQ que gera PDFs com API externa instável (retries, circuit breaker, Dead Letter Queue) | 702 mensagens em 4 cenários de falha, nenhuma perdida. Com a API fora do ar, o circuit breaker deixou passar 46 chamadas em vez de 400 |
| [leaderboard-cache-shield](https://github.com/HuggsF/leaderboard-cache-shield) | Cache stampede em um ranking com 10 mil requisições simultâneas (TTL, Redlock, stale-while-revalidate) | 10.000 queries no MySQL com cache ingênuo contra 1 com stale-while-revalidate. Pior resposta: 13,2 s contra 65 ms |
| [dashboard-bff-graphql](https://github.com/HuggsF/dashboard-bff-graphql) | Over-fetching em um dashboard (BFF com Express, Apollo GraphQL e DataLoader, Clean Architecture e DDD) | Resposta de 9 MB reduzida para 2,6 KB |
| [edtech-cloud-deploy](https://github.com/HuggsF/edtech-cloud-deploy) | Workers Node.js no AWS ECS/Fargate com autoscaling pelo tamanho da fila (Terraform, CI/CD, Prometheus e Grafana) | Medido localmente: 2 workers entregam 1,94× a vazão e 4 entregam 3,22×. Desligamento no meio da carga sem perder tarefas |

Como uso IA nesses projetos: eu defino a especificação, as regras (Clean Architecture, DDD, TypeScript estrito,
testes) e os critérios de aceite. A IA acelera código e testes. Eu cuido dos contratos, dos limites entre camadas e
do comportamento sob falha.

---

## Stack

**Nos repositórios acima:** TypeScript, Node.js, RabbitMQ, Redis, MySQL, GraphQL (Apollo), Docker, Terraform, AWS (ECS/Fargate), Prometheus, Grafana.

**Em produção, em trabalhos anteriores (código privado):** Java, C#/.NET, Kafka, MongoDB, PostgreSQL, Pinecone, Python/FastAPI, Angular.

**Práticas:** TDD, Clean Architecture, DDD, mensageria idempotente, observabilidade, CI/CD.

---

## Experiência

- **UserIn** (2025 até agora): arquitetura e desenvolvimento de uma plataforma de inteligência de conversão com IA. Microsserviços em TypeScript, eventos com Kafka, MongoDB e busca vetorial.
- **SendSpeed** (2024 a 2025): migração de serviços legados para microsserviços na nuvem, APIs REST e mensageria com RabbitMQ.
- **Mobs2** (2022 a 2024) e **Dois S Operation** (2020 a 2022): APIs e microsserviços em C#, Java e PHP, e front-end em Angular.

---

## Second Brain (versão aberta)

Motor local de conhecimento e orquestração de agentes: orquestrador em grafo com 7 nós, circuit breakers,
aprovação humana, quality gates, política de comandos e servidor MCP. Python, com interface em React.

[HuggsF/second-brain-open](https://github.com/HuggsF/second-brain-open)
