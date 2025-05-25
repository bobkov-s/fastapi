from pydantic import BaseModel


# Базовый рецепт
class RecipeBase(BaseModel):
    title: str  # Название блюда
    cooking_time: int  # Время приготовления
    ingredients: str  # Список ингридиентов
    description: str  # Текстовое описание


# Создание блюда
class RecipeIn(RecipeBase):
    pass


class RecipeOut(RecipeBase):
    id: int
    views: int

    class Config:
        orm_mode = True
