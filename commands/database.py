from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
import os


engine = create_engine(os.getenv("DATABASE_URL"))
Base = declarative_base()


class Prefix(Base):
    __tablename__ = "prefix"

    guild_id = Column(String, primary_key=True, nullable=False)
    prefix = Column(String, nullable=False)

    def __repr__(self):
        return "<(guild_id={0.guild_id}, prefix={0.prefix})>".format(self)


class Device(Base):
    __tablename__ = "device"

    device_id = Column(String, primary_key=True, nullable=False)
    signed_versions = Column(ARRAY(JSONB), nullable=False)

    def __repr__(self):
        return "<(device_id={0.device_id}, signed_versions={0.signed_versions}".format(self)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()