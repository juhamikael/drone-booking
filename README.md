# Credentials for .env file
--- 
## Create an .env file in the root of the project folder and attach the files below to it 
```
DATABASE_URL=postgresql://postgres:postgres@db:5432/drones
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=drones
PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=admin
```

# Startup
```
docker-compose up --build
```
