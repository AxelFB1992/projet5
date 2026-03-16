import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
from pymongo import MongoClient
import os

#fonction permettant de retourner un data frame (pandas) depuis un fichier csv

def get_dataframe_kaggle(file_path):
    """
    Lit le fichier CSV et retourne un DataFrame Pandas.
    """
    try:
        print(f"Chargement des données depuis : {file_path}")
        
        # Load the latest version
        df = kagglehub.load_dataset(KaggleDatasetAdapter.PANDAS,"prasad22/healthcare-dataset",file_path)
        # Provide any additional arguments like 
        # sql_query or pandas_kwargs. See the 
        # documenation for more information:
        # https://github.com/Kaggle/kagglehub/blob/main/README.md#kaggledatasetadapterpandas
        
        print(f"Données chargées : {len(df)} lignes détectées.")
        return df
    except Exception as e:
        print(f"Erreur lors de la lecture du CSV : {e}")
        return None

#fonction permettant de retourner un data frame (pandas) depuis un fichier csv
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

#fonction permettant de transformer un data_frame avec la structure de healthcare_db (kaggle) en une collection de documents (tableau de docs)
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

#fonction principale du script : permet d'inserer le tableau de documents (documents) passé en paramètre dans une collection (collection_name)
#, d'une base de données (db_name), d'un serveur mongodb (uri)
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

#fonction main, depuis laquelle toutes les instructions sont excutées, et qui appelle toutes les autres
def migrate():

    """
    Orchestrateur principal de la migration.
    """
    print("\n" + "="*50)
    print(" DÉMARRAGE DE LA MIGRATION HEALTHCARE (MODULAIRE)")
    print("="*50 + "\n")

    #Branch 2 : on essaie de récuperer le data frame healthcare_dataset depuis kaggle
    #Au passage, on le charge aussi dans un fichier .csv de chemin : data/healthcare_dataset.csv
    #df = get_dataframe_kaggle('data/healthcare_dataset.csv')
    df = get_dataframe_from_csv('data/healthcare_dataset.csv')
    # Transformation en documents imbriqués
    #documents = transform_medical_df_to_documents(df)

    # 1. Configuration (Variables d'environnement)
    #mongo_user = os.getenv('MONGO_ROOT_USER', 'root')
    #mongo_pass = os.getenv('MONGO_ROOT_PASSWORD', 'examplepassword')
    #mongo_host = os.getenv('MONGO_HOST', 'mongodb')

    mongo_root = os.getenv('MONGO_ROOT_USER')
    mongo_root_password = os.getenv('MONGO_ROOT_PASSWORD')
    mongo_host = os.getenv('MONGO_HOST')
    mongo_write_user = os.getenv('MONGO_WRITE_USER')
    mongo_write_user_password = os.getenv('MONGO_WRITE_USER_PASSWORD')
    mongo_read_user = os.getenv('MONGO_READ_USER')
    mongo_read_user_password = os.getenv('MONGO_READ_USER_PASSWORD')

    #Apparement, les deux marchent une fois que l'on a correctement renseigné la base admin dans le fichier mongo-init.js pour
    #la création des roles avec la commande db = db.getSiblingDB('admin');
    #uri = f"mongodb://migration_user:password_migration_123@{mongo_host}:27017/"
    uri = f"mongodb://{mongo_write_user}:{mongo_write_user_password}@{mongo_host}:27017/"
    #uri = f"mongodb://migration_user:password_migration_123@{mongo_host}:27017/?authSource=admin"

    # 2. Pipeline de traitement

    try :    
        if df is not None:
            docs = transform_medical_df_to_documents(df)
            
            # 3. Migration finale
            success = insert_to_mongodb(docs, uri, "healthcare_db", "patients")

            if(success):
                print("\n" + "="*50)
                print(" FIN DE LA MISSION")
                print("="*50)
        
        
                print(f"Migration réussie : {len(docs)} patients insérés.")
            else:
                print(f"Pas d'insertion réalisées...")
    except Exception as e:
            print(f"Erreur lors de l'insertion MongoDB : {e}")

   

if __name__ == "__main__":
    migrate()


''' Commentaires sur l'uri de connexion

# Connexion à MongoDB (l'hôte est le nom du service dans docker-compose)

Plusieurs cas de figure possible

#Si on execute depuis la machine local, sans conteneur (script seul) vers mongodb sur la machine local également : on préciste juste le nom du service qui tourne sur local host
#uri = "mongodb://localhost:27017/"

#Si on execute depuis un autre conteneur (comme migrator) vers le conteneur mongodb, il faut utiliser mongodb comme hote
#uri = f"mongodb://{mongo_user}:{mongo_pass}@mongodb:27017/"

#Si on utilise depuis la machine local (script seul) vers le conteneur mongodb, il faut utiliser localhost car on ne peut pas accéder directement au conteneur
#Dans ce cas on tape sur le port 27017 de notre localhost et grâce à la redirection de port du conteneur, on tapera sur le conteneur mongodb
#uri = f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/"


#la manière la plus propre de le faire, qui ajuste les paramètre en fonction de la variable d'environnement    
#uri = f"mongodb://{mongo_root}:{mongo_root_password}@{mongo_host}:27017/"
#uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:27017/"
#uri = f"mongodb://migration_user:password_migration_123@{mongo_host}:27017/?authSource=healthcare_db"


#Apparement, les deux marchent une fois que l'on a correctement renseigné la base admin dans le fichier mongo-init.js pour
#la création des roles avec la commande db = db.getSiblingDB('admin');
#uri = f"mongodb://migration_user:password_migration_123@{mongo_host}:27017/"
uri = f"mongodb://{mongo_write_user}:{mongo_write_user_password}@{mongo_host}:27017/"
#uri = f"mongodb://migration_user:password_migration_123@{mongo_host}:27017/?authSource=admin"


'''
