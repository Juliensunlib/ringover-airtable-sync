import os
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer les clés API depuis les variables d'environnement
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("BASE_ID")
TABLE_NAME = os.getenv("TABLE_NAME")

# Vérifier si les variables sont bien chargées
if not AIRTABLE_API_KEY or not BASE_ID or not TABLE_NAME:
    print("❌ Les variables d'environnement ne sont pas correctement définies.")
    exit()

# URL d'Airtable API
url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'

# En-têtes avec clé API Airtable
headers = {
    'Authorization': f'Bearer {AIRTABLE_API_KEY}',
    'Content-Type': 'application/json'
}

# Faire une requête GET pour récupérer les enregistrements
response = requests.get(url, headers=headers)

# Vérifier le résultat
if response.status_code == 200:
    print("✅ Données récupérées avec succès !")
    records = response.json().get('records', [])
    print("Enregistrements :", records)
else:
    print(f"❌ Erreur lors de la récupération des données. Code d'erreur : {response.status_code}")
