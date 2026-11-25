# -*- coding: utf-8 -*-
"""
Tests unitaires et d'intégration du cycle de vie des signalements dans Grist.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import pytest

from config import (
    AGENTS_INITIAUX,
    CHOIX_ENCADRANT,
    DOC_ID,
    DOC_NAME,
    EMAILS_GESTIONNAIRES,
    ENCADRANT_PAR_DEFAUT,
    WORKSPACE_NAME,
)
from creer_registre_signalements import get_grist_credentials

pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def grist_client():
    api_url, api_key = get_grist_credentials()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    return api_url, headers


def test_referentiel_agents_complet(grist_client):
    """Vérifie que les agents configurés sont présents dans l'annuaire avec leur rôle initial."""
    api_url, headers = grist_client
    r = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Referentiel_Agents/records", headers=headers)
    assert r.status_code == 200
    records = r.json().get("records", [])
    assert len(records) >= len(AGENTS_INITIAUX)
    emails = {rec["fields"]["Email"] for rec in records}
    for agent in AGENTS_INITIAUX:
        assert agent["Email"] in emails
    gestionnaires = {
        rec["fields"]["Email"]
        for rec in records
        if rec["fields"].get("Role") == "Gestionnaire"
    }
    agents = {
        rec["fields"]["Email"]
        for rec in records
        if rec["fields"].get("Role") == "Agent"
    }
    assert gestionnaires == set(EMAILS_GESTIONNAIRES)
    assert len(agents) == len(records) - len(EMAILS_GESTIONNAIRES)


def test_structure_tables_et_colonnes(grist_client):
    """Vérifie l'existence des tables et des colonnes clés."""
    api_url, headers = grist_client
    r = requests.get(f"{api_url}/docs/{DOC_ID}/tables", headers=headers)
    assert r.status_code == 200
    tables = [t["id"] for t in r.json().get("tables", [])]
    assert "Signalements" in tables
    assert "Retours_Actions" in tables
    assert "Referentiel_Agents" in tables
    assert "Acces_Gestionnaires" in tables

    # Vérification de la colonne Est_Connecte et du témoin Acces_Gestionnaires
    r_ref_cols = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Referentiel_Agents/columns", headers=headers)
    assert r_ref_cols.status_code == 200
    assert "Est_Connecte" in [c["id"] for c in r_ref_cols.json().get("columns", [])]

    r_ges = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Acces_Gestionnaires/records", headers=headers)
    assert r_ges.status_code == 200
    assert len(r_ges.json().get("records", [])) >= 1

    # Vérification des colonnes de Signalements
    r_cols = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Signalements/columns", headers=headers)
    assert r_cols.status_code == 200
    col_ids = [c["id"] for c in r_cols.json().get("columns", [])]
    for expected in [
        "Numero_Signalement", "Date_Heure_Reception", "Agent_Recepteur",
        "Agent_Attributaire", "Statut", "Action_Notifier",
        "A_Un_Retour", "Retour_Compte_Rendu", "Retour_Suite_Donnee", "Statut_Manuel",
        "Est_Mon_Dossier", "Encadrant_A_Alerter", "Action_Alerter_Encadrant"
    ]:
        assert expected in col_ids


