# -*- coding: utf-8 -*-
"""Générateur du widget HTML « 🗂️ Mes dossiers » (Lot 2)."""

import html
import json

from config import DOC_URL_PILOTAGE, ENCADRANT_PAR_DEFAUT
from widgets.commun import (
    CHOIX_DEMARCHE,
    CHOIX_SUITE,
    COMMON_JS_HELPERS,
    envelopper_document_html,
)

MES_DOSSIERS_CSS = """
html, body {
  height: 100vh;
  overflow: hidden;
}
.sig-wrap {
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding-bottom: 12px;
}
.sig-header, .md-tabs, .sig-toolbar, #mdBanner {
  flex-shrink: 0;
}
.sig-layout {
  flex: 1 1 auto;
  min-height: 0;
  align-items: stretch;
  grid-template-rows: minmax(0, 1fr);
  overflow: hidden;
}
@media (max-width: 900px) {
  .sig-layout {
    grid-template-rows: minmax(180px, 42%) minmax(0, 1fr);
  }
}
.sig-master, .sig-detail {
  min-height: 0;
  height: 100%;
  overflow-y: auto;
}
.sig-detail {
  padding-right: 2px;
}
.md-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}
.md-tab {
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #334155;
  border-radius: 8px;
  padding: 7px 13px;
  font-family: inherit;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 7px;
}
.md-tab:hover { background: #f1f5f9; }
.md-tab.active {
  background: #005bb5;
  border-color: #005bb5;
  color: #ffffff;
}
.md-tab-count {
  padding: 1px 7px;
  border-radius: 999px;
  font-size: 11px;
  background: rgba(15, 23, 42, 0.08);
}
.md-tab.active .md-tab-count {
  background: rgba(255, 255, 255, 0.22);
  color: #ffffff;
}
.md-list-item {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 9px;
  padding: 10px 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: border-color 0.12s ease, background 0.12s ease;
}
.md-list-item:hover { border-color: #93c5fd; background: #f8fafc; }
.md-list-item.selected {
  border-color: #005bb5;
  border-width: 2px;
  padding: 9px 11px;
  background: #eff6ff;
}
.md-list-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}
.md-num {
  font-weight: 800;
  color: #005bb5;
  font-size: 13.5px;
}
.md-meta {
  font-size: 12px;
  color: #475569;
  margin-top: 3px;
}
.md-fiche-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  border-bottom: 2px solid #005bb5;
  padding-bottom: 10px;
  margin-bottom: 12px;
}
.md-fiche-num {
  margin: 2px 0 0;
  font-size: 20px;
  font-weight: 800;
  color: #005bb5;
}
.md-box-consigne {
  background: #fffbeb;
  border-left: 3px solid #f59e0b;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  color: #78350f;
  margin-top: 6px;
}
.md-box-attente {
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 12.5px;
  color: #9a3412;
  margin-bottom: 10px;
}
.md-pj-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}
.md-pj-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 9px;
  border-radius: 6px;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  font-size: 12px;
  color: #1e293b;
}
.md-pj-note {
  margin-top: 6px;
  font-size: 11.5px;
  color: #64748b;
}
.md-empty {
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
  padding: 28px 18px;
  text-align: center;
  color: #64748b;
}
.md-files-preview {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-top: 6px;
}
@media print {
  html, body, .sig-wrap, .sig-layout, .sig-detail, .sig-fiche {
    height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    display: block !important;
  }
  .sig-master {
    display: none !important;
  }
}
"""


def _options_select(valeurs):
    return "\n".join(
        f'              <option value="{html.escape(v, quote=True)}">{html.escape(v)}</option>'
        for v in valeurs
    )


