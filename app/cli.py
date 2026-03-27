import typer
import csv
from tabulate import tabulate
from sqlmodel import select
from app.database import create_db_and_tables, get_cli_session, drop_all
from app.models import *
from app.auth import encrypt_password

cli = typer.Typer()

@cli.command()
def initialize():
    with get_cli_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = RegularUser(username='bob', email='bob@mail.com',password=encrypt_password('bobpass'))
        rick = RegularUser(username='rick', email='rick@mail.com', password=encrypt_password('rickpass'))
        sally = RegularUser(username='sally', email='sally@mail.com', password=encrypt_password('sallypass'))
        db.add_all([bob, rick, sally])  #add all can save multiple objects at once
        db.commit()

        with open('zelda.csv') as file:
            reader = csv.DictReader(file)
            for row in reader:
                new_zelda = Creatures(
                    id=int(row['Reference Number']),
                    name= str(row['Name']),
                    commonloc=str(row['Common Locations 1'])
                )
                db.add(new_zelda)  #queue changes for saving
            db.commit()

        print("Database Initialized")




@cli.command()
def list_creatures():
    with get_cli_session() as db: # Get a connection to the database
        data = []
        for creature in db.exec(select(Creatures)).all():
            data.append(
                [creature.id, creature.name, creature.commonloc])
        print(tabulate(data, headers=["id", "name", "common location"]))

@cli.command()
def get_user(username:str):
    with get_cli_session() as db: # Get a connection to the database
        user = db.exec(select(RegularUser).where(RegularUser.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)

@cli.command()
def get_creature(name:str):
    with get_cli_session() as db: # Get a connection to the database
        creature = db.exec(select(Creatures).where(Creatures.name == name)).first()
        if not creature:
            print(f'{name} not found!')
            return
        print(creature)

@cli.command()
def get_all_creatures():
    with get_cli_session() as db:
        all_creatures = db.exec(select(Creatures)).all()
        if not all_creatures:
            print("No users found")
        else:
            for creature in all_creatures:
                print(creature)

@cli.command()
def change_name(name: str, new_name:str):
    with get_cli_session() as db: # Get a connection to the database
        creature = db.exec(select(Creatures).where(Creatures.name == name)).first()
        if not creature:
            print(f'{name} not found! Unable to update email.')
            return
        creature.name = new_name
        db.add(creature)
        db.commit()
        print(f"Updated {creature.id}'s name to {creature.name}")

@cli.command()
def delete_creature(name: str):
    with get_cli_session() as db:
        creature = db.exec(select(Creatures).where(Creatures.name == name)).first()
        if not creature:
            print(f'{name} not found! Unable to delete user.')
            return
        db.delete(creature)
        db.commit()
        print(f'{name} deleted')

@cli.command()
def add_creature(new_name: str, commonloc: str):
    with get_cli_session() as db:
        new_creature = Creatures(
            name=new_name,
            commonloc=commonloc
        )

        db.add(new_creature)
        db.commit()

        print("Creature added successfully")

@cli.command()
def add_category(name: str, user_id: int):
    with get_cli_session() as db:
        category = ZeldaCategory(
            name=name,
            user_id=user_id
        )

        db.add(category)
        db.commit()

        print(f"Category '{name}' created")

@cli.command()
def add_creature_to_category(creature_name: str, category_name: str):
    with get_cli_session() as db:
        
        # Find creature
        creature = db.exec(
            select(Creatures).where(Creatures.name == creature_name)
        ).first()

        if not creature:
            print("Creature not found")
            return

        # Find category
        category = db.exec(
            select(ZeldaCategory).where(ZeldaCategory.name == category_name)
        ).first()

        if not category:
            print("Category not found")
            return

        # Link them (THIS is the key part)
        category.creatures.append(creature)

        db.add(category)
        db.commit()

        print(f"{creature_name} added to {category_name}")

@cli.command()
def assign_creature_to_user(creature_name: str, username: str):
    with get_cli_session() as db:

        # Find creature
        creature = db.exec(select(Creatures).where(Creatures.name == creature_name)).first()

        if not creature:
            print("Creature not found")
            return

        # Find user
        user = db.exec(select(RegularUser).where(RegularUser.username == username)).first()

        if not user:
            print("User not found")
            return

        # Assign creature
        creature.user_id = user.id

        db.add(creature)
        db.commit()

        print(f"{creature_name} assigned to {username}")

if __name__ == "__main__":
    cli()