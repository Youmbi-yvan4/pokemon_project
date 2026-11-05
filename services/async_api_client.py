import asyncio
import random

import httpx

from services.exceptions import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    InvalidJSONError,
    RateLimitError,
    ResourceNotFoundError,
    ServerError,
)


RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}


class AsyncAPIClient:
    def __init__(
        self,
        timeout=10,
        max_retries=3,
        backoff_factor=1,
        concurrency_limit=10,
    ):
        if timeout <= 0:
            raise ValueError(
                "Le timeout doit être supérieur à zéro."
            )

        if max_retries < 0:
            raise ValueError(
                "Le nombre de retries ne peut pas être négatif."
            )

        if backoff_factor < 0:
            raise ValueError(
                "Le facteur de backoff ne peut pas être négatif."
            )

        if concurrency_limit <= 0:
            raise ValueError(
                "La limite de concurrence doit être "
                "supérieure à zéro."
            )

        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.concurrency_limit = concurrency_limit

        self.semaphore = asyncio.Semaphore(
            concurrency_limit
        )

    def _calculate_delay(self, attempt):
        exponential_delay = (
            self.backoff_factor * (2 ** attempt)
        )

        jitter = random.uniform(0, 0.5)

        return exponential_delay + jitter

    def _get_retry_delay(
        self,
        response,
        attempt,
    ):
        retry_after = response.headers.get(
            "Retry-After"
        )

        if retry_after:
            try:
                retry_delay = float(retry_after)

                if retry_delay >= 0:
                    return retry_delay

            except ValueError:
                pass

        return self._calculate_delay(attempt)

    def _raise_for_non_retryable_status(
        self,
        response,
    ):
        status_code = response.status_code

        if status_code == 400:
            raise BadRequestError(
                "Requête invalide. Vérifiez les paramètres."
            )

        if status_code == 401:
            raise AuthenticationError(
                "Authentification absente ou invalide."
            )

        if status_code == 403:
            raise ForbiddenError(
                "L'accès à cette ressource est interdit."
            )

        if status_code == 404:
            raise ResourceNotFoundError(
                "La ressource demandée est introuvable."
            )

        if 400 <= status_code < 500:
            raise BadRequestError(
                f"Erreur client HTTP {status_code}."
            )

    def create_client(self):
        timeout_configuration = httpx.Timeout(
            timeout=self.timeout,
            connect=self.timeout,
            read=self.timeout,
            write=self.timeout,
            pool=self.timeout,
        )

        connection_limits = httpx.Limits(
            max_connections=self.concurrency_limit,
            max_keepalive_connections=(
                self.concurrency_limit
            ),
        )

        return httpx.AsyncClient(
            timeout=timeout_configuration,
            limits=connection_limits,
            follow_redirects=True,
        )

    async def get_json(
        self,
        client,
        url,
        params=None,
    ):
        for attempt in range(
            self.max_retries + 1
        ):
            try:
                # Le sémaphore limite seulement l'appel HTTP.
                # Il est libéré pendant les pauses de retry.
                async with self.semaphore:
                    response = await client.get(
                        url,
                        params=params,
                    )

            except httpx.TimeoutException as error:
                if attempt == self.max_retries:
                    raise APITimeoutError(
                        "Le délai d'attente de l'API "
                        "a été dépassé."
                    ) from error

                delay = self._calculate_delay(
                    attempt
                )

                await asyncio.sleep(delay)
                continue

            except httpx.NetworkError as error:
                if attempt == self.max_retries:
                    raise APIConnectionError(
                        "Impossible de se connecter à l'API."
                    ) from error

                delay = self._calculate_delay(
                    attempt
                )

                await asyncio.sleep(delay)
                continue

            except httpx.HTTPError as error:
                raise APIConnectionError(
                    f"Erreur HTTP : {error}"
                ) from error

            if response.status_code == 200:
                try:
                    return response.json()

                except ValueError as error:
                    raise InvalidJSONError(
                        "La réponse reçue n'est pas "
                        "un JSON valide."
                    ) from error

            if (
                response.status_code
                in RETRYABLE_STATUS_CODES
            ):
                if attempt == self.max_retries:
                    if response.status_code == 429:
                        raise RateLimitError(
                            "Limite de requêtes atteinte "
                            "après plusieurs tentatives."
                        )

                    raise ServerError(
                        f"Erreur serveur HTTP "
                        f"{response.status_code} après "
                        "plusieurs tentatives."
                    )

                delay = self._get_retry_delay(
                    response,
                    attempt,
                )

                await asyncio.sleep(delay)
                continue

            self._raise_for_non_retryable_status(
                response
            )

            raise ServerError(
                "Statut HTTP inattendu : "
                f"{response.status_code}."
            )

        raise APIConnectionError(
            "La requête a échoué après toutes "
            "les tentatives."
        )