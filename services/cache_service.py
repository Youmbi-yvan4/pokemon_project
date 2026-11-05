import threading
from dataclasses import dataclass
from typing import Any

from cachetools import TTLCache


DEFAULT_CACHE_TTL = 3600
DEFAULT_CACHE_MAX_SIZE = 5000


@dataclass
class CacheStatistics:
    hits: int = 0
    misses: int = 0
    sets: int = 0


class CacheService:
    def __init__(
        self,
        ttl=DEFAULT_CACHE_TTL,
        max_size=DEFAULT_CACHE_MAX_SIZE,
    ):
        if ttl <= 0:
            raise ValueError(
                "Le TTL doit être supérieur à zéro."
            )

        if max_size <= 0:
            raise ValueError(
                "La taille maximale du cache doit être "
                "supérieure à zéro."
            )

        self.ttl = ttl
        self.max_size = max_size

        self.cache = TTLCache(
            maxsize=max_size,
            ttl=ttl,
        )

        self.statistics = CacheStatistics()

        self.lock = threading.RLock()

    def get(self, key):
        with self.lock:
            if key in self.cache:
                self.statistics.hits += 1

                return True, self.cache[key]

            self.statistics.misses += 1

            return False, None

    def set(
        self,
        key,
        value: Any,
    ):
        with self.lock:
            self.cache[key] = value

            self.statistics.sets += 1

    def delete(self, key):
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True

            return False

    def clear(self):
        with self.lock:
            self.cache.clear()

            self.statistics = CacheStatistics()

    def size(self):
        with self.lock:
            return len(self.cache)

    def contains(self, key):
        with self.lock:
            return key in self.cache

    def get_statistics(self):
        with self.lock:
            hits = self.statistics.hits
            misses = self.statistics.misses
            sets = self.statistics.sets

            total_requests = hits + misses

            if total_requests == 0:
                hit_rate = 0.0

            else:
                hit_rate = (
                    hits
                    / total_requests
                    * 100
                )

            return {
                "hits": hits,
                "misses": misses,
                "sets": sets,
                "size": len(self.cache),
                "max_size": self.max_size,
                "ttl_seconds": self.ttl,
                "hit_rate": hit_rate,
            }


# Cache principal utilisé par l'application.
#
# TTL = 3600 secondes = 1 heure.
api_cache = CacheService(
    ttl=DEFAULT_CACHE_TTL,
    max_size=DEFAULT_CACHE_MAX_SIZE,
)


def build_pokemon_cache_key(identifier):
    normalized_identifier = str(
        identifier
    ).strip().lower()

    return f"pokemon:{normalized_identifier}"


def build_type_cache_key(type_identifier):
    normalized_type = str(
        type_identifier
    ).strip().lower()

    return f"type:{normalized_type}"