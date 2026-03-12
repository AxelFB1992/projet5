import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
from pymongo import MongoClient
import os

# Connexion à MongoDB (l'hôte est le nom du service dans docker-compose)

#client = MongoClient("mongodb://localhost:27017/")
#client = MongoClient("mongodb://127.0.0.1:27017/")
#client = MongoClient("mongodb://root:examplepassword@mongodb:27017/")
#client = MongoClient("mongodb://host.docker.internal:27017/")
#db = client['healthcare_db']
#collection = db['patients']

def get_dataframe_from_csv(file_path):
    """
    Lit le fichier CSV et retourne un DataFrame Pandas.
    """
    try:
        print(f"Chargement des données depuis : {file_path}")
        df = pd.read_csv(file_path)
        print(f"Données chargées : {len(df)} lignes détectées.")
        return df
    except Exception as e:
        print(f"Erreur lors de la lecture du CSV : {e}")
        return None

def transform_medical_df_to_documents(df):
    """
    Transforme un DataFrame Pandas basé sur le data set Healtcare_db  en une liste de documents JSON structurés.
    """
    print("Transformation des données en documents JSON imbriqués...")
    documents = []
    
    # On itère sur les lignes du DataFrame
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
        documents.append(doc)
    
    return documents

def insert_to_mongodb(documents, uri, db_name, collection_name):
    """
    Assure la connexion à MongoDB et insère les documents.
    """
    client = None
    try:
        print(f"Connexion à MongoDB sur : {uri}")
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        db = client[db_name]
        collection = db[collection_name]
        
        # Nettoyage de la collection existante
        print(f"Nettoyage de la collection '{collection_name}'...")
        collection.drop()
        
        # Insertion groupée
        if documents:
            result = collection.insert_many(documents)
            print(f"Succès : {len(result.inserted_ids)} documents insérés dans {db_name}.{collection_name}")
            return True
        else:
            print("Aucun document à insérer.")
            return False
            
    except Exception as e:
        print(f"Erreur lors de l'insertion MongoDB : {e}")
        return False
    finally:
        if client:
            client.close()

def migrate():

    """
    Orchestrateur principal de la migration.
    """
    print("\n" + "="*50)
    print(" DÉMARRAGE DE LA MIGRATION HEALTHCARE (MODULAIRE)")
    print("="*50 + "\n")


    df = get_dataframe_from_csv('data/healthcare_dataset.csv')
    # Transformation en documents imbriqués
    documents = transform_medical_df_to_documents(df)
    
    #collection.insert_many(documents)
    #insert_to_mongodb(documents,"mongodb://localhost:27017/","healthcare_db",'patients')

    # 1. Configuration (Variables d'environnement)
    mongo_user = os.getenv('MONGO_ROOT_USER', 'root')
    mongo_pass = os.getenv('MONGO_ROOT_PASSWORD', 'examplepassword')
    mongo_host = os.getenv('MONGO_HOST', 'mongodb')

    #Si j'utilise le script seul, non conteneurisé 
    #mongo_host = os.getenv('MONGO_HOST', 'localhost')

    #Si on execute depuis la machine local, sans conteneur vers mongodb sur la machine local également : on préciste juste le nom du service qui tourne sur local host
    #uri = "mongodb://localhost:27017/"
    
    #Si on execute depuis un autre conteneur (comme migrator) vers le conteneur mongodb, il faut utiliser mongodb comme hote
    #uri = f"mongodb://{mongo_user}:{mongo_pass}@mongodb:27017/"

    #Si on utilise depuis la machine local (script seul) vers le conteneur mongodb, il faut utiliser localhost car on ne peut pas accéder directement au conteneur
    #Dans ce cas on tape sur le port 27017 de notre localhost et grâce à la redirection de port du conteneur, on tapera sur le conteneur mongodb
    #uri = f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/"


    #la manière la plus propre de le faire, qui ajuste les paramètre en fonction de la variable d'environnement    
    uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:27017/"
    

    # 2. Pipeline de traitement
    #csv_path = download_kaggle_dataset(dataset_url)
    
    #if csv_path:
        #df = get_dataframe_from_csv(csv_path)
    try :    
        if df is not None:
            docs = transform_medical_df_to_documents(df)
            
            # 3. Migration finale
            success = insert_to_mongodb(docs, uri, "healthcare_db", "patients")

            if(success):
                print("\n" + "="*50)
                print(" FIN DE LA MISSION")
                print("="*50)
        
        
                print(f"Migration réussie : {len(documents)} patients insérés.")
            else:
                print(f"Pas d'insertion réalisées...")
    except Exception as e:
            print(f"Erreur lors de l'insertion MongoDB : {e}")

   

if __name__ == "__main__":
    migrate()
