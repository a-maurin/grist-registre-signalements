# Guide d'utilisation du registre des signalements (Grist)

## Présentation générale

Le registre des signalements assure la traçabilité de l'ensemble des informations, doléances et alertes transmises au service par téléphone, courriel, courrier postal, accueil physique ou constat direct, dès lors qu'elles sont susceptibles d'appeler une intervention sur le terrain, une vérification ou une réponse formelle.

L'application est hébergée sur l'instance Grist configurée dans `config_local.py` (paramètre `DOC_URL`).

Les utilisateurs travaillent uniquement à travers des interfaces web intégrées et guidées, sans manipuler directement les tableaux de données brutes. Les grilles natives demeurent masquées du menu latéral et restent accessibles aux propriétaires du document via la section Données brutes de Grist.

## Parcours des agents du service

Le menu principal propose à tous les agents deux écrans dédiés : « ✍️ Nouveau signalement » et « 🗂️ Mes dossiers ».

### Enregistrement d'un nouveau signalement

Lorsqu'un agent reçoit une alerte ou une doléance, il ouvre la page « ✍️ Nouveau signalement ». La date et l'heure de réception ainsi que le nom de l'agent récepteur sont pré-remplis automatiquement à partir de la session ouverte. L'agent indique le canal de réception, les coordonnées du requérant le cas échéant, la commune et le lieu-dit, le domaine d'activité, la description des faits, les éventuelles pièces jointes et l'encadrant à prévenir parmi les responsables configurés.

Dès validation du formulaire, Grist enregistre le dossier, génère un numéro annuel figé au format `AAAA-XXXX` et affiche un écran de confirmation comportant un bouton « ✉️ Alerter l'encadrant par courriel ». Ce bouton ouvre le client de messagerie avec l'adresse de l'encadrant sélectionné, le numéro du signalement, un résumé des faits et le lien direct vers l'écran de pilotage.

### Suivi des dossiers et saisie des retours d'intervention

La page « 🗂️ Mes dossiers » centralise l'ensemble des signalements concernant l'agent connecté sous deux onglets distincts. Les deux colonnes (liste à gauche et fiche détaillée à droite) disposent chacune de leur propre défilement vertical indépendant afin de conserver la liste accessible pendant la lecture d'une fiche longue.

L'onglet « Dossiers attribués » regroupe les missions confiées à l'agent, filtrables par état (À traiter, En cours, Traités ou clos, Tous), triables par priorité ou par date et interrogeables par recherche libre. La fiche de synthèse de droite présente l'origine du signalement, la localisation avec lien OpenStreetMap, les consignes de l'encadrement, les pièces jointes associées et l'historique chronologique complet des retours déjà saisis. Le bouton « 📝 Ajouter un retour d'intervention » ouvre une fenêtre de saisie permettant de renseigner la date, la nature de la démarche, le compte-rendu, la suite donnée et d'éventuelles photographies ou pièces justificatives. Un premier retour sans suite définitive passe le dossier en statut « En cours » ; la saisie d'une suite donnée le fait passer automatiquement en statut « Traité ». Un bouton permet également d'imprimer la fiche complète au format A4.

L'onglet « En attente d'attribution » donne une visibilité en lecture seule à l'agent récepteur sur les signalements qu'il a saisis tant qu'aucun attributaire n'a encore été désigné. Cet onglet lui permet de retrouver le numéro de dossier et de relancer l'encadrement par courriel si besoin. Dès que l'encadrant attribue le dossier à un collègue, ce dernier disparaît de la vue de l'agent récepteur selon les règles de cloisonnement.

Pour des raisons de sécurité propres à Grist sur les droits granulaires, le téléchargement direct des pièces jointes depuis un bouton HTML peut être refusé pour les comptes éditeurs standard. Dans ce cas, les pièces sont listées par leur référence et restent consultables dans le volet replié « 📎 Pièces jointes (accès natif) » situé en haut de la page « 🗂️ Mes dossiers », qui se synchronise automatiquement sur le dossier sélectionné.

## Parcours de l'encadrement

Un regroupement « 🛡️ Espace encadrement » est affiché dans le menu latéral pour les gestionnaires du registre (rôle `Gestionnaire` dans `Referentiel_Agents.Role`). La page d'accueil affiche quatre compteurs en temps réel (nouveaux à attribuer, urgents actifs, attribués et en cours, traités ou clos) et donne accès aux trois écrans d'encadrement indentés dessous.

### Pilotage et attribution

L'écran « 🎯 Pilotage et attribution » offre une vue maître-détail pleine page sur l'ensemble du registre, avec défilement vertical indépendant pour la liste de gauche et la fiche de droite tandis que les filtres restent fixes en haut de l'écran. Un bandeau de compteurs cliquables et une barre de filtres combinés (statut, priorité, domaine d'activité, agent attributaire ou dossiers non attribués, recherche libre) permettent d'isoler immédiatement les dossiers à traiter. Le tableau de gauche est triable en cliquant sur les en-têtes de colonnes (numéro, date de réception, commune, attributaire, priorité, statut).

La fiche de droite intègre un panneau d'action hiérarchique pour attribuer le dossier à un agent (avec remplissage automatique de la date d'attribution si elle est laissée vide), définir le niveau de priorité, rédiger les consignes d'intervention ou imposer un statut manuel qui prime sur le calcul automatique. Après enregistrement, le bouton « ✉️ Envoyer fiche (courriel) » prépare le message complet destiné à l'agent attributaire. La fiche affiche également l'historique complet des retours d'intervention et s'imprime proprement au format A4 sur plusieurs pages si nécessaire. Un bouton « 📥 Exporter CSV » génère un fichier encodé en UTF-8 avec BOM et séparateur point-virgule reprenant les dossiers filtrés, prêt à être ouvert dans LibreOffice Calc ou Excel.

