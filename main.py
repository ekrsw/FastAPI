import asyncio
from models.user import User


async def main():
    await User.create_user("test_user")

if __name__ == "__main__":
    asyncio.run(main())