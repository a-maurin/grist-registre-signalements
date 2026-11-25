# -*- coding: utf-8 -*-
"""Tests unitaires et d'intégration pour les vues encadrement et la navigation du Lot 3."""

import json
import pytest
import requests

from config import DOC_ID, DOC_URL
from tests.test_signalements_workflow import grist_client  # noqa: F401
from widgets.commun import CUSTOM_WIDGET_BUILDER_URL, construire_options_custom_widget
from widgets.espace_encadrement_html import generer_widget_espace_encadrement
from widgets.pilotage_html import generer_widget_pilotage


def test_widget_pilotage_structure_filtres_actions_et_export():
    spec = generer_widget_pilotage()
    html_code = spec["_html"]
    js_code = spec["_js"]

    assert 'grist.ready({ requiredAccess: "full" })' in js_code
    assert "@media print" in html_code
    assert "minmax(0," in html_code
    assert "height: 100vh;" in html_code
    assert "overflow: hidden;" in html_code
    assert "overflow-y: auto;" in html_code
    assert "min-height: 0;" in html_code
    assert "#pilMainApp" in html_code
    assert "max-height: calc(100vh" not in html_code
    assert "pilRestricted" in html_code
    assert "!sessionCtx.isManager" in js_code

    for elem_id in [
        "pilKpiBar",
        "pilFilterStatut",
        "pilFilterPriorite",
        "pilFilterDomaine",
        "pilFilterAgent",
        "pilSearchInput",
        "btnPilResetFilters",
        "btnPilExportCsv",
        "pilMasterTable",
        "pilDetailPane",
        "pilDeleteBackdrop",
        "pilDeleteSummary",
        "btnPilCancelDelete",
        "btnPilConfirmDelete",
    ]:
        assert elem_id in html_code

    for sort_col in [
        "Numero_Signalement",
        "Date_Heure_Reception",
        "Commune",
        "Agent_Attributaire",
        "Priorite",
        "Statut",
    ]:
        assert f'data-sort-col="{sort_col}"' in html_code
    assert "sig-th-sort" in html_code

    assert '["UpdateRecord", "Signalements", dossier.id, payload]' in js_code
    assert "btnDeletePilotage" in js_code
    assert '["BulkRemoveRecord", "Retours_Actions", linkedIds]' in js_code
    assert '["RemoveRecord", "Signalements", targetId]' in js_code
    assert "applyUserActions(actions)" in js_code
    assert "Agent_Attributaire" in js_code
    assert "Priorite" in js_code
    assert "Date_Attribution" in js_code
    assert "Statut_Manuel" in js_code
    assert "Consignes_Hierarchie" in js_code
    assert "Action_Notifier" in js_code
    assert "buildNotifierMailto" in js_code
    assert "buildCsvUtf8Bom" in js_code
    assert "text/csv;charset=utf-8;" in js_code
    assert "window.print()" in js_code
    assert "Retours_Actions" in js_code
    assert "fetchAttachmentsMetaByIds" in js_code

    opts = json.loads(construire_options_custom_widget(spec))
    cv = json.loads(opts["customView"])
    assert cv["url"] == CUSTOM_WIDGET_BUILDER_URL
    assert cv["access"] == "full"


def test_widget_espace_encadrement_kpis_et_liens():
    spec = generer_widget_espace_encadrement(gestion_agents_view_id=11)
    html_code = spec["_html"]
    js_code = spec["_js"]

    assert 'grist.ready({ requiredAccess: "full" })' in js_code
    assert "!ctx.isManager" in js_code
    for elem_id in ["hubNouveaux", "hubUrgents", "hubEnCours", "hubClos"]:
        assert elem_id in html_code
    assert f"{DOC_URL}/p/6" in html_code
    assert f"{DOC_URL}/p/8" in html_code
    assert f"{DOC_URL}/p/11" in html_code
    assert 'target="_top"' in html_code
    assert "data-page-id" in html_code
    assert "getFreshAccessToken" in js_code
    assert "document.referrer" in js_code
    assert "window.top.location" in js_code


@pytest.mark.integration
def test_vues_encadrement_et_navigation_lot3(grist_client):
    """Vérifie le déploiement Lot 3 dans Grist : vues 6 et 10, retrait Fiche_HTML et menu latéral."""
    api_url, headers = grist_client

    r_tables = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Tables/records", headers=headers)
    assert r_tables.status_code == 200
    tables_map = {t["fields"].get("tableId"): t["id"] for t in r_tables.json().get("records", [])}
    table_ges_ref = tables_map["Acces_Gestionnaires"]

    r_cols = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Signalements/columns", headers=headers)
    assert r_cols.status_code == 200
    assert "Fiche_HTML" not in [c["id"] for c in r_cols.json().get("columns", [])]

    r_views = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Views/records", headers=headers)
    assert r_views.status_code == 200
    views_by_id = {v["id"]: v["fields"] for v in r_views.json().get("records", [])}

    r_secs = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Views_section/records", headers=headers)
    assert r_secs.status_code == 200
    secs = r_secs.json().get("records", [])

    # Aucune section personnalisée active de type renderhtml ne doit subsister
    for sec in secs:
        if sec["fields"].get("parentKey") == "custom":
            opts = sec["fields"].get("options") or "{}"
            assert "widget-renderhtml" not in opts

    # Vues 6 (Pilotage) et 10 (Espace encadrement) : pleine page sur Acces_Gestionnaires
    for view_id, expected_name, marker in [
        (6, "🎯 Pilotage et attribution", "Pilotage et attribution"),
        (10, "🛡️ Espace encadrement", "Espace encadrement"),
    ]:
        assert views_by_id[view_id].get("name") == expected_name
        secs_v = [s for s in secs if s["fields"].get("parentId") == view_id]
        assert len(secs_v) == 1
        sec = secs_v[0]
        assert sec["fields"].get("parentKey") == "custom"
        assert sec["fields"].get("tableRef") == table_ges_ref
        assert sec["fields"].get("linkSrcSectionRef") == 0
        cv = json.loads(json.loads(sec["fields"].get("options", "{}")).get("customView", "{}"))
        assert "custom-widget-builder" in cv.get("url", "")
        assert marker in cv.get("widgetOptions", {}).get("_html", "")
        layout = json.loads(views_by_id[view_id].get("layoutSpec", "{}"))
        assert layout.get("children") == [{"size": 100, "leaf": sec["id"]}]

    # Menu latéral réorganisé (incluant la vue bonus Gestion des agents du Lot 4)
    ga_view_id = next(vid for vid, vf in views_by_id.items() if vf.get("name") == "👥 Gestion des agents")
    r_pages = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Pages/records", headers=headers)
    assert r_pages.status_code == 200
    pages_sorted = sorted(r_pages.json().get("records", []), key=lambda p: p["fields"].get("pagePos", 0))
    assert [p["fields"].get("viewRef") for p in pages_sorted] == [5, 9, 10, 6, 8, ga_view_id]
    assert [p["fields"].get("indentation") for p in pages_sorted] == [0, 0, 0, 1, 1, 1]
