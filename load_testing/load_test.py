import argparse
import asyncio
import time
from collections import defaultdict
from collections.abc import Callable

import httpx

from load_testing.models import (
    LoadTestMetrics,
    RequestResult,
)


DEFAULT_BASE_URL = "http://127.0.0.1:8000"

DEFAULT_ROUTES = [
    "/data1",
    "/data2",
    "/data3",
]

RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}


def validate_configuration(
    total_requests,
    batch_size,
    concurrency_limit,
    max_retries,
):
    if total_requests <= 0:
        raise ValueError(
            "Le nombre total de requêtes doit être "
            "supérieur à zéro."
        )

    if batch_size <= 0:
        raise ValueError(
            "La taille du lot doit être supérieure à zéro."
        )

    if concurrency_limit <= 0:
        raise ValueError(
            "La limite de concurrence doit être "
            "supérieure à zéro."
        )

    if max_retries < 0:
        raise ValueError(
            "Le nombre de retries ne peut pas être négatif."
        )


def normalize_base_url(base_url):
    return base_url.rstrip("/")


def calculate_retry_delay(
    response,
    attempt,
    backoff_factor,
):
    retry_after = response.headers.get(
        "Retry-After"
    )

    if retry_after:
        try:
            delay = float(retry_after)

            if delay >= 0:
                return delay

        except ValueError:
            pass

    return backoff_factor * (
        2 ** attempt
    )


async def check_mock_api(
    base_url=DEFAULT_BASE_URL,
    timeout=5,
):
    normalized_url = normalize_base_url(
        base_url
    )

    try:
        async with httpx.AsyncClient(
            timeout=timeout
        ) as client:
            response = await client.get(
                f"{normalized_url}/health"
            )

        return response.status_code == 200

    except httpx.HTTPError:
        return False


async def reset_mock_api(
    base_url=DEFAULT_BASE_URL,
    timeout=5,
):
    normalized_url = normalize_base_url(
        base_url
    )

    async with httpx.AsyncClient(
        timeout=timeout
    ) as client:
        response = await client.post(
            f"{normalized_url}/reset"
        )

        response.raise_for_status()

        return response.json()


async def execute_request(
    client,
    semaphore,
    route,
    max_retries,
    backoff_factor,
):
    start_time = time.perf_counter()

    status_counts = defaultdict(int)

    attempts = 0
    last_status_code = None
    last_error = None

    for attempt in range(
        max_retries + 1
    ):
        attempts += 1

        try:
            async with semaphore:
                response = await client.get(
                    route
                )

            last_status_code = (
                response.status_code
            )

            status_counts[
                response.status_code
            ] += 1

            if 200 <= response.status_code < 300:
                duration = (
                    time.perf_counter()
                    - start_time
                )

                return RequestResult(
                    success=True,
                    route=route,
                    final_status_code=(
                        response.status_code
                    ),
                    duration_seconds=duration,
                    attempts=attempts,
                    retries=attempts - 1,
                    status_counts=dict(
                        status_counts
                    ),
                )

            if (
                response.status_code
                not in RETRYABLE_STATUS_CODES
            ):
                duration = (
                    time.perf_counter()
                    - start_time
                )

                return RequestResult(
                    success=False,
                    route=route,
                    final_status_code=(
                        response.status_code
                    ),
                    duration_seconds=duration,
                    attempts=attempts,
                    retries=attempts - 1,
                    status_counts=dict(
                        status_counts
                    ),
                    error=(
                        "Erreur HTTP non réessayable : "
                        f"{response.status_code}"
                    ),
                )

            if attempt < max_retries:
                delay = calculate_retry_delay(
                    response=response,
                    attempt=attempt,
                    backoff_factor=(
                        backoff_factor
                    ),
                )

                await asyncio.sleep(
                    delay
                )

        except httpx.TimeoutException as error:
            last_error = (
                f"Timeout : {error}"
            )

            if attempt < max_retries:
                delay = (
                    backoff_factor
                    * (2 ** attempt)
                )

                await asyncio.sleep(
                    delay
                )

        except httpx.NetworkError as error:
            last_error = (
                f"Erreur réseau : {error}"
            )

            if attempt < max_retries:
                delay = (
                    backoff_factor
                    * (2 ** attempt)
                )

                await asyncio.sleep(
                    delay
                )

        except httpx.HTTPError as error:
            last_error = (
                f"Erreur HTTPX : {error}"
            )

            break

    duration = (
        time.perf_counter()
        - start_time
    )

    if last_error is None:
        last_error = (
            "La requête a échoué après "
            "toutes les tentatives."
        )

    return RequestResult(
        success=False,
        route=route,
        final_status_code=last_status_code,
        duration_seconds=duration,
        attempts=attempts,
        retries=max(
            0,
            attempts - 1,
        ),
        status_counts=dict(
            status_counts
        ),
        error=last_error,
    )


