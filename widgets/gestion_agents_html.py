# -*- coding: utf-8 -*-
"""Générateur du widget HTML « 👥 Gestion des agents » (Lot 4)."""

import html
import json

from config import CSV_PREFIX, EMAIL_PLACEHOLDER, SERVICE_NOM
from widgets.commun import COMMON_JS_HELPERS, envelopper_document_html

GESTION_AGENTS_CSS = """
.ga-notice {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e3a8a;
  border-radius: 8px;
  padding: 9px 12px;
  margin-bottom: 10px;
  font-size: 12.5px;
}
.ga-restricted {
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
  border-radius: 10px;
  padding: 24px 18px;
  text-align: center;
  font-weight: 600;
}
.ga-row-self td {
  background: #f0f9ff;
}
#gaTableBody td {
  overflow-wrap: anywhere;
}
"""


def generer_widget_gestion_agents():
    """Retourne {_html, _js} pour le widget d'administration de Referentiel_Agents."""
    service_echappe = html.escape(SERVICE_NOM)
    email_placeholder_echappe = html.escape(EMAIL_PLACEHOLDER)
    body_html = f"""  <div class="sig-wrap">
    <div class="sig-header no-print">
      <div class="sig-title-row">
        <div>
          <h1 class="sig-title">👥 Gestion des agents</h1>
          <p class="sig-subtitle">Annuaire du {service_echappe} (table Referentiel_Agents) utilisé pour la réception, l'attribution et les droits d'accès.</p>
        </div>
        <span class="sig-badge badge-info" id="gaCountBadge">0 agents</span>
      </div>
      <div style="display:flex;flex-wrap:wrap;align-items:center;gap:8px;">
        <span class="sig-badge badge-info" id="gaSessionBadge">Vérification...</span>
        <button type="button" class="sig-btn" id="btnGaRefresh">🔄 Actualiser</button>
        <button type="button" class="sig-btn hidden" id="btnGaExportCsv">📥 Exporter annuaire CSV</button>
        <button type="button" class="sig-btn sig-btn-primary hidden" id="btnGaAdd">➕ Ajouter un agent</button>
      </div>
    </div>

    <div id="gaRestricted" class="ga-restricted hidden no-print">
      Accès réservé à l'encadrement.
    </div>

    <div id="gaBanner" class="sig-banner no-print" role="status"></div>

    <div id="gaMainApp" class="hidden">
      <div class="ga-notice no-print">
        <strong>Rôles et partage ProConnect :</strong> le service distingue deux rôles métier configurables ici : <strong>Gestionnaire</strong> (accès encadrement, attribution et suppression de signalements) et <strong>Agent</strong> (saisie et suivi de ses dossiers). Seuls les propriétaires peuvent modifier la structure du classeur. Pour qu'un agent puisse se connecter via ProConnect, invitez son courriel avec le rôle <strong>Éditeur</strong> dans le menu <em>Partager</em> de Grist.
      </div>

      <div class="sig-toolbar no-print">
        <input type="search" class="sig-input" id="gaSearchInput" style="flex:1 1 260px;" placeholder="Rechercher par nom, courriel ou trigramme...">
        <select class="sig-select" id="gaRoleFilter" style="flex:0 1 190px;" aria-label="Filtrer par rôle">
          <option value="">Tous les rôles</option>
          <option value="Gestionnaire">Gestionnaire</option>
          <option value="Agent">Agent</option>
        </select>
        <span id="gaVisibleCount" style="font-size:12px;font-weight:700;color:#475569;">0 affiché(s)</span>
      </div>

      <div class="sig-table-wrap">
        <table class="sig-table">
          <thead>
            <tr>
              <th>Nom de l'agent</th>
              <th>Trigramme</th>
              <th>Rôle</th>
              <th>Courriel professionnel</th>
              <th>Statut session</th>
              <th>Activité registre</th>
              <th class="no-print">Actions</th>
            </tr>
          </thead>
          <tbody id="gaTableBody">
            <tr><td colspan="7" style="text-align:center;color:#64748b;padding:20px;">Chargement de l'annuaire...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div id="gaModalBackdrop" class="sig-modal-backdrop no-print" role="dialog" aria-modal="true" aria-labelledby="gaModalTitle">
    <div class="sig-modal">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <h2 id="gaModalTitle" style="margin:0;font-size:16px;">Ajouter un agent</h2>
        <button type="button" class="sig-btn" id="btnGaCloseModal">Fermer</button>
      </div>
      <div id="gaModalErr" class="sig-banner" role="alert"></div>
      <form id="gaModalForm" novalidate>
        <div class="sig-field">
          <label for="gaInputNom">Nom et prénom *</label>
          <input type="text" id="gaInputNom" required placeholder="Prénom NOM">
        </div>
        <div class="sig-grid-2">
          <div class="sig-field">
            <label for="gaInputEmail">Courriel professionnel *</label>
            <input type="email" id="gaInputEmail" required placeholder="{email_placeholder_echappe}">
          </div>
          <div class="sig-field">
            <label for="gaInputTrigramme">Trigramme</label>
            <input type="text" id="gaInputTrigramme" maxlength="10" placeholder="Auto si vide">
          </div>
        </div>
        <div class="sig-field">
          <label for="gaInputRole">Rôle dans le registre *</label>
          <select id="gaInputRole" required>
            <option value="Agent">Agent</option>
            <option value="Gestionnaire">Gestionnaire</option>
          </select>
          <div style="font-size:11.5px;color:#64748b;margin-top:4px;">Les règles d'accès Grist s'appliquent dynamiquement selon ce rôle (la structure du classeur reste réservée aux propriétaires).</div>
        </div>
        <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:12px;">
          <button type="button" class="sig-btn" id="btnGaCancelModal">Annuler</button>
          <button type="submit" class="sig-btn sig-btn-primary" id="btnGaSaveModal">Enregistrer</button>
        </div>
      </form>
    </div>
  </div>

  <div id="gaDeleteBackdrop" class="sig-modal-backdrop no-print" role="dialog" aria-modal="true" aria-labelledby="gaDeleteTitle">
    <div class="sig-modal" style="max-width:460px;">
      <h2 id="gaDeleteTitle" style="margin:0 0 8px;font-size:16px;color:#991b1b;">Confirmer la suppression</h2>
      <p id="gaDeleteMessage" style="margin:0 0 12px;color:#334155;"></p>
      <div id="gaDeleteErr" class="sig-banner" role="alert"></div>
      <div style="display:flex;justify-content:flex-end;gap:8px;">
        <button type="button" class="sig-btn" id="btnGaCancelDelete">Annuler</button>
        <button type="button" class="sig-btn sig-btn-danger" id="btnGaConfirmDelete">Supprimer définitivement</button>
      </div>
    </div>
  </div>"""

    cfg_json = json.dumps(
        {
            "docTitle": "Gestion des agents",
            "rolesDisponibles": ["Agent", "Gestionnaire"],
            "csvPrefix": CSV_PREFIX,
        },
        ensure_ascii=False,
    )

    js_body = r"""
(function () {
  grist.ready({ requiredAccess: "full" });

  const countBadgeEl = document.getElementById("gaCountBadge");
  const sessionBadgeEl = document.getElementById("gaSessionBadge");
  const btnRefreshEl = document.getElementById("btnGaRefresh");
  const btnExportCsvEl = document.getElementById("btnGaExportCsv");
  const btnAddEl = document.getElementById("btnGaAdd");
  const restrictedEl = document.getElementById("gaRestricted");
  const bannerEl = document.getElementById("gaBanner");
  const mainAppEl = document.getElementById("gaMainApp");
  const searchInputEl = document.getElementById("gaSearchInput");
  const roleFilterEl = document.getElementById("gaRoleFilter");
  const visibleCountEl = document.getElementById("gaVisibleCount");
  const tableBodyEl = document.getElementById("gaTableBody");

  const modalBackdropEl = document.getElementById("gaModalBackdrop");
  const modalTitleEl = document.getElementById("gaModalTitle");
  const modalErrEl = document.getElementById("gaModalErr");
  const modalFormEl = document.getElementById("gaModalForm");
  const inputNomEl = document.getElementById("gaInputNom");
  const inputEmailEl = document.getElementById("gaInputEmail");
  const inputTrigrammeEl = document.getElementById("gaInputTrigramme");
  const inputRoleEl = document.getElementById("gaInputRole");
  const btnCloseModalEl = document.getElementById("btnGaCloseModal");
  const btnCancelModalEl = document.getElementById("btnGaCancelModal");
  const btnSaveModalEl = document.getElementById("btnGaSaveModal");

  const deleteBackdropEl = document.getElementById("gaDeleteBackdrop");
  const deleteMessageEl = document.getElementById("gaDeleteMessage");
  const deleteErrEl = document.getElementById("gaDeleteErr");
  const btnCancelDeleteEl = document.getElementById("btnGaCancelDelete");
  const btnConfirmDeleteEl = document.getElementById("btnGaConfirmDelete");

  let sessionCtx = { agents: [], agentsById: {}, agentsByNom: {}, connectedAgent: null, isManager: false };
  let agentRefsMap = {};
  let editingAgentId = null;
  let deletingAgent = null;
  let reloadTimer = null;

  function suggestTrigramme(nom) {
    const parts = String(nom || "").trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return "";
    if (parts.length === 1) return parts[0].slice(0, 3).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1].slice(0, 2)).toUpperCase();
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function getUsageForAgent(agId) {
    return agentRefsMap[agId] || { attr: 0, rec: 0, ret: 0, total: 0 };
  }

  function getAgentRole(ag) {
    return (ag && ag.Role === "Gestionnaire") ? "Gestionnaire" : "Agent";
  }

  function getFilteredAgents() {
    const q = searchInputEl.value.trim().toLowerCase();
    const roleFilter = roleFilterEl ? roleFilterEl.value : "";
    return sessionCtx.agents.filter((ag) => {
      const role = getAgentRole(ag);
      if (roleFilter && role !== roleFilter) return false;
      if (!q) return true;
      const blob = [ag.Nom, ag.Email, ag.Trigramme, role].join(" ").toLowerCase();
      return blob.includes(q);
    });
  }

  function renderTable() {
    const filtered = getFilteredAgents();
    countBadgeEl.textContent = sessionCtx.agents.length + " agents";
    visibleCountEl.textContent = filtered.length + " / " + sessionCtx.agents.length + " affiché(s)";

    if (!filtered.length) {
      tableBodyEl.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#64748b;padding:20px;">Aucun agent ne correspond à la recherche.</td></tr>';
      return;
    }

    const connectedId = sessionCtx.connectedAgent ? sessionCtx.connectedAgent.id : null;
    tableBodyEl.innerHTML = filtered.map((ag) => {
      const isSelf = ag.Est_Connecte === true || ag.id === connectedId;
      const role = getAgentRole(ag);
      const roleBadge = role === "Gestionnaire"
        ? '<span class="sig-badge badge-attribue">Gestionnaire</span>'
        : '<span class="sig-badge badge-classe">Agent</span>';
      const usage = getUsageForAgent(ag.id);
      const canDelete = usage.total === 0 && !isSelf;
      const deleteTitle = isSelf
        ? "Impossible de supprimer votre propre fiche agent."
        : (usage.total > 0
          ? "Suppression bloquée : cet agent est référencé sur " + usage.total + " dossier(s) ou retour(s)."
          : "Supprimer cet agent sans historique");

      return (
        '<tr class="' + (isSelf ? "ga-row-self" : "") + '">' +
          "<td><strong>" + escapeHtml(ag.Nom || "") + "</strong></td>" +
          "<td>" + (ag.Trigramme ? '<span class="sig-badge badge-classe">' + escapeHtml(ag.Trigramme) + "</span>" : "—") + "</td>" +
          "<td>" + roleBadge + "</td>" +
          "<td>" + escapeHtml(ag.Email || "") + "</td>" +
          "<td>" + (isSelf ? '<span class="sig-badge badge-info">Vous</span>' : '<span style="color:#64748b;">Référencé</span>') + "</td>" +
          '<td style="font-size:12px;color:#475569;">' + usage.attr + " attr. · " + usage.rec + " réc. · " + usage.ret + " ret.</td>" +
          '<td class="no-print">' +
            '<div style="display:flex;gap:6px;">' +
              '<button type="button" class="sig-btn" data-edit-agent="' + ag.id + '">Modifier</button>' +
              '<button type="button" class="sig-btn sig-btn-danger" data-del-agent="' + ag.id + '"' +
                (canDelete ? "" : " disabled") + ' title="' + escapeHtml(deleteTitle) + '">Supprimer</button>' +
            "</div>" +
          "</td>" +
        "</tr>"
      );
    }).join("");
  }

  function openEditModal(agent) {
    editingAgentId = agent ? agent.id : null;
    modalTitleEl.textContent = agent ? ("Modifier l'agent : " + (agent.Nom || "")) : "Ajouter un agent";
    inputNomEl.value = agent ? (agent.Nom || "") : "";
    inputEmailEl.value = agent ? (agent.Email || "") : "";
    inputTrigrammeEl.value = agent ? (agent.Trigramme || "") : "";
    inputRoleEl.value = agent ? getAgentRole(agent) : "Agent";
    showBanner(modalErrEl, null);
    modalBackdropEl.classList.add("open");
    inputNomEl.focus();
  }

  function closeEditModal() {
    modalBackdropEl.classList.remove("open");
    editingAgentId = null;
  }

  function openDeleteModal(agent) {
    const usage = getUsageForAgent(agent.id);
    const connectedId = sessionCtx.connectedAgent ? sessionCtx.connectedAgent.id : null;
    if (usage.total > 0 || agent.id === connectedId) {
      showBanner(bannerEl, "Suppression refusée : fiche liée à votre session ou à un historique du registre.", "warn");
      return;
    }
    deletingAgent = agent;
    deleteMessageEl.textContent = "Confirmez-vous la suppression de « " + (agent.Nom || "") + " » (" + (agent.Email || "") + ") de Referentiel_Agents ?";
    showBanner(deleteErrEl, null);
    deleteBackdropEl.classList.add("open");
  }

  function closeDeleteModal() {
    deleteBackdropEl.classList.remove("open");
    deletingAgent = null;
  }

  function exportAgentsCsv() {
    const filtered = getFilteredAgents();
    const headers = [
      "Nom",
      "Trigramme",
      "Rôle",
      "Courriel",
      "Attributions",
      "Réceptions",
      "Retours",
    ];
    const rows = filtered.map((ag) => {
      const u = getUsageForAgent(ag.id);
      return [
        ag.Nom || "",
        ag.Trigramme || "",
        getAgentRole(ag),
        ag.Email || "",
        String(u.attr),
        String(u.rec),
        String(u.ret),
      ];
    });
    const csv = buildCsvUtf8Bom(headers, rows);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const today = toDatetimeLocalValue(new Date()).slice(0, 10);
    link.href = url;
    link.download = "agents_" + (CFG.csvPrefix || "service") + "_" + today + ".csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  }

  async function loadData() {
    try {
      sessionCtx = await loadSessionContext();
      sessionBadgeEl.textContent = sessionCtx.connectedAgent
        ? ("Connecté : " + sessionCtx.connectedAgent.Nom)
        : "Session active";

      if (!sessionCtx.isManager) {
        mainAppEl.classList.add("hidden");
        btnAddEl.classList.add("hidden");
        btnExportCsvEl.classList.add("hidden");
        restrictedEl.classList.remove("hidden");
        return;
      }

      restrictedEl.classList.add("hidden");
      mainAppEl.classList.remove("hidden");
      btnAddEl.classList.remove("hidden");
      btnExportCsvEl.classList.remove("hidden");

      const refs = {};
      const bump = (id, key) => {
        const num = Number(id);
        if (!Number.isInteger(num) || num <= 0) return;
        if (!refs[num]) refs[num] = { attr: 0, rec: 0, ret: 0, total: 0 };
        refs[num][key]++;
        refs[num].total++;
      };

      try {
        const rawSig = await grist.docApi.fetchTable("Signalements");
        for (const r of tableToRows(rawSig)) {
          bump(r.Agent_Attributaire, "attr");
          bump(r.Agent_Recepteur, "rec");
        }
      } catch (e) {}

      try {
        const rawRet = await grist.docApi.fetchTable("Retours_Actions");
        for (const r of tableToRows(rawRet)) {
          bump(r.Agent_Intervenant, "ret");
        }
      } catch (e) {}

      agentRefsMap = refs;
      showBanner(bannerEl, null);
      renderTable();
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

  searchInputEl.addEventListener("input", renderTable);
  if (roleFilterEl) roleFilterEl.addEventListener("change", renderTable);
  btnRefreshEl.addEventListener("click", loadData);
  btnExportCsvEl.addEventListener("click", exportAgentsCsv);
  btnAddEl.addEventListener("click", () => openEditModal(null));
  btnCloseModalEl.addEventListener("click", closeEditModal);
  btnCancelModalEl.addEventListener("click", closeEditModal);
  btnCancelDeleteEl.addEventListener("click", closeDeleteModal);

  tableBodyEl.addEventListener("click", (ev) => {
    const editBtn = ev.target.closest("button[data-edit-agent]");
    if (editBtn) {
      const ag = sessionCtx.agentsById[Number(editBtn.getAttribute("data-edit-agent"))];
      if (ag) openEditModal(ag);
      return;
    }
    const delBtn = ev.target.closest("button[data-del-agent]");
    if (delBtn) {
      const ag = sessionCtx.agentsById[Number(delBtn.getAttribute("data-del-agent"))];
      if (ag) openDeleteModal(ag);
    }
  });

  modalFormEl.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    showBanner(modalErrEl, null);

    const nom = inputNomEl.value.trim();
    const email = inputEmailEl.value.trim().toLowerCase();
    let trigramme = inputTrigrammeEl.value.trim().toUpperCase();
    const role = inputRoleEl.value === "Gestionnaire" ? "Gestionnaire" : "Agent";

    if (!nom) {
      showBanner(modalErrEl, "Renseignez le nom et le prénom de l'agent.", "err");
      return;
    }
    if (!email || !isValidEmail(email)) {
      showBanner(modalErrEl, "Renseignez une adresse courriel professionnelle valide.", "err");
      return;
    }
    const duplicate = sessionCtx.agents.some((ag) => {
      return ag.id !== editingAgentId && String(ag.Email || "").trim().toLowerCase() === email;
    });
    if (duplicate) {
      showBanner(modalErrEl, "Un agent avec cette adresse courriel existe déjà dans l'annuaire.", "err");
      return;
    }

    const currentAgent = editingAgentId !== null ? sessionCtx.agentsById[editingAgentId] : null;
    const connectedId = sessionCtx.connectedAgent ? sessionCtx.connectedAgent.id : null;
    const isEditingSelf = editingAgentId !== null && (
      editingAgentId === connectedId || (currentAgent && currentAgent.Est_Connecte === true)
    );
    const activeManagersCount = sessionCtx.agents.filter((ag) => getAgentRole(ag) === "Gestionnaire").length;
    if (isEditingSelf && currentAgent && getAgentRole(currentAgent) === "Gestionnaire" && role !== "Gestionnaire" && activeManagersCount <= 1) {
      showBanner(modalErrEl, "Impossible de retirer votre propre rôle Gestionnaire : vous êtes le dernier gestionnaire actif du registre.", "err");
      return;
    }

    if (!trigramme) {
      trigramme = suggestTrigramme(nom);
    }

    // Ne jamais inclure Est_Connecte (colonne formule protégée par les ACL)
    const fields = { Nom: nom, Email: email, Trigramme: trigramme, Role: role };
    btnSaveModalEl.disabled = true;
    btnSaveModalEl.textContent = "Enregistrement...";
    try {
      if (editingAgentId !== null) {
        await grist.docApi.applyUserActions([["UpdateRecord", "Referentiel_Agents", editingAgentId, fields]]);
      } else {
        await grist.docApi.applyUserActions([["AddRecord", "Referentiel_Agents", null, fields]]);
      }
      const savedNom = nom;
      const wasEdit = editingAgentId !== null;
      closeEditModal();
      await loadData();
      showBanner(
        bannerEl,
        (wasEdit ? "Fiche agent mise à jour : " : "Agent ajouté à l'annuaire : ") + savedNom + ".",
        "ok"
      );
    } catch (err) {
      showBanner(modalErrEl, formatGristError(err), "err");
    } finally {
      btnSaveModalEl.disabled = false;
      btnSaveModalEl.textContent = "Enregistrer";
    }
  });

  btnConfirmDeleteEl.addEventListener("click", async () => {
    if (!deletingAgent) return;
    const targetId = deletingAgent.id;
    const targetNom = deletingAgent.Nom || "";
    const usage = getUsageForAgent(targetId);
    const connectedId = sessionCtx.connectedAgent ? sessionCtx.connectedAgent.id : null;
    if (usage.total > 0 || targetId === connectedId) {
      showBanner(deleteErrEl, "Suppression bloquée pour préserver l'intégrité du registre.", "err");
      return;
    }

    btnConfirmDeleteEl.disabled = true;
    btnConfirmDeleteEl.textContent = "Suppression...";
    try {
      await grist.docApi.applyUserActions([["RemoveRecord", "Referentiel_Agents", targetId]]);
      closeDeleteModal();
      await loadData();
      showBanner(bannerEl, "Agent supprimé de l'annuaire : " + targetNom + ".", "ok");
    } catch (err) {
      showBanner(deleteErrEl, formatGristError(err), "err");
    } finally {
      btnConfirmDeleteEl.disabled = false;
      btnConfirmDeleteEl.textContent = "Supprimer définitivement";
    }
  });

  if (typeof grist.onRecords === "function") {
    grist.onRecords(() => scheduleReload());
  }

  loadData();
})();
"""

    return {
        "_html": envelopper_document_html("Gestion des agents", body_html, extra_css=GESTION_AGENTS_CSS),
        "_js": f"const CFG = {cfg_json};\n{COMMON_JS_HELPERS}\n{js_body}".strip(),
    }


__all__ = ["generer_widget_gestion_agents"]
