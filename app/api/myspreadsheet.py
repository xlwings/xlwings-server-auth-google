import xlwings as xw
from fastapi import APIRouter, Body, Security

from .. import settings
from ..core.auth import User, authenticate, authorize

# Require authentication for all endpoints for this router
router = APIRouter(
    dependencies=[Security(authenticate)],
    prefix="/myspreadsheet",
    tags=["My Spreadsheet"],
)


@router.post("/hello1")
async def hello1(data: dict = Body):
    """This endpoint is protected by the router"""
    with xw.Book(json=data) as book:
        sheet = book.sheets[0]
        cell = sheet["A1"]
        if cell.value == "Hello xlwings!":
            cell.value = "Bye xlwings!"
        else:
            cell.value = "Hello xlwings!"
        return book.json()


@router.post("/hello2")
async def hello2(data: dict = Body, current_user: User = Security(authorize)):
    """This is how you access the user object"""
    with xw.Book(json=data) as book:
        sheet = book.sheets[0]
        cell = sheet["A2"]
        user_name = current_user.email.split("@")[0]
        if cell.value == f"Hello {user_name}!":
            cell.value = f"Bye {user_name}!"
        else:
            cell.value = f"Hello {user_name}!"
        return book.json()


@router.post("/hello3")
async def hello3(
    data: dict = Body,
    current_user: User = Security(authorize, scopes=settings.scopes),
):
    """You can require specific permissions by specifying scopes. In this endpoint, we
    require the user to be an admin. The `auth` module will enforce this by checking if
    the user is in the admin group.
    """
    with xw.Book(json=data) as book:
        sheet = book.sheets[0]
        cell = sheet["A3"]
        user_name = current_user.email.split("@")[0]
        if cell.value == f"Hello {user_name}, you are an admin!":
            cell.value = f"Bye {user_name}, you are an admin!"
        else:
            cell.value = f"Hello {user_name}, you are an admin!"
        return book.json()
