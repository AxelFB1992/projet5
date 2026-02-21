from pymongo import MongoClient
import csv

uri = "mongodb://localhost:27017/"
client = MongoClient(uri)

try:
    database = client.get_database("axel")
    healthcol = database.get_collection("Collection2")

    # Query for a movie that has the title 'Back to the Future'
    #query = { "Name": "Bobby JacksOn" }
    #movie = movies.find_one(query)

    #print(movie)

    #healthcol.insert_one({"toto":"tata"})
    
    #on ouvre le fichier csv avec la fonction withopen
    csv_file = "healthcare_dataset.csv"
    with open(csv_file, 'r', encoding='utf-8') as f:
    #print(f.read())
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            print("Name", row['Name'], "Age", row['Age'])
            document = {"Name": row['Name'],"Age": row['Age']} 
            result = healthcol.insert_one(document)
		
    client.close()

except Exception as e:
    raise Exception("Unable to find the document due to the following error: ", e)


"""
ouvrir le ficheir csv ("with open...")
utiliser lib standard csv pour mettre le contenu du csv dans une variable (ou un tableau de variables) https://docs.python.org/fr/3/library/csv.html
se connecter à mongo
pour chaque element du tableau, insérer un document (à partir de l'element du tableau)

"""
