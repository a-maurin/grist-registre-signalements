# -*- coding: utf-8 -*-
"""Socle CSS, JS et constructeurs HTML communs aux widgets du registre des signalements."""

import html
import json

from config import CHOIX_ENCADRANT

CUSTOM_WIDGET_BUILDER_URL = "https://gristlabs.github.io/grist-widget/custom-widget-builder/index.html"
GRIST_PLUGIN_API_URL = "https://docs.getgrist.com/grist-plugin-api.js"

CHOIX_CANAL = [
    "Appel téléphonique",
    "Courriel",
    "Courrier postal",
    "Accueil physique",
    "Constat direct",
    "Autre",
]

CHOIX_DOMAINE = [
    "Eau et milieux aquatiques",
    "Espèces protégées et biodiversité",
    "Chasse et faune sauvage",
    "Pêche",
    "Forêt et espaces naturels",
    "Déchets et pollutions",
    "Autre",
]

CHOIX_PRIORITE = ["Normale", "Urgente", "Faible"]

CHOIX_STATUT = ["Nouveau", "Attribué", "En cours", "Traité", "Classé sans suite"]

CHOIX_DEMARCHE = [
    "Contrôle de terrain",
    "Prise de contact / audition",
    "Rappel à la loi",
    "Constat d'infraction",
    "Transmission à un tiers",
    "Autre",
]

CHOIX_SUITE = [
    "Procès-verbal d'infraction",
    "Rapport de manquement administratif",
    "Régularisation",
    "Classement sans suite",
    "Transmission à un autre service",
    "Autre",
]

BASE_CSS = """
*, *::before, *::after { box-sizing: border-box; }
html, body {
  margin: 0;
  padding: 0;
  background: #f8fafc;
  color: #0f172a;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 13px;
  line-height: 1.45;
}
.sig-wrap {
  width: 100%;
  max-width: 1520px;
  margin: 0 auto;
  padding: 12px 14px 20px;
}
.sig-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 10px;
}
.sig-title-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}
.sig-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}
.sig-subtitle {
  margin: 2px 0 0;
  font-size: 12px;
  color: #64748b;
}
.sig-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 10px;
}
.sig-card h2 {
  margin: 0 0 10px;
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}
.sig-grid-2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.sig-grid-2 > * { min-width: 0; }
.sig-layout {
  display: grid;
  grid-template-columns: minmax(0, 360px) minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}
.sig-master, .sig-detail, .sig-card, .sig-table-wrap {
  min-width: 0;
}
.sig-scroll {
  overflow: visible;
  max-height: none;
}
@media (max-width: 900px) {
  .sig-layout { grid-template-columns: minmax(0, 1fr); }
  .sig-grid-2 { grid-template-columns: 1fr; }
  .sig-scroll { max-height: none; }
}
.sig-toolbar, .sig-filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 9px 12px;
  margin-bottom: 10px;
}
.sig-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.sig-pill {
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #334155;
  border-radius: 999px;
  padding: 5px 11px;
  font-family: inherit;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.sig-pill:hover { background: #f1f5f9; }
.sig-pill.active {
  background: #1d4ed8;
  border-color: #1d4ed8;
  color: #ffffff;
}
.sig-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 9px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 700;
  border: 1px solid transparent;
  white-space: nowrap;
}
.badge-info { background: #eff6ff; color: #1d4ed8; border-color: #bfdbfe; }
.badge-nouveau { background: #fff4e5; color: #8a5300; border-color: #ffd8a8; }
.badge-attribue { background: #e8edff; color: #005bb5; border-color: #b8d1ff; }
.badge-encours { background: #f3e8ff; color: #6b21a8; border-color: #d8b4fe; }
.badge-traite { background: #dcfce7; color: #166534; border-color: #86efac; }
.badge-classe { background: #f1f5f9; color: #475569; border-color: #cbd5e1; }
.badge-urgente { background: #fee2e2; color: #991b1b; border-color: #fca5a5; }
.badge-normale { background: #e8edff; color: #005bb5; border-color: #b8d1ff; }
.badge-faible { background: #f1f5f9; color: #475569; border-color: #cbd5e1; }
.sig-field {
  margin-bottom: 10px;
}
.sig-field label {
  display: block;
  margin-bottom: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #334155;
}
.sig-input, .sig-select, .sig-textarea,
.sig-field input, .sig-field select, .sig-field textarea {
  width: 100%;
  padding: 7px 9px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-family: inherit;
  font-size: 12.5px;
  background: #ffffff;
  color: #0f172a;
}
.sig-field input:focus, .sig-field select:focus, .sig-field textarea:focus,
.sig-input:focus, .sig-select:focus {
  outline: 2px solid #bfdbfe;
  border-color: #1d4ed8;
}
.sig-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #1e293b;
  border-radius: 6px;
  padding: 6px 11px;
  font-family: inherit;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
}
.sig-btn:hover { background: #f1f5f9; }
.sig-btn:disabled { opacity: 0.55; cursor: not-allowed; }
.sig-btn-primary {
  background: #005bb5;
  border-color: #005bb5;
  color: #ffffff;
}
.sig-btn-primary:hover { background: #004994; }
.sig-btn-danger {
  background: #fef2f2;
  border-color: #fecaca;
  color: #b91c1c;
}
.sig-btn-danger:hover { background: #fee2e2; }
.sig-banner {
  display: none;
  border-radius: 8px;
  padding: 9px 12px;
  margin-bottom: 10px;
  font-size: 12.5px;
  font-weight: 600;
}
.sig-banner-ok { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }
.sig-banner-warn { background: #fffbeb; border: 1px solid #fde68a; color: #92400e; }
.sig-banner-err { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
.sig-table-wrap {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  max-width: 100%;
  overflow-x: auto;
}
.sig-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12.5px;
}
.sig-table th {
  text-align: left;
  padding: 8px 10px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  color: #475569;
  font-weight: 700;
  white-space: nowrap;
}
.sig-table th.sig-th-sort { cursor: pointer; user-select: none; }
.sig-table th.sig-th-sort:hover { color: #0f172a; }
.sig-table td {
  padding: 8px 10px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: top;
  overflow-wrap: break-word;
}
.sig-modal-backdrop {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  z-index: 1000;
  align-items: center;
  justify-content: center;
  padding: 16px;
}
.sig-modal-backdrop.open { display: flex; }
.sig-modal {
  background: #ffffff;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  max-width: 640px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  padding: 16px 18px;
}
.sig-retour-item {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 8px;
}
.hidden { display: none !important; }
"""

