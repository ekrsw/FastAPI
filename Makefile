.PHONY: reset_db
reset_db:
	@echo "docker composeを停止し、ボリュームを削除します"
	@docker-compose down -v
	@echo "PostgreSQLのデータを削除します"
	@rm -rf docker/postgresql/data/*
	@echo "マイグレーションファイルを削除します"
	@rm -rf app/migrations/versions/*
