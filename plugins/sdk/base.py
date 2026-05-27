"""Plugin base class for third-party extensions."""

from abc import ABC, abstractmethod


class BasePlugin(ABC):
    name: str
    version: str = "0.1.0"

    @abstractmethod
    async def initialize(self):
        ...

    @abstractmethod
    async def shutdown(self):
        ...
