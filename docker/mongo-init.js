// Ce script est exécuté par MongoDB au premier lancement (dans /docker-entrypoint-initdb.d/)
print("Scripts de création des rôles !");

//db = db.getSiblingDB('healthcare_db');
db = db.getSiblingDB('admin');

const migrationUser = process.env.MONGO_WRITE_USER || 'migration_user';
const migrationPass = process.env.MONGO_WRITE_USER_PASSWORD || 'password_migration_123';

const analystUser = process.env.MONGO_READ_USER || 'analyst_user';
const analystPass = process.env.MONGO_READ_PASSWORD || 'password_analyst_456';

// 1. Création du rôle pour le script de migration (Moindre privilège)
db.createUser({
  user: migrationUser,
  pwd: migrationPass,
  roles: [
    { role: "readWrite", db: "healthcare_db" }
  ]
});

// 2. Création du rôle pour l'analyse (Lecture seule)
db.createUser({
  user: analystUser,
  pwd: analystPass,
  roles: [
    { role: "read", db: "healthcare_db" }
  ]
});

print("Utilisateurs et rôles créés avec succès !");
