# Registre des signalements pour Grist

Solution complète de suivi opérationnel des signalements environnementaux déployée sur [Grist](https://www.getgrist.com/) et compatible avec La Suite numérique.

## Besoin métier

Les services chargés de la police de l'environnement, de la biodiversité ou du contrôle territorial reçoivent chaque jour des alertes, doléances et constats directs par téléphone, courriel, courrier postal ou accueil physique. L'application assure la traçabilité complète de ces saisines, de leur enregistrement initial jusqu'à la clôture après intervention de terrain, tout en garantissant le cloisonnement strict des dossiers entre agents et encadrement.

Chaque utilisateur interagit uniquement à travers des interfaces web intégrées et ergonomiques, sans manipuler directement les tableaux de données brutes.

## Architecture technique

Le classeur Grist repose sur trois tables métier et une table technique de contrôle d'accès :

- `Referentiel_Agents` : annuaire des agents (`Nom`, `Email`, `Trigramme`, `Role` avec choix `Agent` ou `Gestionnaire`, et colonne technique `Est_Connecte`) ;
- `Signalements` : registre principal doté d'une numérotation annuelle figée `AAAA-XXXX`, des champs de réception, d'attribution hiérarchique, des boutons d'alerte courriel (`mailto:`), de la consolidation automatique du dernier retour et d'un statut calculé ou manuel ;
- `Retours_Actions` : historique chronologique multiple des interventions, démarches, comptes-rendus, suites données et pièces justificatives liés à un signalement ;
- `Acces_Gestionnaires` : table témoin réservée aux gestionnaires pour héberger les vues de pilotage, de statistiques, d'accueil et de gestion des agents.

Six widgets HTML, CSS et JavaScript vanilla autonomes (sans CDN tiers ni dépendance externe autre que `grist-plugin-api.js` et `custom-widget-builder` de Grist) composent l'application :

- `widgets/nouveau_signalement_html.py` (« ✍️ Nouveau signalement ») : formulaire guidé de saisie initiale avec dépôt de pièces jointes et préparation du courriel d'alerte à l'encadrant ;
- `widgets/mes_dossiers_html.py` (« 🗂️ Mes dossiers ») : vue maître-détail à double défilement indépendant pour les dossiers attribués à l'agent connecté et ceux qu'il a réceptionnés en attente d'attribution, avec saisie des retours d'intervention et accès replié natif aux pièces jointes ;
- `widgets/espace_encadrement_html.py` (« 🛡️ Espace encadrement ») : accueil synthétique pour la hiérarchie avec compteurs en temps réel et navigation directe vers les écrans d'administration ;
- `widgets/pilotage_html.py` (« 🎯 Pilotage et attribution ») : vue maître-détail à double défilement indépendant pour trier, filtrer, attribuer les dossiers, rédiger les consignes, imprimer, exporter en CSV UTF-8 et supprimer atomiquement un dossier avec ses retours ;
- `widgets/statistiques_html.py` (« 📊 Statistiques ») : tableau de bord filtrable par période, domaine, priorité et agent, avec indicateurs de délais, graphiques SVG intégrés, bilan par agent, impression A4 et export CSV ;
- `widgets/gestion_agents_html.py` (« 👥 Gestion des agents ») : gestion guidée de l'annuaire et des rôles `Agent` / `Gestionnaire`, avec garde-fou empêchant le dernier gestionnaire actif de se retirer ses droits.

Le guide détaillé des écrans figure dans [guide_utilisateur_registre_signalements.md](guide_utilisateur_registre_signalements.md).

## Modèle de sécurité et de cloisonnement

La sécurité s'appuie sur les droits granulaires natifs de Grist via l'attribut utilisateur `user.Agent`, la colonne dynamique `Referentiel_Agents.Role` et la table témoin `Acces_Gestionnaires`. Aucune liste nominative d'adresses électroniques n'est figée dans les formules ACL déployées :

- **Propriétaire** (`user.Access == OWNER`) : seul habilité à modifier la structure du classeur (`-S` bloqué pour tout autre utilisateur) et à consulter les données brutes ;
- **Gestionnaire** (`Referentiel_Agents.Role == "Gestionnaire"`) : dispose des pleins pouvoirs (`+R+U+C+D`) sur les signalements, les retours d'intervention, l'annuaire des agents et l'espace encadrement, y compris la suppression de dossiers ;
- **Agent** (`user.Access == EDITOR` standard) : peut créer de nouveaux signalements, lire ses signalements réceptionnés tant qu'ils ne sont pas attribués, consulter uniquement les dossiers qui lui sont attribués et déposer des retours d'intervention correspondants, sans jamais voir les dossiers des collègues ni supprimer d'enregistrement ;
- **Extérieur ou anonyme** : accès totalement bloqué (`-R-U-C-D`).

Une sauvegarde JSON des règles ACL existantes est automatiquement enregistrée dans le dossier local `sauvegardes_acl/` avant chaque déploiement de droits, avec restauration possible via `python3 configurer_droits_signalements.py --restaurer <fichier.json>`.

## Installation et déploiement pas à pas

Les prérequis se limitent à Python 3.10 ou supérieur et aux bibliothèques `requests` et `pytest`.

1. Importez le classeur modèle vierge [templates/registre_signalements_modele.grist](templates/registre_signalements_modele.grist) dans votre espace de travail Grist cible (menu *Importer un document*), relevez son `DOC_ID` et son `DOC_URL`, puis vérifiez que votre compte possède le rôle `Propriétaire`.
2. Dans la table `Referentiel_Agents` (via *Données brutes*), remplacez les deux fiches d'exemple (`Agent Exemple` et `Gestionnaire Exemple`) par les agents et gestionnaires réels de votre service avec leur adresse courriel Grist exacte.
3. Copiez [config_local.example.py](config_local.example.py) vers `config_local.py` (ignoré par Git) et adaptez les paramètres de votre service (`ORG_ID`, `DOC_ID`, `DOC_URL`, `SERVICE_NOM`, `CSV_PREFIX`, `EMAIL_PLACEHOLDER`, `AGENTS_INITIAUX`, `EMAILS_PROPRIETAIRES`, `EMAILS_GESTIONNAIRES`, `CHOIX_ENCADRANT` et `ENCADRANT_PAR_DEFAUT`), puis fournissez vos identifiants API via les variables d'environnement `GRIST_API_URL` et `GRIST_API_KEY` (ou un fichier `.env` local non versionné).
4. Exécutez les scripts de paramétrage sur le classeur importé dans l'ordre suivant (le script `creer_registre_signalements.py` n'est pas nécessaire lorsque vous partez du modèle importé) :

```bash
python3 configurer_colonnes.py
python3 configurer_droits_signalements.py
python3 configurer_vues_agent.py
python3 configurer_vues_encadrement.py
python3 configurer_vues_bonus.py
```

5. Partagez enfin le document Grist avec chaque membre de votre équipe en attribuant le rôle `Éditeur` aux agents et gestionnaires, et en réservant le rôle `Propriétaire` aux administrateurs du schéma.

## Tests automatisés

Les tests unitaires hors ligne vérifient la génération de tous les widgets HTML/JS et la cohérence des règles ACL à partir de la configuration exemple, sans aucun appel réseau :

```bash
GRIST_USE_EXAMPLE_CONFIG=1 python3 -m pytest tests/ -m "not integration" -v
```

Sur une instance Grist de test configurée dans `config_local.py`, la suite complète incluant les tests d'intégration s'exécute avec :

```bash
python3 -m pytest tests/ -v
```

## Auteur et licence

Auteur originel : **Aguirre Maurin**.

Ce projet est distribué sous licence **GNU General Public License v3.0 (GPL-3.0)**. Consultez le fichier [LICENSE](LICENSE) pour le texte complet de la licence.
