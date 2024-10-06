from flask_sqlalchemy import SQLAlchemy
from blockly_server.app.process.process_control import ProcessManager
from blockly_server.app.robot.roboclass import Agent

db = SQLAlchemy()

process_manager = ProcessManager()

agent = Agent()  # FOSSBot agent for communication with the robot

