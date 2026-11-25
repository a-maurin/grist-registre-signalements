# -*- coding: utf-8 -*-
"""Générateur du widget HTML « 📊 Statistiques » (Lot 4)."""

import html
import json

from config import CSV_PREFIX
from widgets.commun import (
    CHOIX_CANAL,
    CHOIX_DOMAINE,
    CHOIX_PRIORITE,
    CHOIX_STATUT,
    CHOIX_SUITE,
    COMMON_JS_HELPERS,
    envelopper_document_html,
)

STATISTIQUES_CSS = """
.stat-kpis {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}
.stat-charts-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}
@media (max-width: 1020px) {
  .stat-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .stat-charts-grid { grid-template-columns: 1fr; }
}
.stat-kpi-card, .stat-charts-grid > *, .stat-legend { min-width: 0; }
.stat-kpi-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 13px 15px;
}
.stat-kpi-val {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.1;
}
.stat-kpi-lbl {
  margin-top: 4px;
  font-size: 12px;
  font-weight: 700;
  color: #475569;
}
.stat-kpi-sub {
  margin-top: 3px;
  font-size: 11px;
  color: #64748b;
}
.stat-filter-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1 1 150px;
  min-width: 135px;
}
.stat-filter-item label {
  font-size: 11px;
  font-weight: 700;
  color: #475569;
}
.stat-donut-wrap {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
}
.stat-legend {
  flex: 1 1 200px;
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.stat-legend-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 12.5px;
}
.stat-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  margin-right: 6px;
  flex-shrink: 0;
}
.stat-bar-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.stat-bar-row {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.stat-bar-head {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #334155;
  gap: 8px;
}
.stat-bar-track {
  width: 100%;
  height: 9px;
  background: #f1f5f9;
  border-radius: 999px;
  overflow: hidden;
}
.stat-bar-fill {
  height: 100%;
  border-radius: 999px;
}
.stat-restricted {
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
  border-radius: 10px;
  padding: 24px 18px;
  text-align: center;
  font-weight: 600;
}
"""


def _options_select(valeurs):
    return "\n".join(
        f'          <option value="{html.escape(v, quote=True)}">{html.escape(v)}</option>'
        for v in valeurs
    )


