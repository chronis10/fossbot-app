from flask_sqlalchemy import SQLAlchemy
from app.process.process_control import ProcessManager
from app.robot.roboclass import Agent

db = SQLAlchemy()

process_manager = ProcessManager()

agent = Agent()  # FOSSBot agent for communication with the robot