def merge_request_result(
    result,
    counters,
):
    counters["completed_requests"] += 1

    counters["total_attempts"] += (
        result.attempts
    )

    counters["total_retries"] += (
        result.retries
    )

    counters["total_response_time"] += (
        result.duration_seconds
    )

    counters["route_counts"][
        result.route
    ] += 1

    if result.success:
        counters[
            "successful_requests"
        ] += 1

        counters[
            "route_success_counts"
        ][result.route] += 1

    else:
        counters[
            "failed_requests"
        ] += 1

        counters[
            "route_failure_counts"
        ][result.route] += 1

    for status_code, count in (
        result.status_counts.items()
    ):
        counters["status_counts"][
            status_code
        ] += count


async def run_load_test(
    total_requests=1000,
    batch_size=100,
    concurrency_limit=20,
    max_retries=2,
    backoff_factor=0.05,
    base_url=DEFAULT_BASE_URL,
    routes=None,
    request_timeout=10,
    progress_callback: Callable | None = None,
):
    validate_configuration(
        total_requests=total_requests,
        batch_size=batch_size,
        concurrency_limit=(
            concurrency_limit
        ),
        max_retries=max_retries,
    )

    if routes is None:
        routes = DEFAULT_ROUTES

    if not routes:
        raise ValueError(
            "Au moins une route est nécessaire."
        )

    if request_timeout <= 0:
        raise ValueError(
            "Le timeout doit être supérieur à zéro."
        )

    normalized_url = normalize_base_url(
        base_url
    )

    full_routes = [
        f"{normalized_url}{route}"
        for route in routes
    ]

    semaphore = asyncio.Semaphore(
        concurrency_limit
    )

    counters = {
        "completed_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "total_attempts": 0,
        "total_retries": 0,
        "total_response_time": 0.0,
        "status_counts": defaultdict(int),
        "route_counts": defaultdict(int),
        "route_success_counts": defaultdict(int),
        "route_failure_counts": defaultdict(int),
    }

    timeout_configuration = httpx.Timeout(
        timeout=request_timeout,
        connect=request_timeout,
        read=request_timeout,
        write=request_timeout,
        pool=request_timeout,
    )

    connection_limits = httpx.Limits(
        max_connections=concurrency_limit,
        max_keepalive_connections=(
            concurrency_limit
        ),
    )

    test_start_time = time.perf_counter()

    async with httpx.AsyncClient(
        timeout=timeout_configuration,
        limits=connection_limits,
        follow_redirects=True,
    ) as client:
        batch_start = 0

        while batch_start < total_requests:
            current_batch_size = min(
                batch_size,
                total_requests - batch_start,
            )

            tasks = []

            for position in range(
                current_batch_size
            ):
                global_index = (
                    batch_start
                    + position
                )

                route = full_routes[
                    global_index
                    % len(full_routes)
                ]

                task = execute_request(
                    client=client,
                    semaphore=semaphore,
                    route=route,
                    max_retries=max_retries,
                    backoff_factor=(
                        backoff_factor
                    ),
                )

                tasks.append(task)

            results = await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

            for route_position, result in enumerate(
                results
            ):
                if isinstance(
                    result,
                    Exception,
                ):
                    route = full_routes[
                        (
                            batch_start
                            + route_position
                        )
                        % len(full_routes)
                    ]

                    result = RequestResult(
                        success=False,
                        route=route,
                        final_status_code=None,
                        duration_seconds=0.0,
                        attempts=1,
                        retries=0,
                        error=str(result),
                    )

                merge_request_result(
                    result=result,
                    counters=counters,
                )

            batch_start += (
                current_batch_size
            )

            if progress_callback is not None:
                progress_callback(
                    counters[
                        "completed_requests"
                    ],
                    total_requests,
                )

    duration_seconds = (
        time.perf_counter()
        - test_start_time
    )

    completed_requests = counters[
        "completed_requests"
    ]

    if completed_requests == 0:
        average_response_time = 0.0

    else:
        average_response_time = (
            counters[
                "total_response_time"
            ]
            / completed_requests
        )

    if duration_seconds == 0:
        requests_per_second = 0.0

    else:
        requests_per_second = (
            completed_requests
            / duration_seconds
        )

    return LoadTestMetrics(
        total_requested=total_requests,
        completed_requests=(
            completed_requests
        ),
        successful_requests=counters[
            "successful_requests"
        ],
        failed_requests=counters[
            "failed_requests"
        ],
        total_attempts=counters[
            "total_attempts"
        ],
        total_retries=counters[
            "total_retries"
        ],
        status_counts=dict(
            counters["status_counts"]
        ),
        route_counts=dict(
            counters["route_counts"]
        ),
        route_success_counts=dict(
            counters[
                "route_success_counts"
            ]
        ),
        route_failure_counts=dict(
            counters[
                "route_failure_counts"
            ]
        ),
        duration_seconds=duration_seconds,
        average_response_time_seconds=(
            average_response_time
        ),
        requests_per_second=(
            requests_per_second
        ),
        concurrency_limit=(
            concurrency_limit
        ),
        batch_size=batch_size,
        max_retries=max_retries,
    )


