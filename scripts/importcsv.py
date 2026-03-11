import csv
from pymongo import MongoClient
import time

# Connexion à MongoDB
#Si on veut faire cela sur le mongodb local et visualiser la migration via compass
#uri = "mongodb://localhost:27017/"
#Si on veut faire cela sur le mongodb sur conteneur (service) mongodb lancé par le docker-compose.yml
uri = "mongodb://root:examplepassword@mongodb:27017/"
client = MongoClient(uri)

try:
    
    #print("\n" + "="*40)
    print(" Script DE MIGRATION HEALTHCARE")
    #print("="*40)
    #input("\n>>> Appuyez sur ENTRÉE pour démarrer la migration...")
    #print("Migration en cours, veuillez patienter...\n")

    
    #print("La migration démarrera automatiquement dans 5 secondes...")
    #time.sleep(5)
    
    database = client.get_database("healthcare_db")
    healthcol = database.get_collection("patients")

    csv_file = "data/healthcare_dataset.csv"

    healthcol.drop()
    # Utilisation de DictReader pour traiter le fichier
    with open(csv_file, 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        
        records = []
        for row in csv_reader:
            # Transformation des données en document imbriqué
            document = {
                "name": row['Name'],
                "age": int(row['Age']),
                "gender": row['Gender'],
                "blood_type": row['Blood Type'],
                "medical_info": {
                    "condition": row['Medical Condition'],
                    "medication": row['Medication'],
                    "test_results": row['Test Results']
                },
                "hospitalization": {
                    "admission_date": row['Date of Admission'],
                    "discharge_date": row['Discharge Date'],
                    "type": row['Admission Type'],
                    "room": int(row['Room Number']),
                    "doctor": row['Doctor'],
                    "hospital": row['Hospital']
                },
                "billing": {
                    "provider": row['Insurance Provider'],
                    "amount": float(row['Billing Amount'])
                }
            }
            records.append(document)
        
        # Insertion en masse pour optimiser les performances
        if records:
            healthcol.insert_many(records)
            print(f"Migration réussie : {len(records)} patients insérés.")
    
    client.close()

except Exception as e:
    print(f"Une erreur est survenue lors de la migration : {e}")

"""
ouvrir le ficheir csv ("with open...")
utiliser lib standard csv pour mettre le contenu du csv dans une variable (ou un tableau de variables) https://docs.python.org/fr/3/library/csv.html
se connecter à mongo
pour chaque element du tableau, insérer un document (à partir de l'element du tableau)

"""
