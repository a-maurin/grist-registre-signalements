# -*- coding: utf-8 -*-
"""
Fixtures partagées pour les tests unitaires et d'intégration Grist.
"""

import pytest
from creer_registre_signalements import get_grist_credentials


@pytest.fixture(scope="session")
def grist_client():
    """Fournit l'URL de base de l'API et les en-têtes d'authentification."""
    api_url, api_key = get_grist_credentials()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    return api_url, headers
