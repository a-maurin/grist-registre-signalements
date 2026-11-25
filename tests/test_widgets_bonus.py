# -*- coding: utf-8 -*-
"""Tests unitaires et d'intégration pour les vues bonus du Lot 4 (Statistiques et Gestion des agents)."""

import json
import pytest
import requests

from config import AGENTS_INITIAUX, DOC_ID, DOC_URL, EMAILS_GESTIONNAIRES
from tests.test_signalements_workflow import grist_client  # noqa: F401
from widgets.commun import CUSTOM_WIDGET_BUILDER_URL, construire_options_custom_widget
from widgets.gestion_agents_html import generer_widget_gestion_agents
from widgets.statistiques_html import generer_widget_statistiques


def test_widget_statistiques_filtres_svg_delais_et_csv():
    spec = generer_widget_statistiques()
    html_code = spec["_html"]
    js_code = spec["_js"]

    assert 'grist.ready({ requiredAccess: "full" })' in js_code
    assert "!sessionCtx.isManager" in js_code
    assert "statRestricted" in html_code
    assert "@media print" in html_code

    for elem_id in [
        "statPeriode",
        "statDateDebut",
        "statDateFin",
        "statDomaine",
        "statPriorite",
        "statAgent",
        "btnStatResetFilters",
        "btnStatPrint",
        "btnStatExportCsv",
        "kpiTotal",
        "kpiTauxCloture",
        "kpiUrgents",
        "kpiDelaiAttr",
        "kpiDelaiTrait",
        "chartStatuts",
        "chartDomaines",
        "chartMensuel",
        "chartCanauxSuites",
        "statAgentTableBody",
    ]:
        assert elem_id in html_code

    assert "<svg" in js_code
    assert "stroke-dasharray" in js_code
    assert "calcDelaiJours" in js_code
    assert "window.print()" in js_code
    assert "buildCsvUtf8Bom" in js_code
    assert "text/csv;charset=utf-8;" in js_code

    opts = json.loads(construire_options_custom_widget(spec))
    cv = json.loads(opts["customView"])
    assert cv["url"] == CUSTOM_WIDGET_BUILDER_URL
    assert cv["access"] == "full"


def test_widget_gestion_agents_crud_securite_et_integrite():
    spec = generer_widget_gestion_agents()
    html_code = spec["_html"]
    js_code = spec["_js"]

    assert 'grist.ready({ requiredAccess: "full" })' in js_code
    assert "!sessionCtx.isManager" in js_code
    assert "gaRestricted" in html_code
    assert "Partager" in html_code

    for elem_id in [
        "gaSearchInput",
        "gaRoleFilter",
        "btnGaAdd",
        "btnGaExportCsv",
        "gaTableBody",
        "gaModalBackdrop",
        "gaInputNom",
        "gaInputEmail",
        "gaInputTrigramme",
        "gaInputRole",
        "gaDeleteBackdrop",
    ]:
        assert elem_id in html_code

    assert "managerEmails" not in js_code
    assert 'ag.Role === "Gestionnaire"' in js_code
    assert "activeManagersCount <= 1" in js_code
    assert "Gestionnaire" in js_code
    assert "Agent" in js_code
    assert '["AddRecord", "Referentiel_Agents", null, fields]' in js_code
    assert '["UpdateRecord", "Referentiel_Agents", editingAgentId, fields]' in js_code
    assert '["RemoveRecord", "Referentiel_Agents", targetId]' in js_code
    assert "const fields = { Nom: nom, Email: email, Trigramme: trigramme, Role: role };" in js_code
    assert "usage.total === 0 && !isSelf" in js_code
    assert "duplicate" in js_code
    assert "buildCsvUtf8Bom" in js_code

    opts = json.loads(construire_options_custom_widget(spec))
    cv = json.loads(opts["customView"])
    assert cv["url"] == CUSTOM_WIDGET_BUILDER_URL
    assert cv["access"] == "full"


@pytest.mark.integration
def test_vues_bonus_lot4(grist_client):
    """Vérifie les vues Lot 4 dans Grist : Statistiques HTML (vue 8), Gestion des agents HTML et lien vue 10."""
    api_url, headers = grist_client

    r_tables = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Tables/records", headers=headers)
    assert r_tables.status_code == 200
    tables_map = {t["fields"].get("tableId"): t["id"] for t in r_tables.json().get("records", [])}
    table_ges_ref = tables_map["Acces_Gestionnaires"]

    r_views = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Views/records", headers=headers)
    assert r_views.status_code == 200
    views = r_views.json().get("records", [])
    views_by_id = {v["id"]: v["fields"] for v in views}
    ga_view = next((v for v in views if v["fields"].get("name") == "👥 Gestion des agents"), None)
    assert ga_view is not None
    ga_view_id = ga_view["id"]

    r_secs = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section/records", headers=headers)
    assert r_secs.status_code == 200
    secs = r_secs.json().get("records", [])

    for view_id, marker in [(8, "Statistiques d'activité"), (ga_view_id, "Gestion des agents")]:
        secs_v = [s for s in secs if s["fields"].get("parentId") == view_id]
        assert len(secs_v) == 1
        sec = secs_v[0]
        assert sec["fields"].get("parentKey") == "custom"
        assert sec["fields"].get("tableRef") == table_ges_ref
        cv = json.loads(json.loads(sec["fields"].get("options", "{}")).get("customView", "{}"))
        assert "custom-widget-builder" in cv.get("url", "")
        assert marker in cv.get("widgetOptions", {}).get("_html", "")
        layout = json.loads(views_by_id[view_id].get("layoutSpec", "{}"))
        assert layout.get("children") == [{"size": 100, "leaf": sec["id"]}]

    # Vue 10 pointe vers /p/{ga_view_id}
    sec_v10 = next(s for s in secs if s["fields"].get("parentId") == 10 and s["fields"].get("parentKey") == "custom")
    cv_v10 = json.loads(json.loads(sec_v10["fields"].get("options", "{}")).get("customView", "{}"))
    assert f"{DOC_URL}/p/{ga_view_id}" in cv_v10.get("widgetOptions", {}).get("_html", "")

    # Menu latéral : Gestion des agents indentée après Statistiques
    r_pages = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Pages/records", headers=headers)
    assert r_pages.status_code == 200
    pages_sorted = sorted(r_pages.json().get("records", []), key=lambda p: p["fields"].get("pagePos", 0))
    assert [p["fields"].get("viewRef") for p in pages_sorted] == [5, 9, 10, 6, 8, ga_view_id]
    assert [p["fields"].get("indentation") for p in pages_sorted] == [0, 0, 0, 1, 1, 1]

    # Intégrité de Referentiel_Agents, Est_Connecte et Role
    r_cols = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Referentiel_Agents/columns", headers=headers)
    assert r_cols.status_code == 200
    col_ids = [c["id"] for c in r_cols.json().get("columns", [])]
    assert "Est_Connecte" in col_ids
    assert "Role" in col_ids

    r_agents = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Referentiel_Agents/records", headers=headers)
    assert r_agents.status_code == 200
    roles = [rec["fields"].get("Role") for rec in r_agents.json().get("records", [])]
    assert roles.count("Gestionnaire") == len(EMAILS_GESTIONNAIRES)
    assert roles.count("Agent") == len(AGENTS_INITIAUX) - len(EMAILS_GESTIONNAIRES)

    r_ag = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Referentiel_Agents/records", headers=headers)
    assert r_ag.status_code == 200
    assert len(r_ag.json().get("records", [])) >= len(AGENTS_INITIAUX)
