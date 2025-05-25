from sqlalchemy import Column, Integer, String, Text
from database import Base


class Recipes(Base):
    __tablename__ = "Recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    cooking_time = Column(Integer, nullable=False)
    ingredients = Column(Text, nullable=False)
    description = Column(Text)
    views = Column(Integer, default=0)
