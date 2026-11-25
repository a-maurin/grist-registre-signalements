# -*- coding: utf-8 -*-
"""Générateur du widget HTML « ✍️ Nouveau signalement » (Lot 2)."""

import html
import json

from config import DOC_URL_PILOTAGE, ENCADRANT_PAR_DEFAUT, SERVICE_NOM
from widgets.commun import (
    CHOIX_CANAL,
    CHOIX_DOMAINE,
    CHOIX_ENCADRANT,
    COMMON_JS_HELPERS,
    envelopper_document_html,
)

NOUVEAU_SIGNALEMENT_CSS = """
.ns-wrap { max-width: 960px; margin: 0 auto; }
.ns-header {
  border-left: 4px solid #005bb5;
  padding: 10px 14px;
  margin-bottom: 10px;
}
.ns-section {
  padding: 12px 16px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}
.ns-sec-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 8px;
  margin-bottom: 10px;
  border-bottom: 1px solid #f1f5f9;
}
.ns-sec-head h2 {
  margin: 0;
  font-size: 13.5px;
  font-weight: 700;
  color: #0f172a;
}
.ns-step {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 21px;
  height: 21px;
  border-radius: 999px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1d4ed8;
  font-size: 11.5px;
  font-weight: 800;
  flex-shrink: 0;
}
.ns-grid-2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 14px;
}
.ns-grid-2 > * { min-width: 0; }
.ns-grid-2 .sig-field { margin-bottom: 0; }
.ns-stack-gap { margin-top: 10px; }
@media (max-width: 720px) {
  .ns-grid-2 { grid-template-columns: 1fr; }
}
.ns-dropzone {
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  padding: 10px 12px;
}
.ns-drop-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.ns-drop-hint {
  font-size: 11.5px;
  color: #64748b;
}
.ns-file-input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  overflow: hidden;
  pointer-events: none;
}
.ns-files-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
}
.ns-files-list:empty { display: none; }
.ns-file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 6px 10px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 12px;
}
.ns-confirm-card {
  border-color: #86efac;
  background: #f0fdf4;
}
.ns-confirm-num {
  font-size: 22px;
  font-weight: 800;
  color: #166534;
  margin: 4px 0 8px;
}
.ns-row-inline {
  display: flex;
  gap: 8px;
  align-items: center;
}
.ns-row-inline input { flex: 1 1 auto; min-width: 0; }
.ns-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 4px;
}
.ns-required-note {
  font-size: 11.5px;
  color: #64748b;
}
"""


def _options_select(valeurs, valeur_defaut=None):
    return "\n".join(
        f'              <option value="{html.escape(v, quote=True)}"'
        f'{" selected" if v == valeur_defaut else ""}>{html.escape(v)}</option>'
        for v in valeurs
    )


