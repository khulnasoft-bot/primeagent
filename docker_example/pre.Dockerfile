FROM khulnasoft/primeagent:1.0-alpha

CMD ["python", "-m", "primeagent", "run", "--host", "0.0.0.0", "--port", "7860"]
