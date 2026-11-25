# -*- coding: utf-8 -*-
"""
Configuration automatique des droits d'accès granulaires dans Grist (Registre des signalements).

Ce script applique les règles de sécurité définies pour le document Grist :
1. Verrouillage du schéma de structure (-S) pour tout utilisateur autre que les propriétaires
   du document (user.Access == OWNER).
2. Deux rôles métier pilotés dynamiquement par la colonne Referentiel_Agents.Role : Gestionnaire
   (user.Agent.Role == "Gestionnaire") et Agent (éditeurs standard, user.Access == EDITOR).
3. Pleins pouvoirs (+R+U+C+D) réservés aux gestionnaires, y compris la suppression (-D interdit
   aux agents standard et aux comptes externes sur Signalements et Retours_Actions).
4. Les agents du service sont les éditeurs du document (user.Access == EDITOR) : aucune liste
   d'e-mails en dur. L'agent attributaire d'un dossier est reconnu par rec.Agent_Attributaire.Email.
5. Un agent ne lit, dans le Registre des signalements, que les dossiers qui lui sont attribués
   (lecture seule stricte +R-U-D) ou qu'il a réceptionnés avant attribution, et crée de nouveaux
   signalements (+C).
6. Un agent ne lit et ne crée des retours de mission (Retours_Actions) que pour ses propres dossiers.
7. Verrouillage complet (-R-U-C-D) pour toute personne extérieure ou anonyme.

Une sauvegarde JSON des règles existantes est écrite dans le dossier sauvegardes_acl avant toute
purge ; elle est rejouée automatiquement si l'injection des nouvelles règles échoue, ou
manuellement avec : python configurer_droits_signalements.py --restaurer <fichier.json>
"""

import json
import os
import sys
from datetime import datetime

import requests
from config import DOC_ID, EMAILS_GESTIONNAIRES, EMAILS_PROPRIETAIRES
from creer_registre_signalements import get_grist_credentials

DOSSIER_SAUVEGARDES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sauvegardes_acl")

USER_ATTR_AGENT = json.dumps({
    "name": "Agent",
    "tableId": "Referentiel_Agents",
    "lookupColId": "Email",
    "charId": "Email",
})
EST_PROPRIETAIRE = "user.Access == OWNER"
EST_GESTIONNAIRE = '((user.Access == OWNER or user.Access == EDITOR) and user.Agent and user.Agent.Role == "Gestionnaire")'
EST_AGENT = "(user.Access == EDITOR or user.Access == OWNER)"
DOSSIER_DE_L_AGENT = f"{EST_AGENT} and user.Agent and rec.Agent_Attributaire == user.Agent.id"
DOSSIER_RECEPTIONNE_NON_ATTRIBUE = (
    f"{EST_AGENT} and user.Agent and not rec.Agent_Attributaire and not rec.Statut_Manuel "
    "and rec.Agent_Recepteur == user.Agent.id"
)
EST_LIGNE_UTILISATEUR = f"({EST_GESTIONNAIRE} or {EST_AGENT}) and rec.Email == user.Email"
RETOUR_DE_L_AGENT = f"{EST_AGENT} and user.Agent and rec.Agent_Attributaire_Id == user.Agent.id"
NOUVEAU_RETOUR_DE_L_AGENT = f"{EST_AGENT} and user.Agent and newRec.Agent_Attributaire_Id == user.Agent.id"
COLONNES_ATTRIBUTION = "Agent_Attributaire,Date_Attribution,Priorite,Consignes_Hierarchie,Statut_Manuel"

RESSOURCES_ACL = [
    {"tableId": "*", "colIds": "*"},
    {"tableId": "Referentiel_Agents", "colIds": "Est_Connecte"},
    {"tableId": "Referentiel_Agents", "colIds": "*"},
    {"tableId": "Acces_Gestionnaires", "colIds": "*"},
    {"tableId": "Signalements", "colIds": "Est_Mon_Dossier"},
    {"tableId": "Signalements", "colIds": COLONNES_ATTRIBUTION},
    {"tableId": "Signalements", "colIds": "*"},
    {"tableId": "Retours_Actions", "colIds": "*"},
]

