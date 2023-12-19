import asyncio
from pathlib import Path

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.domain.teams.models import TeamRoles
from app.lib.settings import db

here = Path(__file__).parent
engine = create_async_engine(
    URL(
        drivername="postgresql+asyncpg",
        username=db.USER,
        password=db.PASSWORD,
        host=db.HOST,
        port=db.PORT,
        database=db.NAME,
        query={},  # type:ignore[arg-type]
    ),
    echo=db.ECHO,
    poolclass=NullPool,
)

sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)


session = sessionmaker()


raw_users = [
    {
        "id": "97108ac1-ffcb-411d-8b1e-d9183399f63b",
        "email": "phyoakl@hexcode.tech",
        "name": "Phyo Arkar Lwin",
        "password": "0xc0d3admin",
        "is_superuser": True,
        "is_active": True,
    },
    {
        "id": "5ef29f3c-3560-4d15-ba6b-a2e5c721e4d2",
        "email": "admin@hexcode.tech",
        "name": "Scrum Master",
        "password": "0xc0d3admin",
        "is_superuser": False,
        "is_active": True,
    },
    {
        "id": "6ef29f3c-3560-4d15-ba6b-a2e5c721e4d3",
        "email": "dev@hexcode.tech",
        "name": "Developer",
        "password": "0xc0d3admin",
        "is_superuser": False,
        "is_active": True,
    },
    {
        "id": "7ef29f3c-3560-4d15-ba6b-a2e5c721e4e1",
        "email": "client@hexcode.tech",
        "name": "Customer",
        "password": "0xc0d3admin",
        "is_superuser": False,
        "is_active": False,
    },
]


raw_teams = [
    {
        "id": "8ef29f3c-3560-4d15-ba6b-a2e5c721e4d4",
        "slug": "scrum-master",
        "name": "ScrumMaster",
        "description": "This is a description for Zone Partner team.",
        "owner_id": "97108ac1-ffcb-411d-8b1e-d9183399f63b",
    },
    {
        "id": "9ef29f3c-3560-4d15-ba6b-a2e5c721e4d5",
        "slug": "developer",
        "name": "Developer",
        "description": "This is a description for Main Partner team.",
        "owner_id": "97108ac1-ffcb-411d-8b1e-d9183399f63b",
    },
    {
        "id": "aef29f3c-3560-4d15-ba6b-a2e5c721e4d6",
        "slug": "customer",
        "name": "Customer",
        "description": "This is a description for Biker team.",
        "owner_id": "97108ac1-ffcb-411d-8b1e-d9183399f63b",
    },
]
raw_membership = [
    {
        "user_id": "6ef29f3c-3560-4d15-ba6b-a2e5c721e4d3",  # partner@hexcode.tech
        "team_id": "8ef29f3c-3560-4d15-ba6b-a2e5c721e4d4",  # Parnter
        "role": TeamRoles.MEMBER,
        "is_owner": False,
    },
    {
        "user_id": "5ef29f3c-3560-4d15-ba6b-a2e5c721e4d2",  # main@hexcode.tech
        "team_id": "9ef29f3c-3560-4d15-ba6b-a2e5c721e4d5",  # Main Parnter
        "role": TeamRoles.MEMBER,
        "is_owner": False,
    },
    {
        "user_id": "7ef29f3c-3560-4d15-ba6b-a2e5c721e4e1",  # partner@hexcode.tech
        "team_id": "aef29f3c-3560-4d15-ba6b-a2e5c721e4d6",  # Parnter
        "role": TeamRoles.MEMBER,
        "is_owner": False,
    },
]


async def seed_db(
    engine: AsyncEngine,
    sessionmaker: async_sessionmaker[AsyncSession],
    users: list[dict],
    teams: list[dict],
    memberships: list[dict],
    drop: bool = False,
) -> None:
    """Populate test database with.

    Args:
        engine: The SQLAlchemy engine instance.
        sessionmaker: The SQLAlchemy sessionmaker factory.
        users: Test users to add to the database
        teams: Test teams to add to the database
        memberships: Test mebermship to add to the database
        drop: Whether to drop the existing database

    """

    from app.domain.accounts.services import UserService
    from app.domain.teams.services import TeamMemberService, TeamService
    from app.lib.db import orm  # pylint: disable=[import-outside-toplevel,unused-import]

    metadata = orm.DatabaseModel.registry.metadata
    async with engine.begin() as conn:
        if drop:
            await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    async with UserService.new(sessionmaker()) as users_service:
        await users_service.create_many(users)
        await users_service.repository.session.commit()
    async with TeamService.new(sessionmaker()) as teams_services:
        for raw_team in teams:
            await teams_services.create(raw_team)
        await teams_services.repository.session.commit()
    async with TeamMemberService.new(sessionmaker()) as membership_services:
        for membership in memberships:
            await membership_services.create(membership)
        await membership_services.repository.session.commit()


if __name__ == "__main__":
    asyncio.run(
        seed_db(
            engine=engine,
            sessionmaker=sessionmaker,
            users=raw_users,
            teams=raw_teams,
            memberships=raw_membership,
            drop=True,
        ),
    )