def test_cycle_complet_signalement_et_consolidation(grist_client):
    """Teste le cycle complet : création, attribution, mailto, retour d'intervention et consolidation."""
    api_url, headers = grist_client

    r_agents = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Referentiel_Agents/records", headers=headers)
    assert r_agents.status_code == 200
    agents_records = r_agents.json().get("records", [])
    assert len(agents_records) >= 2
    recepteur = agents_records[0]
    attributaire = agents_records[1]

    # 1. Création d'un signalement test
    signalement_payload = {
        "records": [{
            "fields": {
                "Date_Heure_Reception": 1772449200,  # 01/03/2026
                "Agent_Recepteur": recepteur["id"],
                "Canal_Reception": "Appel téléphonique",
                "Requerant_Nom": "M. Test",
                "Requerant_Contact": "0600000000",
                "Commune": "Commune-Test",
                "Lieu_Dit": "Lieu-test",
                "Domaine_Activite": "Chasse et faune sauvage",
                "Description_Faits": "Fait de test signalé.",
                "Agent_Attributaire": attributaire["id"],
                "Priorite": "Urgente",
                "Consignes_Hierarchie": "Consigne de test pour vérification."
            }
        }]
    }

    r_create = requests.post(
        f"{api_url}/docs/{DOC_ID}/tables/Signalements/records",
        headers=headers,
        json=signalement_payload
    )
    assert r_create.status_code == 200
    sig_id = r_create.json()["records"][0]["id"]

    try:
        # Vérification des formules calculées
        r_get = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Signalements/records", headers=headers)
        rec = next(r for r in r_get.json()["records"] if r["id"] == sig_id)["fields"]

        assert rec["Numero_Signalement"] == f"2026-{sig_id:04d}"
        assert rec["Statut"] == "Attribué"
        assert rec["A_Un_Retour"] is False
        assert f"mailto:{attributaire['fields']['Email']}" in rec["Action_Notifier"]
        assert "Commune-Test" in rec["Action_Notifier"]

        # 2. Ajout du retour de mission de l'agent
        retour_payload = {
            "records": [{
                "fields": {
                    "Signalement": sig_id,
                    "Agent_Intervenant": attributaire["id"],
                    "Date_Intervention": 1772535600,
                    "Type_Demarche": "Contrôle de terrain",
                    "Compte_Rendu": "Surveillance opérée. Aucune anomalie relevée.",
                    "Suite_Donnee": "Classement sans suite"
                }
            }]
        }
        r_ret = requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/Retours_Actions/records",
            headers=headers,
            json=retour_payload
        )
        assert r_ret.status_code == 200
        ret_id = r_ret.json()["records"][0]["id"]
        ret_ids = [ret_id]

        try:
            # Vérification de la consolidation instantanée
            r_get_after = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Signalements/records", headers=headers)
            rec_after = next(r for r in r_get_after.json()["records"] if r["id"] == sig_id)["fields"]

            assert rec_after["A_Un_Retour"] is True
            assert rec_after["Statut"] == "Traité"
            assert rec_after["Retour_Type_Demarche"] == "Contrôle de terrain"
            assert "Surveillance opérée" in rec_after["Retour_Compte_Rendu"]
            assert rec_after["Retour_Suite_Donnee"] == "Classement sans suite"

            # Statut imposé par la hiérarchie : prime sur la formule
            requests.patch(
                f"{api_url}/docs/{DOC_ID}/tables/Signalements/records", headers=headers,
                json={"records": [{"id": sig_id, "fields": {"Statut_Manuel": "En cours"}}]}
            ).raise_for_status()
            r_get_manuel = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Signalements/records", headers=headers)
            rec_manuel = next(r for r in r_get_manuel.json()["records"] if r["id"] == sig_id)["fields"]
            assert rec_manuel["Statut"] == "En cours"

        finally:
            # Nettoyage des retours
            requests.post(f"{api_url}/docs/{DOC_ID}/tables/Retours_Actions/data/delete", headers=headers, json=ret_ids)

    finally:
        # Nettoyage du signalement
        requests.post(f"{api_url}/docs/{DOC_ID}/tables/Signalements/data/delete", headers=headers, json=[sig_id])


