# -*- coding: utf-8 -*-
"""
Chargeur centralisé de configuration pour le registre des signalements Grist.

Ordre de priorité :
1. Valeurs génériques de « config_local.example.py » ;
2. Surcharge par « config_local.py » si présent (sauf si GRIST_USE_EXAMPLE_CONFIG=1) ;
3. Fichier local « .env » (variables manquantes dans os.environ) et variables d'environnement.
"""

import importlib.util
import os

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _charger_module_depuis_chemin(nom_module, chemin_fichier):
    """Charge un module Python à partir d'un chemin explicite."""
    spec = importlib.util.spec_from_file_location(nom_module, chemin_fichier)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_exemple = _charger_module_depuis_chemin(
    "config_local_example", os.path.join(_BASE_DIR, "config_local.example.py")
)

_CLES_EXPORTEES = (
    "GRIST_API_URL",
    "GRIST_API_KEY",
    "ORG_ID",
    "WORKSPACE_NAME",
    "DOC_NAME",
    "DOC_ID",
    "DOC_URL",
    "SERVICE_NOM",
    "CSV_PREFIX",
    "EMAIL_PLACEHOLDER",
    "AGENTS_INITIAUX",
    "EMAILS_PROPRIETAIRES",
    "EMAILS_GESTIONNAIRES",
    "CHOIX_ENCADRANT",
    "ENCADRANT_PAR_DEFAUT",
)


def _charger_dotenv(chemin_env):
    """Charge un fichier .env simple (KEY=VALUE) sans écraser os.environ."""
    if not os.path.exists(chemin_env):
        return
    with open(chemin_env, "r", encoding="utf-8") as fichier:
        for ligne in fichier:
            propre = ligne.strip()
            if not propre or propre.startswith("#") or "=" not in propre:
                continue
            cle, valeur = propre.split("=", 1)
            cle = cle.strip()
            if cle.startswith("export "):
                cle = cle[7:].strip()
            valeur = valeur.strip()
            if len(valeur) >= 2 and valeur[0] == valeur[-1] and valeur[0] in ("'", '"'):
                valeur = valeur[1:-1]
            if cle:
                os.environ.setdefault(cle, valeur)


_charger_dotenv(os.path.join(_BASE_DIR, ".env"))

_valeurs = {cle: getattr(_exemple, cle) for cle in _CLES_EXPORTEES}

if os.environ.get("GRIST_USE_EXAMPLE_CONFIG") != "1":
    try:
        import config_local as _local

        for cle in _CLES_EXPORTEES:
            if hasattr(_local, cle):
                _valeurs[cle] = getattr(_local, cle)
    except ImportError:
        pass

if os.environ.get("GRIST_API_URL"):
    _valeurs["GRIST_API_URL"] = os.environ["GRIST_API_URL"]
if os.environ.get("GRIST_API_KEY"):
    _valeurs["GRIST_API_KEY"] = os.environ["GRIST_API_KEY"]
if os.environ.get("GRIST_DOC_ID"):
    _valeurs["DOC_ID"] = os.environ["GRIST_DOC_ID"]
if os.environ.get("GRIST_DOC_URL"):
    _valeurs["DOC_URL"] = os.environ["GRIST_DOC_URL"]
if os.environ.get("GRIST_ORG_ID"):
    org_env = os.environ["GRIST_ORG_ID"].strip()
    _valeurs["ORG_ID"] = int(org_env) if org_env.isdigit() else org_env

GRIST_API_URL = (_valeurs["GRIST_API_URL"] or "").rstrip("/")
GRIST_API_KEY = _valeurs["GRIST_API_KEY"] or ""
ORG_ID = _valeurs["ORG_ID"]
WORKSPACE_NAME = _valeurs["WORKSPACE_NAME"]
DOC_NAME = _valeurs["DOC_NAME"]
DOC_ID = _valeurs["DOC_ID"]
DOC_URL = (_valeurs["DOC_URL"] or "").rstrip("/")
DOC_URL_PILOTAGE = f"{DOC_URL}/p/6" if DOC_URL else "/p/6"
SERVICE_NOM = _valeurs["SERVICE_NOM"]
CSV_PREFIX = _valeurs["CSV_PREFIX"]
EMAIL_PLACEHOLDER = _valeurs["EMAIL_PLACEHOLDER"]
AGENTS_INITIAUX = _valeurs["AGENTS_INITIAUX"]
EMAILS_PROPRIETAIRES = _valeurs["EMAILS_PROPRIETAIRES"]
EMAILS_GESTIONNAIRES = _valeurs["EMAILS_GESTIONNAIRES"]
CHOIX_ENCADRANT = _valeurs["CHOIX_ENCADRANT"]
ENCADRANT_PAR_DEFAUT = _valeurs["ENCADRANT_PAR_DEFAUT"]
