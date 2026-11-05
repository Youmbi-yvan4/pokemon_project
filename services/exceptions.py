class APIError(Exception):
    """Erreur générale lors d'un appel API."""


class BadRequestError(APIError):
    """Requête invalide : statut 400."""


class AuthenticationError(APIError):
    """Authentification absente ou invalide : statut 401."""


class ForbiddenError(APIError):
    """Accès interdit : statut 403."""


class ResourceNotFoundError(APIError):
    """Ressource introuvable : statut 404."""


class RateLimitError(APIError):
    """Trop de requêtes : statut 429."""


class ServerError(APIError):
    """Erreur temporaire du serveur : statuts 5xx."""


class APIConnectionError(APIError):
    """Erreur réseau ou connexion impossible."""


class APITimeoutError(APIError):
    """L'API n'a pas répondu dans le délai autorisé."""


class InvalidJSONError(APIError):
    """La réponse reçue ne contient pas un JSON valide."""