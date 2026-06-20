"""Example: drug lookup plugin."""
from plugins.sdk.base import BasePlugin


class DrugLookupPlugin(BasePlugin):
    name = "drug_lookup" # 药品查询
    version = "0.1.0"

    async def initialize(self):
        pass

    async def shutdown(self):
        pass
