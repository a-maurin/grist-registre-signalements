# -*- coding: utf-8 -*-
"""
Déploiement du Lot 3 : vues encadrement, navigation et nettoyage des vues passives.

Ce script :
1. Déploie le widget d'accueil « 🛡️ Espace encadrement » en pleine page sur la vue 10 (Acces_Gestionnaires).
2. Remplace la vue 6 (« 🎯 Pilotage et attribution ») par le widget HTML maître-détail pleine page.
3. Supprime la section passive renderhtml (vue 3) et retire la colonne calculée Fiche_HTML.
4. Réorganise le menu latéral (_grist_Pages) avec l'arborescence encadrement indentée et sans grilles brutes.
"""

import json
import requests

from config import DOC_ID
from creer_registre_signalements import get_grist_credentials
from widgets.commun import construire_options_custom_widget
from widgets.espace_encadrement_html import generer_widget_espace_encadrement
from widgets.pilotage_html import generer_widget_pilotage

VIEW_PILOTAGE_ID = 6
VIEW_REGISTRE_ID = 3
VIEW_ESPACE_ENCADREMENT_ID = 10
VIEWS_A_MASQUER_MENU = {2, 3, 4, 7}

ORDRE_PAGES_CIBLE = [
    (5, 1.0, 0),   # ✍️ Nouveau signalement
    (9, 2.0, 0),   # 🗂️ Mes dossiers
    (10, 3.0, 0),  # 🛡️ Espace encadrement
    (6, 3.1, 1),   # 🎯 Pilotage et attribution
    (8, 3.2, 1),   # 📊 Statistiques
]


def _lire_table(api_url, headers, table):
    r = requests.get(f"{api_url}/docs/{DOC_ID}/tables/{table}/records", headers=headers)
    r.raise_for_status()
    return r.json().get("records", [])


def _supprimer_sections(api_url, headers, section_ids):
    """Supprime proprement des sections et leurs filtres/champs associés."""
    if not section_ids:
        return
    filters = _lire_table(api_url, headers, "_grist_Filters")
    filter_ids = [f["id"] for f in filters if f["fields"].get("viewSectionRef") in section_ids]
    if filter_ids:
        requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Filters/data/delete",
            headers=headers,
            json=filter_ids,
        ).raise_for_status()

    fields = _lire_table(api_url, headers, "_grist_Views_section_field")
    field_ids = [f["id"] for f in fields if f["fields"].get("parentId") in section_ids]
    if field_ids:
        requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section_field/data/delete",
            headers=headers,
            json=field_ids,
        ).raise_for_status()

    requests.post(
        f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section/data/delete",
        headers=headers,
        json=section_ids,
    ).raise_for_status()


def _deployer_widget_pleine_page_gestionnaires(api_url, headers, view_id, view_name, sec_title, widget_spec, table_ges_ref):
    """Configure une vue entière en Custom Widget Builder adossé à Acces_Gestionnaires."""
    requests.patch(
        f"{api_url}/docs/{DOC_ID}/tables/_grist_Views/records",
        headers=headers,
        json={"records": [{"id": view_id, "fields": {"name": view_name}}]},
    ).raise_for_status()

    sections = _lire_table(api_url, headers, "_grist_Views_section")
    secs_view = [s for s in sections if s["fields"].get("parentId") == view_id]
    sec_custom = next((s for s in secs_view if s["fields"].get("parentKey") == "custom"), None)
    secs_a_supprimer = [s["id"] for s in secs_view if s["fields"].get("parentKey") != "custom"]

    opts = construire_options_custom_widget(widget_spec)
    champs_custom = {
        "tableRef": table_ges_ref,
        "title": sec_title,
        "options": opts,
        "linkSrcSectionRef": 0,
        "linkSrcColRef": 0,
        "linkTargetColRef": 0,
        "sortColRefs": "[]",
        "filterSpec": "",
    }

    if sec_custom:
        sec_id = sec_custom["id"]
        requests.patch(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section/records",
            headers=headers,
            json={"records": [{"id": sec_id, "fields": champs_custom}]},
        ).raise_for_status()
    else:
        r_new = requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section/records",
            headers=headers,
            json={"records": [{"fields": {
                **champs_custom,
                "parentId": view_id,
                "parentKey": "custom",
                "defaultWidth": 100,
                "borderWidth": 1,
            }}]},
        )
        r_new.raise_for_status()
        sec_id = r_new.json()["records"][0]["id"]

    _supprimer_sections(api_url, headers, secs_a_supprimer)

    layout = json.dumps({"children": [{"size": 100, "leaf": sec_id}], "collapsed": []})
    requests.patch(
        f"{api_url}/docs/{DOC_ID}/tables/_grist_Views/records",
        headers=headers,
        json={"records": [{"id": view_id, "fields": {"layoutSpec": layout}}]},
    ).raise_for_status()
    print(f"Vue {view_id} (« {view_name} ») déployée en pleine page (section {sec_id}).")


