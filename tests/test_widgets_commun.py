# -*- coding: utf-8 -*-
"""Tests unitaires hors ligne pour le socle widgets et les règles ACL."""

import json

from configurer_droits_signalements import (
    COLONNES_ATTRIBUTION,
    DOSSIER_DE_L_AGENT,
    DOSSIER_RECEPTIONNE_NON_ATTRIBUE,
    EMAILS_GESTIONNAIRES,
    EMAILS_PROPRIETAIRES,
    EST_AGENT,
    EST_GESTIONNAIRE,
    EST_LIGNE_UTILISATEUR,
    EST_PROPRIETAIRE,
    RESSOURCES_ACL,
    construire_regles,
)
from widgets.commun import (
    COMMON_JS_HELPERS,
    CUSTOM_WIDGET_BUILDER_URL,
    GRIST_PLUGIN_API_URL,
    construire_options_custom_widget,
    envelopper_document_html,
)


def test_construire_options_custom_widget():
    spec = {"_html": "<p>Test</p>", "_js": "console.log('ok');"}
    opts = json.loads(construire_options_custom_widget(spec))
    cv = json.loads(opts["customView"])
    assert cv["mode"] == "url"
    assert cv["url"] == CUSTOM_WIDGET_BUILDER_URL
    assert cv["access"] == "full"
    assert cv["widgetOptions"]["_html"] == "<p>Test</p>"
    assert cv["widgetOptions"]["_js"] == "console.log('ok');"


def test_envelopper_document_html_et_print_css():
    doc = envelopper_document_html("Fiche test", "<div class='sig-wrap'>Contenu</div>")
    assert GRIST_PLUGIN_API_URL in doc
    assert "@media print" in doc
    assert "overflow: visible !important" in doc
    assert "height: auto !important" in doc
    assert ".no-print" in doc


def test_common_js_helpers_fonctions_requises():
    for symbole in [
        "tableToRows",
        "escapeHtml",
        "loadSessionContext",
        "getFreshAccessToken",
        "fetchWithFreshToken",
        "uploadAttachment",
        "fetchAttachmentMeta",
        "fetchAttachmentsMetaByIds",
        "fetchAttachmentBlob",
        "downloadAttachment",
        "decodeAttachmentIds",
        "buildCsvUtf8Bom",
        "X-Requested-With",
        'credentials: "omit"',
        'Role: a.Role || "Agent"',
    ]:
        assert symbole in COMMON_JS_HELPERS


def test_construire_regles_lot1_securite_et_non_regression():
    fake_ids = list(range(101, 101 + len(RESSOURCES_ACL)))
    id_by_res = {(r["tableId"], r["colIds"]): fake_ids[i] for i, r in enumerate(RESSOURCES_ACL)}
    regles = construire_regles(fake_ids)

    # Numérotation séquentielle des rulePos
    assert [r["rulePos"] for r in regles] == [float(i) for i in range(1, len(regles) + 1)]

    # Attribut utilisateur Agent déclaré en première position sur (*, *)
    assert regles[0]["resource"] == id_by_res[("*", "*")]
    assert '"name": "Agent"' in regles[0].get("userAttributes", "")
    assert "Referentiel_Agents" in regles[0].get("userAttributes", "")

    # Aucune règle sur Signalements:* ou Signalements:COLONNES_ATTRIBUTION ne donne +U ou +D à EST_AGENT
    res_sig = id_by_res[("Signalements", "*")]
    res_attrib = id_by_res[("Signalements", COLONNES_ATTRIBUTION)]
    for r in regles:
        if r["resource"] in (res_sig, res_attrib) and EST_AGENT in r["aclFormula"]:
            assert "+U" not in r["permissionsText"]
            assert "+D" not in r["permissionsText"]

    # Comparaison sur user.Agent.id et absence de -C sur les règles de lecture
    assert "rec.Agent_Attributaire == user.Agent.id" in DOSSIER_DE_L_AGENT
    assert "rec.Agent_Recepteur == user.Agent.id" in DOSSIER_RECEPTIONNE_NON_ATTRIBUE
    assert "not rec.Agent_Attributaire" in DOSSIER_RECEPTIONNE_NON_ATTRIBUE

    # Les règles de lecture agent sur Signalements:* n'ont pas -C (ne bloquent pas la création)
    regles_sig_lecture = [
        r for r in regles
        if r["resource"] == res_sig and r["aclFormula"] in (DOSSIER_DE_L_AGENT, DOSSIER_RECEPTIONNE_NON_ATTRIBUE)
    ]
    assert len(regles_sig_lecture) == 2
    for r in regles_sig_lecture:
        assert r["permissionsText"] == "+R-U-D"
        assert "-C" not in r["permissionsText"]

    # Est_Connecte et Acces_Gestionnaires protégés
    res_connecte = id_by_res[("Referentiel_Agents", "Est_Connecte")]
    regles_conn = [r for r in regles if r["resource"] == res_connecte]
    assert len(regles_conn) == 2
    assert regles_conn[0]["aclFormula"] == EST_LIGNE_UTILISATEUR
    assert regles_conn[0]["permissionsText"] == "+R-U"
    assert regles_conn[1]["permissionsText"] == "-R-U"

    res_ges = id_by_res[("Acces_Gestionnaires", "*")]
    regles_ges = [r for r in regles if r["resource"] == res_ges]
    assert len(regles_ges) == 2
    assert regles_ges[0]["permissionsText"] == "+R+U+C+D"
    assert regles_ges[1]["permissionsText"] == "-R-U-C-D"


def test_perimetre_proprietaires_gestionnaires_et_suppression():
    assert len(EMAILS_PROPRIETAIRES) >= 1
    assert len(EMAILS_GESTIONNAIRES) >= len(EMAILS_PROPRIETAIRES)
    assert set(EMAILS_PROPRIETAIRES).issubset(set(EMAILS_GESTIONNAIRES))

    fake_ids = list(range(101, 101 + len(RESSOURCES_ACL)))
    id_by_res = {(r["tableId"], r["colIds"]): fake_ids[i] for i, r in enumerate(RESSOURCES_ACL)}
    regles = construire_regles(fake_ids)

    regles_schema = [r for r in regles if r["resource"] == id_by_res[("*", "*")] and r["permissionsText"] == "-S"]
    assert len(regles_schema) == 1
    assert regles_schema[0]["aclFormula"] == f"not ({EST_PROPRIETAIRE})"
    for email in EMAILS_GESTIONNAIRES:
        assert email not in regles_schema[0]["aclFormula"]
    assert 'user.Agent.Role == "Gestionnaire"' in EST_GESTIONNAIRE
    assert "@" not in EST_GESTIONNAIRE

    for table in ("Signalements", "Retours_Actions"):
        res_id = id_by_res[(table, "*")]
        regles_table = [r for r in regles if r["resource"] == res_id]
        regles_d = [r for r in regles_table if "+D" in r["permissionsText"]]
        assert len(regles_d) == 1
        assert regles_d[0]["aclFormula"] == EST_GESTIONNAIRE
        assert regles_d[0]["permissionsText"] == "+R+U+C+D"
        for r in regles_table:
            if r is not regles_d[0]:
                assert "-D" in r["permissionsText"]
                assert "+D" not in r["permissionsText"]
