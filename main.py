import asyncio

from db.user import User

async def main():
    await User.create_user("john")
    await User.create_user("jane")
    await User.create_user("eisuke")

    await User.delete_user(1)
    user = await User.get_user_by_id(1)
    print(user)

if __name__ == "__main__":
    asyncio.run(main())