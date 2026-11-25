# -*- coding: utf-8 -*-
"""
Déploiement du Lot 2 : parcours agent (vues « ✍️ Nouveau signalement » et « 🗂️ Mes dossiers »).

Ce script :
1. Déploie le widget dynamique « ✍️ Nouveau signalement » en pleine page sur la vue 5.
2. Renomme la vue 9 en « 🗂️ Mes dossiers », déploie le widget dynamique en pleine page,
   configure une section native repliée « 📎 Pièces jointes (accès natif) » synchronisée sur le
   dossier sélectionné (repli Option B) et supprime l'ancienne grille brute de la vue 9.
3. Retire l'entrée « 📝 Retour d'intervention » (vue 7) du menu latéral, sans toucher aux
   vues d'encadrement ni aux règles ACL.
"""

import json
import requests

from config import DOC_ID
from creer_registre_signalements import get_grist_credentials
from widgets.commun import construire_options_custom_widget
from widgets.mes_dossiers_html import generer_widget_mes_dossiers
from widgets.nouveau_signalement_html import generer_widget_nouveau_signalement

VIEW_NOUVEAU_ID = 5
VIEW_RETOUR_ID = 7
VIEW_MES_DOSSIERS_ID = 9
NOM_VUE_MES_DOSSIERS = "🗂️ Mes dossiers"
TITRE_SECTION_PJ = "📎 Pièces jointes (accès natif)"
COLONNES_SECTION_PJ = ["Numero_Signalement", "Pieces_Jointes", "Retour_Pieces_Jointes"]


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

    r_del = requests.post(
        f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section/data/delete",
        headers=headers,
        json=section_ids,
    )
    if not r_del.ok:
        requests.post(
            f"{api_url}/docs/{DOC_ID}/apply",
            headers=headers,
            json=[["RemoveViewSection", sid] for sid in section_ids],
        ).raise_for_status()


def _configurer_vue_nouveau_signalement(api_url, headers, table_ref_agents):
    """Configure la vue 5 en widget pleine page « Nouveau signalement » sans section native."""
    sections = _lire_table(api_url, headers, "_grist_Views_section")
    secs_v5 = [s for s in sections if s["fields"].get("parentId") == VIEW_NOUVEAU_ID]
    sec_custom = next((s for s in secs_v5 if s["fields"].get("parentKey") == "custom"), None)
    secs_a_supprimer = [s["id"] for s in secs_v5 if s["fields"].get("parentKey") != "custom"]
    opts = construire_options_custom_widget(generer_widget_nouveau_signalement())

    if sec_custom:
        sec_id = sec_custom["id"]
        requests.patch(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section/records",
            headers=headers,
            json={"records": [{"id": sec_id, "fields": {
                "tableRef": table_ref_agents,
                "title": "Nouveau signalement",
                "options": opts,
            }}]},
        ).raise_for_status()
    else:
        r_new = requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section/records",
            headers=headers,
            json={"records": [{"fields": {
                "tableRef": table_ref_agents,
                "parentId": VIEW_NOUVEAU_ID,
                "parentKey": "custom",
                "title": "Nouveau signalement",
                "defaultWidth": 100,
                "borderWidth": 1,
                "options": opts,
            }}]},
        )
        r_new.raise_for_status()
        sec_id = r_new.json()["records"][0]["id"]

    _supprimer_sections(api_url, headers, secs_a_supprimer)

    layout = json.dumps({"children": [{"size": 100, "leaf": sec_id}], "collapsed": []})
    requests.patch(
        f"{api_url}/docs/{DOC_ID}/tables/_grist_Views/records",
        headers=headers,
        json={"records": [{"id": VIEW_NOUVEAU_ID, "fields": {"layoutSpec": layout}}]},
    ).raise_for_status()
    print(f"Vue {VIEW_NOUVEAU_ID} (« ✍️ Nouveau signalement ») déployée (section {sec_id}).")


def _configurer_champs_section_pj(api_url, headers, sec_pj_id, table_sig_ref):
    """Restreint la section native single aux 3 colonnes de pièces jointes."""
    cols = _lire_table(api_url, headers, "_grist_Tables_column")
    col_ref_by_id = {
        c["fields"]["colId"]: c["id"]
        for c in cols
        if c["fields"].get("parentId") == table_sig_ref
    }
    wanted_refs = [col_ref_by_id[col_id] for col_id in COLONNES_SECTION_PJ if col_id in col_ref_by_id]

    fields = _lire_table(api_url, headers, "_grist_Views_section_field")
    sec_fields = [f for f in fields if f["fields"].get("parentId") == sec_pj_id]

    to_delete = [f["id"] for f in sec_fields if f["fields"].get("colRef") not in wanted_refs]
    if to_delete:
        requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section_field/data/delete",
            headers=headers,
            json=to_delete,
        ).raise_for_status()

    existing_by_col = {f["fields"].get("colRef"): f["id"] for f in sec_fields if f["fields"].get("colRef") in wanted_refs}
    patches = []
    creates = []
    for idx, col_ref in enumerate(wanted_refs, start=1):
        pos = float(idx * 10)
        if col_ref in existing_by_col:
            patches.append({"id": existing_by_col[col_ref], "fields": {"parentPos": pos}})
        else:
            creates.append({"fields": {"parentId": sec_pj_id, "colRef": col_ref, "parentPos": pos}})
    if patches:
        requests.patch(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section_field/records",
            headers=headers,
            json={"records": patches},
        ).raise_for_status()
    if creates:
        requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section_field/records",
            headers=headers,
            json={"records": creates},
        ).raise_for_status()


