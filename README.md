### テスト
```
python -m pytest -v
```
#### マイグレーションファイルの作成
```
cd app
alembic revision --autogenerate -m "create tables"
```
#### マイグレーションファイルの内容をDBへ反映
```
ad app
alembic upgrade head
```

http://localhost:8080/