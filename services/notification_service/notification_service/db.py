""" All the functionalities related to database """
from fastapi import HTTPException
from sqlmodel import create_engine, SQLModel, Session, select
from notification_service import settings, models



connection_string: str = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg")
engine = create_engine(connection_string, connect_args={},
                       pool_recycle=300, pool_size=10)


def create_tables() -> None:
    """ Function to create tables in database """
    SQLModel.metadata.create_all(engine)


def get_session():
    """ Function to get session """
    with Session(engine) as session:
        yield session


async def add_user_to_db(user: models.Users):
    """ Add user to the database """
    try:
        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
    except Exception as http_excep:
        raise http_excep


# get single user from db
async def get_user_from_db(user_id: int) -> models.Users | None:
    """ Get user from db """
    try:
        with Session(engine) as session:
            statement = select(models.Users).where(models.Users.user_id == user_id)
            user = session.exec(statement).first()
            session.add(user)
            session.commit()
            session.refresh(user)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return user
    except Exception as http_excep:
        raise http_excep


# edit user in db
async def edit_user_in_db(user_data: models.Users):
    """ Edit user in the database """
    try:
        with Session(engine) as session:
            existing_user = await get_user_from_db(user_data.user_id)
            if existing_user is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            # update existing user in db
            existing_user.email = user_data.email
            existing_user.phone = user_data.phone
            existing_user.shipping_address = user_data.shipping_address
            existing_user.payment_token = user_data.payment_token
            session.add(existing_user)
            session.commit()
            session.refresh(existing_user)
            return existing_user
        
    except HTTPException as http_excep:
        raise http_excep
    except Exception as e:
        raise e

# delete order from db
async def delete_user_in_db(user_id: int):
    """ Delete existing order in the database """
    with Session(engine) as session:
        session.delete(session.get(models.Users, user_id))
        session.commit()
