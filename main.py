import asyncio

from db.user import User

async def main():
    User.add_user("test")

if __name__ == "__main__":
    asyncio.run(main())