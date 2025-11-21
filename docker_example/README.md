# Running PrimeAgent with Docker

This guide will help you get PrimeAgent up and running using Docker and Docker Compose.

## Prerequisites

- Docker
- Docker Compose

## Steps

1. Clone the PrimeAgent repository:

   ```sh
   git clone https://github.com/khulnasoft/primeagent.git
   ```

2. Navigate to the `docker_example` directory:

   ```sh
   cd primeagent/docker_example
   ```

3. Run the Docker Compose file:

   ```sh
   docker compose up
   ```

PrimeAgent will now be accessible at [http://localhost:7860/](http://localhost:7860/).

## Docker Compose Configuration

The Docker Compose configuration spins up two services: `primeagent` and `postgres`.

### PrimeAgent Service

The `primeagent` service uses the `khulnasoft/primeagent:latest` Docker image and exposes port 7860. It depends on the `postgres` service.

Environment variables:

- `PRIMEAGENT_DATABASE_URL`: The connection string for the PostgreSQL database.
- `PRIMEAGENT_CONFIG_DIR`: The directory where PrimeAgent stores logs, file storage, monitor data, and secret keys.

Volumes:

- `primeagent-data`: This volume is mapped to `/app/primeagent` in the container.

### PostgreSQL Service

The `postgres` service uses the `postgres:16` Docker image and exposes port 5432.

Environment variables:

- `POSTGRES_USER`: The username for the PostgreSQL database.
- `POSTGRES_PASSWORD`: The password for the PostgreSQL database.
- `POSTGRES_DB`: The name of the PostgreSQL database.

Volumes:

- `primeagent-postgres`: This volume is mapped to `/var/lib/postgresql/data` in the container.

## Switching to a Specific PrimeAgent Version

If you want to use a specific version of PrimeAgent, you can modify the `image` field under the `primeagent` service in the Docker Compose file. For example, to use version 1.0-alpha, change `khulnasoft/primeagent:latest` to `khulnasoft/primeagent:1.0-alpha`.
