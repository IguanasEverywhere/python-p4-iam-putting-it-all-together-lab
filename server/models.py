from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Cannot access password hash")

    @password_hash.setter
    def password_hash(self, password):
        hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    recipes = db.relationship('Recipe', back_populates='user', cascade='all, delete-orphan')

    serialize_rules = ('-recipes.user',)


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    __table_args__ = (
        db.CheckConstraint("length(instructions) >= 50"),
    )

    # @validates('instructions')
    # def validate_instructions(self, key, instructions):
    #     if len(instructions) < 50:
    #         raise ValueError("Instructions should be at least 50 characters long.")
    #     return instructions


    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', back_populates='recipes')

    serialize_rules = ('-users.recipes',)

