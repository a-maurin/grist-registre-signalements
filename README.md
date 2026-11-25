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

## Installation et déploiement dans un nouveau service

### Logique d'ensemble

Le déploiement dans un nouveau service repose sur l'import préalable du classeur modèle vierge [templates/registre_signalements_modele.grist](templates/registre_signalements_modele.grist). Ce fichier fournit d'emblée les quatre tables, leurs colonnes, leurs formules ainsi que les six vues et leurs identifiants attendus, ce qui dispense d'exécuter `creer_registre_signalements.py`.

Les cinq scripts `configurer_*.py` appliquent ensuite la configuration propre à votre service par appels à l'API Grist. L'ensemble des paramètres locaux reste isolé dans `config_local.py` et `.env`, tous deux ignorés par Git, tandis qu'une copie de sauvegarde des règles ACL est enregistrée dans `sauvegardes_acl/` avant toute modification des droits. En exploitation, les autorisations fines découlent directement de la colonne `Referentiel_Agents.Role` (`Agent` ou `Gestionnaire`) sans aucun besoin de relancer les scripts à chaque mouvement d'effectif.

### Prérequis

Sur votre instance Grist ou La Suite numérique, le déploiement requiert un compte administrateur disposant du rôle `Propriétaire` sur le document cible ainsi qu'une clé API Grist personnelle. L'instance doit autoriser les widgets personnalisés et les postes utilisateurs doivent pouvoir charger `custom-widget-builder` et `grist-plugin-api.js`, tout en disposant d'un client de messagerie configuré pour ouvrir les liens `mailto:` générés lors des alertes.

Sur le poste qui exécute l'installation, il suffit d'avoir récupéré ce dépôt Git et de disposer de Python 3.10 ou supérieur avec la bibliothèque `requests` (ainsi que `pytest` en option pour exécuter la suite de tests hors ligne). Ce poste n'est sollicité que lors du déploiement initial ou des mises à jour ultérieures.

### Déploiement pas à pas en six étapes

1. Importez le classeur modèle vierge [templates/registre_signalements_modele.grist](templates/registre_signalements_modele.grist) dans l'espace de travail Grist de votre service via le menu *Importer un document*. Relevez ensuite l'identifiant du document (`DOC_ID`) et son adresse complète (`DOC_URL`) dans la barre d'adresse du navigateur, puis vérifiez que votre compte possède bien le rôle `Propriétaire` sur ce document.

2. Avant de déployer les règles de sécurité, ouvrez la table `Referentiel_Agents` depuis le menu *Données brutes* dans Grist. Remplacez les deux fiches génériques fournies (`Agent Exemple` et `Gestionnaire Exemple`) par les agents et gestionnaires réels de votre service. Veillez à ce que la colonne `Email` corresponde exactement à l'adresse de connexion Grist ou ProConnect de chaque utilisateur, et attribuez la valeur `Gestionnaire` dans la colonne `Role` aux responsables qui doivent accéder à l'espace d'encadrement.

3. Copiez [config_local.example.py](config_local.example.py) vers `config_local.py` (ignoré par Git). Renseignez la connexion à l'API (`GRIST_API_URL`, `GRIST_API_KEY`, qui peuvent aussi être placés dans un fichier `.env` local ou des variables d'environnement), l'identification du document cible (`ORG_ID`, `WORKSPACE_NAME`, `DOC_NAME`, `DOC_ID`, `DOC_URL`), l'identité du service (`SERVICE_NOM`, `CSV_PREFIX`, `EMAIL_PLACEHOLDER`), les listes de référence (`AGENTS_INITIAUX`, `EMAILS_PROPRIETAIRES`, `EMAILS_GESTIONNAIRES`) ainsi que les noms proposés dans la liste déroulante des encadrants à alerter (`CHOIX_ENCADRANT` et `ENCADRANT_PAR_DEFAUT`).

4. Si votre service n'appartient pas au domaine de la police de l'environnement, adaptez les listes de choix métier (`CHOIX_CANAL`, `CHOIX_DOMAINE`, `CHOIX_PRIORITE`, `CHOIX_STATUT`, `CHOIX_DEMARCHE` et `CHOIX_SUITE`) de manière strictement identique aux deux endroits du code où elles sont définies : dans [configurer_colonnes.py](configurer_colonnes.py) et dans [widgets/commun.py](widgets/commun.py).

5. Exécutez les cinq scripts de configuration depuis la racine du dépôt dans l'ordre exact ci-dessous, sans lancer `creer_registre_signalements.py` :

```bash
python3 configurer_colonnes.py
python3 configurer_droits_signalements.py
python3 configurer_vues_agent.py
python3 configurer_vues_encadrement.py
python3 configurer_vues_bonus.py
```

Le premier script met à jour le schéma, les formules `mailto:` et les choix d'encadrants ; le deuxième sauvegarde les règles existantes dans `sauvegardes_acl/` et applique le cloisonnement ACL ; les trois suivants déploient successivement les écrans agent, l'espace d'encadrement et le pilotage, puis les statistiques et la gestion des agents.

6. Partagez enfin le document dans Grist avec l'ensemble des membres de votre équipe en leur attribuant le rôle Grist `Éditeur`, aussi bien pour les agents que pour les gestionnaires, en réservant le rôle `Propriétaire` aux seuls administrateurs techniques du schéma. Réalisez ensuite une recette fonctionnelle rapide : vérifiez avec un compte `Agent` que seuls les écrans *Nouveau signalement* et *Mes dossiers* sont visibles sans accès aux dossiers des collègues, puis vérifiez avec un compte `Gestionnaire` l'accès complet à *Espace encadrement* et à ses trois sous-écrans (*Pilotage et attribution*, *Statistiques* et *Gestion des agents*).

### Exploitation courante

Au quotidien, la gestion de l'annuaire s'effectue directement depuis l'interface Grist dans la vue *Gestion des agents* pour ajouter un arrivant, mettre à jour une fiche ou basculer un rôle entre `Agent` et `Gestionnaire`. Tout nouvel utilisateur doit également être invité dans le menu *Partager* de Grist avec le rôle `Éditeur` afin de pouvoir ouvrir le classeur.

Lorsqu'une évolution de paramétrage devient nécessaire par la suite (ajout d'un encadrant dans `config_local.py`, ajustement d'une liste déroulante ou mise à jour des widgets), il suffit de relancer `configurer_colonnes.py` puis les scripts `configurer_vues_*.py` concernés depuis le poste d'administration.

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

Auteur originel : **Aguirre Maurin — 2026**.

Ce projet est distribué sous licence **GNU General Public License v3.0 (GPL-3.0)**. Consultez le fichier [LICENSE](LICENSE) pour le texte complet de la licence.
