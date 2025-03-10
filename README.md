### セットアップ

#### Github から clone

```
git clone
copy .env.example .env
```

#### コンテナの起動

```
docker-compose up --build -d
```

#### API コンテナに入る

```
docker exec -it FastAPI_app /bin/bash
```

#### マイグレーション

```
cd app
alembic revision --autogenerate -m "create tables"
alembic upgrade head
```

### テスト

```
cd app
python -m pytest -v
```

```
docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit
pytest -m pytest [テストしたいモジュール]
```

#### マイグレーションファイルの作成

```
cd app
alembic revision --autogenerate -m "create tables"
```

#### マイグレーションファイルの内容を DB へ反映

```
cd app
alembic upgrade head
```

http://localhost:8080/

### main の実行

```
python -m app.main
```

### Database への接続

> コンテナへの接続

```
docker exec -it Postgres_db /bin/bash
```

> PostgreSQL への接続

```
psql -h [host名] -p [ポート番号] -U [ユーザー名] -d [データベース名]
```
