from fastapi_pagination import Page

from primeagent.helpers.base_model import BaseModel
from primeagent.services.database.models.flow.model import Flow
from primeagent.services.database.models.folder.model import FolderRead


class FolderWithPaginatedFlows(BaseModel):
    folder: FolderRead
    flows: Page[Flow]