def test_retours_multiples_et_agent_connecte(grist_client):
    """Plusieurs retours : « En cours » sans suite, « Traité » dès qu'une suite est renseignée ;
    l'agent intervenant est renseigné automatiquement avec l'utilisateur connecté."""
    api_url, headers = grist_client
    r_agents = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Referentiel_Agents/records", headers=headers)
    assert r_agents.status_code == 200
    attributaire_id = r_agents.json()["records"][0]["id"]
    r_create = requests.post(
        f"{api_url}/docs/{DOC_ID}/tables/Signalements/records", headers=headers,
        json={"records": [{"fields": {"Date_Heure_Reception": 1772449200, "Agent_Attributaire": attributaire_id}}]}
    )
    assert r_create.status_code == 200
    sig_id = r_create.json()["records"][0]["id"]
    ret_ids = []

    def etat():
        sigs = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Signalements/records", headers=headers).json()["records"]
        return next(r for r in sigs if r["id"] == sig_id)["fields"]

    try:
        for champs, statut_attendu in (
            ({"Compte_Rendu": "Premier passage"}, "En cours"),
            ({"Compte_Rendu": "Second passage", "Suite_Donnee": "Régularisation"}, "Traité"),
        ):
            r_ret = requests.post(
                f"{api_url}/docs/{DOC_ID}/tables/Retours_Actions/records", headers=headers,
                json={"records": [{"fields": {"Signalement": sig_id, **champs}}]}
            )
            assert r_ret.status_code == 200
            ret_ids.append(r_ret.json()["records"][0]["id"])
            fiche = etat()
            assert fiche["Statut"] == statut_attendu
            assert fiche["Retour_Compte_Rendu"] == champs["Compte_Rendu"]

        retours = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Retours_Actions/records", headers=headers).json()["records"]
        for rec in retours:
            if rec["id"] in ret_ids:
                assert rec["fields"]["Agent_Intervenant"]
    finally:
        requests.post(f"{api_url}/docs/{DOC_ID}/tables/Retours_Actions/data/delete", headers=headers, json=ret_ids)
        requests.post(f"{api_url}/docs/{DOC_ID}/tables/Signalements/data/delete", headers=headers, json=[sig_id])


def test_numero_fige_a_la_creation(grist_client):
    """Le numéro de dossier ne change pas si la date de réception est corrigée."""
    api_url, headers = grist_client
    r_create = requests.post(
        f"{api_url}/docs/{DOC_ID}/tables/Signalements/records", headers=headers,
        json={"records": [{"fields": {"Date_Heure_Reception": 1772449200}}]}
    )
    assert r_create.status_code == 200
    sig_id = r_create.json()["records"][0]["id"]
    try:
        requests.patch(
            f"{api_url}/docs/{DOC_ID}/tables/Signalements/records", headers=headers,
            json={"records": [{"id": sig_id, "fields": {"Date_Heure_Reception": 1830000000}}]}
        ).raise_for_status()
        sigs = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Signalements/records", headers=headers).json()["records"]
        assert next(r for r in sigs if r["id"] == sig_id)["fields"]["Numero_Signalement"] == f"2026-{sig_id:04d}"
    finally:
        requests.post(f"{api_url}/docs/{DOC_ID}/tables/Signalements/data/delete", headers=headers, json=[sig_id])