CHAMPS_RESSOURCE = ("tableId", "colIds")
CHAMPS_REGLE = ("resource", "permissionsText", "aclFormula", "rulePos", "userAttributes", "memo")


def _lire_table(api_url, headers, table):
    r = requests.get(f"{api_url}/docs/{DOC_ID}/tables/{table}/records", headers=headers)
    r.raise_for_status()
    return r.json()["records"]


def _supprimer_lignes(api_url, headers, table, ids):
    if ids:
        requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/{table}/data/delete", headers=headers, json=ids
        ).raise_for_status()


def sauvegarder_regles(api_url, headers):
    """Écrit les ressources et règles ACL actuelles dans un fichier JSON horodaté."""
    os.makedirs(DOSSIER_SAUVEGARDES, exist_ok=True)
    chemin = os.path.join(
        DOSSIER_SAUVEGARDES, f"acl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    contenu = {
        table: _lire_table(api_url, headers, table)
        for table in ("_grist_ACLResources", "_grist_ACLRules")
    }
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(contenu, f, ensure_ascii=False, indent=2)
    print(f"Sauvegarde des règles ACL : {chemin}")
    return chemin


def purger_anciennes_regles(api_url, headers):
    """Supprime les règles et ressources antérieures pour repartir d'une base saine."""
    rule_ids = [rec["id"] for rec in _lire_table(api_url, headers, "_grist_ACLRules") if rec["id"] > 1]
    print(f"Purge de {len(rule_ids)} ancienne(s) règle(s)...")
    _supprimer_lignes(api_url, headers, "_grist_ACLRules", rule_ids)

    res_ids = [rec["id"] for rec in _lire_table(api_url, headers, "_grist_ACLResources") if rec["id"] > 1]
    print(f"Purge de {len(res_ids)} ancienne(s) ressource(s)...")
    _supprimer_lignes(api_url, headers, "_grist_ACLResources", res_ids)


def restaurer_regles(api_url, headers, chemin):
    """Rejoue une sauvegarde JSON : remplace les règles actuelles par celles du fichier."""
    with open(chemin, "r", encoding="utf-8") as f:
        sauvegarde = json.load(f)
    purger_anciennes_regles(api_url, headers)

    r_tbls = requests.get(f"{api_url}/docs/{DOC_ID}/tables", headers=headers)
    r_tbls.raise_for_status()
    tables_existantes = {t["id"] for t in r_tbls.json().get("tables", [])}

    anciennes_res = [
        r for r in sauvegarde["_grist_ACLResources"]
        if r["id"] > 1 and (
            r["fields"].get("tableId") == "*" or r["fields"].get("tableId") in tables_existantes
        )
    ]
    correspondance = {1: 1}
    if anciennes_res:
        r = requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_ACLResources/records",
            headers=headers,
            json={"records": [{"fields": {k: a["fields"][k] for k in CHAMPS_RESSOURCE}} for a in anciennes_res]},
        )
        r.raise_for_status()
        for ancienne, nouvelle in zip(anciennes_res, r.json()["records"]):
            correspondance[ancienne["id"]] = nouvelle["id"]

    anciennes_regles = [
        r for r in sauvegarde["_grist_ACLRules"]
        if r["id"] > 1 and r["fields"].get("resource") in correspondance
    ]
    if anciennes_regles:
        records = []
        for a in anciennes_regles:
            champs = {k: a["fields"].get(k) for k in CHAMPS_REGLE}
            if champs.get("userAttributes") is None:
                champs.pop("userAttributes", None)
            champs["resource"] = correspondance[champs["resource"]]
            champs["permissions"] = 0
            champs["principals"] = ""
            records.append({"fields": champs})
        requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_ACLRules/records",
            headers=headers,
            json={"records": records},
        ).raise_for_status()
    print(f"Règles ACL restaurées depuis {chemin}.")


