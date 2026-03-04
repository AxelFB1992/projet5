import pandas as pd
from pymongo import MongoClient
import os

# Connexion à MongoDB (l'hôte est le nom du service dans docker-compose)
#client = MongoClient("mongodb://localhost:27017/")
client = MongoClient("mongodb://root:examplepassword@mongodb:27017/")
db = client['healthcare_db']
collection = db['patients']

def migrate():
    df = pd.read_csv('/app/data/healthcare_dataset.csv')
    
    # Transformation en documents imbriqués
    records = []
    for _, row in df.iterrows():
        doc = {
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
        records.append(doc)
    
    collection.insert_many(records)
    print(f"Migration réussie : {len(records)} patients insérés.")

if __name__ == "__main__":
    migrate()
