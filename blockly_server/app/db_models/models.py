from blockly_server.extensions import db # Import the database instance from your main Flask app
from sqlalchemy_serializer import SerializerMixin  # Assuming SerializerMixin is a dependency

class Projects(db.Model, SerializerMixin):
    project_id = db.Column('project_id', db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    info = db.Column(db.String(500))

    def __init__(self, title, info):
        self.title = title
        self.info = info