def configurer_table_acces_gestionnaires(api_url, headers):
    """Crée la table technique Acces_Gestionnaires si absente et masque sa vue brute du menu."""
    r_tbls = requests.get(f"{api_url}/docs/{DOC_ID}/tables", headers=headers)
    r_tbls.raise_for_status()
    tables_existantes = [t["id"] for t in r_tbls.json().get("tables", [])]

    if "Acces_Gestionnaires" not in tables_existantes:
        print("Création de la table technique 'Acces_Gestionnaires'...")
        payload = {
            "tables": [{
                "id": "Acces_Gestionnaires",
                "columns": [
                    {"id": "Titre", "fields": {"label": "Titre", "type": "Text"}},
                    {"id": "Description", "fields": {"label": "Description", "type": "Text"}},
                ],
            }]
        }
        requests.post(f"{api_url}/docs/{DOC_ID}/tables", headers=headers, json=payload).raise_for_status()

        # Retrait de la page brute créée automatiquement dans le menu latéral
        tables_meta = _lire_table(api_url, headers, "_grist_Tables")
        ag_table_ref = next(
            (t["id"] for t in tables_meta if t["fields"].get("tableId") == "Acces_Gestionnaires"),
            None,
        )
        if ag_table_ref:
            sections = _lire_table(api_url, headers, "_grist_Views_section")
            ag_view_ids = {
                s["fields"].get("parentId")
                for s in sections
                if s["fields"].get("tableRef") == ag_table_ref and s["fields"].get("parentKey") == "record"
            }
            pages = _lire_table(api_url, headers, "_grist_Pages")
            page_ids = [p["id"] for p in pages if p["fields"].get("viewRef") in ag_view_ids]
            _supprimer_lignes(api_url, headers, "_grist_Pages", page_ids)

    recs = _lire_table(api_url, headers, "Acces_Gestionnaires")
    if not recs:
        requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/Acces_Gestionnaires/records",
            headers=headers,
            json={"records": [{"fields": {
                "Titre": "Verrou Espace encadrement",
                "Description": "Table technique d'accès réservé à l'encadrement",
            }}]},
        ).raise_for_status()
        print("Table technique 'Acces_Gestionnaires' initialisée.")


def _regle(resource, permissions, formule, memo, user_attributes=""):
    regle = {
        "resource": resource,
        "permissions": 0,
        "permissionsText": permissions,
        "principals": "",
        "aclFormula": formule,
        "memo": memo,
    }
    if user_attributes:
        regle["userAttributes"] = user_attributes
    return regle