def generer_widget_statistiques():
    """Retourne {_html, _js} pour le tableau de bord « 📊 Statistiques »."""
    domaines_opts = _options_select(CHOIX_DOMAINE)
    priorites_opts = _options_select(CHOIX_PRIORITE)

    body_html = f"""  <div class="sig-wrap">
    <div class="sig-header no-print">
      <div>
        <h1 class="sig-title">📊 Statistiques d'activité</h1>
        <p class="sig-subtitle">Indicateurs filtrables, délais de traitement, graphiques et bilan par agent attributaire.</p>
      </div>
      <div style="display:flex;flex-wrap:wrap;align-items:center;gap:8px;">
        <span class="sig-badge badge-info" id="statSessionBadge">Vérification...</span>
        <button type="button" class="sig-btn" id="btnStatRefresh">🔄 Actualiser</button>
        <button type="button" class="sig-btn" id="btnStatPrint">🖨️ Imprimer</button>
        <button type="button" class="sig-btn sig-btn-primary hidden" id="btnStatExportCsv">📥 Exporter bilan CSV</button>
      </div>
    </div>

    <div id="statRestricted" class="stat-restricted hidden no-print">
      Accès réservé à l'encadrement.
    </div>

    <div id="statBanner" class="sig-banner no-print" role="status"></div>

    <div id="statMainApp" class="hidden">
      <div class="sig-filters no-print">
        <div class="stat-filter-item">
          <label for="statPeriode">Période de réception</label>
          <select class="sig-select" id="statPeriode">
            <option value="toutes">Toutes les périodes</option>
            <option value="annee_courante">Année en cours</option>
            <option value="annee_precedente">Année précédente</option>
            <option value="90j">90 derniers jours</option>
            <option value="30j">30 derniers jours</option>
            <option value="perso">Plage personnalisée</option>
          </select>
        </div>
        <div class="stat-filter-item hidden" id="statDateDebutWrap">
          <label for="statDateDebut">Du</label>
          <input type="date" class="sig-input" id="statDateDebut">
        </div>
        <div class="stat-filter-item hidden" id="statDateFinWrap">
          <label for="statDateFin">Au</label>
          <input type="date" class="sig-input" id="statDateFin">
        </div>
        <div class="stat-filter-item">
          <label for="statDomaine">Domaine</label>
          <select class="sig-select" id="statDomaine">
            <option value="">Tous</option>
{domaines_opts}
          </select>
        </div>
        <div class="stat-filter-item">
          <label for="statPriorite">Priorité</label>
          <select class="sig-select" id="statPriorite">
            <option value="">Toutes</option>
{priorites_opts}
          </select>
        </div>
        <div class="stat-filter-item">
          <label for="statAgent">Agent attributaire</label>
          <select class="sig-select" id="statAgent">
            <option value="">Tous</option>
            <option value="__NON_ATTRIBUE__">Non attribués</option>
          </select>
        </div>
        <div style="display:flex;align-items:flex-end;gap:8px;padding-top:14px;">
          <button type="button" class="sig-btn" id="btnStatResetFilters">Réinitialiser</button>
          <span class="sig-badge badge-info" id="statMatchCount">0 dossier(s)</span>
        </div>
      </div>

      <div class="stat-kpis" id="statKpis">
        <div class="stat-kpi-card print-avoid-break">
          <div class="stat-kpi-val" id="kpiTotal">0</div>
          <div class="stat-kpi-lbl">Total signalements</div>
          <div class="stat-kpi-sub" id="kpiTotalSub">0 actifs · 0 clos</div>
        </div>
        <div class="stat-kpi-card print-avoid-break">
          <div class="stat-kpi-val" id="kpiTauxCloture" style="color:#166534;">0 %</div>
          <div class="stat-kpi-lbl">Taux de clôture</div>
          <div class="stat-kpi-sub" id="kpiTauxSub">Traités ou classés</div>
        </div>
        <div class="stat-kpi-card print-avoid-break">
          <div class="stat-kpi-val" id="kpiUrgents" style="color:#b91c1c;">0</div>
          <div class="stat-kpi-lbl">Urgents actifs</div>
          <div class="stat-kpi-sub">Dossiers prioritaires ouverts</div>
        </div>
        <div class="stat-kpi-card print-avoid-break">
          <div class="stat-kpi-val" id="kpiDelaiAttr" style="color:#005bb5;">—</div>
          <div class="stat-kpi-lbl">Délai moy. attribution</div>
          <div class="stat-kpi-sub" id="kpiDelaiAttrSub">En jours calendaires</div>
        </div>
        <div class="stat-kpi-card print-avoid-break">
          <div class="stat-kpi-val" id="kpiDelaiTrait" style="color:#6b21a8;">—</div>
          <div class="stat-kpi-lbl">Délai moy. traitement</div>
          <div class="stat-kpi-sub" id="kpiDelaiTraitSub">Réception à intervention</div>
        </div>
      </div>

      <div class="stat-charts-grid">
        <div class="sig-card print-avoid-break" style="margin-bottom:0;">
          <h2>Répartition par statut</h2>
          <div id="chartStatuts"></div>
        </div>
        <div class="sig-card print-avoid-break" style="margin-bottom:0;">
          <h2>Répartition par domaine d'activité</h2>
          <div id="chartDomaines"></div>
        </div>
        <div class="sig-card print-avoid-break" style="margin-bottom:0;">
          <h2>Évolution mensuelle des réceptions</h2>
          <div id="chartMensuel"></div>
        </div>
        <div class="sig-card print-avoid-break" style="margin-bottom:0;">
          <h2>Canaux d'entrée et suites données</h2>
          <div id="chartCanauxSuites"></div>
        </div>
      </div>

      <div class="sig-card print-avoid-break">
        <h2>Activité par agent attributaire</h2>
        <div class="sig-table-wrap">
          <table class="sig-table">
            <thead>
              <tr>
                <th>Agent attributaire</th>
                <th>Confiés</th>
                <th>Attribués</th>
                <th>En cours</th>
                <th>Traités / clos</th>
                <th>Taux de clôture</th>
                <th>Retours saisis</th>
                <th>Délai moy. attribution</th>
              </tr>
            </thead>
            <tbody id="statAgentTableBody"></tbody>
          </table>
        </div>
      </div>
    </div>
  </div>"""

    cfg_json = json.dumps(
        {
            "statuts": CHOIX_STATUT,
            "domaines": CHOIX_DOMAINE,
            "canaux": CHOIX_CANAL,
            "priorites": CHOIX_PRIORITE,
            "suites": CHOIX_SUITE,
            "csvPrefix": CSV_PREFIX,
        },
        ensure_ascii=False,
    )

    js_body = r"""
(function () {
  grist.ready({ requiredAccess: "full" });

  const sessionBadgeEl = document.getElementById("statSessionBadge");
  const btnRefreshEl = document.getElementById("btnStatRefresh");
  const btnPrintEl = document.getElementById("btnStatPrint");
  const btnExportCsvEl = document.getElementById("btnStatExportCsv");
  const restrictedEl = document.getElementById("statRestricted");
  const bannerEl = document.getElementById("statBanner");
  const mainAppEl = document.getElementById("statMainApp");

  const periodeEl = document.getElementById("statPeriode");
  const dateDebutWrapEl = document.getElementById("statDateDebutWrap");
  const dateFinWrapEl = document.getElementById("statDateFinWrap");
  const dateDebutEl = document.getElementById("statDateDebut");
  const dateFinEl = document.getElementById("statDateFin");
  const domaineEl = document.getElementById("statDomaine");
  const prioriteEl = document.getElementById("statPriorite");
  const agentEl = document.getElementById("statAgent");
  const btnResetEl = document.getElementById("btnStatResetFilters");
  const matchCountEl = document.getElementById("statMatchCount");

  const kpiTotalEl = document.getElementById("kpiTotal");
  const kpiTotalSubEl = document.getElementById("kpiTotalSub");
  const kpiTauxClotureEl = document.getElementById("kpiTauxCloture");
  const kpiTauxSubEl = document.getElementById("kpiTauxSub");
  const kpiUrgentsEl = document.getElementById("kpiUrgents");
  const kpiDelaiAttrEl = document.getElementById("kpiDelaiAttr");
  const kpiDelaiAttrSubEl = document.getElementById("kpiDelaiAttrSub");
  const kpiDelaiTraitEl = document.getElementById("kpiDelaiTrait");
  const kpiDelaiTraitSubEl = document.getElementById("kpiDelaiTraitSub");

  const chartStatutsEl = document.getElementById("chartStatuts");
  const chartDomainesEl = document.getElementById("chartDomaines");
  const chartMensuelEl = document.getElementById("chartMensuel");
  const chartCanauxSuitesEl = document.getElementById("chartCanauxSuites");
  const agentTableBodyEl = document.getElementById("statAgentTableBody");

  let sessionCtx = { agents: [], agentsById: {}, agentsByNom: {}, connectedAgent: null, isManager: false };
  let allSignalements = [];
  let retoursBySig = {};
  let reloadTimer = null;

  const STATUT_COLORS = {
    "Nouveau": "#f59e0b",
    "Attribué": "#3b82f6",
    "En cours": "#9333ea",
    "Traité": "#16a34a",
    "Classé sans suite": "#64748b",
  };

  function isClosStatut(st) {
    return st === "Traité" || st === "Classé sans suite";
  }

  function populateAgentSelect() {
    const prev = agentEl.value;
    const opts = [
      '<option value="">Tous</option>',
      '<option value="__NON_ATTRIBUE__">Non attribués</option>',
    ];
    for (const ag of sessionCtx.agents) {
      opts.push('<option value="' + ag.id + '">' + escapeHtml(ag.Nom) + "</option>");
    }
    agentEl.innerHTML = opts.join("");
    agentEl.value = prev;
  }

  function getPeriodBounds() {
    const mode = periodeEl.value;
    const now = new Date();
    const yyyy = now.getFullYear();
    if (mode === "annee_courante") {
      return {
        minTs: Math.floor(Date.UTC(yyyy, 0, 1, 0, 0, 0) / 1000),
        maxTs: Math.floor(Date.UTC(yyyy, 11, 31, 23, 59, 59) / 1000),
      };
    }
    if (mode === "annee_precedente") {
      return {
        minTs: Math.floor(Date.UTC(yyyy - 1, 0, 1, 0, 0, 0) / 1000),
        maxTs: Math.floor(Date.UTC(yyyy - 1, 11, 31, 23, 59, 59) / 1000),
      };
    }
    if (mode === "30j" || mode === "90j") {
      const days = mode === "30j" ? 30 : 90;
      const nowTs = Math.floor(Date.now() / 1000);
      return { minTs: nowTs - days * 86400, maxTs: null };
    }
    if (mode === "perso") {
      const d1 = dateDebutEl.value ? parseDateToTs(dateDebutEl.value) : null;
      const d2 = dateFinEl.value ? parseDateToTs(dateFinEl.value) : null;
      return {
        minTs: d1 ? d1 - 43200 : null,
        maxTs: d2 ? d2 + 43199 : null,
      };
    }
    return { minTs: null, maxTs: null };
  }

  function getFilteredSignalements() {
    const bounds = getPeriodBounds();
    const dom = domaineEl.value;
    const prio = prioriteEl.value;
    const ag = agentEl.value;

    return allSignalements.filter((r) => {
      const ts = Number(r.Date_Heure_Reception);
      if (bounds.minTs !== null && (!Number.isFinite(ts) || ts < bounds.minTs)) return false;
      if (bounds.maxTs !== null && (!Number.isFinite(ts) || ts > bounds.maxTs)) return false;
      if (dom && r.Domaine_Activite !== dom) return false;
      if (prio && (r.Priorite || "Normale") !== prio) return false;
      if (ag === "__NON_ATTRIBUE__") {
        if (r.Agent_Attributaire && Number(r.Agent_Attributaire) > 0) return false;
      } else if (ag) {
        if (Number(r.Agent_Attributaire) !== Number(ag)) return false;
      }
      return true;
    });
  }

  function calcDelaiJours(tsStart, tsEnd) {
    const s = Number(tsStart);
    const e = Number(tsEnd);
    if (!Number.isFinite(s) || !Number.isFinite(e) || s <= 0 || e <= 0) return null;
    return Math.max(0, (e - s) / 86400);
  }

  function formatDelai(avgDays) {
    if (avgDays === null || !Number.isFinite(avgDays)) return "—";
    return avgDays.toFixed(1).replace(".", ",") + " j";
  }

  function computeAgentRows(filtered) {
    const buckets = {};
    const ensureBucket = (key, nom) => {
      if (!buckets[key]) {
        buckets[key] = {
          key,
          nom,
          confies: 0,
          attribues: 0,
          encours: 0,
          clos: 0,
          retours: 0,
          delaisAttr: [],
        };
      }
      return buckets[key];
    };

    for (const r of filtered) {
      const attrId = Number(r.Agent_Attributaire) || 0;
      const key = attrId > 0 ? String(attrId) : "0";
      const nom = attrId > 0 && sessionCtx.agentsById[attrId]
        ? sessionCtx.agentsById[attrId].Nom
        : (attrId > 0 ? ("Agent #" + attrId) : "Non attribués");
      const b = ensureBucket(key, nom);
      const st = r.Statut || "Nouveau";
      b.confies++;
      if (st === "Attribué") b.attribues++;
      if (st === "En cours") b.encours++;
      if (isClosStatut(st)) b.clos++;
      b.retours += (retoursBySig[r.id] || []).length;
      const dAttr = calcDelaiJours(r.Date_Heure_Reception, r.Date_Attribution);
      if (dAttr !== null) b.delaisAttr.push(dAttr);
    }

    const list = Object.values(buckets).sort((a, b) => {
      if (a.key === "0") return 1;
      if (b.key === "0") return -1;
      return b.confies - a.confies || a.nom.localeCompare(b.nom, "fr");
    });
    return list;
  }

  function renderDonutStatuts(filtered) {
    const total = filtered.length;
    if (total === 0) {
      chartStatutsEl.innerHTML = '<div style="color:#64748b;padding:18px 0;text-align:center;">Aucune donnée sur ce périmètre.</div>';
      return;
    }
    const counts = {};
    for (const st of CFG.statuts) counts[st] = 0;
    for (const r of filtered) {
      const st = r.Statut || "Nouveau";
      counts[st] = (counts[st] || 0) + 1;
    }

    const radius = 62;
    const circ = 2 * Math.PI * radius;
    let offset = 0;
    const circles = [];
    const legendRows = [];

    for (const st of Object.keys(counts)) {
      const c = counts[st];
      if (c <= 0 && !CFG.statuts.includes(st)) continue;
      const pct = total > 0 ? Math.round((c / total) * 100) : 0;
      const color = STATUT_COLORS[st] || "#005bb5";
      if (c > 0) {
        const dash = (c / total) * circ;
        circles.push(
          '<circle cx="90" cy="90" r="' + radius + '" fill="none" stroke="' + color + '" ' +
          'stroke-width="24" stroke-dasharray="' + dash.toFixed(2) + " " + circ.toFixed(2) + '" ' +
          'stroke-dashoffset="' + (-offset).toFixed(2) + '" transform="rotate(-90 90 90)"></circle>'
        );
        offset += dash;
      }
      legendRows.push(
        '<div class="stat-legend-row">' +
          '<span style="display:inline-flex;align-items:center;"><span class="stat-dot" style="background:' + color + ';"></span>' + escapeHtml(st) + "</span>" +
          "<span><strong>" + c + '</strong> <span style="color:#64748b;">(' + pct + " %)</span></span>" +
        "</div>"
      );
    }

    const svg =
      '<svg viewBox="0 0 180 180" width="165" height="165" role="img" aria-label="Répartition par statut">' +
        '<circle cx="90" cy="90" r="' + radius + '" fill="none" stroke="#f1f5f9" stroke-width="24"></circle>' +
        circles.join("") +
        '<text x="90" y="87" text-anchor="middle" font-size="22" font-weight="800" fill="#0f172a">' + total + "</text>" +
        '<text x="90" y="106" text-anchor="middle" font-size="11" fill="#64748b">dossiers</text>' +
      "</svg>";

    chartStatutsEl.innerHTML =
      '<div class="stat-donut-wrap">' +
        svg +
        '<div class="stat-legend">' + legendRows.join("") + "</div>" +
      "</div>";
  }

  function renderDomainesSvg(filtered) {
    const total = filtered.length;
    if (total === 0) {
      chartDomainesEl.innerHTML = '<div style="color:#64748b;padding:18px 0;text-align:center;">Aucune donnée sur ce périmètre.</div>';
      return;
    }
    const counts = {};
    for (const r of filtered) {
      const dom = r.Domaine_Activite || "Non renseigné";
      counts[dom] = (counts[dom] || 0) + 1;
    }
    const items = Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], "fr"));
    const maxVal = Math.max(1, items[0][1]);
    const rowH = 30;
    const height = Math.max(80, items.length * rowH + 8);
    const labelW = 195;
    const barMaxW = 190;

    const svgRows = items.map(([label, val], idx) => {
      const y = idx * rowH + 6;
      const barW = Math.max(4, Math.round((val / maxVal) * barMaxW));
      const pct = Math.round((val / total) * 100);
      const shortLbl = label.length > 28 ? label.slice(0, 27) + "…" : label;
      return (
        '<text x="0" y="' + (y + 14) + '" font-size="11.5" fill="#334155" font-weight="600">' + escapeHtml(shortLbl) + "</text>" +
        '<rect x="' + labelW + '" y="' + (y + 3) + '" width="' + barMaxW + '" height="14" rx="7" fill="#f1f5f9"></rect>' +
        '<rect x="' + labelW + '" y="' + (y + 3) + '" width="' + barW + '" height="14" rx="7" fill="#005bb5"></rect>' +
        '<text x="' + (labelW + barMaxW + 8) + '" y="' + (y + 14) + '" font-size="11.5" fill="#0f172a" font-weight="700">' + val + " (" + pct + "%)</text>"
      );
    }).join("");

    chartDomainesEl.innerHTML =
      '<svg viewBox="0 0 460 ' + height + '" width="100%" height="' + height + '" role="img" aria-label="Répartition par domaine">' +
        svgRows +
      "</svg>";
  }

  function renderMensuelSvg(filtered) {
    const byMonth = {};
    for (const r of filtered) {
      const ts = Number(r.Date_Heure_Reception);
      if (!Number.isFinite(ts) || ts <= 0) continue;
      const d = new Date(ts * 1000);
      if (Number.isNaN(d.getTime())) continue;
      const ym = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0");
      byMonth[ym] = (byMonth[ym] || 0) + 1;
    }
    const keys = Object.keys(byMonth).sort().slice(-12);
    if (!keys.length) {
      chartMensuelEl.innerHTML = '<div style="color:#64748b;padding:18px 0;text-align:center;">Aucune date de réception exploitable.</div>';
      return;
    }
    const maxVal = Math.max(1, ...keys.map((k) => byMonth[k]));
    const svgW = 460;
    const svgH = 190;
    const plotH = 135;
    const baseY = 155;
    const slotW = Math.floor((svgW - 24) / keys.length);
    const barW = Math.max(14, Math.min(34, slotW - 8));

    const bars = keys.map((ym, idx) => {
      const val = byMonth[ym];
      const h = Math.max(4, Math.round((val / maxVal) * plotH));
      const x = 12 + idx * slotW + Math.floor((slotW - barW) / 2);
      const y = baseY - h;
      const parts = ym.split("-");
      const lbl = parts[1] + "/" + parts[0].slice(2);
      return (
        '<rect x="' + x + '" y="' + y + '" width="' + barW + '" height="' + h + '" rx="4" fill="#3b82f6"></rect>' +
        '<text x="' + (x + barW / 2) + '" y="' + (y - 4) + '" text-anchor="middle" font-size="11" font-weight="700" fill="#0f172a">' + val + "</text>" +
        '<text x="' + (x + barW / 2) + '" y="' + (baseY + 15) + '" text-anchor="middle" font-size="10.5" fill="#64748b">' + escapeHtml(lbl) + "</text>"
      );
    }).join("");

    chartMensuelEl.innerHTML =
      '<svg viewBox="0 0 ' + svgW + " " + svgH + '" width="100%" height="190" role="img" aria-label="Évolution mensuelle">' +
        '<line x1="10" y1="' + baseY + '" x2="' + (svgW - 10) + '" y2="' + baseY + '" stroke="#cbd5e1" stroke-width="1"></line>' +
        bars +
      "</svg>";
  }

  function renderMiniBarSection(title, countsMap, color) {
    const entries = Object.entries(countsMap).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], "fr"));
    if (!entries.length) {
      return '<div style="margin-bottom:10px;"><strong style="font-size:12px;color:#475569;">' + escapeHtml(title) + '</strong><div style="color:#64748b;font-size:12px;margin-top:4px;">Aucune donnée.</div></div>';
    }
    const maxVal = Math.max(1, entries[0][1]);
    const rowsHtml = entries.map(([lbl, val]) => {
      const pctW = Math.max(4, Math.round((val / maxVal) * 100));
      return (
        '<div class="stat-bar-row">' +
          '<div class="stat-bar-head"><span>' + escapeHtml(lbl) + "</span><strong>" + val + "</strong></div>" +
          '<div class="stat-bar-track"><div class="stat-bar-fill" style="width:' + pctW + "%;background:" + color + ';"></div></div>' +
        "</div>"
      );
    }).join("");
    return (
      '<div style="margin-bottom:12px;">' +
        '<div style="font-size:12px;font-weight:700;color:#475569;margin-bottom:6px;">' + escapeHtml(title) + "</div>" +
        '<div class="stat-bar-list">' + rowsHtml + "</div>" +
      "</div>"
    );
  }

  function renderCanauxEtSuites(filtered) {
    const canaux = {};
    const suites = {};
    for (const r of filtered) {
      const c = r.Canal_Reception || "Non précisé";
      canaux[c] = (canaux[c] || 0) + 1;
      for (const ret of (retoursBySig[r.id] || [])) {
        if (ret.Suite_Donnee) {
          suites[ret.Suite_Donnee] = (suites[ret.Suite_Donnee] || 0) + 1;
        }
      }
    }
    chartCanauxSuitesEl.innerHTML =
      renderMiniBarSection("Canaux d'entrée", canaux, "#0ea5e9") +
      renderMiniBarSection("Suites données (retours)", suites, "#16a34a");
  }

  function renderAgentTable(filtered) {
    const rows = computeAgentRows(filtered);
    if (!rows.length) {
      agentTableBodyEl.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#64748b;padding:18px;">Aucun signalement dans cette sélection.</td></tr>';
      return;
    }

    let totConfies = 0;
    let totAttr = 0;
    let totEnc = 0;
    let totClos = 0;
    let totRet = 0;
    const allDelais = [];

    const bodyHtml = rows.map((row) => {
      totConfies += row.confies;
      totAttr += row.attribues;
      totEnc += row.encours;
      totClos += row.clos;
      totRet += row.retours;
      row.delaisAttr.forEach((d) => allDelais.push(d));

      const taux = row.confies > 0 ? Math.round((row.clos / row.confies) * 100) : 0;
      const avgDelai = row.delaisAttr.length
        ? row.delaisAttr.reduce((acc, x) => acc + x, 0) / row.delaisAttr.length
        : null;
      return (
        "<tr>" +
          "<td><strong>" + escapeHtml(row.nom) + "</strong></td>" +
          "<td>" + row.confies + "</td>" +
          "<td>" + row.attribues + "</td>" +
          "<td>" + row.encours + "</td>" +
          "<td>" + row.clos + "</td>" +
          "<td>" + taux + " %</td>" +
          "<td>" + row.retours + "</td>" +
          "<td>" + escapeHtml(formatDelai(avgDelai)) + "</td>" +
        "</tr>"
      );
    }).join("");

    const tauxGlobal = totConfies > 0 ? Math.round((totClos / totConfies) * 100) : 0;
    const delaiGlobal = allDelais.length ? allDelais.reduce((a, b) => a + b, 0) / allDelais.length : null;
    const totalRow =
      '<tr style="background:#f8fafc;font-weight:800;">' +
        "<td>Total sélection</td>" +
        "<td>" + totConfies + "</td>" +
        "<td>" + totAttr + "</td>" +
        "<td>" + totEnc + "</td>" +
        "<td>" + totClos + "</td>" +
        "<td>" + tauxGlobal + " %</td>" +
        "<td>" + totRet + "</td>" +
        "<td>" + escapeHtml(formatDelai(delaiGlobal)) + "</td>" +
      "</tr>";

    agentTableBodyEl.innerHTML = bodyHtml + totalRow;
  }

  function renderDashboard() {
    const isPerso = periodeEl.value === "perso";
    dateDebutWrapEl.classList.toggle("hidden", !isPerso);
    dateFinWrapEl.classList.toggle("hidden", !isPerso);

    const filtered = getFilteredSignalements();
    matchCountEl.textContent = filtered.length + " dossier(s)";

    let nClos = 0;
    let nUrgents = 0;
    const delaisAttr = [];
    const delaisTrait = [];

    for (const r of filtered) {
      const st = r.Statut || "Nouveau";
      const clos = isClosStatut(st);
      if (clos) nClos++;
      if (r.Priorite === "Urgente" && !clos) nUrgents++;

      const da = calcDelaiJours(r.Date_Heure_Reception, r.Date_Attribution);
      if (da !== null) delaisAttr.push(da);

      const rets = (retoursBySig[r.id] || []).slice().sort((a, b) => {
        return (Number(a.Date_Intervention) || a.id) - (Number(b.Date_Intervention) || b.id);
      });
      if (rets.length > 0) {
        const closingRet = rets.find((ret) => ret.Suite_Donnee && Number(ret.Date_Intervention) > 0);
        const targetRet = closingRet || rets[rets.length - 1];
        const dt = calcDelaiJours(r.Date_Heure_Reception, targetRet.Date_Intervention);
        if (dt !== null) delaisTrait.push(dt);
      }
    }

    const total = filtered.length;
    const tauxCloture = total > 0 ? Math.round((nClos / total) * 100) : 0;
    const avgAttr = delaisAttr.length ? delaisAttr.reduce((a, b) => a + b, 0) / delaisAttr.length : null;
    const avgTrait = delaisTrait.length ? delaisTrait.reduce((a, b) => a + b, 0) / delaisTrait.length : null;

    kpiTotalEl.textContent = String(total);
    kpiTotalSubEl.textContent = (total - nClos) + " actifs · " + nClos + " clos";
    kpiTauxClotureEl.textContent = tauxCloture + " %";
    kpiTauxSubEl.textContent = nClos + " / " + total + " dossiers clos";
    kpiUrgentsEl.textContent = String(nUrgents);
    kpiDelaiAttrEl.textContent = formatDelai(avgAttr);
    kpiDelaiAttrSubEl.textContent = delaisAttr.length + " dossier(s) datés";
    kpiDelaiTraitEl.textContent = formatDelai(avgTrait);
    kpiDelaiTraitSubEl.textContent = delaisTrait.length + " dossier(s) intervenus";

    renderDonutStatuts(filtered);
    renderDomainesSvg(filtered);
    renderMensuelSvg(filtered);
    renderCanauxEtSuites(filtered);
    renderAgentTable(filtered);
  }

  function exportStatsCsv() {
    const filtered = getFilteredSignalements();
    const rowsData = computeAgentRows(filtered);
    const headers = [
      "Agent attributaire",
      "Confiés",
      "Attribués",
      "En cours",
      "Traités ou clos",
      "Taux clôture (%)",
      "Retours saisis",
      "Délai moyen attribution (jours)",
    ];
    const rows = rowsData.map((r) => {
      const taux = r.confies > 0 ? Math.round((r.clos / r.confies) * 100) : 0;
      const avg = r.delaisAttr.length
        ? (r.delaisAttr.reduce((a, b) => a + b, 0) / r.delaisAttr.length).toFixed(1)
        : "";
      return [
        r.nom,
        String(r.confies),
        String(r.attribues),
        String(r.encours),
        String(r.clos),
        String(taux),
        String(r.retours),
        avg,
      ];
    });
    const csv = buildCsvUtf8Bom(headers, rows);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const today = toDatetimeLocalValue(new Date()).slice(0, 10);
    link.href = url;
    link.download = "statistiques_signalements_" + (CFG.csvPrefix || "service") + "_" + today + ".csv";
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
        btnExportCsvEl.classList.add("hidden");
        restrictedEl.classList.remove("hidden");
        return;
      }

      restrictedEl.classList.add("hidden");
      mainAppEl.classList.remove("hidden");
      btnExportCsvEl.classList.remove("hidden");
      populateAgentSelect();

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

      showBanner(bannerEl, null);
      renderDashboard();
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

  [periodeEl, dateDebutEl, dateFinEl, domaineEl, prioriteEl, agentEl].forEach((el) => {
    el.addEventListener("change", renderDashboard);
  });

  btnResetEl.addEventListener("click", () => {
    periodeEl.value = "toutes";
    dateDebutEl.value = "";
    dateFinEl.value = "";
    domaineEl.value = "";
    prioriteEl.value = "";
    agentEl.value = "";
    renderDashboard();
  });

  btnRefreshEl.addEventListener("click", loadData);
  btnPrintEl.addEventListener("click", () => window.print());
  btnExportCsvEl.addEventListener("click", exportStatsCsv);

  if (typeof grist.onRecords === "function") {
    grist.onRecords(() => scheduleReload());
  }

  loadData();
})();
"""

    return {
        "_html": envelopper_document_html("Statistiques", body_html, extra_css=STATISTIQUES_CSS),
        "_js": f"const CFG = {cfg_json};\n{COMMON_JS_HELPERS}\n{js_body}".strip(),
    }


__all__ = ["generer_widget_statistiques"]
