# -*- coding: utf-8 -*-
"""Générateur du widget HTML d'accueil « 🛡️ Espace encadrement » (Lot 3)."""

import html
import json

from config import DOC_ID, DOC_URL, SERVICE_NOM
from widgets.commun import COMMON_JS_HELPERS, envelopper_document_html

ESPACE_ENCADREMENT_CSS = """
.hub-kpis {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}
.hub-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}
@media (max-width: 820px) {
  .hub-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .hub-links { grid-template-columns: 1fr; }
}
.hub-kpi-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px 16px;
}
.hub-kpi-val {
  font-size: 26px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.1;
}
.hub-kpi-lbl {
  margin-top: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
}
.hub-restricted {
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
  border-radius: 10px;
  padding: 24px 18px;
  text-align: center;
  font-weight: 600;
}
"""


def generer_widget_espace_encadrement(gestion_agents_view_id=None):
    """Retourne {_html, _js} pour le tableau d'accueil « 🛡️ Espace encadrement »."""
    base_doc_url = DOC_URL
    service_echappe = html.escape(SERVICE_NOM)
    ga_page_id = int(gestion_agents_view_id) if gestion_agents_view_id else None
    if ga_page_id:
        ga_url = f"{base_doc_url}/p/{ga_page_id}"
        ga_btn_html = (
            f'<a class="sig-btn" id="linkHubAgents" data-page-id="{ga_page_id}" '
            f'href="{ga_url}" target="_top">Gérer les agents</a>'
        )
    else:
        ga_url = ""
        ga_btn_html = '<span style="font-size:12px;color:#64748b;">Accessible depuis le menu latéral encadrement.</span>'

    body_html = f"""  <div class="sig-wrap">
    <div class="sig-header">
      <div>
        <h1 class="sig-title">🛡️ Espace encadrement</h1>
        <p class="sig-subtitle">Synthèse instantanée et accès direct aux outils de pilotage, statistiques et annuaire.</p>
      </div>
      <div style="display:flex;align-items:center;gap:8px;">
        <span class="sig-badge badge-info" id="hubSessionBadge">Vérification...</span>
        <button type="button" class="sig-btn" id="btnHubRefresh">🔄 Actualiser</button>
      </div>
    </div>

    <div id="hubRestricted" class="hub-restricted hidden">
      Accès réservé à l'encadrement.
    </div>

    <div id="hubBanner" class="sig-banner" role="status"></div>

    <div id="hubMainApp" class="hidden">
      <div class="hub-kpis">
        <div class="hub-kpi-card">
          <div class="hub-kpi-val" id="hubNouveaux" style="color:#b45309;">0</div>
          <div class="hub-kpi-lbl">Nouveaux à attribuer</div>
        </div>
        <div class="hub-kpi-card">
          <div class="hub-kpi-val" id="hubUrgents" style="color:#b91c1c;">0</div>
          <div class="hub-kpi-lbl">Urgents actifs</div>
        </div>
        <div class="hub-kpi-card">
          <div class="hub-kpi-val" id="hubEnCours" style="color:#005bb5;">0</div>
          <div class="hub-kpi-lbl">Attribués et en cours</div>
        </div>
        <div class="hub-kpi-card">
          <div class="hub-kpi-val" id="hubClos" style="color:#166534;">0</div>
          <div class="hub-kpi-lbl">Traités / clos</div>
        </div>
      </div>

      <div class="hub-links">
        <div class="sig-card" style="margin-bottom:0;">
          <h2>🎯 Pilotage et attribution</h2>
          <p style="color:#475569;margin:0 0 12px;">Consulter l'ensemble des signalements, filtrer, attribuer aux agents, rédiger les consignes, imprimer et exporter en CSV.</p>
          <a class="sig-btn sig-btn-primary" id="linkHubPilotage" data-page-id="6" href="{base_doc_url}/p/6" target="_top">Ouvrir le pilotage</a>
        </div>
        <div class="sig-card" style="margin-bottom:0;">
          <h2>📊 Statistiques</h2>
          <p style="color:#475569;margin:0 0 12px;">Consulter la répartition par statut, domaine d'activité, canal de réception, les délais moyens et le bilan par agent.</p>
          <a class="sig-btn" id="linkHubStats" data-page-id="8" href="{base_doc_url}/p/8" target="_top">Ouvrir les statistiques</a>
        </div>
        <div class="sig-card" style="margin-bottom:0;">
          <h2>👥 Gestion des agents</h2>
          <p style="color:#475569;margin:0 0 12px;">Consulter l'annuaire du {service_echappe}, ajouter ou modifier un agent sans toucher aux grilles brutes ni aux droits.</p>
          {ga_btn_html}
        </div>
      </div>
    </div>
  </div>"""

    cfg_json = json.dumps(
        {
            "docId": DOC_ID,
            "baseDocUrl": base_doc_url,
            "pilotagePageId": 6,
            "statsPageId": 8,
            "gestionAgentsPageId": ga_page_id,
            "pilotageUrl": f"{base_doc_url}/p/6",
            "statsUrl": f"{base_doc_url}/p/8",
            "gestionAgentsUrl": ga_url,
        },
        ensure_ascii=False,
    )

    js_body = r"""
(function () {
  grist.ready({ requiredAccess: "full" });

  const sessionBadgeEl = document.getElementById("hubSessionBadge");
  const btnRefreshEl = document.getElementById("btnHubRefresh");
  const restrictedEl = document.getElementById("hubRestricted");
  const bannerEl = document.getElementById("hubBanner");
  const mainAppEl = document.getElementById("hubMainApp");

  const nouveauxEl = document.getElementById("hubNouveaux");
  const urgentsEl = document.getElementById("hubUrgents");
  const enCoursEl = document.getElementById("hubEnCours");
  const closEl = document.getElementById("hubClos");

  let resolvedBaseUrl = CFG.baseDocUrl;

  function extractDocBaseFromUrl(rawUrl) {
    if (!rawUrl) return "";
    const clean = String(rawUrl).split("#")[0].split("?")[0].replace(/\/+$/, "");
    const withoutPage = clean.replace(/\/p\/\d+$/, "");
    if (/^https?:\/\/.+\/o\/[^/]+\/[^/]+\/[^/]+$/.test(withoutPage) || /^https?:\/\/.+\/doc\/[^/]+$/.test(withoutPage)) {
      return withoutPage;
    }
    return "";
  }

  async function resolveDocBaseUrl() {
    try {
      if (window.top && window.top.location && window.top.location.href) {
        const topBase = extractDocBaseFromUrl(window.top.location.href);
        if (topBase) return topBase;
      }
    } catch (e) {}

    const refBase = extractDocBaseFromUrl(document.referrer);
    if (refBase) return refBase;

    try {
      const tokenInfo = await getFreshAccessToken(true, false);
      const match = tokenInfo && tokenInfo.baseUrl
        ? String(tokenInfo.baseUrl).match(/^(https?:\/\/.+?)\/api\/docs\/([^/?#]+)/)
        : null;
      if (match) {
        if (CFG.docId && match[2] === CFG.docId && CFG.baseDocUrl) {
          return CFG.baseDocUrl;
        }
        return match[1] + "/doc/" + match[2];
      }
    } catch (e) {}

    return CFG.baseDocUrl;
  }

  function applyResolvedNavLinks(baseUrl) {
    resolvedBaseUrl = String(baseUrl || CFG.baseDocUrl).replace(/\/+$/, "");
    document.querySelectorAll("a[data-page-id]").forEach((linkEl) => {
      const pageId = linkEl.getAttribute("data-page-id");
      if (!pageId) return;
      linkEl.setAttribute("href", resolvedBaseUrl + "/p/" + pageId);
      linkEl.setAttribute("target", "_top");
    });
  }

  document.querySelectorAll("a[data-page-id]").forEach((linkEl) => {
    linkEl.addEventListener("click", (ev) => {
      const pageId = linkEl.getAttribute("data-page-id");
      if (!pageId) return;
      const targetUrl = resolvedBaseUrl.replace(/\/+$/, "") + "/p/" + pageId;
      linkEl.setAttribute("href", targetUrl);
      if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey || ev.button !== 0) return;
      try {
        if (window.top && window.top !== window) {
          window.top.location.href = targetUrl;
          ev.preventDefault();
        }
      } catch (e) {
        // Repli natif via target="_top"
      }
    });
  });

  async function loadHub() {
    try {
      applyResolvedNavLinks(await resolveDocBaseUrl());
      const ctx = await loadSessionContext();
      sessionBadgeEl.textContent = ctx.connectedAgent ? ("Connecté : " + ctx.connectedAgent.Nom) : "Session active";
      if (!ctx.isManager) {
        mainAppEl.classList.add("hidden");
        restrictedEl.classList.remove("hidden");
        return;
      }
      restrictedEl.classList.add("hidden");
      mainAppEl.classList.remove("hidden");

      const rawSig = await grist.docApi.fetchTable("Signalements");
      const rows = tableToRows(rawSig);
      let nNouveaux = 0;
      let nUrgents = 0;
      let nEnCours = 0;
      let nClos = 0;
      for (const r of rows) {
        const st = r.Statut || "Nouveau";
        const clos = st === "Traité" || st === "Classé sans suite";
        if (st === "Nouveau") nNouveaux++;
        if (st === "Attribué" || st === "En cours") nEnCours++;
        if (clos) nClos++;
        if (r.Priorite === "Urgente" && !clos) nUrgents++;
      }
      nouveauxEl.textContent = String(nNouveaux);
      urgentsEl.textContent = String(nUrgents);
      enCoursEl.textContent = String(nEnCours);
      closEl.textContent = String(nClos);
      showBanner(bannerEl, null);
    } catch (err) {
      showBanner(bannerEl, formatGristError(err), "err");
    }
  }

  btnRefreshEl.addEventListener("click", loadHub);
  if (typeof grist.onRecords === "function") {
    grist.onRecords(() => loadHub());
  }
  loadHub();
})();
"""

    return {
        "_html": envelopper_document_html("Espace encadrement", body_html, extra_css=ESPACE_ENCADREMENT_CSS),
        "_js": f"const CFG = {cfg_json};\n{COMMON_JS_HELPERS}\n{js_body}".strip(),
    }


__all__ = ["generer_widget_espace_encadrement"]
