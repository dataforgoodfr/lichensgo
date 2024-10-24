# Récupérer les datasets

## 1 - Logique

Récupération des données depuis la base de données PostgreSQL sur le cloud. Pour info, le schéma se trouve dans le fichier [model.py](my_data/model.py). 

> Sytème évolutif en fonction du projet
L'ensemble des données sont récupérés et concerti au format `pd.DataFrame()` pour faciliter la création de graphique
cf. [datasets.py](my_data/datasets.py)

Prérequis 
> À installer 
```bash
poetry add sqlalchemy psycopg2-binary python-dotenv
```

## 2 - Utilisation du module
Vous récupérez ensuite les données en important le module :
```python
import my_data.datasets as df
```
Ceci va renvoyer un `pandas.DataFrame` directement utilisable pour vos visualisation.

### Liste des données
- get_environment_data
- get_lichen_data
- get_lichen_species_data
- get_observation_data
- get_table_data
- get_tree_data 
- get_tree_species
- get_lichen_ecology

## 3 - Exemple d'import et résultats 
Le cas de ma visualisation du fichier [demo_streamlit.py](demo_streamlit.py). 

```python
import my_data.datasets as df

lichen_ecology = df.get_lichen_ecology()

lichen_ecology.head()
```
> RESULTATS
```txt
id                                       taxon             pH       aridity eutrophication poleotolerance
0    1  Amandinea punctata / Lecidella elaeochroma  neutrophilous   xerophilous    mesotrophic      resistant
1    2                         Anaptychia ciliaris  neutrophilous   mesophilous    mesotrophic   intermediate
2    3                         Candelaria concolor  neutrophilous   xerophilous      eutrophic      resistant
3    4                           Candelariella sp.  neutrophilous   mesophilous      eutrophic      resistant
4    5                         Diploicia canescens    basophilous   mesophilous    mesotrophic   intermediate
```


> Contactez mandresyandri pour récupérer les .env de connexion à la DB 