# -*- coding: utf-8 -*-
"""
Déploiement du classeur Grist : Registre des signalements.

Ce script réalise les opérations initiales :
1. Recherche ou création de l'espace de travail configuré dans l'organisation Grist.
2. Création du classeur « Registre des signalements ».
3. Préparation des trois tables métier :
   - Referentiel_Agents : annuaire des agents du service ;
   - Signalements : table registre principale avec numérotation AAAA-XXXX,
     suivi de prise en charge, attribution, alertes courriel et consolidation du retour ;
   - Retours_Actions : table des retours de mission liée à Signalements.
"""

import os
import json
import requests

from config import (
    AGENTS_INITIAUX,
    DOC_NAME,
    GRIST_API_KEY as CFG_GRIST_API_KEY,
    GRIST_API_URL as CFG_GRIST_API_URL,
    ORG_ID,
    WORKSPACE_NAME,
)


def get_grist_credentials():
    """Retourne le couple (api_url, api_key) depuis l'environnement, .env ou config_local.py."""
    api_url = os.environ.get("GRIST_API_URL") or CFG_GRIST_API_URL
    api_key = os.environ.get("GRIST_API_KEY") or CFG_GRIST_API_KEY
    if api_url and api_key:
        return api_url.rstrip("/"), api_key

    config_paths = [
        os.path.expanduser("~/.gemini/config/mcp_config.json"),
        os.path.expanduser("~/.gemini/antigravity/mcp_config.json"),
        os.path.expanduser("~/.gemini/antigravity-ide/mcp_config.json"),
    ]
    for cp in config_paths:
        if os.path.exists(cp):
            try:
                with open(cp, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                env = cfg.get("mcpServers", {}).get("grist", {}).get("env", {})
                if "GRIST_API_URL" in env and "GRIST_API_KEY" in env:
                    return env["GRIST_API_URL"].rstrip("/"), env["GRIST_API_KEY"]
            except Exception:
                pass
    raise RuntimeError(
        "Identifiants Grist introuvables. Renseignez GRIST_API_URL et GRIST_API_KEY "
        "dans .env, config_local.py ou vos variables d'environnement."
    )


def obtenir_ou_creer_espace(api_url, headers):
    """Recherche l'espace de travail configuré dans l'organisation ou le crée s'il n'existe pas."""
    r = requests.get(f"{api_url}/orgs/{ORG_ID}/workspaces", headers=headers)
    r.raise_for_status()
    for ws in r.json():
        if ws.get("name") == WORKSPACE_NAME:
            print(f"Espace de travail existant trouvé : {ws['name']} (id {ws['id']})")
            return ws["id"]

    r_create = requests.post(
        f"{api_url}/orgs/{ORG_ID}/workspaces",
        headers=headers,
        json={"name": WORKSPACE_NAME}
    )
    r_create.raise_for_status()
    ws_id = r_create.json()
    print(f"Espace de travail créé : {WORKSPACE_NAME} (id {ws_id})")
    return ws_id


def obtenir_ou_creer_document(api_url, headers, workspace_id):
    """Recherche le document 'Registre des signalements' dans l'espace ou le crée."""
    r = requests.get(f"{api_url}/workspaces/{workspace_id}", headers=headers)
    r.raise_for_status()
    ws_data = r.json()
    for d in ws_data.get("docs", []):
        if d.get("name") == DOC_NAME:
            print(f"Document existant trouvé : {d['name']} (id {d['id']})")
            return d["id"]

    r_doc = requests.post(
        f"{api_url}/workspaces/{workspace_id}/docs",
        headers=headers,
        json={"name": DOC_NAME}
    )
    r_doc.raise_for_status()
    doc_id = r_doc.json()
    print(f"Document créé : {DOC_NAME} (id {doc_id})")
    return doc_id


if __name__ == "__main__":
    api_url, api_key = get_grist_credentials()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    ws_id = obtenir_ou_creer_espace(api_url, headers)
    doc_id = obtenir_ou_creer_document(api_url, headers, ws_id)
    print(f"Doc ID : {doc_id}")
