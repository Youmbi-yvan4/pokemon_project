import asyncio
from collections import defaultdict
from threading import Lock

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse


app = FastAPI(
    title="API locale de simulation",
    description=(
        "API locale utilisée pour les tests de charge "
        "du mini-projet Pokémon."
    ),
    version="1.0.0",
)


request_counters = defaultdict(int)
counter_lock = Lock()


def increment_counter(route_name):
    with counter_lock:
        request_counters[route_name] += 1

        return request_counters[route_name]


def get_all_counters():
    with counter_lock:
        return dict(request_counters)


def reset_all_counters():
    with counter_lock:
        request_counters.clear()


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "pokemon-load-test-mock-api",
    }


@app.get("/metrics")
async def metrics():
    return {
        "request_counters": get_all_counters(),
    }


@app.post("/reset")
async def reset_metrics():
    reset_all_counters()

    return {
        "message": "Compteurs réinitialisés."
    }


@app.get("/data1")
async def data1(
    latency_ms: int = Query(
        default=20,
        ge=0,
        le=5000,
    ),
):
    request_number = increment_counter(
        "data1"
    )

    await asyncio.sleep(
        latency_ms / 1000
    )

    return {
        "route": "data1",
        "request_number": request_number,
        "message": "Réponse data1 réussie.",
    }


@app.get("/data2")
async def data2(
    latency_ms: int = Query(
        default=30,
        ge=0,
        le=5000,
    ),
):
    request_number = increment_counter(
        "data2"
    )

    await asyncio.sleep(
        latency_ms / 1000
    )

    if request_number % 10 == 0:
        return JSONResponse(
            status_code=429,
            headers={
                "Retry-After": "0.1",
            },
            content={
                "route": "data2",
                "request_number": request_number,
                "error": "Too Many Requests",
            },
        )

    return {
        "route": "data2",
        "request_number": request_number,
        "message": "Réponse data2 réussie.",
    }


@app.get("/data3")
async def data3(
    latency_ms: int = Query(
        default=40,
        ge=0,
        le=5000,
    ),
):
    request_number = increment_counter(
        "data3"
    )

    await asyncio.sleep(
        latency_ms / 1000
    )

    if request_number % 13 == 0:
        return JSONResponse(
            status_code=500,
            content={
                "route": "data3",
                "request_number": request_number,
                "error": "Internal Server Error",
            },
        )

    if request_number % 8 == 0:
        return JSONResponse(
            status_code=503,
            content={
                "route": "data3",
                "request_number": request_number,
                "error": "Service Unavailable",
            },
        )

    return {
        "route": "data3",
        "request_number": request_number,
        "message": "Réponse data3 réussie.",
    }