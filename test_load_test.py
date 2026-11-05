import asyncio

from load_testing.load_test import (
    DEFAULT_BASE_URL,
    check_mock_api,
    reset_mock_api,
    run_load_test,
)


async def main():
    available = await check_mock_api(
        base_url=DEFAULT_BASE_URL
    )

    if not available:
        print(
            "Le serveur local n'est pas accessible."
        )

        print(
            "Démarrez-le avec :"
        )

        print(
            "python -m uvicorn "
            "load_testing.mock_api:app "
            "--host 127.0.0.1 --port 8000"
        )

        return

    await reset_mock_api(
        base_url=DEFAULT_BASE_URL
    )

    metrics = await run_load_test(
        total_requests=100,
        batch_size=20,
        concurrency_limit=10,
        max_retries=2,
        backoff_factor=0.05,
        base_url=DEFAULT_BASE_URL,
        request_timeout=5,
    )

    print(
        "Demandées :",
        metrics.total_requested,
    )

    print(
        "Terminées :",
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
        "Retries :",
        metrics.total_retries,
    )

    print(
        "Statuts :",
        metrics.status_counts,
    )

    print(
        "Durée :",
        f"{metrics.duration_seconds:.3f} s",
    )

    print(
        "Débit :",
        f"{metrics.requests_per_second:.2f} req/s",
    )

    assert (
        metrics.total_requested == 100
    )

    assert (
        metrics.completed_requests == 100
    )

    assert (
        metrics.successful_requests
        + metrics.failed_requests
        == 100
    )


if __name__ == "__main__":
    asyncio.run(main())