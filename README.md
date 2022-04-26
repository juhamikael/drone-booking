# Kredentiaalit .env tiedostolle
--- 
## Luo .env tiedosto kansion projektin juureen ja CopyPastee alla olevat tiedostot siihen 
```
DATABASE_URL=postgresql://postgres:postgres@db:5432/drones
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=drones
PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=admin
```

# Käynnistys
```
docker-compose up --build
```
