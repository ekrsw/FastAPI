import asyncio

from db.user import User

async def main():
    await User.create_user("test")

    user = await User.get_user_by_id(1)
    print(user.username)

if __name__ == "__main__":
    asyncio.run(main())