Les gestionnaires disposent également d'un bouton « 🗑️ Supprimer » dans l'en-tête de la fiche. Cette action ouvre une fenêtre de confirmation affichant le numéro, l'objet du signalement et le nombre éventuel de retours liés dans `Retours_Actions`, puis supprime en une seule opération atomique ces retours liés et le signalement lui-même.

### Statistiques d'activité

La page « 📊 Statistiques » propose un tableau de bord HTML filtrable par période (toutes périodes, année en cours, année précédente, 30 derniers jours, 90 derniers jours ou plage personnalisée), par domaine d'activité, par priorité et par agent attributaire.

Cinq indicateurs synthétisent le périmètre sélectionné : volume total, taux de clôture, nombre de dossiers urgents actifs, délai moyen d'attribution et délai moyen de traitement entre la réception et l'intervention. Quatre graphiques SVG intégrés illustrent la répartition par statut, les domaines d'activité, l'évolution mensuelle des réceptions ainsi que les canaux d'entrée et suites données. Un tableau récapitule l'activité par agent attributaire et s'exporte au format CSV (UTF-8 avec BOM et séparateur point-virgule) ou s'imprime au format A4.

### Gestion des agents

La page « 👥 Gestion des agents » permet de consulter, filtrer (par texte ou par rôle : Gestionnaire ou Agent), ajouter, modifier ou supprimer les fiches de `Referentiel_Agents` depuis une interface guidée, sans ouvrir de grille brute ni toucher aux formules de session. Le sélecteur de rôle dans les fenêtres d'ajout et de modification met à jour la colonne `Role` de `Referentiel_Agents` et ajuste immédiatement les droits d'accès du compte concerné. Un garde-fou empêche le dernier gestionnaire actif de se retirer son propre rôle afin d'éviter tout verrouillage accidentel de l'espace encadrement.

Pour préserver l'intégrité historique du registre et la session en cours, la suppression d'un agent est automatiquement bloquée dès qu'il est référencé comme récepteur, attributaire ou intervenant dans un signalement ou un retour. Lors de l'ajout d'un nouvel agent, un rappel invite à partager également le classeur à son courriel professionnel avec le rôle Éditeur dans Grist afin qu'il puisse se connecter et n'accéder qu'à ses propres dossiers. Un bouton permet d'exporter l'annuaire, les rôles et les compteurs d'activité au format CSV.

## Confidentialité et règles de sécurité

La protection des données et le secret des investigations reposent sur les règles d'accès configurées dans Grist via l'attribut utilisateur `user.Agent`, la colonne `Referentiel_Agents.Role` et la table témoin `Acces_Gestionnaires`. Le service distingue uniquement deux rôles métier : **Gestionnaire** et **Agent**.

Les **Propriétaires** du document Grist (`user.Access == OWNER`) sont seuls habilités à modifier la structure du classeur (`-S` bloqué pour tout autre compte) et à accéder aux données brutes d'administration.

Les **Gestionnaires** (tout utilisateur disposant de la valeur `Gestionnaire` dans `Referentiel_Agents.Role`) disposent des droits complets de lecture, d'écriture, d'attribution et de suppression (`+R+U+C+D`) sur les signalements, les retours d'intervention, l'annuaire des agents et l'espace encadrement.

Les **Agents** ayant le rôle Éditeur sur le document peuvent créer de nouveaux signalements, consulter en lecture seule les signalements qu'ils ont réceptionnés tant qu'ils ne sont pas attribués, et consulter ou compléter par des retours d'intervention les seuls dossiers qui leur sont attribués. Les dossiers confiés aux collègues restent strictement invisibles et toute modification directe ou suppression d'un signalement existant, d'un retour ou de l'annuaire par un agent non gestionnaire est bloquée.

Les utilisateurs externes ou anonymes n'ont aucun accès au document.

## Scripts d'administration et maintenance

Les scripts Python du répertoire assurent le déploiement reproductible et la vérification du classeur :

`config.py` charge les paramètres depuis `config_local.py` (ou `config_local.example.py` par défaut) et les variables d'environnement. `creer_registre_signalements.py` gère la connexion et la création ou le rattachement du document Grist. `configurer_colonnes.py` paramètre les types de colonnes, les choix colorés, les formules métier et les colonnes techniques (`Est_Connecte`, `Agent_Attributaire_Id`, `Role`). `configurer_droits_signalements.py` sauvegarde puis déploie les règles ACL dans `sauvegardes_acl/` (restauration possible avec `python3 configurer_droits_signalements.py --restaurer <fichier.json>`). `configurer_vues_agent.py` déploie les widgets HTML du parcours agent (« ✍️ Nouveau signalement » et « 🗂️ Mes dossiers »). `configurer_vues_encadrement.py` déploie « 🛡️ Espace encadrement » et « 🎯 Pilotage et attribution », retire l'ancienne vue passive et organise le menu latéral. `configurer_vues_bonus.py` déploie les vues HTML « 📊 Statistiques » et « 👥 Gestion des agents » et actualise les liens de l'espace encadrement.

La suite unitaire hors ligne se lance avec `GRIST_USE_EXAMPLE_CONFIG=1 python3 -m pytest tests/ -m "not integration" -v`, et la suite complète (incluant les tests d'intégration sur un classeur de test) avec `python3 -m pytest tests/ -v`.
