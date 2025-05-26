# import sys
from fastapi import Depends, FastAPI
from sqlalchemy import select, update

import models
from database import AsyncSession, a_sess, engine
from schemas import RecipeIn, RecipeOut

# uvicorn main:app --reload
# sys.path.append("/home/runner/work/fastapi/fastapi/main/")
app = FastAPI()


@app.on_event("startup")
async def shutdown():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


async def get_db() -> AsyncSession:
    async with a_sess() as session:
        yield session


# @app.on_event("shutdown")
# async def shutdown():
#     await session.close()
#     await engine.dispose()


# Эндпоинты API
@app.get("/")
def root():
    """
    Создает приветственное сообщение.
    """
    return {"message": "Добро пожаловать в API Кулинарной книги!"}


@app.post("/recipes/", response_model=RecipeOut)
async def post_recipes(recipe: RecipeIn, db=Depends(get_db)) -> models.Recipes:
    """
    Создает новый рецепт в базе данных.

    - **title**: Название блюда (макс. 100 символов)
    - **cooking_time**: Время приготовления в минутах
    - **ingredients**: Список ингредиентов с количеством
    - **description**: Текстовое описание рецепта
    """

    new_recipe = models.Recipes(**recipe.dict())
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)
    return new_recipe


@app.get("/recipes/")
async def get_recipes(db=Depends(get_db)):
    """
    Получает список всех рецептов с пагинацией.

    Сортировка:
        1. По количеству просмотров (по убыванию)
        2. По времени приготовления (по возрастанию)
    """

    resalt = await db.execute(
        select(models.Recipes).order_by(
            models.Recipes.views.desc(), models.Recipes.cooking_time.asc()
        )
    )

    res = resalt.scalars().all()

    return [
        {
            "title": res[x].title,
            "views": res[x].views,
            "cooking_time": res[x].cooking_time,
        }
        for x in range(len(res))
    ]


@app.get("/recipes/{recipe_id}")
async def get_recipes_id(recipe_id: int, db=Depends(get_db)):
    """
    Получает детальную информацию о рецепте по его ID.

    При каждом успешном запросе увеличивает счетчик просмотров на 1.

    Возвращает:
    - Название блюда
    - Время приготовления
    - Список ингредиентов
    - Описание рецепта
    """

    await db.execute(
        update(models.Recipes)
        .where(models.Recipes.id == recipe_id)
        .values(views=models.Recipes.views + 1)
    )
    await db.commit()

    resalt = await db.execute(
        select(models.Recipes).filter(models.Recipes.id == recipe_id)
    )

    res = resalt.scalars().first()
    return {
        "title": res.title,
        "cooking_time": res.cooking_time,
        "ingredients": res.ingredients,
        "description": res.description,
    }
