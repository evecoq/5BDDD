# 5BDDD

-- Creation environement
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip freeze


Variables d'environement à définir :
```text
BDD
Username
Password
```

fastapi dev main.py

Accès http://127.0.0.1:8000/
Accès au Swagger http://127.0.0.1:8000/docs
Accès  à la page Index http://127.0.0.1:8000/static/index.html

Build de l'image :
 docker build -t myfastapiapp .
Execution conteneur :
 docker run -d -p 8000:8000 --name myfastapiapp myfastapiapp

Alembic
Création de la migration - après MaJ du modele
 alembic revision --autogenerate -m "COMMENTAIRE" --- maj BDD (ajout table, colonnes etc)
 alembic upgrade head # Mise à jour BDD
