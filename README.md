# テスト
```
python -m pytest -v
```

# マイグレーション
## マイグレーションファイルの作成
`alembic revision --autogenerate -m "create tables"`
## マイグレーションファイルの内容をDBへ反映
`alembic upgrade head`