def test_regles_acl_actives(grist_client):
    """Vérifie les règles d'accès : attribut utilisateur Agent, lecture limitée aux dossiers attribués."""
    api_url, headers = grist_client
    r_rules = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_ACLRules/records", headers=headers)
    assert r_rules.status_code == 200
    rules = r_rules.json().get("records", [])
    assert len(rules) >= 14
    formules = [r["fields"].get("aclFormula", "") for r in rules]

    # Agents = éditeurs du document, sans liste d'e-mails en dur
    assert any("user.Access == EDITOR" in f for f in formules)
    assert not any("@" in f for f in formules)

    # Attribut utilisateur Agent configuré
    assert any('"name": "Agent"' in (r["fields"].get("userAttributes") or "") for r in rules)

    # Lecture des signalements limitée à l'agent attributaire ou récepteur avant attribution
    assert any("rec.Agent_Attributaire == user.Agent.id" in f for f in formules)
    assert any("rec.Agent_Recepteur == user.Agent.id" in f and "not rec.Agent_Attributaire" in f for f in formules)
    assert any("rec.Agent_Attributaire_Id == user.Agent.id" in f for f in formules)
    assert not any("rec.A_Un_Retour" in f for f in formules)

    # Vérification des règles Est_Connecte et Acces_Gestionnaires
    r_res = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_ACLResources/records", headers=headers)
    assert r_res.status_code == 200
    res_ids_map = {
        (r["fields"].get("tableId"), r["fields"].get("colIds")): r["id"]
        for r in r_res.json().get("records", [])
    }
    assert ("Referentiel_Agents", "Est_Connecte") in res_ids_map
    assert ("Acces_Gestionnaires", "*") in res_ids_map
    res_conn_id = res_ids_map[("Referentiel_Agents", "Est_Connecte")]
    res_ges_id = res_ids_map[("Acces_Gestionnaires", "*")]
    assert any(r["fields"].get("resource") == res_conn_id and "rec.Email == user.Email" in r["fields"].get("aclFormula", "") for r in rules)
    assert any(r["fields"].get("resource") == res_ges_id and r["fields"].get("permissionsText") == "-R-U-C-D" for r in rules)

    # Vérification de la règle -S réservée aux seuls propriétaires
    res_all_id = res_ids_map[("*", "*")]
    regles_schema = [
        r for r in rules
        if r["fields"].get("resource") == res_all_id and r["fields"].get("permissionsText") == "-S"
    ]
    assert len(regles_schema) == 1
    assert "user.Access == OWNER" in regles_schema[0]["fields"].get("aclFormula", "")
    for email in EMAILS_GESTIONNAIRES:
        assert email not in regles_schema[0]["fields"].get("aclFormula", "")

    # Vérification de la suppression (+D) sur Signalements réservée aux seuls gestionnaires dynamiques
    res_sig_id = res_ids_map[("Signalements", "*")]
    regles_sig = [r for r in rules if r["fields"].get("resource") == res_sig_id]
    regles_sig_d = [r for r in regles_sig if "+D" in (r["fields"].get("permissionsText") or "")]
    assert len(regles_sig_d) == 1
    assert 'user.Agent.Role == "Gestionnaire"' in regles_sig_d[0]["fields"].get("aclFormula", "")
    for r in regles_sig:
        if r is not regles_sig_d[0]:
            assert "-D" in (r["fields"].get("permissionsText") or "")

    # Vérification des règles dynamiques basées sur Referentiel_Agents.Role
    rule_role_gestionnaire = any(
        'user.Agent.Role == "Gestionnaire"' in r["fields"].get("aclFormula", "")
        for r in rules
    )
    assert rule_role_gestionnaire is True


def test_suppression_atomique_signalement_et_retours(grist_client):
    """Vérifie la suppression atomique d'un signalement et de ses retours liés via /apply."""
    api_url, headers = grist_client

    r_sig = requests.post(
        f"{api_url}/docs/{DOC_ID}/tables/Signalements/records",
        headers=headers,
        json={"records": [{"fields": {
            "Date_Heure_Reception": 1772449200,
            "Commune": "Commune-Test",
            "Description_Faits": "Test suppression atomique.",
        }}]},
    )
    assert r_sig.status_code == 200
    sig_id = r_sig.json()["records"][0]["id"]

    r_ret = requests.post(
        f"{api_url}/docs/{DOC_ID}/tables/Retours_Actions/records",
        headers=headers,
        json={"records": [{"fields": {
            "Signalement": sig_id,
            "Compte_Rendu": "Retour test à supprimer atomiquement.",
        }}]},
    )
    assert r_ret.status_code == 200
    ret_id = r_ret.json()["records"][0]["id"]

    r_apply = requests.post(
        f"{api_url}/docs/{DOC_ID}/apply",
        headers=headers,
        json=[
            ["BulkRemoveRecord", "Retours_Actions", [ret_id]],
            ["RemoveRecord", "Signalements", sig_id],
        ],
    )
    assert r_apply.status_code == 200

    sigs_ids = {
        r["id"]
        for r in requests.get(f"{api_url}/docs/{DOC_ID}/tables/Signalements/records", headers=headers).json()["records"]
    }
    rets_ids = {
        r["id"]
        for r in requests.get(f"{api_url}/docs/{DOC_ID}/tables/Retours_Actions/records", headers=headers).json()["records"]
    }
    assert sig_id not in sigs_ids
    assert ret_id not in rets_ids


