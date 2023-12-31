pybabel extract -F babel.cfg -k _l -o messages.pot .
pybabel update -i messages.pot -d src/translations
pybabel compile -d src/translations
# pybabel init -i messages.pot -d src/translations -l fr