import os
from dotenv import load_dotenv
import requests
from airtable import Airtable

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Obtenir les clés API et autres informations depuis les variables d'environnement
ringover_api_key = os.getenv('RINGOVER_API_KEY')
airtable_api_key = os.getenv('AIRTABLE_API_KEY')
base_id = os.getenv('AIRTABLE_BASE_ID')
table_name = os.getenv('AIRTABLE_TABLE_NAME')

# Authentification Airtable
airtable_client = Airtable(base_id, table_name, api_key=airtable_api_key)

# Fonction pour récupérer les appels depuis Ringover
def get_ringover_calls():
    ringover_api_url = 'https://api.ringover.com/v1/calls'  # Vérifie l'URL correcte
    headers = {'Authorization': f'Bearer {ringover_api_key}'}
    response = requests.get(ringover_api_url, headers=headers)
    if response.status_code == 200:
        return response.json()['data']  # Adapte selon la structure des données reçues
    else:
        print(f"Erreur en récupérant les appels: {response.status_code}")
        return []

# Fonction pour insérer un appel dans Airtable
def insert_call_to_airtable(call_data):
    data = {
        'Abonné': call_data['subscriber_name'],
        'Numéro de téléphone': call_data['phone_number'],
        'Date et heure de l\'appel': call_data['date'],
        'Durée de l\'appel': call_data['duration'],
        'Notes': call_data['notes'],
        'Assigné à': call_data['assigned_to'],
        'Média': 'Téléphone',  # Comme l'appel provient de Ringover
        'Status': 'Terminé'
    }
    airtable_client.insert(data)

# Récupérer les appels et les insérer dans Airtable
calls = get_ringover_calls()
for call in calls:
    insert_call_to_airtable(call)
