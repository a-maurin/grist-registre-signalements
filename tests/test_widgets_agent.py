# -*- coding: utf-8 -*-
"""Tests unitaires hors ligne pour les widgets agent du Lot 2."""

import json

from config import DOC_URL_PILOTAGE, ENCADRANT_PAR_DEFAUT
from widgets.commun import CUSTOM_WIDGET_BUILDER_URL, construire_options_custom_widget
from widgets.mes_dossiers_html import generer_widget_mes_dossiers
from widgets.nouveau_signalement_html import generer_widget_nouveau_signalement


def test_widget_nouveau_signalement_structure_et_champs():
    spec = generer_widget_nouveau_signalement()
    html_code = spec["_html"]
    js_code = spec["_js"]

    assert 'grist.ready({ requiredAccess: "full" })' in js_code
    for champ_id in [
        "dateReception",
        "agentRecepteur",
        "canalReception",
        "requerantNom",
        "requerantContact",
        "commune",
        "lieuDit",
        "domaineActivite",
        "descriptionFaits",
        "piecesJointesInput",
        "encadrantAlerter",
        "btnAlerterEncadrant",
    ]:
        assert champ_id in html_code

    assert ENCADRANT_PAR_DEFAUT in html_code
    assert "ns-grid-2" in html_code
    assert "ns-dropzone" in html_code
    assert "toDatetimeLocalValue" in js_code
    assert "loadSessionContext" in js_code
    assert "uploadAttachment" in js_code
    assert '["AddRecord", "Signalements", null, fields]' in js_code
    assert "Action_Alerter_Encadrant" in js_code
    assert "Numero_Signalement" in js_code
    assert DOC_URL_PILOTAGE in js_code

    opts = json.loads(construire_options_custom_widget(spec))
    cv = json.loads(opts["customView"])
    assert cv["url"] == CUSTOM_WIDGET_BUILDER_URL
    assert cv["access"] == "full"


def test_widget_mes_dossiers_onglets_retours_et_repli_pj():
    spec = generer_widget_mes_dossiers()
    html_code = spec["_html"]
    js_code = spec["_js"]

    assert 'grist.ready({ requiredAccess: "full" })' in js_code
    assert "height: 100vh;" in html_code
    assert "overflow: hidden;" in html_code
    assert "overflow-y: auto;" in html_code
    assert "min-height: 0;" in html_code
    assert "@media print" in html_code
    assert DOC_URL_PILOTAGE in js_code
    assert "tabAttribues" in html_code
    assert "tabAttente" in html_code
    assert "isDossierAttribueAMoi" in js_code
    assert "isDossierEnAttenteParMoi" in js_code
    assert "!rec.Statut_Manuel" in js_code
    assert "btnOpenRetourModal" in js_code
    assert '["AddRecord", "Retours_Actions", null, fields]' in js_code
    assert "uploadAttachment" in js_code
    assert "fetchAttachmentsMetaByIds" in js_code
    assert "Pièces jointes (accès natif)" in js_code
    assert "setCursorPos" in js_code
    assert "window.print()" in js_code
    assert "encadrant par courriel" in js_code
    assert "openRetourModal" in js_code
    assert "if (!isDossierAttribueAMoi(dossier)) return;" in js_code
