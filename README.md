# Flux Study
Now live in beta, as [FluxStudy on Heroku](https://fluxstudy-3cc38d8670a8.herokuapp.com)!
This webapp project is for everyone, including me, who wishes they could do more with their time. I'm developing this website so that I can keep track of my assignments and other to-dos and gain helpful insights into my study habits.

## Features
### Current
This app is in beta testing, and has the following features:
- Tracking for semesters, courses, assignments, and study sessions
- To-do list functionality
- Progressive web app capabilities
- Graphs
- Customizable course colors

### Planned
Over the next several months, I plan to develop:
- Calendar/agenda tracking, maybe with Google Calendar integration
- More graphs
- UI enhancements, including more themes, potential wrap layout, and better mobile experience
- A helpful getting started tutorial
- Statistical analysis of study habits
- Guided study timers
- Grade analysis and breakdown
- Class schedule
- Social networking features for users in the same classes, at the same universities
- Notifications for todos and due dates
- And more, as beta testing shows the need

## Setting Up a Development Environment
### Flask and Basics
Backend code is written in Python 3, and HTML Jinja2 templates are rendered and filled by the Flask framework. Postgres is used on the server, but SQLite works out of the box if you don't have Postgres. SQLAlchemy is the database software. All requirements are listed and can be pipped to build a full development environment. To run a local site, do the following:
1. Install [the latest Python](https://www.python.org/downloads/). I also use [VSCode](https://code.visualstudio.com) with the Python extensions, [Postgres](https://www.postgresql.org), [Homebrew](https://brew.sh) and the [Xcode Command Line Tools](https://mac.install.guide/commandlinetools/)
2. Clone this repository.
```bash
git clone https://github.com/Amenhotep314/study.git
```
3. Prepare the Python environment.
```bash
cd study
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
4. Create a config file.
```bash
touch src/config.json
```
5. Generate a secret key. In a python shell:
```python
import secrets
secrets.token_hex(64)
```
6. Now use that key as an environment variable. In config.json, write
```json
{
    "SECRET_KEY": "YOUR_SECRET_KEY_FROM_ABOVE"
}
```
7. Compile the translations.
```bash
chmod a+x babel_actions.sh
./babel_actions.sh
```
8. Run the test server.
```bash
flask --app src run
```

### Postgres
If you want to configure Postgres, do the following:
1. Install it using Homebrew (link to Homebrew is above).
```bash
brew install postgresql
```
2. Initialize a db and start the server. You may need to replace 14 with the version you have installed.
```bash
initdb /opt/homebrew/var/postgresql@14/
brew services start postgresql@14
psql postgres
```
3. Create the user and database. Your username and password can be anything, just remember them.
```sql
CREATE ROLE your_username WITH LOGIN PASSWORD 'your_password';
ALTER ROLE your_username CREATEDB;
```
4. Log out, then back in to the database from your new role.
```bash
psql postgres -U your_username
```
5. Create the database
```sql
CREATE DATABASE study;
GRANT ALL PRIVILEGES ON DATABASE study TO your_username;
```
6. In src/config.json, below your secret key, add this line:
```json
"SQLALCHEMY_DATABASE_URI": "postgresql://your_username:your_password@localhost/study"
```

## Project Structure Overview
At the root level:
 - This file, README.md, and LICENSE.txt are for community reference
 - .github contains specifications for dependabot auto-bumping of dependency versions. .gitignore excludes generated and secure files from commits
 - Procfile defines server behaviors. runtime.txt specifies the Python version in use on the server. requirements.txt lists the dependencies.
 - babel.cfg lists locations to look for translatable strings. babel_actions.sh is an executable that compiles translations. It should be run before and after translating.
 - sqlite.showtables.sql is a handy script to see tables in the absence of Postgres, but using the VSCode SQLTools SQLite package.
 - **src** contains the source code
    - \_\_init\_\_.py creates new sessions when they begin and handles all the configuration
    - auth.py contains Flask routes for all pages that can be viewed when logged out
    - main.py contains Flask routes for all pages that require a login to view
    - ajax.py contains Flask routes for all calls made asynchronously by client-side JavaScript
    - models.py contains database objects that correspond to tables in the database
    - forms.py contains Form objects that are used to make webforms to get user input
    - db_util.py contains miscellaneous functions for database reading and writing
    - util.py contains miscellaneous functions that do not deal directly with the database, mostly timezone things right now
    - config.json can be placed at this level and used to store the SECRET_KEY environment variable
    - The translations directory contains translated strings
    - static contains all static resources and scripts that are not executed server-side:
       - app.webmanifest defines PWA properties. serviceworker.js is loaded on login to provide PWA behavior. Various icons here are for PWA use as well.
       - scripts.js contains all non-serviceworker JavaScript, including timers, chart construction, and ajax page updates.
       - stylesheet.css defines styling properties that are universal across the site. greensboro_winter.css and serenity_now.css define configurable themes.
       - The Chart.js and JQuery libraries are also kept here, outside of a package manager. They must be kept up to date manually. In all honesty, I'm not exactly sure where I got them from.
    - templates contains HTML templates that are filled by Flask using Jinja.
       - base.html contains HTML that appears on every page of the site
       - base_auth.html appears on every logged-out page
       - base_main.html appears on every logged-in page