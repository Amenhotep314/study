from flask import current_app
import click
import os


# Work in progress


@current_app.cli.group()
def translate():
    pass


@translate.command()
def update():
    os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .')
    os.system('pybabel update -i messages.pot -d src/translations')


@translate.command()
def compile():
    os.system('pybabel compile -d src/translations')


@translate.command()
@click.argument("lang")
def init(lang):
    os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .')
    os.system('pybabel init -i messages.pot -d src/translations -l ' + lang)
