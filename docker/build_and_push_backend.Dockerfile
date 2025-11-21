# syntax=docker/dockerfile:1
# Keep this syntax directive! It's used to enable Docker BuildKit

ARG PRIMEAGENT_IMAGE
FROM $PRIMEAGENT_IMAGE

RUN rm -rf /app/.venv/primeagent/frontend

CMD ["python", "-m", "primeagent", "run", "--host", "0.0.0.0", "--port", "7860", "--backend-only"]
