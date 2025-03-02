# Documentação - Realmate Challenge API

## Requisitos do Sistema

- Python 3.13 ou superior
- Poetry (gerenciador de dependências)

## Configuração do Ambiente

### 1. Instalar o Poetry

Caso ainda não tenha o Poetry instalado:

```bash
pip install poetry
```

### 2. Clonar o Repositório

```bash
git clone <url-do-repositorio>
cd realmate-challenge
```

### 3. Instalar Dependências

```bash
poetry install
```

### 4. Ativar o Ambiente Virtual

```bash
poetry shell
```

## Executando a Aplicação

### 1. Aplicar Migrações

```bash
python manage.py migrate
```

### 2. Iniciar o Servidor de Desenvolvimento

```bash
python manage.py runserver
```

O servidor estará disponível em: http://localhost:8000/

## Estrutura da API

A API possui dois endpoints principais:

1. **Webhook** (`/webhook/`): Para receber eventos de conversas e mensagens
2. **Detalhes da Conversa** (`/conversations/{id}/`): Para consultar conversas e suas mensagens

## Testando a API

### Executando Testes Automatizados

Para executar todos os testes:

```bash
python manage.py test api
```

Para executar um teste específico:

```bash
python manage.py test api.tests.WebhookTestCase.test_create_new_conversation
```

### Testes Manuais com cURL ou Postman

#### 1. Criar uma Nova Conversa

```bash
curl -X POST http://localhost:8000/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "NEW_CONVERSATION",
    "timestamp": "2025-03-01T10:20:41.349308",
    "data": {
        "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}'
```

#### 2. Adicionar Mensagem a uma Conversa

```bash
curl -X POST http://localhost:8000/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "NEW_MESSAGE",
    "timestamp": "2025-03-01T10:20:42.349308",
    "data": {
        "id": "49108c71-4dca-4af3-9f32-61bc745926e2",
        "direction": "RECEIVED",
        "content": "Olá, tudo bem?",
        "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}'
```

#### 3. Fechar uma Conversa

```bash
curl -X POST http://localhost:8000/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "CLOSE_CONVERSATION",
    "timestamp": "2025-03-01T10:20:45.349308",
    "data": {
        "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}'
```

#### 4. Consultar uma Conversa

```bash
curl http://localhost:8000/conversations/6a41b347-8d80-4ce9-84ba-7af66f369f6a/
```

## Regras de Negócio

1. Toda conversa inicia com status `OPEN`
2. Uma conversa com status `CLOSED` não pode receber novas mensagens
3. As mensagens estão sempre associadas a uma conversa existente
4. Os IDs de conversas e mensagens são UUIDs únicos