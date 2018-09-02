# This script is run when the postgres container starts up. It'll create the 
# halliganhelper user, the halliganhelper database, and configure the proper
# permissions.

HH_PW=$(cat /run/secrets/db_password)

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO
    $do
    IF NOT EXISTS (
        SELECT
        FROM pg_catalog.pg_roles
        WHERE rolname = 'halliganhelper'
    ) THEN
        CREATE USER halliganhelper WITH PASSWORD '$HH_PW';
        CREATE DATABASE halliganhelper;
        GRANT ALL PRIVILEGES ON DATABASE halliganhelper TO halliganhelper;
    END IF;
    END
    $do$;
EOSQL
