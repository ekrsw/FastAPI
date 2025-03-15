#!/bin/bash
set -e

# PostgreSQLのデフォルトデータベース（postgres）に接続
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    -- my_databaseが存在しない場合のみ作成
    SELECT 'CREATE DATABASE my_database' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'my_database')\gexec
    GRANT ALL PRIVILEGES ON DATABASE my_database TO $POSTGRES_USER;
EOSQL
