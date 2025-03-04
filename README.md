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