def _nettoyer_fiche_html_passive(api_url, headers):
    """Retire la section passive renderhtml de la vue 3 et supprime la colonne Fiche_HTML."""
    sections = _lire_table(api_url, headers, "_grist_Views_section")
    secs_v3 = [s for s in sections if s["fields"].get("parentId") == VIEW_REGISTRE_ID]
    custom_v3_ids = [s["id"] for s in secs_v3 if s["fields"].get("parentKey") == "custom"]
    record_v3 = next((s for s in secs_v3 if s["fields"].get("parentKey") == "record"), None)

    if custom_v3_ids:
        _supprimer_sections(api_url, headers, custom_v3_ids)
        print(f"Section(s) passive(s) {custom_v3_ids} supprimée(s) de la vue {VIEW_REGISTRE_ID}.")

    if record_v3:
        layout_v3 = json.dumps({"children": [{"size": 100, "leaf": record_v3["id"]}], "collapsed": []})
        requests.patch(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Views/records",
            headers=headers,
            json={"records": [{"id": VIEW_REGISTRE_ID, "fields": {"layoutSpec": layout_v3}}]},
        ).raise_for_status()

    r_cols = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Signalements/columns", headers=headers)
    r_cols.raise_for_status()
    if any(c["id"] == "Fiche_HTML" for c in r_cols.json().get("columns", [])):
        requests.post(
            f"{api_url}/docs/{DOC_ID}/apply",
            headers=headers,
            json=[["RemoveColumn", "Signalements", "Fiche_HTML"]],
        ).raise_for_status()
        print("Colonne redondante « Fiche_HTML » supprimée de Signalements.")


def _reorganiser_navigation_laterale(api_url, headers):
    """Masque les grilles brutes du menu et structure l'espace encadrement indenté."""
    pages = _lire_table(api_url, headers, "_grist_Pages")
    a_supprimer = [p["id"] for p in pages if p["fields"].get("viewRef") in VIEWS_A_MASQUER_MENU]
    if a_supprimer:
        requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Pages/data/delete",
            headers=headers,
            json=a_supprimer,
        ).raise_for_status()
        print(f"{len(a_supprimer)} entrée(s) obsolète(s) retirée(s) du menu latéral.")

    pages = _lire_table(api_url, headers, "_grist_Pages")
    page_by_view = {p["fields"].get("viewRef"): p["id"] for p in pages}

    patches = []
    creates = []
    for view_ref, pos, indent in ORDRE_PAGES_CIBLE:
        if view_ref in page_by_view:
            patches.append({
                "id": page_by_view[view_ref],
                "fields": {"pagePos": pos, "indentation": indent},
            })
        else:
            creates.append({
                "fields": {"viewRef": view_ref, "pagePos": pos, "indentation": indent},
            })

    if patches:
        requests.patch(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Pages/records",
            headers=headers,
            json={"records": patches},
        ).raise_for_status()
    if creates:
        requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Pages/records",
            headers=headers,
            json={"records": creates},
        ).raise_for_status()

    print(f"Navigation latérale réorganisée ({len(ORDRE_PAGES_CIBLE)} pages actives).")


def deployer_vues_encadrement():
    """Point d'entrée du déploiement Lot 3."""
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
        VIEW_ESPACE_ENCADREMENT_ID,
        "🛡️ Espace encadrement",
        "Espace encadrement",
        generer_widget_espace_encadrement(),
        table_ges_ref,
    )
    _deployer_widget_pleine_page_gestionnaires(
        api_url,
        headers,
        VIEW_PILOTAGE_ID,
        "🎯 Pilotage et attribution",
        "Pilotage et attribution",
        generer_widget_pilotage(),
        table_ges_ref,
    )
    _nettoyer_fiche_html_passive(api_url, headers)
    _reorganiser_navigation_laterale(api_url, headers)
    print("Déploiement Lot 3 (encadrement et navigation) terminé avec succès.")


if __name__ == "__main__":
    deployer_vues_encadrement()
