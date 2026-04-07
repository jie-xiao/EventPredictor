"""P2.1 Auth Flow End-to-End Test"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.database import init_db, get_session_factory, cleanup_db
from app.services.auth_service import auth_service


async def main():
    # Clean start
    await cleanup_db()

    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "eventpredictor.db")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            print("DB locked, using existing DB")

    await init_db()
    factory = get_session_factory()

    async with factory() as session:
        # 1. Register
        user = await auth_service.register(session, "testuser", "test@example.com", "password123")
        print(f"1. Register OK: id={user.id}, username={user.username}")

        # 2. Login
        user2, access, refresh = await auth_service.login(session, "testuser", "password123")
        print(f"2. Login OK: access_token={access[:30]}...")

        # 3. Refresh
        new_access, new_refresh = await auth_service.refresh(session, refresh)
        print(f"3. Refresh OK: new_access={new_access[:30]}...")

        # 4. Decode
        from app.core.security import decode_token
        payload = decode_token(new_access)
        print(f"4. Decode OK: sub={payload['sub']}, username={payload['username']}")

        # 5. Logout
        await auth_service.logout(session, new_refresh)
        print("5. Logout OK")

        print()
        print("ALL AUTH TESTS PASSED!")

    await cleanup_db()


if __name__ == "__main__":
    asyncio.run(main())
