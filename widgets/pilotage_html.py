# -*- coding: utf-8 -*-
"""Générateur du widget HTML « 🎯 Pilotage et attribution » (Lot 3)."""

import html
import json

from config import CSV_PREFIX, DOC_URL
from widgets.commun import (
    CHOIX_DOMAINE,
    CHOIX_PRIORITE,
    CHOIX_STATUT,
    COMMON_JS_HELPERS,
    envelopper_document_html,
)

PILOTAGE_CSS = """
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
.sig-header, #pilRestricted, .pil-kpis, .sig-filters, #pilBanner {
  flex-shrink: 0;
}
#pilMainApp {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.sig-layout {
  flex: 1 1 auto;
  min-height: 0;
  align-items: stretch;
  grid-template-rows: minmax(0, 1fr);
  overflow: hidden;
}
@media (min-width: 1180px) {
  .sig-layout {
    grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
  }
}
@media (max-width: 1179px) {
  .sig-layout {
    grid-template-columns: minmax(0, 1fr);
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
#pilMasterTable thead th {
  position: sticky;
  top: 0;
  z-index: 2;
}
.sig-filters > * { min-width: 0; }
.pil-kpis {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-bottom: 10px;
}
.pil-kpi-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #334155;
  border-radius: 999px;
  padding: 5px 12px;
  font-family: inherit;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}
.pil-kpi-pill:hover { background: #f1f5f9; }
.pil-kpi-pill.active {
  background: #005bb5;
  border-color: #005bb5;
  color: #ffffff;
}
.pil-kpi-count {
  padding: 1px 7px;
  border-radius: 999px;
  font-size: 11px;
  background: rgba(15, 23, 42, 0.08);
}
.pil-kpi-pill.active .pil-kpi-count {
  background: rgba(255, 255, 255, 0.22);
  color: #ffffff;
}
.pil-filter-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1 1 150px;
  min-width: 0;
}
.pil-filter-item label {
  font-size: 11px;
  font-weight: 700;
  color: #475569;
}
#pilMasterTable {
  width: 100%;
  border-collapse: collapse;
}
#pilMasterTable th,
#pilMasterTable td {
  padding: 7px 6px;
  font-size: 12px;
  vertical-align: middle;
}
#pilMasterTable th {
  font-size: 11.5px;
  white-space: nowrap;
}
#pilMasterTable td:nth-child(1),
#pilMasterTable td:nth-child(2),
#pilMasterTable td:nth-child(5),
#pilMasterTable td:nth-child(6) {
  white-space: nowrap;
}
#pilMasterTable td:nth-child(3),
#pilMasterTable td:nth-child(4) {
  white-space: normal;
  overflow-wrap: break-word;
}
#pilMasterTable .sig-badge {
  padding: 2px 7px;
  font-size: 11px;
}
.pil-master-row { cursor: pointer; }
.pil-master-row:hover td { background: #f8fafc; }
.pil-master-row.selected td {
  background: #eff6ff;
  border-bottom-color: #bfdbfe;
}
.pil-num {
  font-weight: 800;
  color: #005bb5;
  white-space: nowrap;
}
.pil-fiche-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  border-bottom: 2px solid #005bb5;
  padding-bottom: 10px;
  margin-bottom: 12px;
}
.pil-fiche-num {
  margin: 2px 0 0;
  font-size: 20px;
  font-weight: 800;
  color: #005bb5;
}
.pil-action-panel {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
}
.pil-pj-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}
.pil-pj-chip {
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
.pil-empty {
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
  padding: 28px 18px;
  text-align: center;
  color: #64748b;
}
.pil-restricted {
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
  border-radius: 10px;
  padding: 24px 18px;
  text-align: center;
  font-weight: 600;
}
@media print {
  html, body, .sig-wrap, #pilMainApp, .sig-layout, .sig-detail, .sig-fiche {
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
        f'          <option value="{html.escape(v, quote=True)}">{html.escape(v)}</option>'
        for v in valeurs
    )


def generer_widget_pilotage():
    """Retourne {_html, _js} pour le widget d'encadrement « 🎯 Pilotage et attribution »."""
    statuts_opts = _options_select(CHOIX_STATUT)
    priorites_opts = _options_select(CHOIX_PRIORITE)
    domaines_opts = _options_select(CHOIX_DOMAINE)

    body_html = f"""  <div class="sig-wrap">
    <div class="sig-header no-print">
      <div>
        <h1 class="sig-title">🎯 Pilotage et attribution</h1>
        <p class="sig-subtitle">Suivi global des signalements, attribution aux agents, consignes et export consolidé.</p>
      </div>
      <div style="display:flex;flex-wrap:wrap;align-items:center;gap:8px;">
        <span class="sig-badge badge-info" id="pilSessionBadge">Vérification...</span>
        <button type="button" class="sig-btn" id="btnPilRefresh">🔄 Actualiser</button>
        <button type="button" class="sig-btn sig-btn-primary hidden" id="btnPilExportCsv">📥 Exporter CSV</button>
      </div>
    </div>

    <div id="pilRestricted" class="pil-restricted hidden no-print">
      Accès réservé à l'encadrement. Utilisez les pages « ✍️ Nouveau signalement » et « 🗂️ Mes dossiers » depuis le menu latéral.
    </div>

    <div id="pilMainApp" class="hidden">
      <div class="pil-kpis no-print" id="pilKpiBar">
        <button type="button" class="pil-kpi-pill active" data-kpi="tous">Tous <span class="pil-kpi-count" id="kpiTous">0</span></button>
        <button type="button" class="pil-kpi-pill" data-kpi="nouveau">Nouveaux <span class="pil-kpi-count" id="kpiNouveau">0</span></button>
        <button type="button" class="pil-kpi-pill" data-kpi="urgent">Urgents actifs <span class="pil-kpi-count" id="kpiUrgent">0</span></button>
        <button type="button" class="pil-kpi-pill" data-kpi="attribue">Attribués <span class="pil-kpi-count" id="kpiAttribue">0</span></button>
        <button type="button" class="pil-kpi-pill" data-kpi="encours">En cours <span class="pil-kpi-count" id="kpiEncours">0</span></button>
        <button type="button" class="pil-kpi-pill" data-kpi="clos">Traités / clos <span class="pil-kpi-count" id="kpiClos">0</span></button>
      </div>

      <div class="sig-filters no-print">
        <div class="pil-filter-item">
          <label for="pilFilterStatut">Statut</label>
          <select class="sig-select" id="pilFilterStatut">
            <option value="">Tous</option>
            <option value="__ACTIFS__">Non clos (actifs)</option>
{statuts_opts}
          </select>
        </div>
        <div class="pil-filter-item">
          <label for="pilFilterPriorite">Priorité</label>
          <select class="sig-select" id="pilFilterPriorite">
            <option value="">Toutes</option>
{priorites_opts}
          </select>
        </div>
        <div class="pil-filter-item">
          <label for="pilFilterDomaine">Domaine</label>
          <select class="sig-select" id="pilFilterDomaine">
            <option value="">Tous</option>
{domaines_opts}
          </select>
        </div>
        <div class="pil-filter-item">
          <label for="pilFilterAgent">Agent attributaire</label>
          <select class="sig-select" id="pilFilterAgent">
            <option value="">Tous</option>
            <option value="__NON_ATTRIBUE__">Non attribué</option>
          </select>
        </div>
        <div class="pil-filter-item" style="flex:2 1 220px;">
          <label for="pilSearchInput">Recherche libre</label>
          <input type="search" class="sig-input" id="pilSearchInput" placeholder="Numéro, commune, lieu-dit, requérant, faits...">
        </div>
        <div style="display:flex;align-items:flex-end;gap:8px;padding-top:14px;">
          <button type="button" class="sig-btn" id="btnPilResetFilters">Réinitialiser</button>
          <span id="pilMatchCount" style="font-size:12px;font-weight:700;color:#475569;white-space:nowrap;">0 / 0 dossiers</span>
        </div>
      </div>

      <div id="pilBanner" class="sig-banner no-print" role="status"></div>

      <div class="sig-layout">
        <div class="sig-master no-print">
          <div class="sig-table-wrap">
            <table class="sig-table" id="pilMasterTable">
              <thead>
                <tr>
                  <th class="sig-th-sort" data-sort-col="Numero_Signalement">N°</th>
                  <th class="sig-th-sort" data-sort-col="Date_Heure_Reception">Réception</th>
                  <th class="sig-th-sort" data-sort-col="Commune">Commune</th>
                  <th class="sig-th-sort" data-sort-col="Agent_Attributaire">Attributaire</th>
                  <th class="sig-th-sort" data-sort-col="Priorite">Priorité</th>
                  <th class="sig-th-sort" data-sort-col="Statut">Statut</th>
                </tr>
              </thead>
              <tbody id="pilMasterBody">
                <tr><td colspan="6" style="text-align:center;color:#64748b;padding:24px;">Chargement des signalements...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="sig-detail sig-fiche" id="pilDetailPane">
          <div class="pil-empty">Sélectionnez un signalement dans la liste pour afficher sa fiche complète et procéder à l'attribution.</div>
        </div>
      </div>
    </div>
  </div>

  <div id="pilDeleteBackdrop" class="sig-modal-backdrop no-print" role="dialog" aria-modal="true" aria-labelledby="pilDeleteTitle">
    <div class="sig-modal" style="max-width:500px;">
      <h2 id="pilDeleteTitle" style="margin:0 0 8px;font-size:16px;color:#991b1b;">Confirmer la suppression du signalement</h2>
      <div id="pilDeleteSummary" style="margin:0 0 12px;color:#334155;font-size:13px;"></div>
      <div id="pilDeleteErr" class="sig-banner" role="alert"></div>
      <div style="display:flex;justify-content:flex-end;gap:8px;">
        <button type="button" class="sig-btn" id="btnPilCancelDelete">Annuler</button>
        <button type="button" class="sig-btn sig-btn-danger" id="btnPilConfirmDelete">Supprimer définitivement</button>
      </div>
    </div>
  </div>"""

    cfg_json = json.dumps(
        {
            "choixPriorite": CHOIX_PRIORITE,
            "choixStatut": CHOIX_STATUT,
            "docUrl": DOC_URL,
            "csvPrefix": CSV_PREFIX,
        },
        ensure_ascii=False,
    )

    js_body = r"""
(function () {
  grist.ready({ requiredAccess: "full" });

  const sessionBadgeEl = document.getElementById("pilSessionBadge");
  const btnRefreshEl = document.getElementById("btnPilRefresh");
  const btnExportCsvEl = document.getElementById("btnPilExportCsv");
  const restrictedEl = document.getElementById("pilRestricted");
  const mainAppEl = document.getElementById("pilMainApp");
  const kpiBarEl = document.getElementById("pilKpiBar");
  const kpiTousEl = document.getElementById("kpiTous");
  const kpiNouveauEl = document.getElementById("kpiNouveau");
  const kpiUrgentEl = document.getElementById("kpiUrgent");
  const kpiAttribueEl = document.getElementById("kpiAttribue");
  const kpiEncoursEl = document.getElementById("kpiEncours");
  const kpiClosEl = document.getElementById("kpiClos");

  const filterStatutEl = document.getElementById("pilFilterStatut");
  const filterPrioriteEl = document.getElementById("pilFilterPriorite");
  const filterDomaineEl = document.getElementById("pilFilterDomaine");
  const filterAgentEl = document.getElementById("pilFilterAgent");
  const searchInputEl = document.getElementById("pilSearchInput");
  const btnResetFiltersEl = document.getElementById("btnPilResetFilters");
  const matchCountEl = document.getElementById("pilMatchCount");
  const bannerEl = document.getElementById("pilBanner");
  const masterTableEl = document.getElementById("pilMasterTable");
  const masterBodyEl = document.getElementById("pilMasterBody");
  const detailPaneEl = document.getElementById("pilDetailPane");
  const deleteBackdropEl = document.getElementById("pilDeleteBackdrop");
  const deleteSummaryEl = document.getElementById("pilDeleteSummary");
  const deleteErrEl = document.getElementById("pilDeleteErr");
  const btnCancelDeleteEl = document.getElementById("btnPilCancelDelete");
  const btnConfirmDeleteEl = document.getElementById("btnPilConfirmDelete");

  let sessionCtx = { agents: [], agentsById: {}, agentsByNom: {}, connectedAgent: null, isManager: false };
  let allSignalements = [];
  let retoursBySig = {};
  let activeKpi = "tous";
  let sortCol = "Date_Heure_Reception";
  let sortDir = "desc";
  let selectedId = null;
  let deletingDossier = null;
  let reloadTimer = null;
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

  function statutRank(statut) {
    const order = {
      "Nouveau": 0,
      "Attribué": 1,
      "En cours": 2,
      "Traité": 3,
      "Classé sans suite": 4,
    };
    return Object.prototype.hasOwnProperty.call(order, statut) ? order[statut] : 5;
  }

  function isClosStatut(statut) {
    return statut === "Traité" || statut === "Classé sans suite";
  }

  function agentNomFromVal(val, fallback) {
    if (typeof val === "number" && val > 0 && sessionCtx.agentsById[val]) {
      return sessionCtx.agentsById[val].Nom;
    }
    if (typeof val === "string" && val.trim()) return val.trim();
    return fallback;
  }

  function tsToDateInputValue(ts) {
    if (ts === null || ts === undefined || ts === "") return "";
    const num = Number(ts);
    if (!Number.isFinite(num)) return "";
    const d = new Date(num * 1000);
    if (Number.isNaN(d.getTime())) return "";
    const pad = (n) => String(n).padStart(2, "0");
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
  }

  function todayLocalIso() {
    return toDatetimeLocalValue(new Date()).slice(0, 10);
  }

  function renderContactHtml(contactRaw) {
    const c = String(contactRaw || "").trim();
    if (!c) return "Non communiqué";
    if (c.includes("@")) {
      return '<a href="mailto:' + encodeURIComponent(c) + '" style="color:#005bb5;font-weight:600;text-decoration:none;">✉️ ' + escapeHtml(c) + "</a>";
    }
    return '<a href="tel:' + encodeURIComponent(c) + '" style="color:#005bb5;font-weight:600;text-decoration:none;">📞 ' + escapeHtml(c) + "</a>";
  }

  function buildNotifierMailto(rec) {
    const attrId = typeof rec.Agent_Attributaire === "number" ? rec.Agent_Attributaire : 0;
    const agent = attrId > 0 ? sessionCtx.agentsById[attrId] : null;
    if (!agent || !agent.Email) return "";
    const num = rec.Numero_Signalement || ("#" + rec.id);
    const commune = rec.Commune || "";
    const sujet = "[Signalement " + num + "] Attribution de mission - " + commune;
    const corps = [
      "Bonjour " + agent.Nom + ",",
      "",
      "Un signalement vous a été attribué.",
      "",
      "N° Signalement : " + num,
      "Date de réception : " + formatDateFr(rec.Date_Heure_Reception, true),
      "Localisation : " + (commune || "Non précisée") + (rec.Lieu_Dit ? " - " + rec.Lieu_Dit : ""),
      "Domaine : " + (rec.Domaine_Activite || "Non précisé"),
      "Priorité : " + (rec.Priorite || "Normale"),
      "Consignes : " + (rec.Consignes_Hierarchie || "Aucune consigne particulière"),
      "",
      "Description des faits :",
      rec.Description_Faits || "Aucune description",
      "",
      "Accès direct : " + CFG.docUrl + "/p/9",
    ].join("\n");
    return "mailto:" + encodeURIComponent(agent.Email) + "?subject=" + encodeURIComponent(sujet) + "&body=" + encodeURIComponent(corps);
  }

  function renderAttachmentChips(attIds, containerId) {
    if (!attIds.length) return '<span style="color:#64748b;font-size:12px;">Aucune pièce jointe.</span>';
    const chips = attIds.map((id) => {
      const meta = attMetaCache[id];
      if (meta && meta.fileName) {
        const kb = meta.fileSize ? " (" + Math.max(1, Math.round(meta.fileSize / 1024)) + " Ko)" : "";
        return (
          '<span class="pil-pj-chip" data-att-chip="' + id + '">' +
          "<span>📎 " + escapeHtml(meta.fileName) + kb + "</span>" +
          '<button type="button" class="sig-btn no-print" style="padding:2px 7px;font-size:11px;" data-dl-att="' + id + '" data-dl-name="' + escapeHtml(meta.fileName) + '">Télécharger</button>' +
          "</span>"
        );
      }
      return '<span class="pil-pj-chip" data-att-chip="' + id + '">📎 Pièce jointe #' + id + "</span>";
    }).join("");
    return '<div class="pil-pj-list" id="' + containerId + '">' + chips + "</div>";
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
      // Repli silencieux Option B si le rôle ne permet pas l'accès REST aux pièces jointes
    }
  }

  function populateAgentFilter() {
    const previous = filterAgentEl.value;
    const opts = [
      '<option value="">Tous</option>',
      '<option value="__NON_ATTRIBUE__">Non attribué</option>',
    ];
    for (const ag of sessionCtx.agents) {
      opts.push('<option value="' + ag.id + '">' + escapeHtml(ag.Nom) + "</option>");
    }
    filterAgentEl.innerHTML = opts.join("");
    filterAgentEl.value = previous;
  }

  function updateKpis() {
    let nNouveau = 0;
    let nUrgent = 0;
    let nAttribue = 0;
    let nEncours = 0;
    let nClos = 0;
    for (const r of allSignalements) {
      const st = r.Statut || "Nouveau";
      if (st === "Nouveau") nNouveau++;
      if (st === "Attribué") nAttribue++;
      if (st === "En cours") nEncours++;
      if (isClosStatut(st)) nClos++;
      if (r.Priorite === "Urgente" && !isClosStatut(st)) nUrgent++;
    }
    kpiTousEl.textContent = String(allSignalements.length);
    kpiNouveauEl.textContent = String(nNouveau);
    kpiUrgentEl.textContent = String(nUrgent);
    kpiAttribueEl.textContent = String(nAttribue);
    kpiEncoursEl.textContent = String(nEncours);
    kpiClosEl.textContent = String(nClos);
  }

  function compareSignalements(a, b) {
    let cmp = 0;
    if (sortCol === "Numero_Signalement") {
      cmp = String(a.Numero_Signalement || "").localeCompare(String(b.Numero_Signalement || ""), "fr");
    } else if (sortCol === "Commune") {
      cmp = String(a.Commune || "").localeCompare(String(b.Commune || ""), "fr");
    } else if (sortCol === "Agent_Attributaire") {
      const nomA = agentNomFromVal(a.Agent_Attributaire, "zzz");
      const nomB = agentNomFromVal(b.Agent_Attributaire, "zzz");
      cmp = nomA.localeCompare(nomB, "fr");
    } else if (sortCol === "Priorite") {
      cmp = prioriteRank(a.Priorite) - prioriteRank(b.Priorite);
    } else if (sortCol === "Statut") {
      cmp = statutRank(a.Statut) - statutRank(b.Statut);
    } else {
      cmp = (Number(a.Date_Heure_Reception) || 0) - (Number(b.Date_Heure_Reception) || 0);
    }
    if (cmp === 0) {
      cmp = (Number(a.Date_Heure_Reception) || 0) - (Number(b.Date_Heure_Reception) || 0);
      if (cmp === 0) cmp = a.id - b.id;
    }
    return sortDir === "asc" ? cmp : -cmp;
  }

  function getFilteredAndSorted() {
    let list = allSignalements.slice();

    if (activeKpi === "nouveau") {
      list = list.filter((r) => (r.Statut || "Nouveau") === "Nouveau");
    } else if (activeKpi === "urgent") {
      list = list.filter((r) => r.Priorite === "Urgente" && !isClosStatut(r.Statut));
    } else if (activeKpi === "attribue") {
      list = list.filter((r) => r.Statut === "Attribué");
    } else if (activeKpi === "encours") {
      list = list.filter((r) => r.Statut === "En cours");
    } else if (activeKpi === "clos") {
      list = list.filter((r) => isClosStatut(r.Statut));
    }

    const stFilter = filterStatutEl.value;
    if (stFilter === "__ACTIFS__") {
      list = list.filter((r) => !isClosStatut(r.Statut));
    } else if (stFilter) {
      list = list.filter((r) => r.Statut === stFilter);
    }

    const prioFilter = filterPrioriteEl.value;
    if (prioFilter) {
      list = list.filter((r) => (r.Priorite || "Normale") === prioFilter);
    }

    const domFilter = filterDomaineEl.value;
    if (domFilter) {
      list = list.filter((r) => r.Domaine_Activite === domFilter);
    }

    const agFilter = filterAgentEl.value;
    if (agFilter === "__NON_ATTRIBUE__") {
      list = list.filter((r) => !r.Agent_Attributaire || Number(r.Agent_Attributaire) === 0);
    } else if (agFilter) {
      const targetId = Number(agFilter);
      list = list.filter((r) => Number(r.Agent_Attributaire) === targetId);
    }

    const q = searchInputEl.value.trim().toLowerCase();
    if (q) {
      list = list.filter((r) => {
        const blob = [
          r.Numero_Signalement,
          r.Commune,
          r.Lieu_Dit,
          r.Domaine_Activite,
          r.Requerant_Nom,
          r.Requerant_Contact,
          r.Description_Faits,
          r.Consignes_Hierarchie,
          agentNomFromVal(r.Agent_Recepteur, ""),
          agentNomFromVal(r.Agent_Attributaire, ""),
          r.Statut,
        ].join(" ").toLowerCase();
        return blob.includes(q);
      });
    }

    list.sort(compareSignalements);
    return list;
  }

  function updateSortHeadersUi() {
    const labels = {
      Numero_Signalement: "N°",
      Date_Heure_Reception: "Réception",
      Commune: "Commune",
      Agent_Attributaire: "Attributaire",
      Priorite: "Priorité",
      Statut: "Statut",
    };
    masterTableEl.querySelectorAll("th[data-sort-col]").forEach((th) => {
      const col = th.getAttribute("data-sort-col");
      const base = labels[col] || col;
      if (col === sortCol) {
        th.textContent = base + (sortDir === "asc" ? " ▲" : " ▼");
      } else {
        th.textContent = base;
      }
    });
  }

  function renderDetail(dossier) {
    if (!dossier) {
      detailPaneEl.innerHTML = '<div class="pil-empty">Aucun signalement ne correspond aux filtres actifs.</div>';
      return;
    }

    const num = dossier.Numero_Signalement || ("#" + dossier.id);
    const statut = dossier.Statut || "Nouveau";
    const prio = dossier.Priorite || "Normale";
    const commune = dossier.Commune || "Non renseignée";
    const lieuDit = dossier.Lieu_Dit || "";
    const domaine = dossier.Domaine_Activite || "Non spécifié";
    const reqNom = dossier.Requerant_Nom || "Anonyme / Non communiqué";
    const agRec = agentNomFromVal(dossier.Agent_Recepteur, "Non renseigné");
    const agAttId = typeof dossier.Agent_Attributaire === "number" ? dossier.Agent_Attributaire : 0;
    const agAtt = agentNomFromVal(dossier.Agent_Attributaire, "Non attribué");
    const dateRec = formatDateFr(dossier.Date_Heure_Reception, true);
    const dateAtt = dossier.Date_Attribution ? formatDateFr(dossier.Date_Attribution, false) : "Non datée";
    const dateAttInput = tsToDateInputValue(dossier.Date_Attribution);
    const consignes = String(dossier.Consignes_Hierarchie || "").trim();
    const statutManuel = String(dossier.Statut_Manuel || "").trim();
    const encadrantAlerte = String(dossier.Encadrant_A_Alerter || "").trim();

    const locQuery = (commune + " " + lieuDit).trim();
    const locUrl = locQuery && locQuery !== "Non renseignée"
      ? "https://www.openstreetmap.org/search?query=" + encodeURIComponent(locQuery)
      : "";

    const mailtoNotifier = (dossier.Action_Notifier && String(dossier.Action_Notifier).startsWith("mailto:"))
      ? dossier.Action_Notifier
      : buildNotifierMailto(dossier);

    const notifyBtnHtml = mailtoNotifier
      ? '<a class="sig-btn sig-btn-primary no-print" href="' + escapeHtml(mailtoNotifier) + '">✉️ Envoyer fiche (courriel)</a>'
      : '<button type="button" class="sig-btn no-print" disabled title="Attribuez d\'abord un agent pour envoyer la fiche.">✉️ Envoyer fiche (courriel)</button>';

    const agentSelectOpts = ['<option value="0">-- Non attribué --</option>']
      .concat(sessionCtx.agents.map((ag) => {
        const sel = ag.id === agAttId ? " selected" : "";
        return '<option value="' + ag.id + '"' + sel + ">" + escapeHtml(ag.Nom) + "</option>";
      }))
      .join("");

    const prioSelectOpts = CFG.choixPriorite.map((p) => {
      const sel = p === prio ? " selected" : "";
      return '<option value="' + escapeHtml(p) + '"' + sel + ">" + escapeHtml(p) + "</option>";
    }).join("");

    const statutManuelOpts = ['<option value="">-- Automatique selon workflow --</option>']
      .concat(CFG.choixStatut.map((s) => {
        const sel = s === statutManuel ? " selected" : "";
        return '<option value="' + escapeHtml(s) + '"' + sel + ">" + escapeHtml(s) + "</option>";
      }))
      .join("");

    const sigPjIds = decodeAttachmentIds(dossier.Pieces_Jointes);
    const retours = (retoursBySig[dossier.id] || []).slice().sort((a, b) => {
      return (Number(a.Date_Intervention) || a.id) - (Number(b.Date_Intervention) || b.id);
    });
    const allPjIds = sigPjIds.slice();

    let retoursHtml = "";
    if (retours.length === 0) {
      retoursHtml = '<div class="sig-card"><h2 style="margin-bottom:6px;">🏁 Retours d\'intervention (0)</h2><p style="margin:0;color:#64748b;">Aucun retour enregistré pour le moment.</p></div>';
    } else {
      const itemsHtml = retours.map((ret) => {
        const rPjIds = decodeAttachmentIds(ret.Pieces_Jointes);
        rPjIds.forEach((id) => allPjIds.push(id));
        const rAgent = agentNomFromVal(ret.Agent_Intervenant, "Agent");
        const suiteBadge = ret.Suite_Donnee
          ? '<span class="sig-badge badge-traite">' + escapeHtml(ret.Suite_Donnee) + "</span>"
          : '<span class="sig-badge badge-encours">En cours</span>';
        return (
          '<div class="sig-retour-item print-avoid-break">' +
            '<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:6px;">' +
              "<strong>" + escapeHtml(formatDateFr(ret.Date_Intervention, false)) + " — " + escapeHtml(ret.Type_Demarche || "Démarche") + "</strong>" +
              suiteBadge +
            "</div>" +
            '<div style="font-size:12px;color:#64748b;margin-bottom:6px;">Intervenant : ' + escapeHtml(rAgent) + "</div>" +
            '<div style="white-space:pre-wrap;font-size:12.5px;color:#1e293b;margin-bottom:8px;">' + escapeHtml(ret.Compte_Rendu || "Aucun compte-rendu.") + "</div>" +
            renderAttachmentChips(rPjIds, "pilPjRetour_" + ret.id) +
          "</div>"
        );
      }).join("");
      retoursHtml = '<div class="sig-card"><h2>🏁 Historique des retours d\'intervention (' + retours.length + ")</h2>" + itemsHtml + "</div>";
    }

    detailPaneEl.innerHTML =
      '<div class="sig-card">' +
        '<div class="pil-fiche-head">' +
          "<div>" +
            '<div style="font-size:11px;font-weight:700;text-transform:uppercase;color:#64748b;">Fiche de synthèse signalement</div>' +
            '<h2 class="pil-fiche-num">' + escapeHtml(num) + "</h2>" +
          "</div>" +
          '<div style="display:flex;flex-wrap:wrap;align-items:center;gap:6px;">' +
            '<span class="sig-badge ' + prioriteBadgeClass(prio) + '">' + escapeHtml(prio) + "</span>" +
            '<span class="sig-badge ' + statutBadgeClass(statut) + '">' + escapeHtml(statut) + "</span>" +
            (statutManuel ? '<span class="sig-badge badge-classe">Statut imposé</span>' : "") +
            '<button type="button" class="sig-btn no-print" id="btnPrintPilotage">🖨️ Imprimer</button>' +
            notifyBtnHtml +
            (sessionCtx.isManager ? '<button type="button" class="sig-btn sig-btn-danger no-print" id="btnDeletePilotage">🗑️ Supprimer</button>' : "") +
          "</div>" +
        "</div>" +
        '<div class="sig-grid-2">' +
          '<div class="sig-card print-avoid-break" style="margin-bottom:0;">' +
            "<h2>👤 Origine de la saisine</h2>" +
            '<div style="font-weight:700;margin-bottom:4px;">' + escapeHtml(reqNom) + "</div>" +
            '<div style="font-size:12px;color:#475569;margin-bottom:4px;"><strong>Contact :</strong> ' + renderContactHtml(dossier.Requerant_Contact) + "</div>" +
            '<div style="font-size:12px;color:#64748b;">Reçu le ' + escapeHtml(dateRec) + " via <em>" + escapeHtml(dossier.Canal_Reception || "Non précisé") + "</em> (par " + escapeHtml(agRec) + ")</div>" +
            (encadrantAlerte ? '<div style="font-size:11.5px;color:#64748b;margin-top:4px;">Encadrant alerté : ' + escapeHtml(encadrantAlerte) + "</div>" : "") +
          "</div>" +
          '<div class="sig-card print-avoid-break" style="margin-bottom:0;">' +
            "<h2>🎯 Prise en charge hiérarchique</h2>" +
            '<div style="font-weight:700;margin-bottom:4px;">Attribué à : <span style="color:#005bb5;">' + escapeHtml(agAtt) + "</span></div>" +
            '<div style="font-size:12px;color:#64748b;margin-bottom:4px;">Date d\'attribution : ' + escapeHtml(dateAtt) + " · Priorité : " + escapeHtml(prio) + "</div>" +
            (consignes ? '<div style="background:#fffbeb;border-left:3px solid #f59e0b;padding:7px 10px;border-radius:4px;font-size:12px;color:#78350f;margin-top:6px;"><strong>Consignes :</strong> ' + escapeHtml(consignes) + "</div>" : '<div style="font-size:12px;color:#64748b;">Aucune consigne renseignée.</div>') +
          "</div>" +
        "</div>" +
      "</div>" +

      '<div class="sig-card pil-action-panel no-print">' +
        "<h2>🛠️ Attribution et consignes hiérarchiques</h2>" +
        '<form id="pilEditForm" novalidate>' +
          '<div class="sig-grid-2">' +
            '<div class="sig-field">' +
              '<label for="pilInputAgent">Agent attributaire</label>' +
              '<select id="pilInputAgent">' + agentSelectOpts + "</select>" +
            "</div>" +
            '<div class="sig-field">' +
              '<label for="pilInputPriorite">Priorité</label>' +
              '<select id="pilInputPriorite">' + prioSelectOpts + "</select>" +
            "</div>" +
            '<div class="sig-field">' +
              '<label for="pilInputDateAttr">Date d\'attribution (auto si vide à l\'attribution)</label>' +
              '<input type="date" id="pilInputDateAttr" value="' + escapeHtml(dateAttInput) + '">' +
            "</div>" +
            '<div class="sig-field">' +
              '<label for="pilInputStatutManuel">Statut imposé (hiérarchie)</label>' +
              '<select id="pilInputStatutManuel">' + statutManuelOpts + "</select>" +
            "</div>" +
          "</div>" +
          '<div class="sig-field">' +
            '<label for="pilInputConsignes">Consignes pour l\'agent</label>' +
            '<textarea id="pilInputConsignes" rows="3" placeholder="Orientations de contrôle, points de vigilance, urgence...">' + escapeHtml(consignes) + "</textarea>" +
          "</div>" +
          '<div style="display:flex;justify-content:flex-end;gap:8px;">' +
            '<button type="submit" class="sig-btn sig-btn-primary" id="btnPilSaveDossier">Enregistrer les modifications</button>' +
          "</div>" +
        "</form>" +
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
        renderAttachmentChips(sigPjIds, "pilPjSig_" + dossier.id) +
      "</div>" +

      retoursHtml;

    const btnPrintEl = document.getElementById("btnPrintPilotage");
    if (btnPrintEl) {
      btnPrintEl.addEventListener("click", () => window.print());
    }

    const btnDeleteEl = document.getElementById("btnDeletePilotage");
    if (btnDeleteEl) {
      btnDeleteEl.addEventListener("click", () => openDeleteModal(dossier));
    }

    const editFormEl = document.getElementById("pilEditForm");
    if (editFormEl) {
      editFormEl.addEventListener("submit", async (ev) => {
        ev.preventDefault();
        const btnSave = document.getElementById("btnPilSaveDossier");
        const agentVal = Number(document.getElementById("pilInputAgent").value) || 0;
        const prioVal = document.getElementById("pilInputPriorite").value || "Normale";
        const dateRaw = document.getElementById("pilInputDateAttr").value;
        const statutManVal = document.getElementById("pilInputStatutManuel").value;
        const consignesVal = document.getElementById("pilInputConsignes").value.trim();

        let dateTs = null;
        if (dateRaw) {
          dateTs = parseDateToTs(dateRaw);
        } else if (agentVal > 0) {
          dateTs = parseDateToTs(todayLocalIso());
        }

        const payload = {
          Agent_Attributaire: agentVal,
          Priorite: prioVal,
          Date_Attribution: dateTs,
          Statut_Manuel: statutManVal,
          Consignes_Hierarchie: consignesVal,
        };

        btnSave.disabled = true;
        btnSave.textContent = "Enregistrement...";
        showBanner(bannerEl, null);
        try {
          await grist.docApi.applyUserActions([["UpdateRecord", "Signalements", dossier.id, payload]]);
          selectedId = dossier.id;
          await loadData();
          showBanner(bannerEl, "Dossier " + num + " mis à jour.", "ok");
        } catch (err) {
          showBanner(bannerEl, formatGristError(err), "err");
        } finally {
          btnSave.disabled = false;
          btnSave.textContent = "Enregistrer les modifications";
        }
      });
    }

    if (allPjIds.length > 0) {
      hydrateAttachmentChips(allPjIds);
    }
  }

  function renderView() {
    updateKpis();
    updateSortHeadersUi();
    kpiBarEl.querySelectorAll(".pil-kpi-pill").forEach((pill) => {
      pill.classList.toggle("active", pill.getAttribute("data-kpi") === activeKpi);
    });

    const filtered = getFilteredAndSorted();
    matchCountEl.textContent = filtered.length + " / " + allSignalements.length + " dossiers";

    if (!filtered.length) {
      selectedId = null;
      masterBodyEl.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#64748b;padding:24px;">Aucun dossier ne correspond aux filtres sélectionnés.</td></tr>';
      renderDetail(null);
      return;
    }

    if (!filtered.some((r) => r.id === selectedId)) {
      selectedId = filtered[0].id;
    }

    masterBodyEl.innerHTML = filtered.map((r) => {
      const selCls = r.id === selectedId ? " selected" : "";
      const statut = r.Statut || "Nouveau";
      const prio = r.Priorite || "Normale";
      const agAtt = agentNomFromVal(r.Agent_Attributaire, "Non attribué");
      return (
        '<tr class="pil-master-row' + selCls + '" data-sig-id="' + r.id + '">' +
          '<td class="pil-num">' + escapeHtml(r.Numero_Signalement || ("#" + r.id)) + "</td>" +
          "<td>" + escapeHtml(formatDateFr(r.Date_Heure_Reception, false)) + "</td>" +
          "<td>" + escapeHtml(r.Commune || "—") + "</td>" +
          "<td>" + escapeHtml(agAtt) + "</td>" +
          '<td><span class="sig-badge ' + prioriteBadgeClass(prio) + '">' + escapeHtml(prio) + "</span></td>" +
          '<td><span class="sig-badge ' + statutBadgeClass(statut) + '">' + escapeHtml(statut) + "</span></td>" +
        "</tr>"
      );
    }).join("");

    const selected = filtered.find((r) => r.id === selectedId) || filtered[0];
    renderDetail(selected);
  }

  function exportFilteredCsv() {
    const filtered = getFilteredAndSorted();
    const headers = [
      "N° Signalement",
      "Date réception",
      "Statut",
      "Statut imposé",
      "Priorité",
      "Domaine",
      "Commune",
      "Lieu-dit",
      "Canal",
      "Agent récepteur",
      "Requérant",
      "Contact requérant",
      "Agent attributaire",
      "Date attribution",
      "Consignes hiérarchie",
      "Nb retours",
      "Dernière date intervention",
      "Dernière démarche",
      "Dernière suite donnée",
      "Dernier compte-rendu",
      "Description des faits",
    ];
    const rows = filtered.map((r) => {
      const rets = (retoursBySig[r.id] || []).slice().sort((a, b) => {
        return (Number(a.Date_Intervention) || a.id) - (Number(b.Date_Intervention) || b.id);
      });
      const last = rets.length ? rets[rets.length - 1] : null;
      return [
        r.Numero_Signalement || ("#" + r.id),
        formatDateFr(r.Date_Heure_Reception, true),
        r.Statut || "Nouveau",
        r.Statut_Manuel || "",
        r.Priorite || "Normale",
        r.Domaine_Activite || "",
        r.Commune || "",
        r.Lieu_Dit || "",
        r.Canal_Reception || "",
        agentNomFromVal(r.Agent_Recepteur, ""),
        r.Requerant_Nom || "",
        r.Requerant_Contact || "",
        agentNomFromVal(r.Agent_Attributaire, "Non attribué"),
        r.Date_Attribution ? formatDateFr(r.Date_Attribution, false) : "",
        r.Consignes_Hierarchie || "",
        String(rets.length),
        last && last.Date_Intervention ? formatDateFr(last.Date_Intervention, false) : "",
        last ? (last.Type_Demarche || "") : "",
        last ? (last.Suite_Donnee || "") : "",
        last ? (last.Compte_Rendu || "") : "",
        r.Description_Faits || "",
      ];
    });
    const csvContent = buildCsvUtf8Bom(headers, rows);
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "signalements_" + (CFG.csvPrefix || "service") + "_" + todayLocalIso() + ".csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  }

  async function loadData() {
    try {
      sessionCtx = await loadSessionContext();
      if (sessionCtx.connectedAgent) {
        sessionBadgeEl.textContent = "Connecté : " + sessionCtx.connectedAgent.Nom;
      } else {
        sessionBadgeEl.textContent = "Session active";
      }

      if (!sessionCtx.isManager) {
        mainAppEl.classList.add("hidden");
        btnExportCsvEl.classList.add("hidden");
        restrictedEl.classList.remove("hidden");
        return;
      }

      restrictedEl.classList.add("hidden");
      mainAppEl.classList.remove("hidden");
      btnExportCsvEl.classList.remove("hidden");
      populateAgentFilter();

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

  kpiBarEl.addEventListener("click", (ev) => {
    const pill = ev.target.closest("button[data-kpi]");
    if (!pill) return;
    const chosen = pill.getAttribute("data-kpi") || "tous";
    activeKpi = (activeKpi === chosen && chosen !== "tous") ? "tous" : chosen;
    renderView();
  });

  [filterStatutEl, filterPrioriteEl, filterDomaineEl, filterAgentEl].forEach((sel) => {
    sel.addEventListener("change", renderView);
  });
  searchInputEl.addEventListener("input", renderView);

  btnResetFiltersEl.addEventListener("click", () => {
    activeKpi = "tous";
    filterStatutEl.value = "";
    filterPrioriteEl.value = "";
    filterDomaineEl.value = "";
    filterAgentEl.value = "";
    searchInputEl.value = "";
    renderView();
  });

  masterTableEl.querySelector("thead").addEventListener("click", (ev) => {
    const th = ev.target.closest("th[data-sort-col]");
    if (!th) return;
    const col = th.getAttribute("data-sort-col");
    if (sortCol === col) {
      sortDir = sortDir === "asc" ? "desc" : "asc";
    } else {
      sortCol = col;
      sortDir = (col === "Date_Heure_Reception" || col === "Numero_Signalement") ? "desc" : "asc";
    }
    renderView();
  });

  masterBodyEl.addEventListener("click", (ev) => {
    const tr = ev.target.closest("tr[data-sig-id]");
    if (!tr) return;
    selectedId = Number(tr.getAttribute("data-sig-id"));
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
        "Téléchargement direct bloqué pour ce rôle (HTTP 403 Grist). Consultez la pièce jointe via les données brutes si nécessaire.",
        "warn"
      );
    } finally {
      dlBtn.disabled = false;
    }
  });

  function openDeleteModal(dossier) {
    if (!dossier || !sessionCtx.isManager) return;
    deletingDossier = dossier;
    const num = dossier.Numero_Signalement || ("#" + dossier.id);
    const commune = dossier.Commune || "Commune non précisée";
    const domaine = dossier.Domaine_Activite || "Domaine non précisé";
    const extraitRaw = String(dossier.Description_Faits || "").trim();
    const extrait = extraitRaw.length > 140 ? (extraitRaw.slice(0, 140) + "...") : (extraitRaw || "Aucune description.");
    const linked = retoursBySig[dossier.id] || [];
    const impactHtml = linked.length > 0
      ? '<div style="margin-top:8px;padding:8px 10px;border-radius:6px;background:#fef2f2;border:1px solid #fecaca;color:#991b1b;font-weight:600;">Impact : ' + linked.length + ' retour(s) d\'intervention lié(s) dans Retours_Actions seront également supprimé(s) définitivement.</div>'
      : '<div style="margin-top:8px;color:#64748b;font-size:12px;">Aucun retour d\'intervention lié dans Retours_Actions.</div>';

    deleteSummaryEl.innerHTML =
      '<p style="margin:0 0 8px;">Voulez-vous supprimer définitivement le signalement <strong>' + escapeHtml(num) + "</strong> ?</p>" +
      '<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:8px 10px;font-size:12.5px;">' +
        "<div><strong>Objet :</strong> " + escapeHtml(commune) + " — " + escapeHtml(domaine) + "</div>" +
        '<div style="margin-top:4px;color:#475569;">' + escapeHtml(extrait) + "</div>" +
      "</div>" +
      impactHtml;
    showBanner(deleteErrEl, null);
    deleteBackdropEl.classList.add("open");
    btnCancelDeleteEl.focus();
  }

  function closeDeleteModal() {
    deleteBackdropEl.classList.remove("open");
    deletingDossier = null;
  }

  btnCancelDeleteEl.addEventListener("click", closeDeleteModal);
  btnConfirmDeleteEl.addEventListener("click", async () => {
    if (!deletingDossier || !sessionCtx.isManager) return;
    const targetId = deletingDossier.id;
    const targetNum = deletingDossier.Numero_Signalement || ("#" + targetId);
    const linkedIds = (retoursBySig[targetId] || [])
      .map((r) => Number(r.id))
      .filter((id) => Number.isInteger(id) && id > 0);
    const actions = [];
    if (linkedIds.length > 0) {
      actions.push(["BulkRemoveRecord", "Retours_Actions", linkedIds]);
    }
    actions.push(["RemoveRecord", "Signalements", targetId]);

    btnConfirmDeleteEl.disabled = true;
    btnConfirmDeleteEl.textContent = "Suppression...";
    showBanner(deleteErrEl, null);
    try {
      await grist.docApi.applyUserActions(actions);
      closeDeleteModal();
      selectedId = null;
      await loadData();
      const suffix = linkedIds.length > 0
        ? (" (avec " + linkedIds.length + " retour(s) lié(s) supprimé(s))")
        : "";
      showBanner(bannerEl, "Signalement " + targetNum + " supprimé définitivement" + suffix + ".", "ok");
    } catch (err) {
      showBanner(deleteErrEl, formatGristError(err), "err");
    } finally {
      btnConfirmDeleteEl.disabled = false;
      btnConfirmDeleteEl.textContent = "Supprimer définitivement";
    }
  });

  btnRefreshEl.addEventListener("click", loadData);
  btnExportCsvEl.addEventListener("click", exportFilteredCsv);

  if (typeof grist.onRecords === "function") {
    grist.onRecords(() => scheduleReload());
  }

  loadData();
})();
"""

    return {
        "_html": envelopper_document_html("Pilotage et attribution", body_html, extra_css=PILOTAGE_CSS),
        "_js": f"const CFG = {cfg_json};\n{COMMON_JS_HELPERS}\n{js_body}".strip(),
    }


__all__ = ["generer_widget_pilotage"]
