from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .database import engine, Base
from . import models


app = FastAPI()


Base.metadata.create_all(bind=engine)


templates = Jinja2Templates(directory="app/templates")


app.mount("/static", StaticFiles(directory="app/static"), name="static")


from .routes import books, readers, issues, pages, recommendations

app.include_router(books.router)
app.include_router(readers.router)
app.include_router(issues.router)
app.include_router(pages.router)
app.include_router(recommendations.router)