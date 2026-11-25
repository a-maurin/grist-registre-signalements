# -*- coding: utf-8 -*-
"""
Configuration complète des colonnes, options visuelles, choix et formules
pour les tables du registre des signalements dans Grist.
"""

import json
import requests
from config import (
    CHOIX_ENCADRANT,
    DOC_ID,
    DOC_URL_PILOTAGE,
    EMAILS_GESTIONNAIRES,
    ENCADRANT_PAR_DEFAUT,
)
from creer_registre_signalements import get_grist_credentials


def configurer_colonnes():
    api_url, api_key = get_grist_credentials()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 1. Récupération des IDs des colonnes pour les liaisons
    r_cols = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Tables_column/records", headers=headers)
    r_cols.raise_for_status()
    r_tables = requests.get(f"{api_url}/docs/{DOC_ID}/tables/_grist_Tables/records", headers=headers)
    r_tables.raise_for_status()
    tables_ref = {t["fields"]["tableId"]: t["id"] for t in r_tables.json().get("records", [])}
    cols_map = {}
    for c in r_cols.json().get("records", []):
        f = c["fields"]
        table_ref = f.get("parentId")
        col_id = f.get("colId")
        cols_map[(table_ref, col_id)] = c["id"]

    col_nom_agent_id = cols_map[(tables_ref["Referentiel_Agents"], "Nom")]
    col_num_sig_id = cols_map[(tables_ref["Signalements"], "Numero_Signalement")]

    # Définition des listes de choix et styles
    CHOIX_CANAL = ["Appel téléphonique", "Courriel", "Courrier postal", "Accueil physique", "Constat direct", "Autre"]
    CHOIX_DOMAINE = [
        "Eau et milieux aquatiques",
        "Espèces protégées et biodiversité",
        "Chasse et faune sauvage",
        "Pêche",
        "Forêt et espaces naturels",
        "Déchets et pollutions",
        "Autre"
    ]
    CHOIX_PRIORITE = ["Normale", "Urgente", "Faible"]
    OPTIONS_PRIORITE = {
        "choiceOptions": {
            "Normale": {"fillColor": "#64B5F6", "textColor": "#FFFFFF", "fontBold": True},
            "Urgente": {"fillColor": "#E53935", "textColor": "#FFFFFF", "fontBold": True},
            "Faible": {"fillColor": "#B0BEC5", "textColor": "#000000", "fontBold": False}
        }
    }
    CHOIX_STATUT = ["Nouveau", "Attribué", "En cours", "Traité", "Classé sans suite"]
    OPTIONS_STATUT = {
        "choiceOptions": {
            "Nouveau": {"fillColor": "#FFB74D", "textColor": "#000000", "fontBold": True},
            "Attribué": {"fillColor": "#4FC3F7", "textColor": "#000000", "fontBold": True},
            "En cours": {"fillColor": "#BA68C8", "textColor": "#FFFFFF", "fontBold": True},
            "Traité": {"fillColor": "#81C784", "textColor": "#000000", "fontBold": True},
            "Classé sans suite": {"fillColor": "#CFD8DC", "textColor": "#000000", "fontBold": False}
        }
    }
    CHOIX_DEMARCHE = [
        "Contrôle de terrain",
        "Prise de contact / audition",
        "Rappel à la loi",
        "Constat d'infraction",
        "Transmission à un tiers",
        "Autre"
    ]
    CHOIX_SUITE = [
        "Procès-verbal d'infraction",
        "Rapport de manquement administratif",
        "Régularisation",
        "Classement sans suite",
        "Transmission à un autre service",
        "Autre"
    ]
    CHOIX_ROLE = ["Agent", "Gestionnaire"]
    OPTIONS_ROLE = {
        "choiceOptions": {
            "Agent": {"fillColor": "#CFD8DC", "textColor": "#000000", "fontBold": False},
            "Gestionnaire": {"fillColor": "#4FC3F7", "textColor": "#000000", "fontBold": True},
        }
    }

    FORMULE_NUMERO = 'f"{(rec.Date_Heure_Reception or NOW()).year}-{rec.id:04d}"'
    FORMULE_AGENT_CONNECTE = '''agent = Referentiel_Agents.lookupOne(Email=user.Email)
return agent.id if agent else None'''

    FORMULE_MAILTO = '''import urllib.parse
if not rec.Agent_Attributaire or not rec.Agent_Attributaire.Email:
  return ""
email = rec.Agent_Attributaire.Email
num = rec.Numero_Signalement
commune = rec.Commune or ""
date_str = rec.Date_Heure_Reception.strftime("%d/%m/%Y %H:%M") if rec.Date_Heure_Reception else "Non précisée"
sujet = f"[Signalement {num}] Attribution de mission - {commune}"
corps = f"""Bonjour {rec.Agent_Attributaire.Nom},

Un nouveau signalement vous a été attribué par la hiérarchie.

=== FICHE DE SIGNALEMENT {num} ===
- Date de réception : {date_str}
- Agent récepteur : {rec.Agent_Recepteur.Nom if rec.Agent_Recepteur else 'Non précisé'}
- Canal d'entrée : {rec.Canal_Reception or 'Non précisé'}
- Requérant : {rec.Requerant_Nom or 'Anonyme / Non précisé'} ({rec.Requerant_Contact or 'Pas de coordonnées'})
- Localisation : {commune} - {rec.Lieu_Dit or ''}
- Domaine : {rec.Domaine_Activite or 'Non précisé'}

DESCRIPTION DES FAITS :
{rec.Description_Faits or 'Aucune description'}

CONSIGNES DE LA HIÉRARCHIE :
- Priorité : {rec.Priorite or 'Normale'}
- Consignes : {rec.Consignes_Hierarchie or 'Aucune consigne particulière'}

=== RETOUR D'INTERVENTION ===
Une fois vos vérifications et diligences effectuées, merci de bien vouloir renseigner le formulaire de retour d'intervention en sélectionnant le dossier {num}.

Bien cordialement."""

params = urllib.parse.urlencode({'subject': sujet, 'body': corps}, quote_via=urllib.parse.quote)
return f"mailto:{email}?{params}"'''

    encadrant_defaut_json = json.dumps(ENCADRANT_PAR_DEFAUT, ensure_ascii=False)
    FORMULE_MAILTO_ENCADRANT = f'''import urllib.parse
val = rec.Encadrant_A_Alerter
if isinstance(val, str) and val:
  destinataire = Referentiel_Agents.lookupOne(Nom=val)
elif hasattr(val, "Email"):
  destinataire = val
elif isinstance(val, int) and val:
  destinataire = Referentiel_Agents.lookupOne(id=val)
else:
  destinataire = Referentiel_Agents.lookupOne(Nom={encadrant_defaut_json})
if not destinataire or not destinataire.Email:
  destinataire = Referentiel_Agents.lookupOne(Nom={encadrant_defaut_json})
if not destinataire or not destinataire.Email:
  return ""
email = destinataire.Email
num = rec.Numero_Signalement
commune = rec.Commune or "Non précisée"
date_str = rec.Date_Heure_Reception.strftime("%d/%m/%Y %H:%M") if rec.Date_Heure_Reception else "Non précisée"
sujet = f"[Signalement {{num}}] Nouveau signalement à attribuer - {{commune}}"
corps = f"""Bonjour {{destinataire.Nom}},

Un nouveau signalement a été enregistré dans le registre et est en attente d'attribution de mission.

=== FICHE DE SIGNALEMENT {{num}} ===
- Date de réception : {{date_str}}
- Agent récepteur : {{rec.Agent_Recepteur.Nom if rec.Agent_Recepteur else 'Non précisé'}}
- Canal d'entrée : {{rec.Canal_Reception or 'Non précisé'}}
- Requérant : {{rec.Requerant_Nom or 'Anonyme / Non précisé'}} ({{rec.Requerant_Contact or 'Pas de coordonnées'}})
- Localisation : {{commune}} - {{rec.Lieu_Dit or ''}}
- Domaine : {{rec.Domaine_Activite or 'Non précisé'}}

DESCRIPTION DES FAITS :
{{rec.Description_Faits or 'Aucune description'}}

=== ACCÈS AU DOSSIER DANS GRIST ===
Pour consulter la fiche complète et procéder à l'attribution de la mission :
{DOC_URL_PILOTAGE}

Bien cordialement."""

params = urllib.parse.urlencode({{'subject': sujet, 'body': corps}}, quote_via=urllib.parse.quote)
return f"mailto:{{email}}?{{params}}"'''

    DERNIER_RETOUR = """retours = list(Retours_Actions.lookupRecords(Signalement=rec.id, order_by="id"))
r = retours[-1] if retours else None
"""
    FORMULE_RETOUR_DATE = DERNIER_RETOUR + "return r.Date_Intervention if r else None"
    FORMULE_RETOUR_DEMARCHE = DERNIER_RETOUR + 'return r.Type_Demarche if r else ""'
    FORMULE_RETOUR_CR = DERNIER_RETOUR + 'return r.Compte_Rendu if r else ""'
    FORMULE_RETOUR_SUITE = DERNIER_RETOUR + 'return r.Suite_Donnee if r else ""'
    FORMULE_RETOUR_PJ = DERNIER_RETOUR + "return r.Pieces_Jointes if r else None"

    FORMULE_A_UN_RETOUR = "return len(Retours_Actions.lookupRecords(Signalement=rec.id)) > 0"

    FORMULE_STATUT = '''if rec.Statut_Manuel:
  return rec.Statut_Manuel
retours = Retours_Actions.lookupRecords(Signalement=rec.id)
if any(r.Suite_Donnee for r in retours):
  return "Traité"
if len(retours) > 0:
  return "En cours"
if rec.Agent_Attributaire:
  return "Attribué"
return "Nouveau"'''

    colonne_statut_manuel = [] if (tables_ref["Signalements"], "Statut_Manuel") in cols_map else [
        ["AddColumn", "Signalements", "Statut_Manuel", {
            "type": "Choice",
            "isFormula": False,
            "label": "Statut imposé (hiérarchie)",
            "widgetOptions": json.dumps({
                "widget": "Choice",
                "choices": CHOIX_STATUT,
                "choiceOptions": OPTIONS_STATUT["choiceOptions"]
            })
        }]
    ]

    colonne_est_mon_dossier = [] if (tables_ref["Signalements"], "Est_Mon_Dossier") in cols_map else [
        ["AddColumn", "Signalements", "Est_Mon_Dossier", {
            "type": "Text",
            "isFormula": True,
            "formula": 'return "OUI"',
            "label": "Est mon dossier"
        }]
    ]

    colonne_encadrant = [] if (tables_ref["Signalements"], "Encadrant_A_Alerter") in cols_map else [
        ["AddColumn", "Signalements", "Encadrant_A_Alerter", {
            "type": "Choice",
            "isFormula": False,
            "formula": f"return {encadrant_defaut_json}",
            "label": "Encadrant à alerter",
            "widgetOptions": json.dumps({"widget": "Choice", "choices": CHOIX_ENCADRANT})
        }]
    ]

    colonne_action_alerter = [] if (tables_ref["Signalements"], "Action_Alerter_Encadrant") in cols_map else [
        ["AddColumn", "Signalements", "Action_Alerter_Encadrant", {
            "type": "Text",
            "isFormula": True,
            "formula": FORMULE_MAILTO_ENCADRANT,
            "label": "Alerter l'encadrant (courriel)",
            "widgetOptions": json.dumps({"widget": "HyperLink"})
        }]
    ]

    colonne_est_connecte = [] if (tables_ref["Referentiel_Agents"], "Est_Connecte") in cols_map else [
        ["AddColumn", "Referentiel_Agents", "Est_Connecte", {
            "type": "Bool",
            "isFormula": True,
            "formula": "return True",
            "label": "Est connecté",
            "untieColIdFromLabel": True,
        }]
    ]

    colonne_role = [] if (tables_ref["Referentiel_Agents"], "Role") in cols_map else [
        ["AddColumn", "Referentiel_Agents", "Role", {
            "type": "Choice",
            "isFormula": False,
            "formula": 'return "Agent"',
            "recalcWhen": 0,
            "recalcDeps": None,
            "label": "Rôle",
            "untieColIdFromLabel": True,
            "widgetOptions": json.dumps({
                "widget": "Choice",
                "choices": CHOIX_ROLE,
                "choiceOptions": OPTIONS_ROLE["choiceOptions"],
            }),
        }]
    ]

    colonne_agent_attr_id = [] if (tables_ref["Retours_Actions"], "Agent_Attributaire_Id") in cols_map else [
        ["AddColumn", "Retours_Actions", "Agent_Attributaire_Id", {
            "type": "Int",
            "isFormula": True,
            "formula": "return rec.Signalement.Agent_Attributaire.id if rec.Signalement and rec.Signalement.Agent_Attributaire else 0",
            "label": "ID agent attributaire du dossier",
            "untieColIdFromLabel": True,
        }]
    ]

    actions = [
        # Table Signalements
        ["ModifyColumn", "Signalements", "Numero_Signalement", {
            "untieColIdFromLabel": True,
            "label": "N° Signalement",
            "isFormula": False,
            "formula": FORMULE_NUMERO,
            "recalcWhen": 0,
            "recalcDeps": None
        }],
        ["ModifyColumn", "Signalements", "Date_Heure_Reception", {
            "untieColIdFromLabel": True,
            "label": "Date et heure de réception",
            "widgetOptions": json.dumps({"widget": "DateTime", "dateFormat": "DD/MM/YYYY", "timeFormat": "HH:mm"})
        }],
        ["ModifyColumn", "Signalements", "Agent_Recepteur", {
            "untieColIdFromLabel": True,
            "label": "Agent récepteur",
            "visibleCol": col_nom_agent_id
        }],
        ["ModifyColumn", "Signalements", "Canal_Reception", {
            "untieColIdFromLabel": True,
            "label": "Canal d'entrée",
            "widgetOptions": json.dumps({"widget": "Choice", "choices": CHOIX_CANAL})
        }],
        ["ModifyColumn", "Signalements", "Requerant_Nom", {"untieColIdFromLabel": True, "label": "Identité du requérant"}],
        ["ModifyColumn", "Signalements", "Requerant_Contact", {"untieColIdFromLabel": True, "label": "Coordonnées de contact"}],
        ["ModifyColumn", "Signalements", "Commune", {"untieColIdFromLabel": True, "label": "Commune"}],
        ["ModifyColumn", "Signalements", "Lieu_Dit", {"untieColIdFromLabel": True, "label": "Lieu-dit / Détail localisation"}],
        ["ModifyColumn", "Signalements", "Domaine_Activite", {
            "untieColIdFromLabel": True,
            "label": "Domaine d'activité",
            "widgetOptions": json.dumps({"widget": "Choice", "choices": CHOIX_DOMAINE})
        }],
        ["ModifyColumn", "Signalements", "Description_Faits", {"untieColIdFromLabel": True, "label": "Description des faits signalés"}],
        ["ModifyColumn", "Signalements", "Pieces_Jointes", {"untieColIdFromLabel": True, "label": "Pièces jointes initiales"}],
        *colonne_encadrant,
        *colonne_action_alerter,
        ["ModifyColumn", "Signalements", "Encadrant_A_Alerter", {
            "type": "Choice",
            "untieColIdFromLabel": True,
            "label": "Encadrant à alerter",
            "isFormula": False,
            "formula": f"return {encadrant_defaut_json}",
            "recalcWhen": 0,
            "recalcDeps": None,
            "widgetOptions": json.dumps({"widget": "Choice", "choices": CHOIX_ENCADRANT})
        }],
        ["ModifyColumn", "Signalements", "Action_Alerter_Encadrant", {
            "untieColIdFromLabel": True,
            "label": "Alerter l'encadrant (courriel)",
            "isFormula": True,
            "formula": FORMULE_MAILTO_ENCADRANT,
            "widgetOptions": json.dumps({"widget": "HyperLink"})
        }],

        # Attribution
        ["ModifyColumn", "Signalements", "Agent_Attributaire", {
            "untieColIdFromLabel": True,
            "label": "Agent attributaire",
            "visibleCol": col_nom_agent_id
        }],
        ["ModifyColumn", "Signalements", "Date_Attribution", {
            "untieColIdFromLabel": True,
            "label": "Date d'attribution",
            "widgetOptions": json.dumps({"widget": "Date", "dateFormat": "DD/MM/YYYY"})
        }],
        ["ModifyColumn", "Signalements", "Priorite", {
            "untieColIdFromLabel": True,
            "label": "Priorité",
            "widgetOptions": json.dumps({
                "widget": "Choice",
                "choices": CHOIX_PRIORITE,
                "choiceOptions": OPTIONS_PRIORITE["choiceOptions"]
            })
        }],
        ["ModifyColumn", "Signalements", "Consignes_Hierarchie", {"untieColIdFromLabel": True, "label": "Consignes de la hiérarchie"}],
        *colonne_statut_manuel,
        *colonne_est_mon_dossier,
        ["ModifyColumn", "Signalements", "Statut", {
            "untieColIdFromLabel": True,
            "label": "Statut du dossier",
            "isFormula": True,
            "formula": FORMULE_STATUT,
            "widgetOptions": json.dumps({
                "widget": "Choice",
                "choices": CHOIX_STATUT,
                "choiceOptions": OPTIONS_STATUT["choiceOptions"]
            })
        }],
        ["ModifyColumn", "Signalements", "Action_Notifier", {
            "untieColIdFromLabel": True,
            "label": "Envoyer fiche (courriel)",
            "isFormula": True,
            "formula": FORMULE_MAILTO,
            "widgetOptions": json.dumps({"widget": "HyperLink"})
        }],

        # Consolidation du retour
        ["ModifyColumn", "Signalements", "Retour_Date_Intervention", {
            "untieColIdFromLabel": True,
            "label": "Date de l'action / intervention",
            "isFormula": True,
            "formula": FORMULE_RETOUR_DATE,
            "widgetOptions": json.dumps({"widget": "Date", "dateFormat": "DD/MM/YYYY"})
        }],
        ["ModifyColumn", "Signalements", "Retour_Type_Demarche", {
            "untieColIdFromLabel": True,
            "label": "Type d'action réalisée",
            "isFormula": True,
            "formula": FORMULE_RETOUR_DEMARCHE
        }],
        ["ModifyColumn", "Signalements", "Retour_Compte_Rendu", {
            "untieColIdFromLabel": True,
            "label": "Compte-rendu de l'agent",
            "isFormula": True,
            "formula": FORMULE_RETOUR_CR
        }],
        ["ModifyColumn", "Signalements", "Retour_Suite_Donnee", {
            "untieColIdFromLabel": True,
            "label": "Suite administrative ou judiciaire",
            "isFormula": True,
            "formula": FORMULE_RETOUR_SUITE
        }],
        ["ModifyColumn", "Signalements", "Retour_Pieces_Jointes", {
            "untieColIdFromLabel": True,
            "label": "Pièces jointes de clôture",
            "isFormula": True,
            "formula": FORMULE_RETOUR_PJ
        }],
        ["ModifyColumn", "Signalements", "A_Un_Retour", {
            "untieColIdFromLabel": True,
            "label": "Retour effectué",
            "isFormula": True,
            "formula": FORMULE_A_UN_RETOUR
        }],
        ["ModifyColumn", "Signalements", "Est_Mon_Dossier", {
            "untieColIdFromLabel": True,
            "label": "Est mon dossier",
            "isFormula": True,
            "formula": 'return "OUI"'
        }],

        # Table Retours_Actions
        ["ModifyColumn", "Retours_Actions", "Signalement", {
            "untieColIdFromLabel": True,
            "label": "Dossier de signalement concerné",
            "visibleCol": col_num_sig_id
        }],
        ["ModifyColumn", "Retours_Actions", "Agent_Intervenant", {
            "untieColIdFromLabel": True,
            "label": "Agent",
            "visibleCol": col_nom_agent_id,
            "isFormula": False,
            "formula": FORMULE_AGENT_CONNECTE,
            "recalcWhen": 0,
            "recalcDeps": None
        }],
        ["ModifyColumn", "Retours_Actions", "Date_Intervention", {
            "untieColIdFromLabel": True,
            "label": "Date de l'intervention / démarche",
            "widgetOptions": json.dumps({"widget": "Date", "dateFormat": "DD/MM/YYYY"})
        }],
        ["ModifyColumn", "Retours_Actions", "Type_Demarche", {
            "untieColIdFromLabel": True,
            "label": "Nature de la démarche",
            "widgetOptions": json.dumps({"widget": "Choice", "choices": CHOIX_DEMARCHE})
        }],
        ["ModifyColumn", "Retours_Actions", "Compte_Rendu", {
            "untieColIdFromLabel": True,
            "label": "Compte-rendu des constatations"
        }],
        ["ModifyColumn", "Retours_Actions", "Suite_Donnee", {
            "untieColIdFromLabel": True,
            "label": "Suite donnée",
            "widgetOptions": json.dumps({"widget": "Choice", "choices": CHOIX_SUITE})
        }],
        ["ModifyColumn", "Retours_Actions", "Pieces_Jointes", {
            "untieColIdFromLabel": True,
            "label": "Photographies et pièces justificatives"
        }],
        *colonne_agent_attr_id,
        ["ModifyColumn", "Retours_Actions", "Agent_Attributaire_Id", {
            "untieColIdFromLabel": True,
            "label": "ID agent attributaire du dossier",
            "type": "Int",
            "isFormula": True,
            "formula": "return rec.Signalement.Agent_Attributaire.id if rec.Signalement and rec.Signalement.Agent_Attributaire else 0",
        }],

        # Table Referentiel_Agents
        *colonne_est_connecte,
        ["ModifyColumn", "Referentiel_Agents", "Est_Connecte", {
            "untieColIdFromLabel": True,
            "label": "Est connecté",
            "type": "Bool",
            "isFormula": True,
            "formula": "return True",
        }],
        *colonne_role,
        ["ModifyColumn", "Referentiel_Agents", "Role", {
            "untieColIdFromLabel": True,
            "label": "Rôle",
            "type": "Choice",
            "isFormula": False,
            "formula": 'return "Agent"',
            "recalcWhen": 0,
            "recalcDeps": None,
            "widgetOptions": json.dumps({
                "widget": "Choice",
                "choices": CHOIX_ROLE,
                "choiceOptions": OPTIONS_ROLE["choiceOptions"],
            }),
        }],
    ]

    for act in actions:
        r = requests.post(f"{api_url}/docs/{DOC_ID}/apply", headers=headers, json=[act])
        if r.status_code != 200:
            print(f"Erreur sur action {act[1]}.{act[2]} : {r.text}")
            r.raise_for_status()

    # Initialisation idempotente de Referentiel_Agents.Role pour les fiches non encore renseignées
    r_agents = requests.get(f"{api_url}/docs/{DOC_ID}/tables/Referentiel_Agents/records", headers=headers)
    r_agents.raise_for_status()
    emails_gestionnaires_norm = {e.strip().lower() for e in EMAILS_GESTIONNAIRES}
    patches_role = []
    for rec in r_agents.json().get("records", []):
        role_actuel = rec["fields"].get("Role")
        if role_actuel in ("Agent", "Gestionnaire"):
            continue
        email = (rec["fields"].get("Email") or "").strip().lower()
        role_cible = "Gestionnaire" if email in emails_gestionnaires_norm else "Agent"
        patches_role.append({"id": rec["id"], "fields": {"Role": role_cible}})

    if patches_role:
        r_patch_role = requests.patch(
            f"{api_url}/docs/{DOC_ID}/tables/Referentiel_Agents/records",
            headers=headers,
            json={"records": patches_role},
        )
        r_patch_role.raise_for_status()
        print(f"Colonne Role initialisée sur {len(patches_role)} fiche(s) agent.")

    print("Toutes les colonnes et formules ont été configurées avec succès.")


if __name__ == "__main__":
    configurer_colonnes()
