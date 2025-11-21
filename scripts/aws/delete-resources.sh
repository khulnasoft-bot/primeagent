# aws cloudformation delete-stack --stack-name PrimeagentAppStack
aws ecr delete-repository --repository-name primeagent-backend-repository --force
# aws ecr delete-repository --repository-name primeagent-frontend-repository --force
# aws ecr describe-repositories --output json | jq -re ".repositories[].repositoryName"