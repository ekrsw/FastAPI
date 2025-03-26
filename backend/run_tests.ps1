# エラー発生時にスクリプトを停止
$ErrorActionPreference = "Stop"

Write-Host "テスト環境をセットアップしています..." -ForegroundColor Cyan

# 既存のコンテナをクリーンアップ
Write-Host "既存のコンテナをクリーンアップしています..." -ForegroundColor Yellow
docker-compose -f docker-compose.test.yml down

# テスト用コンテナを起動
Write-Host "テスト用コンテナを起動しています..." -ForegroundColor Yellow
docker-compose -f docker-compose.test.yml up -d

# コンテナの起動を待機（数秒）
Write-Host "コンテナの起動を待機しています（5秒）..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# テストを実行
Write-Host "テストを実行しています..." -ForegroundColor Green
docker exec test_app /bin/bash -c "python -m pytest -v"

# 終了時のクリーンアップ
Write-Host "テスト環境をクリーンアップしています..." -ForegroundColor Yellow
docker-compose -f docker-compose.test.yml down

Write-Host "テスト実行が完了しました" -ForegroundColor Cyan