def test_vue_statistiques_et_widgets(grist_client):
    """Vérifie la création, l'agencement et les widgets de la vue Statistiques."""
    api_url, headers = grist_client

    # 1. Vérification de la vue et de la page
    r_views = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Views/records", headers=headers)
    assert r_views.status_code == 200
    views = {v["id"]: v["fields"] for v in r_views.json().get("records", [])}
    stat_view_id = next(vid for vid, v in views.items() if v.get("name") == "📊 Statistiques")
    assert stat_view_id is not None

    r_pages = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Pages/records", headers=headers)
    assert r_pages.status_code == 200
    stat_page = next(p for p in r_pages.json().get("records", []) if p["fields"].get("viewRef") == stat_view_id)
    assert 1.5 < stat_page["fields"].get("pagePos") < 6.0

    # 2. Vérification du widget HTML Statistiques pleine page (Lot 4) sur Acces_Gestionnaires
    r_tables = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Tables/records", headers=headers)
    assert r_tables.status_code == 200
    table_ges_ref = next(
        t["id"] for t in r_tables.json().get("records", []) if t["fields"].get("tableId") == "Acces_Gestionnaires"
    )

    r_sections = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section/records", headers=headers)
    assert r_sections.status_code == 200
    stat_sections = [s for s in r_sections.json().get("records", []) if s["fields"].get("parentId") == stat_view_id]
    assert len(stat_sections) == 1
    sec_stat = stat_sections[0]
    assert sec_stat["fields"].get("parentKey") == "custom"
    assert sec_stat["fields"].get("tableRef") == table_ges_ref
    cv_stat = json.loads(json.loads(sec_stat["fields"].get("options", "{}")).get("customView", "{}"))
    assert "custom-widget-builder" in cv_stat.get("url", "")
    assert "Statistiques d'activité" in cv_stat.get("widgetOptions", {}).get("_html", "")
    layout_stat = json.loads(views[stat_view_id].get("layoutSpec", "{}"))
    assert layout_stat.get("children") == [{"size": 100, "leaf": sec_stat["id"]}]


def test_vue_mes_dossiers_et_regle_filtrage(grist_client):
    """Vérifie le filtrage dynamique et la règle de sécurité de la vue Mes dossiers à traiter."""
    api_url, headers = grist_client

    # 1. Vérification de la colonne et de sa formule
    r_cols = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Signalements/columns", headers=headers)
    assert r_cols.status_code == 200
    col_dict = {c["id"]: c["fields"] for c in r_cols.json().get("columns", [])}
    assert "Est_Mon_Dossier" in col_dict
    assert 'return "OUI"' in col_dict["Est_Mon_Dossier"].get("formula", "")

    # 2. Vérification de la règle ACL sur la colonne technique
    r_res = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_ACLResources/records", headers=headers)
    assert r_res.status_code == 200
    res_mon_dossier = next(
        (r["id"] for r in r_res.json()["records"]
         if r["fields"].get("tableId") == "Signalements" and r["fields"].get("colIds") == "Est_Mon_Dossier"),
        None
    )
    assert res_mon_dossier is not None

    r_rules = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_ACLRules/records", headers=headers)
    assert r_rules.status_code == 200
    rules_col = [r for r in r_rules.json()["records"] if r["fields"].get("resource") == res_mon_dossier]
    assert len(rules_col) == 2
    assert any("rec.Agent_Attributaire == user.Agent.id" in r["fields"].get("aclFormula", "") for r in rules_col)

    # 3. Vérification de la nouvelle vue Mes dossiers (widget plein écran + volet PJ natif replié)
    r_views = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Views/records", headers=headers)
    assert r_views.status_code == 200
    views_by_id = {v["id"]: v["fields"] for v in r_views.json().get("records", [])}
    vue_mes_dossiers = next(
        (v for v in r_views.json()["records"] if "Mes dossiers" in v["fields"].get("name", "")),
        None
    )
    assert vue_mes_dossiers is not None
    assert vue_mes_dossiers["fields"].get("name") == "🗂️ Mes dossiers"

    r_sections = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section/records", headers=headers)
    assert r_sections.status_code == 200
    secs_v9 = [s for s in r_sections.json()["records"] if s["fields"].get("parentId") == vue_mes_dossiers["id"]]
    sec_custom = next((s for s in secs_v9 if s["fields"].get("parentKey") == "custom"), None)
    sec_single = next((s for s in secs_v9 if s["fields"].get("parentKey") == "single"), None)
    assert sec_custom is not None
    assert sec_single is not None
    assert sec_single["fields"].get("linkSrcSectionRef") == sec_custom["id"]

    opts_v9 = json.loads(sec_custom["fields"].get("options", "{}"))
    cv_v9 = json.loads(opts_v9.get("customView", "{}"))
    assert "custom-widget-builder" in cv_v9.get("url", "")
    assert "Mes dossiers" in cv_v9.get("widgetOptions", {}).get("_html", "")

    layout_v9 = json.loads(views_by_id[vue_mes_dossiers["id"]].get("layoutSpec", "{}"))
    assert layout_v9.get("children") == [{"size": 100, "leaf": sec_custom["id"]}]
    assert layout_v9.get("collapsed") == [{"leaf": sec_single["id"]}]


