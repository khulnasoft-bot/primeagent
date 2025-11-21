from primeagent.services.base import Service
from primeagent.services.factory import ServiceFactory
from primeagent.services.job_queue.service import JobQueueService


class JobQueueServiceFactory(ServiceFactory):
    def __init__(self):
        super().__init__(JobQueueService)

    def create(self) -> Service:
        return JobQueueService()
