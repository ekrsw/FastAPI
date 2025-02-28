import asyncio
from models.user import User


async def main():
    await User.create_user(
        username="test_user",
        plain_password="initial_password",
        is_admin=False
        )
    await User.update_password(user_id=1, plain_password="test_password")
    users = await User.get_all_users()
    for user in users:
        print(f"username: {user.username}, password: {user.hashed_password}, is_admin: {user.is_admin}")

if __name__ == "__main__":
    asyncio.run(main())
