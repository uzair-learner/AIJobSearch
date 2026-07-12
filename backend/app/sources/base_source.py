from abc import ABC, abstractmethod


class BaseSource(ABC):
    source_name = "base"

    @abstractmethod
    async def fetch(self) -> list[dict]:
        raise NotImplementedError
