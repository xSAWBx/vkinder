import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

from config import db_url_object

Base = declarative_base()
Session = sessionmaker()


class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)


def add_user(engine, profile_id, worksheet_id):
    session = Session(bind=engine)
    to_db = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
    session.add(to_db)
    session.commit()
    session.close()


def check_user(engine, profile_id, worksheet_id):
    session = Session(bind=engine)
    from_db = session.query(Viewed).filter(
        Viewed.profile_id == profile_id,
        Viewed.worksheet_id == worksheet_id
    ).first()
    session.close()
    return True if from_db else False


if __name__ == '__main__':
    engine = create_engine(db_url_object)
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)

    add_user(engine, 2113, 12451200)
    res = check_user(engine, 2113, 12451200)
    print(res)
