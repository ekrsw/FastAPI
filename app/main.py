import asyncio
from app.models.user import User

async def main():
    await User.create_user(username="test_user", password="test_password")
    user = await User.get_user_by_username("test_user")
    print(user.username)

if __name__ == "__main__":
    asyncio.run(main())