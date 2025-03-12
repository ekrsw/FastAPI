from .database import Database


class AsyncContextManager:
    async def __aenter__(self):
        db = Database()
        await db.init()
        session_factory = await db.connect_db()
        self.session = session_factory()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            # エラーが発生した場合はロールバック、そうでなければコミット
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            # 最後にセッションをクローズ
            await self.session.close()