def display_metrics(metrics):
    print()
    print("=" * 50)
    print("RÉSULTATS DU TEST DE CHARGE")
    print("=" * 50)

    print(
        "Requêtes demandées :",
        metrics.total_requested,
    )

    print(
        "Requêtes terminées :",
        metrics.completed_requests,
    )

    print(
        "Succès :",
        metrics.successful_requests,
    )

    print(
        "Échecs :",
        metrics.failed_requests,
    )

    print(
        "Tentatives HTTP totales :",
        metrics.total_attempts,
    )

    print(
        "Retries :",
        metrics.total_retries,
    )

    print(
        "Durée totale :",
        f"{metrics.duration_seconds:.3f} s",
    )

    print(
        "Temps moyen par requête logique :",
        (
            f"{metrics.average_response_time_seconds:.6f} s"
        ),
    )

    print(
        "Débit :",
        (
            f"{metrics.requests_per_second:.2f} "
            "requêtes/s"
        ),
    )

    print()
    print("Statuts HTTP :")

    for status_code, count in sorted(
        metrics.status_counts.items()
    ):
        print(
            f"- {status_code} : {count}"
        )

    print()
    print("Répartition par route :")

    for route, count in (
        metrics.route_counts.items()
    ):
        successes = (
            metrics.route_success_counts.get(
                route,
                0,
            )
        )

        failures = (
            metrics.route_failure_counts.get(
                route,
                0,
            )
        )

        print(
            f"- {route} : "
            f"{count} requêtes logiques, "
            f"{successes} succès, "
            f"{failures} échecs"
        )


async def main_async(args):
    server_available = await check_mock_api(
        base_url=args.base_url
    )

    if not server_available:
        print(
            "Le serveur de simulation n'est pas accessible."
        )

        print(
            "Lancez-le dans un autre terminal avec :"
        )

        print(
            "python -m uvicorn "
            "load_testing.mock_api:app "
            "--host 127.0.0.1 --port 8000"
        )

        return

    await reset_mock_api(
        base_url=args.base_url
    )

    metrics = await run_load_test(
        total_requests=args.total,
        batch_size=args.batch,
        concurrency_limit=args.concurrency,
        max_retries=args.retries,
        backoff_factor=args.backoff,
        base_url=args.base_url,
        request_timeout=args.timeout,
    )

    display_metrics(
        metrics
    )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Test de charge asynchrone local."
        )
    )

    parser.add_argument(
        "--total",
        type=int,
        default=1000,
        help="Nombre total de requêtes logiques.",
    )

    parser.add_argument(
        "--batch",
        type=int,
        default=100,
        help="Nombre de tâches créées par lot.",
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=20,
        help=(
            "Nombre maximal de requêtes simultanées."
        ),
    )

    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="Nombre maximal de retries.",
    )

    parser.add_argument(
        "--backoff",
        type=float,
        default=0.05,
        help="Facteur de backoff.",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=10,
        help="Timeout HTTP en secondes.",
    )

    parser.add_argument(
        "--base-url",
        type=str,
        default=DEFAULT_BASE_URL,
        help="Adresse de l'API locale.",
    )

    return parser.parse_args()


def main():
    arguments = parse_arguments()

    asyncio.run(
        main_async(arguments)
    )


if __name__ == "__main__":
    main()