def construire_regles(ids):
    """Retourne la liste ordonnée des règles ; rulePos est attribué selon l'ordre de la liste."""
    (
        res_all,
        res_ref_connecte,
        res_ref,
        res_ges,
        res_mon_dossier,
        res_attrib,
        res_sig,
        res_ret,
    ) = ids
    regles = [
        _regle(
            res_all,
            "",
            "",
            "Attribut utilisateur Agent (lien Referentiel_Agents par Email)",
            user_attributes=USER_ATTR_AGENT,
        ),
        _regle(res_all, "-S", f"not ({EST_PROPRIETAIRE})", "Structure du registre réservée aux propriétaires (Schema Edit)"),

        _regle(res_ref_connecte, "+R-U", EST_LIGNE_UTILISATEUR, "Identification de session : lecture de Est_Connecte sur sa propre ligne"),
        _regle(res_ref_connecte, "-R-U", "", "Masquage de Est_Connecte sur les autres lignes"),

        _regle(res_ref, "+R+U+C+D", EST_GESTIONNAIRE, "Gestion annuaire réservée aux gestionnaires"),
        _regle(res_ref, "+R-U-C-D", EST_AGENT, "Consultation annuaire pour les agents du service"),
        _regle(res_ref, "-R-U-C-D", "", "Accès refusé aux tiers et anonymes"),

        _regle(res_ges, "+R+U+C+D", EST_GESTIONNAIRE, "Table technique réservée aux gestionnaires"),
        _regle(res_ges, "-R-U-C-D", "", "Accès refusé aux non-gestionnaires"),

        _regle(res_mon_dossier, "+R-U", "user.Agent and rec.Agent_Attributaire == user.Agent.id", "Accessible uniquement si le dossier est attribué à l'utilisateur connecté"),
        _regle(res_mon_dossier, "-R-U", "", "Masqué pour tout autre dossier, y compris pour les propriétaires"),

        _regle(res_attrib, "+R+U", EST_GESTIONNAIRE, "Attribution et consignes réservées aux gestionnaires"),
        _regle(res_attrib, "+R-U", DOSSIER_DE_L_AGENT, "Attribution en lecture seule pour l'agent attributaire du dossier"),
        _regle(res_attrib, "+R-U", DOSSIER_RECEPTIONNE_NON_ATTRIBUE, "Lecture seule des champs d'attribution pour l'agent récepteur avant attribution"),
        _regle(res_attrib, "-R-U", "", "Masqué pour les autres agents, les tiers et anonymes"),

        _regle(res_sig, "+R+U+C+D", EST_GESTIONNAIRE, "Pleins pouvoirs et suppression réservés aux gestionnaires"),
        _regle(res_sig, "+R-U-D", DOSSIER_DE_L_AGENT, "Lecture seule des seuls dossiers attribués à l'agent"),
        _regle(res_sig, "+R-U-D", DOSSIER_RECEPTIONNE_NON_ATTRIBUE, "Lecture seule pour l'agent récepteur tant que le dossier n'est pas attribué"),
        _regle(res_sig, "+C-R-U-D", EST_AGENT, "Dépôt d'un nouveau signalement autorisé pour les agents"),
        _regle(res_sig, "-R-U-C-D", "", "Accès refusé pour les dossiers d'autrui et utilisateurs externes"),

        _regle(res_ret, "+R+U+C+D", EST_GESTIONNAIRE, "Pleins pouvoirs et suppression sur les retours réservés aux gestionnaires"),
        _regle(res_ret, "+R-U-C-D", RETOUR_DE_L_AGENT, "Consultation des retours de ses propres dossiers"),
        _regle(res_ret, "+C-R-U-D", NOUVEAU_RETOUR_DE_L_AGENT, "Dépôt d'un retour uniquement sur ses propres dossiers"),
        _regle(res_ret, "-R-U-C-D", "", "Accès refusé aux autres agents, tiers et anonymes"),
    ]
    for position, regle in enumerate(regles, start=1):
        regle["rulePos"] = float(position)
    return regles


def appliquer_regles_acces():
    api_url, api_key = get_grist_credentials()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print("=== Étape 0 : Vérification de la table technique Acces_Gestionnaires ===")
    configurer_table_acces_gestionnaires(api_url, headers)

    print("=== Étape 1 : Sauvegarde et nettoyage des anciennes règles ===")
    sauvegarde = sauvegarder_regles(api_url, headers)
    purger_anciennes_regles(api_url, headers)

    try:
        print("=== Étape 2 : Création des ressources de sécurité ===")
        r_res = requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_ACLResources/records",
            headers=headers,
            json={"records": [{"fields": r} for r in RESSOURCES_ACL]}
        )
        r_res.raise_for_status()
        ids = [r["id"] for r in r_res.json()["records"]]
        print(f"{len(ids)} ressource(s) d'accès créée(s).")

        print("=== Étape 3 : Injection des règles d'accès sécurisées ===")
        regles_a_creer = construire_regles(ids)
        r_rules = requests.post(
            f"{api_url}/docs/{DOC_ID}/tables/_grist_ACLRules/records",
            headers=headers,
            json={"records": [{"fields": r} for r in regles_a_creer]}
        )
        r_rules.raise_for_status()
        print(f"{len(r_rules.json()['records'])} règles d'accès injectées avec succès.")
    except Exception:
        print("Échec : restauration de la sauvegarde des règles ACL.")
        restaurer_regles(api_url, headers, sauvegarde)
        raise


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--restaurer":
        _url, _cle = get_grist_credentials()
        restaurer_regles(_url, {"Authorization": f"Bearer {_cle}", "Content-Type": "application/json"}, sys.argv[2])
    else:
        appliquer_regles_acces()
