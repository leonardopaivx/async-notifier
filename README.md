# Async-Notifier

**Async-Notifier** é um microserviço de notificação assíncrona construído com FastAPI, aio-pika (RabbitMQ) e pipelines de processamento extensíveis.

## Branches

- **main-challenge-branch**: código exatamente como estava até o horário limite do desafio.
- **main**: branch principal com ajustes e correções feitos após o horário limite, para corrigir bugs e problemas de estabilidade.

**Observação:**  
Após o horário limite do desafio, realizei algumas alterações no código e subi na branch `main` para corrigir alguns bugs e problemas que estavam quebrando a aplicação. A versão original, com o código existente até o prazo, está disponível na branch `main-challenge-branch`.

## Tecnologias

- Python 3.11+
- FastAPI
- aio-pika (RabbitMQ)
- Pydantic / pydantic-settings
- Docker & Docker Compose
- pytest / pytest-asyncio

## Pré-requisitos

- Docker e Docker Compose

## Instalação e execução

### 1. Usando Docker Compose

```bash
# clone o repositório
git clone git@github.com:leonardopaivx/async-notifier.git
cd async-notifier

# configure variáveis em .env (exemplo já incluído)
# RABBIT_URL, ENTRY_QUEUE, RETRY_QUEUE, VALIDATION_QUEUE, DLQ_QUEUE

# suba todos os serviços (API, consumidores, RabbitMQ)
docker-compose up --build
```

- **API** disponível em `http://localhost:8000`
- **Swagger UI** em `http://localhost:8000/docs`
- **RabbitMQ Management** em `http://localhost:15672` (usuário/senha: `guest`/`guest`)

### 2. Execução local (sem Docker)

```bash
# clone e entre no diretório
git clone https://github.com/SEU_USUARIO/async-notifier.git
cd async-notifier

# criar e ativar virtualenv
python3 -m venv .venv
source .venv/bin/activate

# instalar dependências
pip install -r requirements.txt

# iniciar RabbitMQ local (ou via Docker)
rabbitmq-server &
# ou docker run ... rabbitmq:3-management

# executar API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# em terminais separados, executar consumidores:
python app/consumers/entry_processor.py
python app/consumers/retry_processor.py
python app/consumers/validation_processor.py
python app/consumers/dlq_processor.py
```

## Endpoints

- `POST /api/notify`
  Dispara uma nova notificação.
  **Request** (JSON):

  ```json
  {
    "message_content": "Conteúdo da mensagem",
    "notification_type": "EMAIL" // ou SMS, PUSH
  }
  ```

  **Response**:

  ```json
  {
    "message_id": "<UUID>",
    "trace_id": "<UUID>"
  }
  ```

- `GET /api/notification/status/{trace_id}`
  Retorna status e histórico da notificação.
  **Response** (JSON):

  ```json
  {
    "trace_id": "<UUID>",
    "message_id": "<UUID>",
    "message_content": "...",
    "notification_type": "EMAIL",
    "status": "SENT_SUCCESS",
    "history": [
      { "status": "RECEIVED", "timestamp": "..." },
      { "status": "...", "timestamp": "..." }
    ]
  }
  ```

- `GET /health`
  Verifica se a fila de entrada existe e retorna `{"status":"ok"}`.

## Testes

Para rodar unit tests:

```bash
pytest
```

## Estrutura de diretórios

```
notification_system/
├── app/
│   ├── config.py           # configurações via pydantic-settings
│   ├── constants.py        # enums de status
│   ├── rabbit.py           # gerenciador de conexão RabbitMQ
│   ├── memory_store.py     # armazenamento in-memory de rastreamento
│   ├── schemas.py          # modelos Pydantic
│   ├── main.py             # aplicação FastAPI e lógica de publicação
│   └── consumers/          # pipelines de processamento
│       ├── base_processor.py
│       ├── entry_processor.py
│       ├── retry_processor.py
│       ├── validation_processor.py
│       └── dlq_processor.py
├── tests/
│   └── test_publisher.py   # teste isolado de publicação
├── Dockerfile              # imagem Python e app
├── docker-compose.yml      # orquestra serviços
├── requirements.txt        # dependências Python
├── .env-example            # exemplo de variáveis de ambiente
└── README.md               # este guia
```

## Contribuição

1. Faça um _fork_ do projeto
2. Crie uma _branch_ com sua feature: `git checkout -b feature/minha-feature`
3. Faça _commit_ das alterações: `git commit -m 'Add minha feature'`
4. _Push_ para seu repositório: `git push origin feature/minha-feature`
5. Abra um _Pull Request_
