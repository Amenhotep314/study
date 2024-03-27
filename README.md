# Flux Study
Now live in beta, as [FluxStudy on Heroku](https://fluxstudy-3cc38d8670a8.herokuapp.com)!
This webapp project is for everyone, including me, who wishes they could do more with their time. I'm developing this website so that I can keep track of my assignments and other to-dos and gain helpful insights into my study habits.

## Features
This app is in beta testing, and has the following features:
- Tracking for semesters, courses, assignments, and study sessions
- To-do list functionality
- Progressive web app capabilities
- Graphs
- Customizable course colors

## Planned Features
Over the next several months, I plan to develop:
- Calendar/agenda tracking
- More graphs
- UI enhancements, including customizable more themes and potential wrap layout
- Statistical analysis of study habits
- Guided study timers
- Grade analysis and breakdown
- Class schedule
- Social networking features for users in the same classes, at the same universities
- And more, as beta testing shows the need

## Setup
Backend code is written in Python 3, and HTML Jinja2 templates are rendered and filled by the Flask framework. SQLAlchemy is the database software. All requirements are listed and can be pipped to build a full development environment. To run a mirror, do the following:
1. Mirror this repository.
```bash
git clone https://github.com/Amenhotep314/study.git
```
2. Prepare the Python environment.
```bash
cd study
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
3. Generate a secret key. In a python shell:
```python
import secrets
secrets.token_hex(64)
```
3. Now use that key as an environment variable.
```bash
export SECRET_KEY = "YOUR_GENERATED_VALUE_FROM_ABOVE"
```
4. Compile the translations.
```bash
chmod a+x babel_actions.sh
./babel_actions.sh
```
4. Run the test server.
```bash
flask --app src run
```