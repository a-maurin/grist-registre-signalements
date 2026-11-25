# -*- coding: utf-8 -*-
"""
Déploiement du Lot 4 : vues bonus HTML (« 📊 Statistiques » et « 👥 Gestion des agents »).

Ce script :
1. Remplace les sections natives de la vue 8 (« 📊 Statistiques ») par le tableau de bord HTML
   pleine page adossé à Acces_Gestionnaires (sans supprimer les tables Signalements_summary_*).
2. Crée ou met à jour la vue « 👥 Gestion des agents » en pleine page sur Acces_Gestionnaires et
   l'ajoute dans le menu latéral encadrement (pagePos 3.3, indentation 1).
3. Met à jour le hub « 🛡️ Espace encadrement » (vue 10) avec le lien direct vers la gestion des agents.
"""

import requests

from configurer_vues_encadrement import (
    DOC_ID,
    VIEW_ESPACE_ENCADREMENT_ID,
    _deployer_widget_pleine_page_gestionnaires,
    _lire_table,
)
from creer_registre_signalements import get_grist_credentials
from widgets.espace_encadrement_html import generer_widget_espace_encadrement
from widgets.gestion_agents_html import generer_widget_gestion_agents
from widgets.statistiques_html import generer_widget_statistiques

VIEW_STATISTIQUES_ID = 8
NOM_VUE_STATISTIQUES = "📊 Statistiques"
NOM_VUE_GESTION_AGENTS = "👥 Gestion des agents"


def _ordonner_pages_lot4(api_url, headers, view_ga_id):
    """Garantit la présence et l'ordre strict des 6 pages actives dans _grist_Pages."""
    pages = _lire_table(api_url, headers, "_grist_Pages")
    existing = next((p for p in pages if p["fields"].get("viewRef") == view_ga_id), None)
    if not existing:
        requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Pages/records",
            headers=headers,
            json={"records": [{"fields": {"viewRef": view_ga_id, "pagePos": 10.0, "indentation": 1}}]},
        ).raise_for_status()
        pages = _lire_table(api_url, headers, "_grist_Pages")

    page_by_view = {p["fields"].get("viewRef"): p["id"] for p in pages}
    cibles = [
        (5, 1.0, 0),
        (9, 2.0, 0),
        (10, 3.0, 0),
        (6, 3.5, 1),
        (VIEW_STATISTIQUES_ID, 4.0, 1),
        (view_ga_id, 4.5, 1),
    ]
    patches = [
        {"id": page_by_view[vref], "fields": {"pagePos": pos, "indentation": indent}}
        for vref, pos, indent in cibles
        if vref in page_by_view
    ]
    if patches:
        requests.patch(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Pages/records",
            headers=headers,
            json={"records": patches},
        ).raise_for_status()


def _assurer_vue_gestion_agents(api_url, headers):
    """Retourne l'ID de la vue « 👥 Gestion des agents » (la crée si absente)."""
    views = _lire_table(api_url, headers, "_grist_Views")
    existing = next((v for v in views if v["fields"].get("name") == NOM_VUE_GESTION_AGENTS), None)
    if existing:
        return existing["id"]

    r_new = requests.post(
        f"{api_url}/docs/{DOC_ID}/tables/_grist_Views/records",
        headers=headers,
        json={"records": [{"fields": {"name": NOM_VUE_GESTION_AGENTS, "type": "empty", "layoutSpec": ""}}]},
    )
    r_new.raise_for_status()
    return r_new.json()["records"][0]["id"]


def deployer_vues_bonus():
    """Point d'entrée du déploiement Lot 4."""
    api_url, api_key = get_grist_credentials()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    tables = _lire_table(api_url, headers, "_grist_Tables")
    tables_map = {t["fields"].get("tableId"): t["id"] for t in tables}
    table_ges_ref = tables_map["Acces_Gestionnaires"]

    _deployer_widget_pleine_page_gestionnaires(
        api_url,
        headers,
        VIEW_STATISTIQUES_ID,
        NOM_VUE_STATISTIQUES,
        "Statistiques",
        generer_widget_statistiques(),
        table_ges_ref,
    )

    view_ga_id = _assurer_vue_gestion_agents(api_url, headers)
    _deployer_widget_pleine_page_gestionnaires(
        api_url,
        headers,
        view_ga_id,
        NOM_VUE_GESTION_AGENTS,
        "Gestion des agents",
        generer_widget_gestion_agents(),
        table_ges_ref,
    )
    _ordonner_pages_lot4(api_url, headers, view_ga_id)

    _deployer_widget_pleine_page_gestionnaires(
        api_url,
        headers,
        VIEW_ESPACE_ENCADREMENT_ID,
        "🛡️ Espace encadrement",
        "Espace encadrement",
        generer_widget_espace_encadrement(gestion_agents_view_id=view_ga_id),
        table_ges_ref,
    )
    print(f"Déploiement Lot 4 terminé avec succès (vue gestion agents = {view_ga_id}).")
    return view_ga_id


if __name__ == "__main__":
    deployer_vues_bonus()
