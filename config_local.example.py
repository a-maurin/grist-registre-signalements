# -*- coding: utf-8 -*-
"""
Modèle de configuration locale pour le registre des signalements Grist.

Copiez ce fichier vers « config_local.py » (ignoré par Git) et adaptez les valeurs
à votre instance Grist et à votre service avant d'exécuter les scripts de déploiement.
"""

# Paramètres de connexion à l'API Grist (peuvent aussi être fournis par .env ou l'environnement)
GRIST_API_URL = "https://grist.exemple.fr/api"
GRIST_API_KEY = ""

# Identification de l'organisation, de l'espace de travail et du document Grist
ORG_ID = 0
WORKSPACE_NAME = "Signalements"
DOC_NAME = "Registre des signalements"
DOC_ID = "REMPLACER_PAR_ID_DOCUMENT"
DOC_URL = "https://grist.exemple.fr/o/mon-service/XXXXXXXXXXXX/Registre-des-signalements"

# Libellés et formats propres au service
SERVICE_NOM = "service"
CSV_PREFIX = "service"
EMAIL_PLACEHOLDER = "prenom.nom@exemple.fr"

# Annuaire initial importé dans Referentiel_Agents lors du déploiement
AGENTS_INITIAUX = [
    {"Nom": "Alice MARTIN", "Email": "alice.martin@exemple.fr", "Trigramme": "AM"},
    {"Nom": "Bob DUPONT", "Email": "bob.dupont@exemple.fr", "Trigramme": "BD"},
    {"Nom": "Claire BERNARD", "Email": "claire.bernard@exemple.fr", "Trigramme": "CB"},
    {"Nom": "David LEROY", "Email": "david.leroy@exemple.fr", "Trigramme": "DL"},
    {"Nom": "Emma MOREAU", "Email": "emma.moreau@exemple.fr", "Trigramme": "EM"},
]

# Périmètres initiaux des rôles (le rôle Gestionnaire devient ensuite dynamique via Referentiel_Agents.Role)
EMAILS_PROPRIETAIRES = (
    "alice.martin@exemple.fr",
    "bob.dupont@exemple.fr",
)
EMAILS_GESTIONNAIRES = (*EMAILS_PROPRIETAIRES, "claire.bernard@exemple.fr")

# Encadrants proposés dans la liste « Encadrant à alerter »
CHOIX_ENCADRANT = [
    "Alice MARTIN",
    "Bob DUPONT",
    "Claire BERNARD",
]
ENCADRANT_PAR_DEFAUT = "Alice MARTIN"
