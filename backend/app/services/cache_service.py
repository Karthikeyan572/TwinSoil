import hashlib
import json
from typing import Any, Optional

class CacheService:
    def __init__(self):
        self._memory_cache: dict[str, Any] = {}

    def _generate_key(self, prefix: str, data: Any) -> str:
        serialized = json.dumps(data, sort_keys=True, default=str)
        hash_val = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return f"{prefix}:{hash_val}"

    def get(self, prefix: str, key_data: Any) -> Optional[Any]:
        key = self._generate_key(prefix, key_data)
        return self._memory_cache.get(key)

    def set(self, prefix: str, key_data: Any, value: Any):
        key = self._generate_key(prefix, key_data)
        self._memory_cache[key] = value

    def clear(self):
        self._memory_cache.clear()

cache_service = CacheService()