def test_vues_agent_lot2(grist_client):
    """Vérifie le déploiement du widget Nouveau signalement, le retrait du banc d'essai Lot 1 et de la vue 7."""
    api_url, headers = grist_client

    r_views = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Views/records", headers=headers)
    assert r_views.status_code == 200
    views = r_views.json().get("records", [])
    assert not any("Test pièces jointes" in (v["fields"].get("name") or "") for v in views)

    vue_nouveau = next((v for v in views if v["id"] == 5), None)
    assert vue_nouveau is not None
    r_secs = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section/records", headers=headers)
    assert r_secs.status_code == 200
    secs_v5 = [s for s in r_secs.json().get("records", []) if s["fields"].get("parentId") == 5]
    assert len(secs_v5) == 1
    assert secs_v5[0]["fields"].get("parentKey") == "custom"
    sec_c5 = secs_v5[0]
    cv_c5 = json.loads(json.loads(sec_c5["fields"].get("options", "{}")).get("customView", "{}"))
    assert "custom-widget-builder" in cv_c5.get("url", "")
    assert "Nouveau signalement" in cv_c5.get("widgetOptions", {}).get("_html", "")
    assert json.loads(vue_nouveau["fields"].get("layoutSpec", "{}")).get("children") == [{"size": 100, "leaf": sec_c5["id"]}]

    r_pages = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Pages/records", headers=headers)
    assert r_pages.status_code == 200
    view_refs_menu = {p["fields"].get("viewRef") for p in r_pages.json().get("records", [])}
    assert 7 not in view_refs_menu


