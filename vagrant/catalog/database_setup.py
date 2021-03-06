import sys

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = "user"

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	picture = Column(String(250))


class Category(Base):
	__tablename__ = "category"
	name = Column(String(80), nullable=False)
	id = Column(Integer, primary_key=True)
	description = Column(String(250))

	user_id = Column(Integer, ForeignKey("user.id"))
	user = relationship(User)

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
		'name': self.name,
		'id': self.id,
		'user_id': self.user_id
		}


class Recipe(Base):
	__tablename__ = "recipe"
	name = Column(String(80), nullable=False)
	id = Column(Integer, primary_key=True)
	description = Column(String(250))
	steps = Column(String(250), nullable=False)

	# Foreign Keys
	category_id = Column(
		Integer, ForeignKey('category.id'))

	category = relationship(Category)

	user_id = Column(Integer, ForeignKey("user.id"))
	user = relationship(User)

	@property
	def serialize(self):
	    # Returns object data in easily serializeable format
	    return {
	    'name': self.name,
	    'description': self.description,
	    'steps': self.steps,
	    'id': self.id,
	    }

### Insert at the end of file ###
engine = create_engine(
	'sqlite:///recipesite.db')

Base.metadata.create_all(engine)