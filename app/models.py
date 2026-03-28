from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from pydantic import EmailStr   #insert at top of the file

class User(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password: str
    role:str = ""

class Admin(User, table=True):
    role:str = "admin"

class RegularUser(User, table=True):
    role:str = "regular_user"

    todos: list['Todo'] = Relationship(back_populates="user")
    creatures: list['Creatures'] = Relationship(back_populates="user")

class TodoCategory(SQLModel, table=True):
    category_id: int = Field(foreign_key="category.id", primary_key=True)
    todo_id: int = Field(foreign_key="todo.id", primary_key=True)


class CreatureCategory(SQLModel, table=True):
    category_id: int = Field(foreign_key="zeldacategory.id", primary_key=True)
    creature_id: int = Field(foreign_key="creatures.id", primary_key=True)

class ZeldaCategory(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="regularuser.id")
    name: str

    creatures: list['Creatures'] = Relationship(back_populates="categories",link_model=CreatureCategory)

class Category(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="regularuser.id")
    text:str

    todos:list['Todo'] = Relationship(back_populates="categories", link_model=TodoCategory)

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="regularuser.id")
    text:str
    done: bool = False

    user: RegularUser = Relationship(back_populates="todos")
    categories:list['Category'] = Relationship(back_populates="todos", link_model=TodoCategory)

    def toggle(self):
        self.done = not self.done
    
    def get_cat_list(self):
        return ', '.join([category.text for category in self.categories])
    

class TodoCreate(SQLModel):
    text:str

class TodoResponse(SQLModel):
    id: Optional[int] = Field(primary_key=True, default=None)
    text:str
    done: bool = False

class TodoUpdate(SQLModel):
    text: Optional[str] = None
    done: Optional[bool] = None    

class UserCreate(SQLModel):
    username:str
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)

class Token(SQLModel):
    access_token: str
    token_type: str

class UserResponse(SQLModel):
    id: int
    username: str = Field(max_length=255)
    email: EmailStr = Field(max_length=255)
    role: str

class Creatures(SQLModel, table=True):
    id: Optional[int] = Field(default = None, primary_key=True)
    name: str
    commonloc: Optional[str] = Field(default = None)
    user: RegularUser = Relationship(back_populates = "creatures")
    user_id: Optional[int] = Field(foreign_key="regularuser.id")
    categories: list['ZeldaCategory'] = Relationship(back_populates="creatures",link_model=CreatureCategory)

class CreatureCreate(SQLModel):
    name: str
    commonloc: Optional[str] = Field(default=None)

class CreatureResponse(SQLModel):
    id: int
    name: str
    commonloc: Optional[str] = None

class UserCreature(SQLModel, table=True):
    user_id: int = Field(foreign_key="regularuser.id", primary_key=True)
    creature_id: int = Field(foreign_key="creatures.id", primary_key=True)