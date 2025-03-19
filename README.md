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
# テスト用コンテナを立ち上げる
docker-compose -f docker-compose.test.yml up --build -d
# テスト用コンテナに入る
docker exec -it test_app /bin/bash
# 全体をテストする
python -m pytest -v
# モジュールごとにテストする
pytest -m pytest [テストしたいモジュールのパス] -v
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

### 管理画面

http://localhost:8001/admin/login

## モデルフィールドの追加方法

以下のファイルの`# ここにフィールドを追加`と記載されている箇所に追加する。

1. app/models/user.py
2. app/schemas/user_schema.py
3. app/admin/views/users.py
