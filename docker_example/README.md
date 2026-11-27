# Run PrimeAgent with Docker

This guide will help you get PrimeAgent up and running using Docker and Docker Compose.

## Prerequisites

- Docker
- Docker Compose

## Steps

1. Clone the PrimeAgent repository:

   ```sh
   git clone https://github.com/khulnasoft-bot/primeagent.git
   ```

2. Navigate to the `docker_example` directory:

   ```sh
   cd primeagent/docker_example
   ```

3. Create a `.env` file with the PrimeAgent admin password set:

   ```sh
   PRIMEAGENT_SUPERUSER_PASSWORD=SUPERUSER_PASSWORD
   ```

   Replace `SUPERUSER_PASSWORD` with a strong password for the PrimeAgent superuser.
   The default admin username is `primeagent`.

4. Run the Docker Compose file:

   ```sh
   docker compose up
   ```

PrimeAgent will now be accessible at [http://localhost:7860/](http://localhost:7860/).

## Configure Docker Compose

The Docker Compose configuration spins up two services: `primeagent` and `postgres`.

### PrimeAgent service

The `primeagent` service uses the `khulnasoft/primeagent:latest` Docker image and exposes port 7860. It depends on the `postgres` service.

Environment variables:

- `PRIMEAGENT_DATABASE_URL`: The connection string for the PostgreSQL database.
- `PRIMEAGENT_SUPERUSER_PASSWORD`: The initial admin password. This value is required in `.env`.
- `PRIMEAGENT_CONFIG_DIR`: The directory where PrimeAgent stores logs, file storage, monitor data, and secret keys.

Volumes:

- `primeagent-data`: This volume is mapped to `/app/primeagent` in the container.

### PostgreSQL service

The `postgres` service uses the `postgres:16-trixie` Docker image and exposes port 5432. The image is pinned to a specific Debian base (`trixie`, Debian 13) so the `postgres:16` tag cannot silently roll its underlying OS, which would otherwise produce a glibc collation version mismatch warning on existing data volumes.

Environment variables:

- `POSTGRES_USER`: The username for the PostgreSQL database.
- `POSTGRES_PASSWORD`: The password for the PostgreSQL database.
- `POSTGRES_DB`: The name of the PostgreSQL database.

Volumes:

- `primeagent-postgres`: This volume is mapped to `/var/lib/postgresql/data` in the container.

### Upgrading from a `bookworm`-initialized volume

Earlier versions of this example used `postgres:16`, which initially shipped on Debian Bookworm (glibc 2.36). The pinned image now uses Trixie (glibc 2.41). On the first start against a volume that was initialized under Bookworm, PostgreSQL logs a one-time warning:

```
WARNING: database "primeagent" has a collation version mismatch
DETAIL: The database was created using collation version 2.36, but the operating system provides version 2.41.
```

To clear it, refresh the collation version against the running database (one-off, takes seconds on a typical PrimeAgent database):

```sh
docker compose exec postgres \
  psql -U primeagent -d primeagent \
  -c "REINDEX DATABASE primeagent;" \
  -c "ALTER DATABASE primeagent REFRESH COLLATION VERSION;"
```

Fresh installs are unaffected.

## Switching to a specific PrimeAgent version

If you want to use a specific version of PrimeAgent, you can modify the `image` field under the `primeagent` service in the Docker Compose file. For example, to use version 1.0-alpha, change `khulnasoft/primeagent:latest` to `khulnasoft/primeagent:1.0-alpha`.
