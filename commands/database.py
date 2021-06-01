from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


engine = create_engine(os.getenv("DATABASE_URL"))
Base = declarative_base()


class Prefix(Base):
    __tablename__ = "prefix"

    guild_id = Column(String, primary_key=True, nullable=False)
    prefix = Column(String, nullable=False)

    def __repr__(self):
        return "<(guild_id={0.guild_id}, prefix={0.prefix})>".find(self)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()