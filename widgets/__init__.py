# -*- coding: utf-8 -*-
"""Widgets HTML autonomes pour le registre des signalements (Grist)."""

from widgets.commun import (
    BASE_CSS,
    CHOIX_CANAL,
    CHOIX_DEMARCHE,
    CHOIX_DOMAINE,
    CHOIX_ENCADRANT,
    CHOIX_PRIORITE,
    CHOIX_STATUT,
    CHOIX_SUITE,
    COMMON_JS_HELPERS,
    CUSTOM_WIDGET_BUILDER_URL,
    GRIST_PLUGIN_API_URL,
    PRINT_CSS,
    construire_options_custom_widget,
    envelopper_document_html,
)
from widgets.espace_encadrement_html import generer_widget_espace_encadrement
from widgets.gestion_agents_html import generer_widget_gestion_agents
from widgets.mes_dossiers_html import generer_widget_mes_dossiers
from widgets.nouveau_signalement_html import generer_widget_nouveau_signalement
from widgets.pilotage_html import generer_widget_pilotage
from widgets.statistiques_html import generer_widget_statistiques

__all__ = [
    "BASE_CSS",
    "CHOIX_CANAL",
    "CHOIX_DEMARCHE",
    "CHOIX_DOMAINE",
    "CHOIX_ENCADRANT",
    "CHOIX_PRIORITE",
    "CHOIX_STATUT",
    "CHOIX_SUITE",
    "COMMON_JS_HELPERS",
    "CUSTOM_WIDGET_BUILDER_URL",
    "GRIST_PLUGIN_API_URL",
    "PRINT_CSS",
    "construire_options_custom_widget",
    "envelopper_document_html",
    "generer_widget_espace_encadrement",
    "generer_widget_gestion_agents",
    "generer_widget_mes_dossiers",
    "generer_widget_nouveau_signalement",
    "generer_widget_pilotage",
    "generer_widget_statistiques",
]