def test_alerte_encadrant_attribution(grist_client):
    """Vérifie le fonctionnement de l'alerte courriel pour attribution vers l'encadrant."""
    api_url, headers = grist_client

    r_agents = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Referentiel_Agents/records", headers=headers)
    assert r_agents.status_code == 200
    agents_records = r_agents.json().get("records", [])
    par_nom = {r["fields"].get("Nom"): r["fields"].get("Email") for r in agents_records}
    email_defaut = par_nom[ENCADRANT_PAR_DEFAUT]
    encadrant_suppleant = next(n for n in CHOIX_ENCADRANT if n != ENCADRANT_PAR_DEFAUT)
    email_suppleant = par_nom[encadrant_suppleant]

    # 1. Création d'un signalement sans encadrant explicite (doit cibler ENCADRANT_PAR_DEFAUT)
    payload_defaut = {
        "records": [{
            "fields": {
                "Date_Heure_Reception": 1772449200,
                "Agent_Recepteur": agents_records[0]["id"],
                "Canal_Reception": "Courriel",
                "Requerant_Nom": "Mme Test Alerte",
                "Commune": "Commune-A",
                "Domaine_Activite": "Déchets et pollutions",
                "Description_Faits": "Dépôt de déchets constaté."
            }
        }]
    }
    r1 = requests.post(f"{api_url}/docs/{DOC_ID}/tables/Signalements/records", headers=headers, json=payload_defaut)
    assert r1.status_code == 200
    id1 = r1.json()["records"][0]["id"]

    # 2. Création d'un signalement avec encadrant suppléant explicite
    payload_suppleant = {
        "records": [{
            "fields": {
                "Date_Heure_Reception": 1772449200,
                "Agent_Recepteur": agents_records[-1]["id"],
                "Canal_Reception": "Appel téléphonique",
                "Requerant_Nom": "M. Alerte Suppléant",
                "Commune": "Commune-B",
                "Domaine_Activite": "Pêche",
                "Description_Faits": "Engin non conforme signalé.",
                "Encadrant_A_Alerter": encadrant_suppleant
            }
        }]
    }
    r2 = requests.post(f"{api_url}/docs/{DOC_ID}/tables/Signalements/records", headers=headers, json=payload_suppleant)
    assert r2.status_code == 200
    id2 = r2.json()["records"][0]["id"]

    try:
        r_recs = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Signalements/records", headers=headers)
        assert r_recs.status_code == 200
        recs = {r["id"]: r["fields"] for r in r_recs.json()["records"]}

        # Contrôle du signalement 1 (encadrant par défaut)
        f1 = recs[id1]
        assert f1.get("Encadrant_A_Alerter") in [ENCADRANT_PAR_DEFAUT, None, ""] or email_defaut in f1.get("Action_Alerter_Encadrant", "")
        assert f"mailto:{email_defaut}" in f1["Action_Alerter_Encadrant"]
        assert "Commune-A" in f1["Action_Alerter_Encadrant"]
        assert "Nouveau%20signalement%20%C3%A0%20attribuer" in f1["Action_Alerter_Encadrant"]
        assert "p%2F6" in f1["Action_Alerter_Encadrant"]

        # Contrôle du signalement 2 (suppléance explicite)
        f2 = recs[id2]
        assert f2.get("Encadrant_A_Alerter") == encadrant_suppleant
        assert f"mailto:{email_suppleant}" in f2["Action_Alerter_Encadrant"]
        assert "Commune-B" in f2["Action_Alerter_Encadrant"]
        assert "p%2F6" in f2["Action_Alerter_Encadrant"]

    finally:
        requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/Signalements/data/delete",
            headers=headers,
            json=[id1, id2]
        )


def test_ordre_colonnes_grilles(grist_client):
    """Vérifie que les colonnes prioritaires sont bien positionnées sur la gauche dans la grille du registre."""
    api_url, headers = grist_client

    r_cols = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Tables_column/records", headers=headers)
    assert r_cols.status_code == 200
    cols = {c["id"]: c["fields"]["colId"] for c in r_cols.json().get("records", [])}

    r_fields = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section_field/records", headers=headers)
    assert r_fields.status_code == 200
    all_fields = r_fields.json().get("records", [])

    # Section 7 : Registre des signalements
    sec7_fields = [f["fields"] for f in all_fields if f["fields"].get("parentId") == 7]
    sec7_fields.sort(key=lambda x: x.get("parentPos", 0))
    ordered_col_ids = [cols.get(f.get("colRef")) for f in sec7_fields]

    # Vérification des 5 premières colonnes stratégiques
    assert ordered_col_ids[:5] == [
        "Numero_Signalement",
        "Statut",
        "Priorite",
        "Agent_Attributaire",
        "Date_Heure_Reception",
    ]

    # La commune et le domaine doivent se trouver avant l'identité du requérant
    assert ordered_col_ids.index("Commune") < ordered_col_ids.index("Requerant_Nom")
    assert ordered_col_ids.index("Domaine_Activite") < ordered_col_ids.index("Requerant_Nom")