def generer_widget_nouveau_signalement():
    """Retourne {_html, _js} pour le formulaire dynamique « ✍️ Nouveau signalement »."""
    canaux_opts = _options_select(CHOIX_CANAL)
    domaines_opts = _options_select(CHOIX_DOMAINE)
    encadrants_opts = _options_select(CHOIX_ENCADRANT, valeur_defaut=ENCADRANT_PAR_DEFAUT)
    service_echappe = html.escape(SERVICE_NOM)

    body_html = f"""  <div class="sig-wrap ns-wrap">
    <div class="sig-header ns-header">
      <div>
        <h1 class="sig-title">✍️ Nouveau signalement</h1>
        <p class="sig-subtitle">Enregistrement initial d'une information, doléance ou alerte transmise au {service_echappe}.</p>
      </div>
      <span class="sig-badge badge-info" id="nsSessionBadge">Session en cours...</span>
    </div>

    <div id="nsBanner" class="sig-banner" role="status"></div>

    <div id="nsConfirmCard" class="sig-card ns-confirm-card hidden">
      <div style="font-size:12px;font-weight:700;text-transform:uppercase;color:#166534;">Signalement enregistré</div>
      <div class="ns-confirm-num" id="nsConfirmNum">2026-0000</div>
      <p id="nsConfirmSummary" style="margin:0 0 12px;color:#14532d;"></p>
      <div style="display:flex;flex-wrap:wrap;gap:8px;">
        <a id="btnAlerterEncadrant" class="sig-btn sig-btn-primary" href="#">✉️ Alerter l'encadrant par courriel</a>
        <button type="button" class="sig-btn" id="btnNouveauAutre">Enregistrer un autre signalement</button>
      </div>
    </div>

    <form id="nsForm" novalidate>
      <div class="sig-card ns-section">
        <div class="ns-sec-head">
          <span class="ns-step">1</span>
          <h2>Réception de la saisine</h2>
        </div>
        <div class="ns-grid-2">
          <div class="sig-field">
            <label for="dateReception">Date et heure de réception *</label>
            <div class="ns-row-inline">
              <input type="datetime-local" id="dateReception" required>
              <button type="button" class="sig-btn" id="btnMaintenant">Maintenant</button>
            </div>
          </div>
          <div class="sig-field">
            <label for="canalReception">Canal d'entrée *</label>
            <select id="canalReception" required>
              <option value="">-- Sélectionnez un canal --</option>
{canaux_opts}
            </select>
          </div>
          <div class="sig-field">
            <label for="agentRecepteur">Agent récepteur *</label>
            <select id="agentRecepteur" required>
              <option value="">-- Sélectionnez un agent --</option>
            </select>
          </div>
          <div class="sig-field">
            <label for="encadrantAlerter">Encadrant à alerter pour attribution</label>
            <select id="encadrantAlerter">
{encadrants_opts}
            </select>
          </div>
        </div>
      </div>

      <div class="sig-card ns-section">
        <div class="ns-sec-head">
          <span class="ns-step">2</span>
          <h2>Requérant et localisation</h2>
        </div>
        <div class="ns-grid-2">
          <div class="sig-field">
            <label for="requerantNom">Identité du requérant (ou mention anonyme)</label>
            <input type="text" id="requerantNom" placeholder="Ex. M. Dupont, Mairie de..., Anonyme">
          </div>
          <div class="sig-field">
            <label for="requerantContact">Coordonnées de contact (téléphone ou courriel)</label>
            <input type="text" id="requerantContact" placeholder="Ex. 06 12 34 56 78 ou nom@exemple.fr">
          </div>
          <div class="sig-field">
            <label for="commune">Commune *</label>
            <input type="text" id="commune" required placeholder="Ex. Saint-Martin">
          </div>
          <div class="sig-field">
            <label for="domaineActivite">Domaine d'activité *</label>
            <select id="domaineActivite" required>
              <option value="">-- Sélectionnez un domaine --</option>
{domaines_opts}
            </select>
          </div>
        </div>
        <div class="sig-field ns-stack-gap" style="margin-bottom:0;">
          <label for="lieuDit">Lieu-dit / Détail de localisation</label>
          <input type="text" id="lieuDit" placeholder="Ex. Chemin des Moulins, parcelle...">
        </div>
      </div>

      <div class="sig-card ns-section">
        <div class="ns-sec-head">
          <span class="ns-step">3</span>
          <h2>Faits signalés et pièces jointes</h2>
        </div>
        <div class="sig-field">
          <label for="descriptionFaits">Description des faits signalés *</label>
          <textarea id="descriptionFaits" rows="3" required placeholder="Circonstances, constatations transmises, éléments utiles à l'intervention..."></textarea>
        </div>
        <div class="sig-field" style="margin-bottom:0;">
          <label for="piecesJointesInput">Pièces jointes initiales</label>
          <div class="ns-dropzone">
            <div class="ns-drop-bar">
              <label for="piecesJointesInput" class="sig-btn" style="margin:0;cursor:pointer;">📎 Ajouter des pièces jointes</label>
              <span class="ns-drop-hint">Photographies, courriels, documents PDF ou images (ajout multiple possible)</span>
            </div>
            <input type="file" id="piecesJointesInput" class="ns-file-input" multiple>
            <div id="piecesJointesList" class="ns-files-list"></div>
          </div>
        </div>
      </div>

      <div class="ns-footer">
        <span class="ns-required-note">* Champs obligatoires</span>
        <button type="submit" class="sig-btn sig-btn-primary" id="btnSubmitSignalement">Enregistrer le signalement</button>
      </div>
    </form>
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

  const sessionBadgeEl = document.getElementById("nsSessionBadge");
  const bannerEl = document.getElementById("nsBanner");
  const confirmCardEl = document.getElementById("nsConfirmCard");
  const confirmNumEl = document.getElementById("nsConfirmNum");
  const confirmSummaryEl = document.getElementById("nsConfirmSummary");
  const btnAlerterEl = document.getElementById("btnAlerterEncadrant");
  const btnNouveauAutreEl = document.getElementById("btnNouveauAutre");
  const formEl = document.getElementById("nsForm");
  const dateEl = document.getElementById("dateReception");
  const btnMaintenantEl = document.getElementById("btnMaintenant");
  const agentRecepteurEl = document.getElementById("agentRecepteur");
  const canalEl = document.getElementById("canalReception");
  const reqNomEl = document.getElementById("requerantNom");
  const reqContactEl = document.getElementById("requerantContact");
  const communeEl = document.getElementById("commune");
  const lieuDitEl = document.getElementById("lieuDit");
  const domaineEl = document.getElementById("domaineActivite");
  const descEl = document.getElementById("descriptionFaits");
  const pjInputEl = document.getElementById("piecesJointesInput");
  const pjListEl = document.getElementById("piecesJointesList");
  const encadrantEl = document.getElementById("encadrantAlerter");
  const btnSubmitEl = document.getElementById("btnSubmitSignalement");

  let sessionCtx = { agents: [], agentsById: {}, agentsByNom: {}, connectedAgent: null, isManager: false };
  let selectedFiles = [];

  function renderSelectedFiles() {
    pjListEl.innerHTML = "";
    if (!selectedFiles.length) return;
    selectedFiles.forEach((file, idx) => {
      const item = document.createElement("div");
      item.className = "ns-file-item";
      const sizeKb = Math.max(1, Math.round((file.size || 0) / 1024));
      item.innerHTML =
        "<span>📎 " + escapeHtml(file.name) + " (" + sizeKb + " Ko)</span>" +
        '<button type="button" class="sig-btn" data-remove-idx="' + idx + '">Retirer</button>';
      pjListEl.appendChild(item);
    });
  }

  function resetFormDefaults() {
    formEl.reset();
    selectedFiles = [];
    renderSelectedFiles();
    dateEl.value = toDatetimeLocalValue(new Date());
    encadrantEl.value = CFG.defaultEncadrant;
    if (sessionCtx.connectedAgent) {
      agentRecepteurEl.value = String(sessionCtx.connectedAgent.id);
    }
  }

  function buildFallbackMailto(info) {
    const dest = sessionCtx.agentsByNom[info.encadrant] || sessionCtx.agentsByNom[CFG.defaultEncadrant];
    const email = dest && dest.Email ? dest.Email : "";
    if (!email) return "#";
    const destNom = dest ? dest.Nom : info.encadrant;
    const sujet = "[Signalement " + info.numero + "] Nouveau signalement à attribuer - " + (info.commune || "Non précisée");
    const corps = [
      "Bonjour " + destNom + ",",
      "",
      "Un nouveau signalement a été enregistré dans le registre et est en attente d'attribution de mission.",
      "",
      "=== FICHE DE SIGNALEMENT " + info.numero + " ===",
      "- Date de réception : " + formatDateFr(info.dateTs, true),
      "- Agent récepteur : " + (info.agentNom || "Non précisé"),
      "- Canal d'entrée : " + (info.canal || "Non précisé"),
      "- Requérant : " + (info.reqNom || "Anonyme / Non précisé") + " (" + (info.reqContact || "Pas de coordonnées") + ")",
      "- Localisation : " + (info.commune || "Non précisée") + " - " + (info.lieuDit || ""),
      "- Domaine : " + (info.domaine || "Non précisé"),
      "",
      "DESCRIPTION DES FAITS :",
      info.desc || "Aucune description",
      "",
      "=== ACCÈS AU DOSSIER DANS GRIST ===",
      "Pour consulter la fiche complète et procéder à l'attribution de la mission :",
      CFG.docUrlPilotage,
      "",
      "Bien cordialement.",
    ].join("\n");
    return "mailto:" + encodeURIComponent(email) + "?subject=" + encodeURIComponent(sujet) + "&body=" + encodeURIComponent(corps);
  }

  async function readCreatedRecord(newId) {
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        const rows = tableToRows(await grist.docApi.fetchTable("Signalements"));
        const match = rows.find((r) => r.id === newId);
        if (match) return match;
      } catch (e) {}
      await new Promise((resolve) => setTimeout(resolve, 250));
    }
    return null;
  }

  pjInputEl.addEventListener("change", () => {
    const incoming = Array.from(pjInputEl.files || []);
    if (incoming.length) {
      selectedFiles = selectedFiles.concat(incoming);
      pjInputEl.value = "";
      renderSelectedFiles();
    }
  });

  pjListEl.addEventListener("click", (ev) => {
    const btn = ev.target.closest("button[data-remove-idx]");
    if (!btn) return;
    const idx = Number(btn.getAttribute("data-remove-idx"));
    if (Number.isInteger(idx) && idx >= 0 && idx < selectedFiles.length) {
      selectedFiles.splice(idx, 1);
      renderSelectedFiles();
    }
  });

  btnMaintenantEl.addEventListener("click", () => {
    dateEl.value = toDatetimeLocalValue(new Date());
  });

  btnNouveauAutreEl.addEventListener("click", () => {
    confirmCardEl.classList.add("hidden");
    formEl.classList.remove("hidden");
    showBanner(bannerEl, null);
    resetFormDefaults();
  });

  formEl.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    showBanner(bannerEl, null);

    const dateTs = parseDatetimeLocalToTs(dateEl.value);
    const agentRecepteurId = Number(agentRecepteurEl.value);
    const canal = canalEl.value.trim();
    const commune = communeEl.value.trim();
    const lieuDit = lieuDitEl.value.trim();
    const domaine = domaineEl.value.trim();
    const desc = descEl.value.trim();
    const reqNom = reqNomEl.value.trim();
    const reqContact = reqContactEl.value.trim();
    const encadrant = encadrantEl.value.trim() || CFG.defaultEncadrant;

    if (!dateTs) {
      showBanner(bannerEl, "Renseignez une date et une heure de réception valides.", "err");
      dateEl.focus();
      return;
    }
    if (!Number.isInteger(agentRecepteurId) || agentRecepteurId <= 0) {
      showBanner(bannerEl, "Sélectionnez l'agent récepteur du signalement.", "err");
      agentRecepteurEl.focus();
      return;
    }
    if (!canal) {
      showBanner(bannerEl, "Sélectionnez le canal d'entrée.", "err");
      canalEl.focus();
      return;
    }
    if (!commune) {
      showBanner(bannerEl, "Indiquez la commune concernée.", "err");
      communeEl.focus();
      return;
    }
    if (!domaine) {
      showBanner(bannerEl, "Sélectionnez le domaine d'activité.", "err");
      domaineEl.focus();
      return;
    }
    if (!desc) {
      showBanner(bannerEl, "Renseignez la description des faits signalés.", "err");
      descEl.focus();
      return;
    }

    btnSubmitEl.disabled = true;
    btnSubmitEl.textContent = "Enregistrement en cours...";
    try {
      const attIds = [];
      for (const file of selectedFiles) {
        const attId = await uploadAttachment(file);
        attIds.push(attId);
      }

      const fields = {
        Date_Heure_Reception: dateTs,
        Agent_Recepteur: agentRecepteurId,
        Canal_Reception: canal,
        Requerant_Nom: reqNom,
        Requerant_Contact: reqContact,
        Commune: commune,
        Lieu_Dit: lieuDit,
        Domaine_Activite: domaine,
        Description_Faits: desc,
        Encadrant_A_Alerter: encadrant,
      };
      if (attIds.length > 0) {
        fields.Pieces_Jointes = ["L", ...attIds];
      }

      const res = await grist.docApi.applyUserActions([["AddRecord", "Signalements", null, fields]]);
      const newId = res && Array.isArray(res.retValues) ? Number(res.retValues[0]) : null;
      const created = newId ? await readCreatedRecord(newId) : null;

      const year = new Date(dateTs * 1000).getFullYear();
      const numero = (created && created.Numero_Signalement) || (newId ? year + "-" + String(newId).padStart(4, "0") : "Enregistré");
      const agentObj = sessionCtx.agentsById[agentRecepteurId];
      const mailtoHref = (created && created.Action_Alerter_Encadrant) || buildFallbackMailto({
        numero,
        dateTs,
        agentNom: agentObj ? agentObj.Nom : "",
        canal,
        reqNom,
        reqContact,
        commune,
        lieuDit,
        domaine,
        desc,
        encadrant,
      });

      confirmNumEl.textContent = numero;
      confirmSummaryEl.textContent =
        "Commune : " + commune + " — Domaine : " + domaine +
        " — Pièces jointes : " + attIds.length + " — Encadrant à alerter : " + encadrant + ".";
      btnAlerterEl.setAttribute("href", mailtoHref);
      if (mailtoHref === "#") {
        btnAlerterEl.classList.add("hidden");
      } else {
        btnAlerterEl.classList.remove("hidden");
      }

      formEl.classList.add("hidden");
      confirmCardEl.classList.remove("hidden");
      showBanner(bannerEl, "Le signalement " + numero + " a été enregistré.", "ok");
    } catch (err) {
      showBanner(bannerEl, formatGristError(err), "err");
    } finally {
      btnSubmitEl.disabled = false;
      btnSubmitEl.textContent = "Enregistrer le signalement";
    }
  });

  (async function init() {
    sessionCtx = await loadSessionContext();
    agentRecepteurEl.innerHTML = '<option value="">-- Sélectionnez un agent --</option>';
    for (const ag of sessionCtx.agents) {
      const opt = document.createElement("option");
      opt.value = String(ag.id);
      opt.textContent = ag.Nom;
      agentRecepteurEl.appendChild(opt);
    }
    if (sessionCtx.connectedAgent) {
      sessionBadgeEl.textContent = "Connecté : " + sessionCtx.connectedAgent.Nom;
    } else {
      sessionBadgeEl.textContent = "Session non rattachée à l'annuaire";
    }
    resetFormDefaults();
  })();
})();
"""

    return {
        "_html": envelopper_document_html("Nouveau signalement", body_html, extra_css=NOUVEAU_SIGNALEMENT_CSS),
        "_js": f"const CFG = {cfg_json};\n{COMMON_JS_HELPERS}\n{js_body}".strip(),
    }


__all__ = ["generer_widget_nouveau_signalement"]
