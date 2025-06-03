from typing import Generic

from app.data.repository import RepoType, SchemaType, ModelType


class BaseService(Generic[RepoType]):
    def __init__(self, repo: type[RepoType]):
        self.repo = repo
