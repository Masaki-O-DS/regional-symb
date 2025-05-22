from sqlalchemy import Column, Integer, String
from app.db.database import Base


class Resident(Base):
    __tablename__ = "residents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    phone = Column(String)
    email = Column(String, nullable=True)
    join_date = Column(String, nullable=True)
