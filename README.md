# Lichens GO

Lichens GO est un projet visant à étudier et comprendre l'écologie des lichens à travers l'analyse et la visualisation de données. En exploitant divers ensembles de données, le projet cherche à fournir des informations sur les facteurs environnementaux affectant les espèces de lichens et leur distribution.

Ce repo a pour objectif de créer un tableau de bord interactif permettant de visualiser et d'analyser les données écologiques des lichens. La version déployée est disponible ici : [https://saisie.lichensgo.eu/resultsLG](https://saisie.lichensgo.eu/resultsLG)

## Architecture technique

Le dashboard est organisé autour de plusieurs composants :

- **Interface utilisateur** : Construite avec Dash pour permettre aux utilisateurs de :
  - Sélectionner des zones géographiques d'intérêt
  - Filtrer les données par période et type de lichen
  - Interagir avec les visualisations en temps réel

- **Visualisation des données** : Implémentée avec Plotly pour :
  - Afficher la distribution spatiale des lichens sur une carte interactive
  - Générer différents graphiques de distribution des lichens

- **Géolocalisation** : Utilisation de GeoPy pour :
  - Retrouver l'adresse de l'observation sélectionnée par l'utilisateur

- **Backend** : Intégration avec Django via DjangoDash pour :
  - Gérer les sessions utilisateurs et les droits d'accès
  - Stocker les préférences et les filtres des utilisateurs
  - Assurer la communication avec la base de données

## Guide de contribution

**Important** :

- Le backend Django est géré dans un dépôt privé séparé
- Les données de production sont hébergées sur un serveur dédié
- La version actuelle du repository repose sur un dump de la base de données
Contactez `mandresyandri` ou `benoitfrisque` pour obtenir les identifiants de connexion à la base de données (`.env`)

### Prérequis

#### Installation de Poetry

Poetry est notre gestionnaire de dépendances. Voici les deux méthodes d'installation recommandées :

##### 1. Via pipx (méthode recommandée)

```bash
# Installation de pipx sous Ubuntu 23.04+
sudo apt update
sudo apt install pipx
pipx ensurepath

# Installation de Poetry
pipx install poetry
```

##### 2. Via l'installateur officiel

Consultez la [documentation officielle](https://python-poetry.org/docs/#installing-with-the-official-installer) pour les instructions détaillées.

### Configuration de l'environnement

#### 1. Création de l'environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 2. Gestion des dépendances avec Poetry

```bash
# Installation des dépendances
poetry install

# Ajout d'une dépendance
poetry add <package>

# Mise à jour des dépendances
poetry update
```

### Outils de développement

#### Tests et qualité du code

```bash
# Exécution des pre-commit hooks
pre-commit run --all-files

# Exécution des tests avec Tox
tox -vv
```

### Accès aux données

#### Configuration de la base de données

Prérequis :

```bash
poetry add sqlalchemy psycopg2-binary python-dotenv
```

#### Utilisation du module de données

```python
import my_data.datasets as df

# Exemple d'utilisation
lichen_ecology = df.get_lichen_ecology()
```

#### Jeux de données disponibles

- `get_environment_data`
- `get_lichen_data`
- `get_lichen_species_data`
- `get_observation_data`
- `get_table_data`
- `get_tree_data`
- `get_tree_species`
- `get_lichen_ecology`

#### Exemple de sortie

```python
# Aperçu des données d'écologie des lichens
lichen_ecology.head()
```

### Exécution du Dashboard

Pour lancer le dashboard en local, suivez les étapes ci-dessous :

1. Activez votre environnement virtuel :

    ```bash
    source .venv/bin/activate
    ```

2. Exécutez le script principal :

    ```bash
    # Pour le dashboard
    python -m dashboard.plotly_app

    # Pour le tableau de téléchargement des données
    python -m dashboard_plotly_app_download
    ```

3. Ouvrez votre navigateur et accédez à `http://localhost:8050` pour consulter le dashboard.
