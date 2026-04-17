"""
Cost Guard — monthly budget per user, Redis-backed.

Rule cho bài lab:
- Mỗi user có budget $10 / tháng
- Track spending theo key tháng trong Redis
- Raise 402 khi vượt budget
"""
import os
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from fastapi import HTTPException

try:
    import redis
except ImportError:  # pragma: no cover
    redis = None

logger = logging.getLogger(__name__)

PRICE_PER_1K_INPUT_TOKENS = 0.00015
PRICE_PER_1K_OUTPUT_TOKENS = 0.0006


@dataclass
class UsageRecord:
    user_id: str
    month: str
    input_tokens: int
    output_tokens: int
    request_count: int
    total_cost_usd: float


class CostGuard:
    def __init__(self, monthly_budget_usd: float = 10.0):
        self.monthly_budget_usd = monthly_budget_usd
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._fallback_cache: dict[str, dict[str, float | int]] = {}
        self._redis = None
        if redis is not None:
            try:
                self._redis = redis.from_url(self.redis_url, decode_responses=True)
                self._redis.ping()
            except Exception as exc:  # pragma: no cover
                logger.warning("Redis unavailable, using in-memory fallback: %s", exc)
                self._redis = None

    @staticmethod
    def _month_key() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m")

    def _key(self, user_id: str, month: str) -> str:
        return f"budget:{user_id}:{month}"

    def _read(self, user_id: str, month: str) -> dict[str, float | int]:
        key = self._key(user_id, month)
        if self._redis:
            raw = self._redis.hgetall(key)
            if not raw:
                return {"cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0, "requests": 0}
            return {
                "cost_usd": float(raw.get("cost_usd", 0.0)),
                "input_tokens": int(raw.get("input_tokens", 0)),
                "output_tokens": int(raw.get("output_tokens", 0)),
                "requests": int(raw.get("requests", 0)),
            }
        return self._fallback_cache.get(
            key,
            {"cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0, "requests": 0},
        )

    def _write(self, user_id: str, month: str, data: dict[str, float | int]) -> None:
        key = self._key(user_id, month)
        if self._redis:
            ttl_seconds = 32 * 24 * 3600
            self._redis.hset(
                key,
                mapping={
                    "cost_usd": str(data["cost_usd"]),
                    "input_tokens": str(data["input_tokens"]),
                    "output_tokens": str(data["output_tokens"]),
                    "requests": str(data["requests"]),
                },
            )
            self._redis.expire(key, ttl_seconds)
            return
        self._fallback_cache[key] = data

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        value = (
            (input_tokens / 1000) * PRICE_PER_1K_INPUT_TOKENS
            + (output_tokens / 1000) * PRICE_PER_1K_OUTPUT_TOKENS
        )
        return round(value, 6)

    def check_budget(self, user_id: str, estimated_cost: float = 0.0) -> None:
        month = self._month_key()
        record = self._read(user_id, month)
        projected = float(record["cost_usd"]) + estimated_cost
        if projected > self.monthly_budget_usd:
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "Monthly budget exceeded",
                    "month": month,
                    "used_usd": round(float(record["cost_usd"]), 6),
                    "estimated_next_cost_usd": round(estimated_cost, 6),
                    "budget_usd": self.monthly_budget_usd,
                },
            )

    def record_usage(self, user_id: str, input_tokens: int, output_tokens: int) -> UsageRecord:
        month = self._month_key()
        record = self._read(user_id, month)
        cost = self._estimate_cost(input_tokens, output_tokens)

        updated = {
            "cost_usd": round(float(record["cost_usd"]) + cost, 6),
            "input_tokens": int(record["input_tokens"]) + input_tokens,
            "output_tokens": int(record["output_tokens"]) + output_tokens,
            "requests": int(record["requests"]) + 1,
        }
        self._write(user_id, month, updated)

        return UsageRecord(
            user_id=user_id,
            month=month,
            input_tokens=int(updated["input_tokens"]),
            output_tokens=int(updated["output_tokens"]),
            request_count=int(updated["requests"]),
            total_cost_usd=float(updated["cost_usd"]),
        )

    def get_usage(self, user_id: str) -> dict:
        month = self._month_key()
        record = self._read(user_id, month)
        used = float(record["cost_usd"])
        return {
            "user_id": user_id,
            "month": month,
            "requests": int(record["requests"]),
            "input_tokens": int(record["input_tokens"]),
            "output_tokens": int(record["output_tokens"]),
            "cost_usd": used,
            "budget_usd": self.monthly_budget_usd,
            "budget_remaining_usd": max(0.0, round(self.monthly_budget_usd - used, 6)),
            "budget_used_pct": round((used / self.monthly_budget_usd) * 100, 2),
            "storage": "redis" if self._redis else "memory-fallback",
        }


cost_guard = CostGuard(monthly_budget_usd=10.0)