PRINT_CSS = """
@media print {
  @page { margin: 12mm; }
  html, body {
    background: #ffffff !important;
    color: #000000 !important;
  }
  .no-print,
  .sig-master,
  .sig-toolbar,
  .sig-filters,
  .sig-actions,
  .sig-modal-backdrop,
  button.no-print {
    display: none !important;
  }
  html, body,
  .sig-wrap,
  .sig-layout,
  .sig-detail,
  .sig-fiche,
  .sig-scroll {
    overflow: visible !important;
    height: auto !important;
    max-height: none !important;
    position: static !important;
    display: block !important;
    width: 100% !important;
    max-width: none !important;
    padding: 0 !important;
    margin: 0 !important;
  }
  .sig-card,
  .sig-retour-item,
  .print-avoid-break {
    break-inside: avoid;
    page-break-inside: avoid;
    box-shadow: none !important;
  }
}
"""

COMMON_JS_HELPERS = r"""
function tableToRows(tableData) {
  if (!tableData || !Array.isArray(tableData.id)) return [];
  const keys = Object.keys(tableData);
  const rows = [];
  for (let i = 0; i < tableData.id.length; i++) {
    const row = {};
    for (const k of keys) {
      row[k] = tableData[k][i];
    }
    rows.push(row);
  }
  return rows;
}

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;");
}

function formatDateFr(ts, withTime) {
  if (ts === null || ts === undefined || ts === "") return "Non renseignée";
  const num = Number(ts);
  if (!Number.isFinite(num)) return String(ts);
  const d = new Date(num * 1000);
  if (Number.isNaN(d.getTime())) return String(ts);
  const dd = String(d.getDate()).padStart(2, "0");
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const yyyy = d.getFullYear();
  if (!withTime) return dd + "/" + mm + "/" + yyyy;
  const hh = String(d.getHours()).padStart(2, "0");
  const min = String(d.getMinutes()).padStart(2, "0");
  return dd + "/" + mm + "/" + yyyy + " à " + hh + ":" + min;
}

function toDatetimeLocalValue(date) {
  const d = date instanceof Date ? date : new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return (
    d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) +
    "T" + pad(d.getHours()) + ":" + pad(d.getMinutes())
  );
}

function parseDatetimeLocalToTs(str) {
  if (!str) return null;
  const ms = Date.parse(str);
  return Number.isNaN(ms) ? null : Math.floor(ms / 1000);
}

function parseDateToTs(str) {
  if (!str) return null;
  const parts = String(str).split("-").map(Number);
  if (parts.length !== 3 || parts.some(Number.isNaN)) return null;
  const ms = Date.UTC(parts[0], parts[1] - 1, parts[2], 12, 0, 0);
  return Math.floor(ms / 1000);
}

function formatGristError(err) {
  const raw = (err && (err.message || String(err))) || "Erreur inconnue";
  if (raw.includes("Access") || raw.includes("Blocked") || raw.includes("403")) {
    return "Opération refusée par les règles de confidentialité Grist (" + raw + ").";
  }
  return "Échec de l'opération : " + raw;
}

function showBanner(el, msg, kind) {
  if (!el) return;
  if (!msg) {
    el.style.display = "none";
    el.textContent = "";
    el.className = "sig-banner";
    return;
  }
  const cls = kind === "err" ? "sig-banner-err" : (kind === "warn" ? "sig-banner-warn" : "sig-banner-ok");
  el.className = "sig-banner " + cls;
  el.textContent = msg;
  el.style.display = "block";
}

async function loadSessionContext() {
  let agents = [];
  let connectedAgent = null;
  const agentsById = {};
  const agentsByNom = {};
  try {
    const rawAgents = await grist.docApi.fetchTable("Referentiel_Agents");
    agents = tableToRows(rawAgents).filter((r) => r && r.Nom);
    agents.sort((a, b) => String(a.Nom).localeCompare(String(b.Nom), "fr"));
    for (const a of agents) {
      agentsById[a.id] = a;
      agentsByNom[a.Nom] = a;
      if (a.Est_Connecte === true) {
        connectedAgent = {
          id: a.id,
          Nom: a.Nom,
          Email: a.Email || "",
          Trigramme: a.Trigramme || "",
          Role: a.Role || "Agent",
        };
      }
    }
  } catch (e) {
    // Repli silencieux si l'annuaire est inaccessible
  }

  let isManager = false;
  try {
    const rawGes = await grist.docApi.fetchTable("Acces_Gestionnaires");
    const gesRows = tableToRows(rawGes);
    isManager = gesRows.length > 0 && gesRows.some((r) => typeof r.Titre === "string" && r.Titre.length > 0);
  } catch (e) {
    isManager = false;
  }

  return { agents, agentsById, agentsByNom, connectedAgent, isManager };
}

const _tokenCache = { ro: null, rw: null };

async function getFreshAccessToken(readOnly, forceRefresh) {
  const modeKey = readOnly ? "ro" : "rw";
  const cached = _tokenCache[modeKey];
  if (!forceRefresh && cached && cached.token && cached.baseUrl && Date.now() < cached.expiresAt) {
    return cached;
  }
  if (!grist || !grist.docApi || typeof grist.docApi.getAccessToken !== "function") {
    throw new Error("API de jeton Grist indisponible dans ce contexte.");
  }
  const info = await grist.docApi.getAccessToken({ readOnly: Boolean(readOnly) });
  if (!info || !info.token || !info.baseUrl) {
    throw new Error("Jeton d'accès Grist vide ou incomplet.");
  }
  const ttl = Number(info.ttlMsecs) || 60000;
  const entry = {
    token: info.token,
    baseUrl: String(info.baseUrl).replace(/\/+$/, ""),
    ttlMsecs: ttl,
    expiresAt: Date.now() + Math.max(5000, ttl - 15000),
  };
  _tokenCache[modeKey] = entry;
  return entry;
}

async function fetchWithFreshToken(readOnly, buildRequest) {
  const tokenInfo = await getFreshAccessToken(readOnly, false);
  let resp = await buildRequest(tokenInfo);
  if (resp.status === 401 || resp.status === 403) {
    const refreshed = await getFreshAccessToken(readOnly, true);
    resp = await buildRequest(refreshed);
  }
  return resp;
}

async function uploadAttachment(file) {
  if (!file) throw new Error("Aucun fichier fourni.");
  const resp = await fetchWithFreshToken(false, ({ baseUrl, token }) => {
    const fd = new FormData();
    fd.append("upload", file, file.name || "piece_jointe");
    return fetch(baseUrl + "/attachments?auth=" + encodeURIComponent(token), {
      method: "POST",
      credentials: "omit",
      headers: { "X-Requested-With": "XMLHttpRequest" },
      body: fd,
    });
  });
  if (!resp.ok) {
    const txt = await resp.text().catch(() => "");
    throw new Error("HTTP " + resp.status + (txt ? " : " + txt : ""));
  }
  const data = await resp.json();
  if (Array.isArray(data) && data.length > 0) {
    return Number(data[0]);
  }
  throw new Error("Identifiant de pièce jointe absent de la réponse Grist.");
}

async function fetchAttachmentMeta(attId) {
  const resp = await fetchWithFreshToken(true, ({ baseUrl, token }) =>
    fetch(baseUrl + "/attachments/" + encodeURIComponent(attId) + "?auth=" + encodeURIComponent(token), {
      credentials: "omit",
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
  );
  if (!resp.ok) {
    const txt = await resp.text().catch(() => "");
    throw new Error("HTTP " + resp.status + (txt ? " : " + txt : ""));
  }
  return await resp.json();
}

async function fetchAttachmentsMetaByIds(attIds) {
  const uniqueIds = Array.from(new Set((attIds || []).map(Number).filter((n) => Number.isInteger(n) && n > 0)));
  const metaMap = {};
  await Promise.all(
    uniqueIds.map(async (id) => {
      try {
        metaMap[id] = await fetchAttachmentMeta(id);
      } catch (e) {
        metaMap[id] = null;
      }
    })
  );
  return metaMap;
}

async function fetchAttachmentBlob(attId) {
  const resp = await fetchWithFreshToken(true, ({ baseUrl, token }) =>
    fetch(baseUrl + "/attachments/" + encodeURIComponent(attId) + "/download?auth=" + encodeURIComponent(token), {
      credentials: "omit",
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
  );
  if (!resp.ok) {
    const txt = await resp.text().catch(() => "");
    throw new Error("HTTP " + resp.status + (txt ? " : " + txt : ""));
  }
  const blob = await resp.blob();
  return { blob, contentType: resp.headers.get("content-type") || blob.type || "" };
}

async function downloadAttachment(attId, fileName) {
  const { blob } = await fetchAttachmentBlob(attId);
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName || ("piece_jointe_" + attId);
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 10000);
}

function decodeAttachmentIds(rawVal) {
  if (!Array.isArray(rawVal)) return [];
  const ids = [];
  for (const item of rawVal) {
    if (item === "L") continue;
    const n = Number(item);
    if (Number.isInteger(n) && n > 0) ids.push(n);
  }
  return ids;
}

function buildCsvUtf8Bom(headers, rows) {
  const esc = (val) => {
    const s = String(val ?? "");
    if (/[;"\r\n]/.test(s)) {
      return '"' + s.replace(/"/g, '""') + '"';
    }
    return s;
  };
  const lines = [headers.map(esc).join(";")];
  for (const row of rows || []) {
    lines.push(row.map(esc).join(";"));
  }
  return "\uFEFF" + lines.join("\r\n");
}
"""


def envelopper_document_html(titre, body_html, extra_css=""):
    """Assemble un document HTML5 autonome prêt pour Custom Widget Builder."""
    titre_safe = html.escape(titre)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="fr">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f"  <title>{titre_safe}</title>\n"
        f'  <script src="{GRIST_PLUGIN_API_URL}"></script>\n'
        f"  <style>{BASE_CSS}\n{PRINT_CSS}\n{extra_css}</style>\n"
        "</head>\n"
        "<body>\n"
        f"{body_html}\n"
        "</body>\n"
        "</html>"
    )


def construire_options_custom_widget(widget_spec, access="full"):
    """Construit la chaîne JSON de _grist_Views_section.options pour Custom Widget Builder."""
    return json.dumps(
        {
            "customView": json.dumps(
                {
                    "mode": "url",
                    "url": CUSTOM_WIDGET_BUILDER_URL,
                    "access": access,
                    "widgetOptions": {
                        "_html": widget_spec["_html"],
                        "_js": widget_spec["_js"],
                    },
                },
                ensure_ascii=False,
            )
        },
        ensure_ascii=False,
    )