def generer_widget_mes_dossiers():
    """Retourne {_html, _js} pour l'espace unifié « 🗂️ Mes dossiers »."""
    demarches_opts = _options_select(CHOIX_DEMARCHE)
    suites_opts = _options_select(CHOIX_SUITE)

    body_html = f"""  <div class="sig-wrap">
    <div class="sig-header no-print">
      <div>
        <h1 class="sig-title">🗂️ Mes dossiers</h1>
        <p class="sig-subtitle">Suivi des signalements qui vous sont attribués et des saisies en attente d'attribution.</p>
      </div>
      <span class="sig-badge badge-info" id="mdSessionBadge">Session en cours...</span>
    </div>

    <div class="md-tabs no-print" role="tablist">
      <button type="button" class="md-tab active" id="tabAttribues" data-tab="attribues">
        Dossiers attribués <span class="md-tab-count" id="cntAttribues">0</span>
      </button>
      <button type="button" class="md-tab" id="tabAttente" data-tab="attente">
        En attente d'attribution <span class="md-tab-count" id="cntAttente">0</span>
      </button>
    </div>

    <div class="sig-toolbar no-print">
      <div class="sig-pills" id="mdStatusPills">
        <button type="button" class="sig-pill active" data-status="a_traiter">À traiter</button>
        <button type="button" class="sig-pill" data-status="en_cours">En cours</button>
        <button type="button" class="sig-pill" data-status="clos">Traités / clos</button>
        <button type="button" class="sig-pill" data-status="tous">Tous</button>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:8px;flex:1 1 320px;justify-content:flex-end;">
        <select class="sig-select" id="mdSortSelect" style="width:auto;min-width:160px;max-width:100%;" aria-label="Trier les dossiers">
          <option value="prio_date">Tri : Priorité puis récents</option>
          <option value="date_desc">Tri : Date décroissante</option>
          <option value="date_asc">Tri : Date croissante</option>
          <option value="statut">Tri : Statut</option>
        </select>
        <input type="search" class="sig-input" id="mdSearchInput" style="flex:1 1 200px;max-width:300px;" placeholder="Rechercher numéro, commune, domaine...">
      </div>
    </div>

    <div id="mdBanner" class="sig-banner no-print" role="status"></div>

    <div class="sig-layout">
      <div class="sig-master no-print" id="mdMasterList">
        <div class="md-empty">Chargement de vos dossiers...</div>
      </div>
      <div class="sig-detail sig-fiche" id="mdDetailPane">
        <div class="md-empty">Sélectionnez un dossier dans la liste pour afficher sa fiche complète.</div>
      </div>
    </div>
  </div>

  <div id="retourModalBackdrop" class="sig-modal-backdrop no-print" role="dialog" aria-modal="true" aria-labelledby="retourModalTitle">
    <div class="sig-modal">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <h2 id="retourModalTitle" style="margin:0;font-size:16px;">📝 Ajouter un retour d'intervention</h2>
        <button type="button" class="sig-btn" id="btnCloseRetourModal">Fermer</button>
      </div>
      <p id="retourModalDossier" style="margin:0 0 10px;font-size:12.5px;color:#475569;font-weight:600;"></p>
      <div id="retourModalErr" class="sig-banner" role="alert"></div>
      <form id="retourModalForm" novalidate>
        <div class="sig-grid-2">
          <div class="sig-field">
            <label for="retourDate">Date de l'intervention *</label>
            <input type="date" id="retourDate" required>
          </div>
          <div class="sig-field">
            <label for="retourDemarche">Nature de la démarche *</label>
            <select id="retourDemarche" required>
              <option value="">-- Sélectionnez une démarche --</option>
{demarches_opts}
            </select>
          </div>
        </div>
        <div class="sig-field">
          <label for="retourCompteRendu">Compte-rendu des constatations *</label>
          <textarea id="retourCompteRendu" rows="4" required placeholder="Constats effectués sur le terrain, échanges, éléments recueillis..."></textarea>
        </div>
        <div class="sig-field">
          <label for="retourSuite">Suite donnée (laisser vide si l'action reste en cours)</label>
          <select id="retourSuite">
            <option value="">-- Aucune suite définitive (reste En cours) --</option>
{suites_opts}
          </select>
        </div>
        <div class="sig-field">
          <label for="retourPjInput">Photographies et pièces justificatives</label>
          <input type="file" id="retourPjInput" multiple>
          <div id="retourPjList" class="md-files-preview"></div>
        </div>
        <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:12px;">
          <button type="button" class="sig-btn" id="btnCancelRetour">Annuler</button>
          <button type="submit" class="sig-btn sig-btn-primary" id="btnSaveRetour">Valider le retour</button>
        </div>
      </form>
    </div>
  </div>"""

    cfg_json = json.dumps(
        {
            "docUrlPilotage": DOC_URL_PILOTAGE,
            "defaultEncadrant": ENCADRANT_PAR_DEFAUT,
        },
        ensure_ascii=False,
    )

    js_body = r"""
(function () {
  grist.ready({ requiredAccess: "full" });

  const sessionBadgeEl = document.getElementById("mdSessionBadge");
  const tabAttribuesEl = document.getElementById("tabAttribues");
  const tabAttenteEl = document.getElementById("tabAttente");
  const cntAttribuesEl = document.getElementById("cntAttribues");
  const cntAttenteEl = document.getElementById("cntAttente");
  const statusPillsEl = document.getElementById("mdStatusPills");
  const sortSelectEl = document.getElementById("mdSortSelect");
  const searchInputEl = document.getElementById("mdSearchInput");
  const bannerEl = document.getElementById("mdBanner");
  const masterListEl = document.getElementById("mdMasterList");
  const detailPaneEl = document.getElementById("mdDetailPane");

  const modalBackdropEl = document.getElementById("retourModalBackdrop");
  const modalDossierEl = document.getElementById("retourModalDossier");
  const modalErrEl = document.getElementById("retourModalErr");
  const modalFormEl = document.getElementById("retourModalForm");
  const retourDateEl = document.getElementById("retourDate");
  const retourDemarcheEl = document.getElementById("retourDemarche");
  const retourCrEl = document.getElementById("retourCompteRendu");
  const retourSuiteEl = document.getElementById("retourSuite");
  const retourPjInputEl = document.getElementById("retourPjInput");
  const retourPjListEl = document.getElementById("retourPjList");
  const btnCloseModalEl = document.getElementById("btnCloseRetourModal");
  const btnCancelRetourEl = document.getElementById("btnCancelRetour");
  const btnSaveRetourEl = document.getElementById("btnSaveRetour");

  let sessionCtx = { agents: [], agentsById: {}, agentsByNom: {}, connectedAgent: null, isManager: false };
  let allSignalements = [];
  let retoursBySig = {};
  let activeTab = "attribues";
  let statusFilter = "a_traiter";
  let selectedId = null;
  let reloadTimer = null;
  let modalFiles = [];
  let modalTargetDossier = null;
  let attMetaCache = {};

  function statutBadgeClass(statut) {
    if (statut === "Nouveau") return "badge-nouveau";
    if (statut === "Attribué") return "badge-attribue";
    if (statut === "En cours") return "badge-encours";
    if (statut === "Traité") return "badge-traite";
    if (statut === "Classé sans suite") return "badge-classe";
    return "badge-info";
  }

  function prioriteBadgeClass(prio) {
    if (prio === "Urgente") return "badge-urgente";
    if (prio === "Faible") return "badge-faible";
    return "badge-normale";
  }

  function prioriteRank(prio) {
    if (prio === "Urgente") return 0;
    if (prio === "Normale" || !prio) return 1;
    return 2;
  }

  function agentNomFromVal(val, fallback) {
    if (typeof val === "number" && val > 0 && sessionCtx.agentsById[val]) {
      return sessionCtx.agentsById[val].Nom;
    }
    if (typeof val === "string" && val.trim()) return val.trim();
    return fallback;
  }

  function isDossierAttribueAMoi(rec) {
    if (!sessionCtx.connectedAgent) return false;
    return typeof rec.Agent_Attributaire === "number" && rec.Agent_Attributaire === sessionCtx.connectedAgent.id;
  }

  function isDossierEnAttenteParMoi(rec) {
    if (!sessionCtx.connectedAgent) return false;
    const attrVide = rec.Agent_Attributaire === 0 || rec.Agent_Attributaire === null || rec.Agent_Attributaire === "";
    return attrVide && !rec.Statut_Manuel &&
      typeof rec.Agent_Recepteur === "number" && rec.Agent_Recepteur === sessionCtx.connectedAgent.id;
  }

  function buildFallbackMailto(rec) {
    const encNom = (typeof rec.Encadrant_A_Alerter === "string" && rec.Encadrant_A_Alerter) ? rec.Encadrant_A_Alerter : CFG.defaultEncadrant;
    const dest = sessionCtx.agentsByNom[encNom] || sessionCtx.agentsByNom[CFG.defaultEncadrant];
    const email = dest && dest.Email ? dest.Email : "";
    if (!email) return "#";
    const num = rec.Numero_Signalement || String(rec.id);
    const commune = rec.Commune || "Non précisée";
    const sujet = "[Signalement " + num + "] Nouveau signalement à attribuer - " + commune;
    const corps = [
      "Bonjour " + (dest ? dest.Nom : encNom) + ",",
      "",
      "Pour rappel, le signalement " + num + " (" + commune + ") est en attente d'attribution.",
      "Lien vers le pilotage : " + CFG.docUrlPilotage,
    ].join("\n");
    return "mailto:" + encodeURIComponent(email) + "?subject=" + encodeURIComponent(sujet) + "&body=" + encodeURIComponent(corps);
  }

  function renderContactHtml(contactRaw) {
    const c = String(contactRaw || "").trim();
    if (!c) return "Non communiqué";
    if (c.includes("@")) {
      return '<a href="mailto:' + encodeURIComponent(c) + '" style="color:#005bb5;font-weight:600;text-decoration:none;">✉️ ' + escapeHtml(c) + "</a>";
    }
    return '<a href="tel:' + encodeURIComponent(c) + '" style="color:#005bb5;font-weight:600;text-decoration:none;">📞 ' + escapeHtml(c) + "</a>";
  }

  function renderAttachmentChips(attIds, containerId) {
    if (!attIds.length) return '<span style="color:#64748b;font-size:12px;">Aucune pièce jointe.</span>';
    const chips = attIds.map((id) => {
      const meta = attMetaCache[id];
      if (meta && meta.fileName) {
        const kb = meta.fileSize ? " (" + Math.max(1, Math.round(meta.fileSize / 1024)) + " Ko)" : "";
        return (
          '<span class="md-pj-chip" data-att-chip="' + id + '">' +
          "<span>📎 " + escapeHtml(meta.fileName) + kb + "</span>" +
          '<button type="button" class="sig-btn no-print" style="padding:2px 7px;font-size:11px;" data-dl-att="' + id + '" data-dl-name="' + escapeHtml(meta.fileName) + '">Télécharger</button>' +
          "</span>"
        );
      }
      return '<span class="md-pj-chip" data-att-chip="' + id + '">📎 Pièce jointe #' + id + "</span>";
    }).join("");
    return (
      '<div class="md-pj-list" id="' + containerId + '">' + chips + "</div>" +
      '<div class="md-pj-note no-print">Consultation native : ouvrez le volet « 📎 Pièces jointes (accès natif) » en haut de la page.</div>'
    );
  }

  async function hydrateAttachmentChips(attIds) {
    const missing = attIds.filter((id) => !Object.prototype.hasOwnProperty.call(attMetaCache, id));
    if (!missing.length) return;
    try {
      const fetched = await fetchAttachmentsMetaByIds(missing);
      for (const id of missing) {
        attMetaCache[id] = fetched[id] || null;
      }
      for (const id of missing) {
        const meta = attMetaCache[id];
        if (!meta || !meta.fileName) continue;
        const nodes = detailPaneEl.querySelectorAll('[data-att-chip="' + id + '"]');
        const kb = meta.fileSize ? " (" + Math.max(1, Math.round(meta.fileSize / 1024)) + " Ko)" : "";
        nodes.forEach((node) => {
          node.innerHTML =
            "<span>📎 " + escapeHtml(meta.fileName) + kb + "</span>" +
            '<button type="button" class="sig-btn no-print" style="padding:2px 7px;font-size:11px;" data-dl-att="' + id + '" data-dl-name="' + escapeHtml(meta.fileName) + '">Télécharger</button>';
        });
      }
    } catch (e) {
      // Repli Option B silencieux en rôle éditeur
    }
  }

  function getFilteredDossiers() {
    const listAttrib = allSignalements.filter(isDossierAttribueAMoi);
    const listAttente = allSignalements.filter(isDossierEnAttenteParMoi);
    cntAttribuesEl.textContent = String(listAttrib.length);
    cntAttenteEl.textContent = String(listAttente.length);

    let base = activeTab === "attribues" ? listAttrib : listAttente;
    if (activeTab === "attribues") {
      if (statusFilter === "a_traiter") {
        base = base.filter((r) => r.Statut !== "Traité" && r.Statut !== "Classé sans suite");
      } else if (statusFilter === "en_cours") {
        base = base.filter((r) => r.Statut === "En cours");
      } else if (statusFilter === "clos") {
        base = base.filter((r) => r.Statut === "Traité" || r.Statut === "Classé sans suite");
      }
    }

    const q = searchInputEl.value.trim().toLowerCase();
    if (q) {
      base = base.filter((r) => {
        const blob = [
          r.Numero_Signalement,
          r.Commune,
          r.Lieu_Dit,
          r.Domaine_Activite,
          r.Requerant_Nom,
          r.Description_Faits,
          r.Statut,
        ].join(" ").toLowerCase();
        return blob.includes(q);
      });
    }

    const sortMode = sortSelectEl.value;
    base = base.slice().sort((a, b) => {
      if (sortMode === "date_asc") {
        return (Number(a.Date_Heure_Reception) || 0) - (Number(b.Date_Heure_Reception) || 0);
      }
      if (sortMode === "date_desc") {
        return (Number(b.Date_Heure_Reception) || 0) - (Number(a.Date_Heure_Reception) || 0);
      }
      if (sortMode === "statut") {
        return String(a.Statut || "").localeCompare(String(b.Statut || ""), "fr") ||
          ((Number(b.Date_Heure_Reception) || 0) - (Number(a.Date_Heure_Reception) || 0));
      }
      const pDiff = prioriteRank(a.Priorite) - prioriteRank(b.Priorite);
      if (pDiff !== 0) return pDiff;
      return (Number(b.Date_Heure_Reception) || 0) - (Number(a.Date_Heure_Reception) || 0);
    });

    return base;
  }

  function syncCursor(rowId) {
    try {
      if (grist && typeof grist.setCursorPos === "function" && rowId) {
        grist.setCursorPos({ rowId });
      }
    } catch (e) {}
  }

  function renderDetail(dossier) {
    if (!dossier) {
      detailPaneEl.innerHTML = '<div class="md-empty">Aucun dossier sélectionné dans cet onglet.</div>';
      return;
    }
    const attribueAMoi = isDossierAttribueAMoi(dossier);
    const statut = attribueAMoi ? (dossier.Statut || "Attribué") : "En attente d'attribution";
    const prio = (attribueAMoi && dossier.Priorite) ? dossier.Priorite : "Normale";
    const num = dossier.Numero_Signalement || ("#" + dossier.id);
    const commune = dossier.Commune || "Non renseignée";
    const lieuDit = dossier.Lieu_Dit || "";
    const domaine = dossier.Domaine_Activite || "Non spécifié";
    const reqNom = dossier.Requerant_Nom || "Anonyme / Non communiqué";
    const agRec = agentNomFromVal(dossier.Agent_Recepteur, "Non renseigné");
    const agAtt = attribueAMoi ? agentNomFromVal(dossier.Agent_Attributaire, "Non attribué") : "Non attribué";
    const dateRec = formatDateFr(dossier.Date_Heure_Reception, true);
    const dateAtt = dossier.Date_Attribution ? formatDateFr(dossier.Date_Attribution, false) : "En attente";
    const consignes = attribueAMoi ? String(dossier.Consignes_Hierarchie || "").trim() : "";
    const locQuery = (commune + " " + lieuDit).trim();
    const locUrl = locQuery && locQuery !== "Non renseignée"
      ? "https://www.openstreetmap.org/search?query=" + encodeURIComponent(locQuery)
      : "";

    const sigPjIds = decodeAttachmentIds(dossier.Pieces_Jointes);
    const retours = (retoursBySig[dossier.id] || []).slice().sort((a, b) => {
      return (Number(a.Date_Intervention) || a.id) - (Number(b.Date_Intervention) || b.id);
    });

    const allPjIds = sigPjIds.slice();
    let retoursHtml = "";
    if (attribueAMoi) {
      if (retours.length === 0) {
        retoursHtml = '<div class="sig-card"><h2 style="margin-bottom:6px;">🏁 Retours d\'intervention (0)</h2><p style="margin:0;color:#64748b;">Aucun retour enregistré pour le moment.</p></div>';
      } else {
        const itemsHtml = retours.map((ret) => {
          const rPjIds = decodeAttachmentIds(ret.Pieces_Jointes);
          rPjIds.forEach((id) => allPjIds.push(id));
          const rAgent = agentNomFromVal(ret.Agent_Intervenant, "Agent");
          const suiteTxt = ret.Suite_Donnee ? '<span class="sig-badge badge-traite">' + escapeHtml(ret.Suite_Donnee) + "</span>" : '<span class="sig-badge badge-encours">En cours</span>';
          return (
            '<div class="sig-retour-item print-avoid-break">' +
              '<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:6px;">' +
                "<strong>" + escapeHtml(formatDateFr(ret.Date_Intervention, false)) + " — " + escapeHtml(ret.Type_Demarche || "Démarche") + "</strong>" +
                suiteTxt +
              "</div>" +
              '<div style="font-size:12px;color:#64748b;margin-bottom:6px;">Intervenant : ' + escapeHtml(rAgent) + "</div>" +
              '<div style="white-space:pre-wrap;font-size:12.5px;color:#1e293b;margin-bottom:8px;">' + escapeHtml(ret.Compte_Rendu || "Aucun compte-rendu.") + "</div>" +
              renderAttachmentChips(rPjIds, "pjRetour_" + ret.id) +
            "</div>"
          );
        }).join("");
        retoursHtml = '<div class="sig-card"><h2>🏁 Historique des retours d\'intervention (' + retours.length + ")</h2>" + itemsHtml + "</div>";
      }
    }

    const actionHeaderHtml = attribueAMoi
      ? '<button type="button" class="sig-btn sig-btn-primary no-print" id="btnOpenRetourModal">📝 Ajouter un retour d\'intervention</button>'
      : '<a class="sig-btn sig-btn-primary no-print" href="' + escapeHtml((dossier.Action_Alerter_Encadrant && String(dossier.Action_Alerter_Encadrant).startsWith("mailto:")) ? dossier.Action_Alerter_Encadrant : buildFallbackMailto(dossier)) + '">✉️ Alerter l\'encadrant par courriel</a>';

    const priseEnChargeHtml = attribueAMoi
      ? (
        '<div class="sig-card print-avoid-break">' +
          "<h2>🎯 Prise en charge hiérarchique</h2>" +
          '<div style="font-weight:700;margin-bottom:4px;">Attribué à : <span style="color:#005bb5;">' + escapeHtml(agAtt) + "</span></div>" +
          '<div style="font-size:12px;color:#64748b;">Attribution : ' + escapeHtml(dateAtt) + "</div>" +
          (consignes ? '<div class="md-box-consigne"><strong>Consignes hiérarchie :</strong> ' + escapeHtml(consignes) + "</div>" : "") +
        "</div>"
      )
      : (
        '<div class="sig-card print-avoid-break">' +
          "<h2>⏳ Attribution hiérarchique</h2>" +
          '<div class="md-box-attente">Dossier en attente d\'attribution (consultation en lecture seule jusqu\'à prise en charge par l\'encadrement).</div>' +
        "</div>"
      );

    detailPaneEl.innerHTML =
      '<div class="sig-card">' +
        '<div class="md-fiche-head">' +
          "<div>" +
            '<div style="font-size:11px;font-weight:700;text-transform:uppercase;color:#64748b;">Fiche de synthèse signalement</div>' +
            '<h2 class="md-fiche-num">' + escapeHtml(num) + "</h2>" +
          "</div>" +
          '<div style="display:flex;flex-wrap:wrap;align-items:center;gap:6px;">' +
            (attribueAMoi ? '<span class="sig-badge ' + prioriteBadgeClass(prio) + '">' + escapeHtml(prio) + "</span>" : "") +
            '<span class="sig-badge ' + statutBadgeClass(statut) + '">' + escapeHtml(statut) + "</span>" +
            '<button type="button" class="sig-btn no-print" id="btnPrintFiche">🖨️ Imprimer</button>' +
            actionHeaderHtml +
          "</div>" +
        "</div>" +
        '<div class="sig-grid-2">' +
          '<div class="sig-card print-avoid-break" style="margin-bottom:0;">' +
            "<h2>👤 Origine de la saisine</h2>" +
            '<div style="font-weight:700;margin-bottom:4px;">' + escapeHtml(reqNom) + "</div>" +
            '<div style="font-size:12px;color:#475569;margin-bottom:4px;"><strong>Contact :</strong> ' + renderContactHtml(dossier.Requerant_Contact) + "</div>" +
            '<div style="font-size:12px;color:#64748b;">Reçu le ' + escapeHtml(dateRec) + " via <em>" + escapeHtml(dossier.Canal_Reception || "Non précisé") + "</em> (par " + escapeHtml(agRec) + ")</div>" +
          "</div>" +
          priseEnChargeHtml.replace('class="sig-card print-avoid-break"', 'class="sig-card print-avoid-break" style="margin-bottom:0;"') +
        "</div>" +
      "</div>" +
      '<div class="sig-card print-avoid-break">' +
        '<div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:8px;margin-bottom:8px;">' +
          "<div>" +
            '<span style="font-size:11px;font-weight:700;text-transform:uppercase;color:#64748b;">📍 Localisation :</span> ' +
            "<strong>" + escapeHtml(commune) + "</strong>" +
            (lieuDit ? '<span style="color:#64748b;"> (' + escapeHtml(lieuDit) + ")</span>" : "") +
            (locUrl ? ' <a href="' + locUrl + '" target="_blank" rel="noopener" class="sig-btn no-print" style="padding:2px 8px;font-size:11.5px;margin-left:6px;">🗺️ Carte</a>' : "") +
          "</div>" +
          '<span class="sig-badge badge-classe">' + escapeHtml(domaine) + "</span>" +
        "</div>" +
        '<div style="font-size:12px;font-weight:700;color:#475569;margin-bottom:4px;">Description des faits :</div>' +
        '<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:10px;white-space:pre-wrap;margin-bottom:10px;">' + escapeHtml(dossier.Description_Faits || "Aucune description.") + "</div>" +
        '<div style="font-size:12px;font-weight:700;color:#475569;">Pièces jointes du signalement :</div>' +
        renderAttachmentChips(sigPjIds, "pjSignalement_" + dossier.id) +
      "</div>" +
      retoursHtml;

    const btnPrintEl = document.getElementById("btnPrintFiche");
    if (btnPrintEl) {
      btnPrintEl.addEventListener("click", () => window.print());
    }
    const btnOpenModalEl = document.getElementById("btnOpenRetourModal");
    if (btnOpenModalEl) {
      btnOpenModalEl.addEventListener("click", () => openRetourModal(dossier));
    }

    if (allPjIds.length > 0) {
      hydrateAttachmentChips(allPjIds);
    }
  }

  function renderView() {
    statusPillsEl.classList.toggle("hidden", activeTab !== "attribues");
    const filtered = getFilteredDossiers();
    if (!filtered.length) {
      selectedId = null;
      masterListEl.innerHTML = '<div class="md-empty">Aucun dossier ne correspond aux filtres sélectionnés.</div>';
      renderDetail(null);
      return;
    }

    if (!filtered.some((r) => r.id === selectedId)) {
      selectedId = filtered[0].id;
    }

    masterListEl.innerHTML = filtered.map((r) => {
      const selCls = r.id === selectedId ? " selected" : "";
      const attrib = isDossierAttribueAMoi(r);
      const statut = attrib ? (r.Statut || "Attribué") : "En attente d'attribution";
      const prio = (attrib && r.Priorite) ? r.Priorite : "Normale";
      const pjCount = decodeAttachmentIds(r.Pieces_Jointes).length;
      const retCount = (retoursBySig[r.id] || []).length;
      return (
        '<div class="md-list-item' + selCls + '" data-sig-id="' + r.id + '">' +
          '<div class="md-list-top">' +
            '<span class="md-num">' + escapeHtml(r.Numero_Signalement || ("#" + r.id)) + "</span>" +
            '<div style="display:flex;gap:4px;">' +
              (attrib ? '<span class="sig-badge ' + prioriteBadgeClass(prio) + '">' + escapeHtml(prio) + "</span>" : "") +
              '<span class="sig-badge ' + statutBadgeClass(statut) + '">' + escapeHtml(statut) + "</span>" +
            "</div>" +
          "</div>" +
          '<div style="font-weight:700;color:#0f172a;">' + escapeHtml(r.Commune || "Commune non précisée") + (r.Lieu_Dit ? " — " + escapeHtml(r.Lieu_Dit) : "") + "</div>" +
          '<div class="md-meta">' + escapeHtml(r.Domaine_Activite || "Domaine non précisé") + " · " + escapeHtml(formatDateFr(r.Date_Heure_Reception, true)) + "</div>" +
          '<div class="md-meta">📎 ' + pjCount + " PJ" + (attrib ? (" · 🏁 " + retCount + " retour(s)") : "") + "</div>" +
        "</div>"
      );
    }).join("");

    const selected = filtered.find((r) => r.id === selectedId) || filtered[0];
    syncCursor(selected.id);
    renderDetail(selected);
  }

  function renderModalFiles() {
    retourPjListEl.innerHTML = "";
    modalFiles.forEach((f, idx) => {
      const item = document.createElement("div");
      item.style.cssText = "display:flex;justify-content:space-between;align-items:center;padding:4px 8px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;";
      item.innerHTML =
        "<span>📎 " + escapeHtml(f.name) + "</span>" +
        '<button type="button" class="sig-btn" style="padding:2px 7px;font-size:11px;" data-rm-modal-pj="' + idx + '">Retirer</button>';
      retourPjListEl.appendChild(item);
    });
  }

  function openRetourModal(dossier) {
    if (!isDossierAttribueAMoi(dossier)) return;
    modalTargetDossier = dossier;
    modalFiles = [];
    modalFormEl.reset();
    retourDateEl.value = new Date().toISOString().slice(0, 10);
    renderModalFiles();
    showBanner(modalErrEl, null);
    modalDossierEl.textContent = "Dossier " + (dossier.Numero_Signalement || ("#" + dossier.id)) + " — " + (dossier.Commune || "");
    modalBackdropEl.classList.add("open");
  }

  function closeRetourModal() {
    modalBackdropEl.classList.remove("open");
    modalTargetDossier = null;
  }

  async function loadData() {
    try {
      sessionCtx = await loadSessionContext();
      if (sessionCtx.connectedAgent) {
        sessionBadgeEl.textContent = "Connecté : " + sessionCtx.connectedAgent.Nom;
      } else {
        sessionBadgeEl.textContent = "Agent non identifié";
      }

      const rawSig = await grist.docApi.fetchTable("Signalements");
      allSignalements = tableToRows(rawSig);

      retoursBySig = {};
      try {
        const rawRet = await grist.docApi.fetchTable("Retours_Actions");
        for (const ret of tableToRows(rawRet)) {
          const sid = Number(ret.Signalement);
          if (sid > 0) {
            if (!retoursBySig[sid]) retoursBySig[sid] = [];
            retoursBySig[sid].push(ret);
          }
        }
      } catch (e) {
        retoursBySig = {};
      }
      renderView();
    } catch (err) {
      showBanner(bannerEl, formatGristError(err), "err");
    }
  }

  function scheduleReload() {
    if (reloadTimer) clearTimeout(reloadTimer);
    reloadTimer = setTimeout(() => {
      loadData();
    }, 250);
  }

  [tabAttribuesEl, tabAttenteEl].forEach((tabBtn) => {
    tabBtn.addEventListener("click", () => {
      activeTab = tabBtn.getAttribute("data-tab") || "attribues";
      tabAttribuesEl.classList.toggle("active", activeTab === "attribues");
      tabAttenteEl.classList.toggle("active", activeTab === "attente");
      selectedId = null;
      renderView();
    });
  });

  statusPillsEl.addEventListener("click", (ev) => {
    const btn = ev.target.closest("button[data-status]");
    if (!btn) return;
    statusFilter = btn.getAttribute("data-status") || "a_traiter";
    statusPillsEl.querySelectorAll(".sig-pill").forEach((p) => {
      p.classList.toggle("active", p === btn);
    });
    renderView();
  });

  sortSelectEl.addEventListener("change", renderView);
  searchInputEl.addEventListener("input", renderView);

  masterListEl.addEventListener("click", (ev) => {
    const item = ev.target.closest(".md-list-item[data-sig-id]");
    if (!item) return;
    selectedId = Number(item.getAttribute("data-sig-id"));
    renderView();
  });

  detailPaneEl.addEventListener("click", async (ev) => {
    const dlBtn = ev.target.closest("button[data-dl-att]");
    if (!dlBtn) return;
    const attId = Number(dlBtn.getAttribute("data-dl-att"));
    const fname = dlBtn.getAttribute("data-dl-name") || ("piece_jointe_" + attId);
    dlBtn.disabled = true;
    try {
      await downloadAttachment(attId, fname);
    } catch (err) {
      showBanner(
        bannerEl,
        "Téléchargement direct bloqué pour ce rôle. Utilisez le volet replié « 📎 Pièces jointes (accès natif) » en haut de la page.",
        "warn"
      );
    } finally {
      dlBtn.disabled = false;
    }
  });

  retourPjInputEl.addEventListener("change", () => {
    const incoming = Array.from(retourPjInputEl.files || []);
    if (incoming.length) {
      modalFiles = modalFiles.concat(incoming);
      retourPjInputEl.value = "";
      renderModalFiles();
    }
  });

  retourPjListEl.addEventListener("click", (ev) => {
    const btn = ev.target.closest("button[data-rm-modal-pj]");
    if (!btn) return;
    const idx = Number(btn.getAttribute("data-rm-modal-pj"));
    if (Number.isInteger(idx) && idx >= 0 && idx < modalFiles.length) {
      modalFiles.splice(idx, 1);
      renderModalFiles();
    }
  });

  btnCloseModalEl.addEventListener("click", closeRetourModal);
  btnCancelRetourEl.addEventListener("click", closeRetourModal);

  modalFormEl.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    if (!modalTargetDossier || !sessionCtx.connectedAgent) return;
    showBanner(modalErrEl, null);

    const dateTs = parseDateToTs(retourDateEl.value);
    const demarche = retourDemarcheEl.value.trim();
    const cr = retourCrEl.value.trim();
    const suite = retourSuiteEl.value.trim();

    if (!dateTs) {
      showBanner(modalErrEl, "Renseignez la date de l'intervention.", "err");
      return;
    }
    if (!demarche) {
      showBanner(modalErrEl, "Sélectionnez la nature de la démarche.", "err");
      return;
    }
    if (!cr) {
      showBanner(modalErrEl, "Renseignez le compte-rendu des constatations.", "err");
      return;
    }

    btnSaveRetourEl.disabled = true;
    btnSaveRetourEl.textContent = "Enregistrement...";
    try {
      const attIds = [];
      for (const file of modalFiles) {
        const attId = await uploadAttachment(file);
        attIds.push(attId);
      }
      const fields = {
        Signalement: modalTargetDossier.id,
        Agent_Intervenant: sessionCtx.connectedAgent.id,
        Date_Intervention: dateTs,
        Type_Demarche: demarche,
        Compte_Rendu: cr,
        Suite_Donnee: suite,
      };
      if (attIds.length > 0) {
        fields.Pieces_Jointes = ["L", ...attIds];
      }
      await grist.docApi.applyUserActions([["AddRecord", "Retours_Actions", null, fields]]);
      const numLabel = modalTargetDossier.Numero_Signalement || ("#" + modalTargetDossier.id);
      closeRetourModal();
      await loadData();
      showBanner(bannerEl, "Retour d'intervention enregistré sur le dossier " + numLabel + ".", "ok");
    } catch (err) {
      showBanner(modalErrEl, formatGristError(err), "err");
    } finally {
      btnSaveRetourEl.disabled = false;
      btnSaveRetourEl.textContent = "Valider le retour";
    }
  });

  if (typeof grist.onRecords === "function") {
    grist.onRecords(() => scheduleReload());
  }

  loadData();
})();
"""

    return {
        "_html": envelopper_document_html("Mes dossiers", body_html, extra_css=MES_DOSSIERS_CSS),
        "_js": f"const CFG = {cfg_json};\n{COMMON_JS_HELPERS}\n{js_body}".strip(),
    }


__all__ = ["generer_widget_mes_dossiers"]