def _configurer_vue_mes_dossiers(api_url, headers, table_sig_ref):
    """Configure la vue 9 (« 🗂️ Mes dossiers ») en widget pleine page + section PJ native repliée."""
    requests.patch(
        f"{api_url}/docs/{DOC_ID}/tables/_grist_Views/records",
        headers=headers,
        json={"records": [{"id": VIEW_MES_DOSSIERS_ID, "fields": {"name": NOM_VUE_MES_DOSSIERS}}]},
    ).raise_for_status()

    sections = _lire_table(api_url, headers, "_grist_Views_section")
    secs_v9 = [s for s in sections if s["fields"].get("parentId") == VIEW_MES_DOSSIERS_ID]
    sec_custom = next((s for s in secs_v9 if s["fields"].get("parentKey") == "custom"), None)
    sec_single = next((s for s in secs_v9 if s["fields"].get("parentKey") == "single"), None)
    secs_record = [s for s in secs_v9 if s["fields"].get("parentKey") == "record"]

    opts = construire_options_custom_widget(generer_widget_mes_dossiers())
    if sec_custom:
        sec_custom_id = sec_custom["id"]
        requests.patch(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section/records",
            headers=headers,
            json={"records": [{"id": sec_custom_id, "fields": {
                "tableRef": table_sig_ref,
                "title": "Mes dossiers",
                "options": opts,
            }}]},
        ).raise_for_status()
    else:
        r_new = requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section/records",
            headers=headers,
            json={"records": [{"fields": {
                "tableRef": table_sig_ref,
                "parentId": VIEW_MES_DOSSIERS_ID,
                "parentKey": "custom",
                "title": "Mes dossiers",
                "defaultWidth": 100,
                "borderWidth": 1,
                "options": opts,
            }}]},
        )
        r_new.raise_for_status()
        sec_custom_id = r_new.json()["records"][0]["id"]

    if sec_single:
        sec_pj_id = sec_single["id"]
    else:
        r_single = requests.post(
            f"{api_url}/docs/{DOC_ID}/apply",
            headers=headers,
            json=[["CreateViewSection", table_sig_ref, VIEW_MES_DOSSIERS_ID, "single", None, None]],
        )
        r_single.raise_for_status()
        sec_pj_id = r_single.json()["retValues"][0]["sectionRef"]

    requests.patch(
        f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section/records",
        headers=headers,
        json={"records": [{"id": sec_pj_id, "fields": {
            "title": TITRE_SECTION_PJ,
            "linkSrcSectionRef": sec_custom_id,
            "linkSrcColRef": 0,
            "linkTargetColRef": 0,
        }}]},
    ).raise_for_status()

    _configurer_champs_section_pj(api_url, headers, sec_pj_id, table_sig_ref)

    # Suppression de l'ancienne grille brute sur la vue 9
    if secs_record:
        _supprimer_sections(api_url, headers, [s["id"] for s in secs_record])

    layout = json.dumps({
        "children": [{"size": 100, "leaf": sec_custom_id}],
        "collapsed": [{"leaf": sec_pj_id}],
    })
    requests.patch(
        f"{api_url}/docs/{DOC_ID}/tables/_grist_Views/records",
        headers=headers,
        json={"records": [{"id": VIEW_MES_DOSSIERS_ID, "fields": {"layoutSpec": layout}}]},
    ).raise_for_status()
    print(f"Vue {VIEW_MES_DOSSIERS_ID} (« {NOM_VUE_MES_DOSSIERS} ») déployée (section {sec_custom_id}, PJ native {sec_pj_id}).")


def _retirer_page_retour_menu(api_url, headers):
    """Retire la page séparée « 📝 Retour d'intervention » (vue 7) du menu latéral."""
    pages = _lire_table(api_url, headers, "_grist_Pages")
    page_ids = [p["id"] for p in pages if p["fields"].get("viewRef") == VIEW_RETOUR_ID]
    if page_ids:
        requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_Pages/data/delete",
            headers=headers,
            json=page_ids,
        ).raise_for_status()
        print("Page séparée « 📝 Retour d'intervention » retirée du menu latéral.")


def deployer_vues_agent():
    """Point d'entrée du déploiement Lot 2."""
    api_url, api_key = get_grist_credentials()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    tables = _lire_table(api_url, headers, "_grist_Tables")
    tables_map = {t["fields"].get("tableId"): t["id"] for t in tables}

    _configurer_vue_nouveau_signalement(api_url, headers, tables_map["Referentiel_Agents"])
    _configurer_vue_mes_dossiers(api_url, headers, tables_map["Signalements"])
    _retirer_page_retour_menu(api_url, headers)
    print("Déploiement Lot 2 (vues agent) terminé avec succès.")


if __name__ == "__main__":
    deployer_vues_agent()
