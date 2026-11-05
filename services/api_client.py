import random
import time

import requests

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


class APIClient:
    def __init__(
        self,
        timeout=10,
        max_retries=3,
        backoff_factor=1,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.session = requests.Session()

    def _calculate_delay(self, attempt):
        exponential_delay = self.backoff_factor * (2 ** attempt)
        jitter = random.uniform(0, 0.5)

        return exponential_delay + jitter

    def _get_retry_delay(self, response, attempt):
        retry_after = response.headers.get("Retry-After")

        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass

        return self._calculate_delay(attempt)

    def _raise_for_non_retryable_status(self, response):
        status_code = response.status_code

        if status_code == 400:
            raise BadRequestError(
                "Requête invalide. Vérifiez les paramètres envoyés."
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

    def get_json(self, url, params=None):
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                )

            except requests.exceptions.Timeout as error:
                last_error = APITimeoutError(
                    f"Le délai d'attente de {self.timeout} secondes "
                    "a été dépassé."
                )

                if attempt == self.max_retries:
                    raise last_error from error

                delay = self._calculate_delay(attempt)

                print(
                    f"Timeout. Nouvelle tentative dans "
                    f"{delay:.2f} seconde(s)."
                )

                time.sleep(delay)
                continue

            except requests.exceptions.ConnectionError as error:
                last_error = APIConnectionError(
                    "Impossible de se connecter à l'API."
                )

                if attempt == self.max_retries:
                    raise last_error from error

                delay = self._calculate_delay(attempt)

                print(
                    f"Erreur de connexion. Nouvelle tentative dans "
                    f"{delay:.2f} seconde(s)."
                )

                time.sleep(delay)
                continue

            except requests.exceptions.RequestException as error:
                raise APIConnectionError(
                    f"Erreur pendant la requête : {error}"
                ) from error

            if response.status_code == 200:
                try:
                    return response.json()
                except requests.exceptions.JSONDecodeError as error:
                    raise InvalidJSONError(
                        "La réponse de l'API n'est pas un JSON valide."
                    ) from error

            if response.status_code in RETRYABLE_STATUS_CODES:
                if attempt == self.max_retries:
                    if response.status_code == 429:
                        raise RateLimitError(
                            "Limite de requêtes atteinte après "
                            "plusieurs tentatives."
                        )

                    raise ServerError(
                        f"Erreur serveur HTTP {response.status_code} "
                        "après plusieurs tentatives."
                    )

                delay = self._get_retry_delay(response, attempt)

                print(
                    f"Erreur HTTP {response.status_code}. "
                    f"Nouvelle tentative dans {delay:.2f} seconde(s)."
                )

                time.sleep(delay)
                continue

            self._raise_for_non_retryable_status(response)

            raise ServerError(
                f"Statut HTTP inattendu : {response.status_code}."
            )

        raise APIConnectionError(
            f"La requête a échoué : {last_error}"
        )