# PrimeAgent IDE chart

Helm chart for PrimeAgent as IDE with a persistent storage or an external database (for example PostgreSQL).


## Quick start

Install the chart:

```bash
helm repo add primeagent https://khulnasoft.github.io/primeagent
helm repo update
helm install primeagent-ide primeagent/primeagent-ide -n primeagent --create-namespace
```


## Examples
See more examples in the [examples directory](https://github.com/khulnasoft/primeagent/tree/main/examples/primeagent-ide).