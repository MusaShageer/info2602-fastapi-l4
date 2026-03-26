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


if __name__ == "__main__":
    cli()