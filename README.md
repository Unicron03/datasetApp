### Exécution avec Docker

```bash
docker build -t tst_app --progress=plain .
```

Puis

```bash
docker run -p 8501:8501 tst_app
```

### Exécution en ligne

Vous pouvez visualiser le site en ligne ici : https://unicron03-datasetapp.streamlit.app/

### But
Créer, modifier et sélectionner des informations dans un jeu de données à l'aide d'une IHM simple et intuitive.

### Fonctionnement

- Page d'accueil permettant de naviguer à travers les pages et de retrouver quelques informations sur notre équipe mais aussi le fonctionnement de streamlit.
- Page "Create" : permet de créer un jeu de données.
- Page "Update" : permet de modifier un jeu de données.
- Page "View" : permet de sélectionner des données dans un jeu de données.
