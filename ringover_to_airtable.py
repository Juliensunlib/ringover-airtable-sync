import os
import requests
import pyairtable
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
import sys

# Charger les variables d'environnement
load_dotenv()

class RingOverAirtableSync:
    def __init__(self):
        """
        Initialise la synchronisation en chargeant la configuration depuis .env
        """
        self.ringover_api_key = os.getenv('RINGOVER_API_KEY')
        self.airtable_api_key = os.getenv('AIRTABLE_API_KEY')
        self.airtable_base_id = os.getenv('BASE_ID')
        self.airtable_table_name = os.getenv('TABLE_NAME')
        
        # Initialisation de la table Airtable
        api = pyairtable.Api(self.airtable_api_key)
        self.table = api.table(self.airtable_base_id, self.airtable_table_name)
        
        # Configuration du logging
        log_path = os.path.join(os.path.dirname(__file__), 'ringover_sync.log')
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s',
            filename=log_path,
            filemode='a'  # Mode append pour ne pas écraser les logs précédents
        )
        self.logger = logging.getLogger(__name__)

    def get_call_notes(self, call_id):
        """
        Récupère les notes détaillées d'un appel
        """
        headers = {
            "Authorization": f"Bearer {self.ringover_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Endpoint pour récupérer les notes de l'appel
            response = requests.get(
                f"https://api.ringover.com/v2/calls/{call_id}/notes", 
                headers=headers
            )
            
            response.raise_for_status()
            notes_data = response.json()
            
            # Formater les notes
            formatted_notes = []
            for note in notes_data.get('notes', []):
                note_entry = f"Date: {note.get('created_at', 'N/A')}"
                note_entry += f"\nAuteur: {note.get('author', {}).get('name', 'Inconnu')}"
                note_entry += f"\nContenu: {note.get('content', 'Aucun contenu')}"
                formatted_notes.append(note_entry)
            
            # Retourner les notes formatées sous forme de texte
            return "\n\n---\n\n".join(formatted_notes) if formatted_notes else "Aucune note"
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erreur lors de la récupération des notes de l'appel {call_id} : {e}")
            return "Erreur de récupération des notes"

    def get_calls(self, start_date=None, end_date=None):
        """
        Récupère les appels de RingOver
        """
        if not start_date:
            # Récupère les appels des dernières 24 heures
            start_date = datetime.now() - timedelta(hours=24)
        
        if not end_date:
            end_date = datetime.now()
        
        headers = {
            "Authorization": f"Bearer {self.ringover_api_key}",
            "Content-Type": "application/json"
        }
        
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "limit": 1000
        }
        
        try:
            response = requests.get(
                "https://api.ringover.com/v2/calls", 
                headers=headers, 
                params=params
            )
            
            response.raise_for_status()
            calls = response.json().get('calls', [])
            
            self.logger.info(f"Récupération de {len(calls)} appels")
            return calls
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erreur lors de la récupération des appels : {e}")
            return []

    def prepare_airtable_records(self, calls):
        """
        Prépare les enregistrements pour Airtable avec les notes d'appels
        """
        records = []
        for call in calls:
            # Récupérer les notes de l'appel
            call_id = call.get('id')
            notes = self.get_call_notes(call_id)
            
            record = {
                "ID Appel": call_id,
                "Date": call.get('start_time'),
                "Durée (s)": call.get('duration'),
                "Numéro Source": call.get('source_number'),
                "Numéro Destination": call.get('destination_number'),
                "Type d'appel": call.get('type'),
                "Statut": call.get('status'),
                "Notes Détaillées": notes  # Champ pour les notes complètes
            }
            records.append(record)
        return records

    def sync_calls_to_airtable(self):
        """
        Synchronise les appels de RingOver vers Airtable
        """
        try:
            # Récupération des appels
            calls = self.get_calls()
            
            if calls:
                # Préparation des enregistrements
                records = self.prepare_airtable_records(calls)
                
                # Création en batch dans Airtable
                created_records = self.table.batch_create(records)
                
                print(f"Synchronisation terminée : {len(created_records)} enregistrements créés")
                self.logger.info(f"Synchronisation terminée : {len(created_records)} enregistrements créés")
            else:
                print("Aucun nouvel appel à synchroniser")
                self.logger.info("Aucun nouvel appel à synchroniser")
        
        except Exception as e:
            print(f"Erreur lors de la synchronisation : {e}")
            self.logger.error(f"Erreur lors de la synchronisation : {e}")

def main():
    # Initialisation du synchronisateur
    sync = RingOverAirtableSync()

    # Synchronisation unique
    sync.sync_calls_to_airtable()

if __name__ == "__main__":
    main()