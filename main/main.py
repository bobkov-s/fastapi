import sys
from sqlalchemy import select, update
from fastapi import FastAPI
import main.models
from main.schemas import RecipeIn, RecipeOut
from main.database import engine, session

# uvicorn main:app --reload
sys.path.append("/home/runner/work/fastapi/fastapi/main/")
app = FastAPI()


@app.on_event("startup")
async def shutdown():
    async with engine.begin() as conn:
        await conn.run_sync(main.models.Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await session.close()
    await engine.dispose()


# Эндпоинты API
@app.get("/")
def root():
    """
    Создает приветственное сообщение.
    """
    return {"message": "Добро пожаловать в API Кулинарной книги!"}


@app.post("/recipes/", response_model=RecipeOut)
async def post_recipes(recipe: RecipeIn) -> main.models.Recipes:
    """
    Создает новый рецепт в базе данных.

    - **title**: Название блюда (макс. 100 символов)
    - **cooking_time**: Время приготовления в минутах
    - **ingredients**: Список ингредиентов с количеством
    - **description**: Текстовое описание рецепта
    """

    new_recipe = main.models.Recipes(**recipe.dict())
    async with session.begin():
        session.add(new_recipe)
    return new_recipe


@app.get("/recipes/")
async def get_recipes():
    """
    Получает список всех рецептов с пагинацией.

    Сортировка:
        1. По количеству просмотров (по убыванию)
        2. По времени приготовления (по возрастанию)
    """
    resalt = await session.execute(
        select(main.models.Recipes).order_by(
            main.models.Recipes.views.desc(), main.models.Recipes.cooking_time.asc()
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
async def get_recipes_id(recipe_id: int):
    """
    Получает детальную информацию о рецепте по его ID.

    При каждом успешном запросе увеличивает счетчик просмотров на 1.

    Возвращает:
    - Название блюда
    - Время приготовления
    - Список ингредиентов
    - Описание рецепта
    """

    await session.execute(
        update(main.models.Recipes)
        .where(main.models.Recipes.id == recipe_id)
        .values(views=main.models.Recipes.views + 1)
    )
    await session.commit()

    resalt = await session.execute(
        select(main.models.Recipes).filter(main.models.Recipes.id == recipe_id)
    )

    res = resalt.scalars().first()
    return {
        "title": res.title,
        "cooking_time": res.cooking_time,
        "ingredients": res.ingredients,
        "description": res.description,
    }
