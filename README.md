### セットアップ
```
git clone
copy .env.example .env
```

### テスト
```
cd app
python -m pytest -v
```
#### マイグレーションファイルの作成
```
cd app
alembic revision --autogenerate -m "create tables"
```
#### マイグレーションファイルの内容をDBへ反映
```
cd app
alembic upgrade head
```

http://localhost:8080/

### mainの実行
```
python -m app.main
```

### Databaseへの接続
> コンテナへの接続
```
docker exec -it Postgres_db /bin/bash
```
> PostgreSQLへの接続
```
psql -h [host名] -p [ポート番号] -U [ユーザー名] -d [データベース名]
``` 
