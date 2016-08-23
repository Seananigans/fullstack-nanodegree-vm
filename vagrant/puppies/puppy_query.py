from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Shelter, Puppy

import datetime as dt 

engine = create_engine("sqlite:///puppyshelter.db")

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

puppies = session.query(Puppy).order_by(Puppy.name)
for puppy in puppies:
	print puppy.name

today = dt.date.today()
sixMonthsAgo = today - dt.timedelta(days=183)
puppies = session.query(Puppy).filter(Puppy.dateOfBirth <= sixMonthsAgo).order_by(Puppy.dateOfBirth.desc())
for puppy in puppies:
	print puppy.name, puppy.dateOfBirth


puppies = session.query(Puppy).order_by(Puppy.weight)
for puppy in puppies:
	print "{} weighs {}".format(puppy.name, puppy.weight)

puppies = session.query(Shelter, func.count(Puppy.id)).join(Puppy).group_by(Shelter.id).all()
# puppies = session.query(Puppy).group_by(Puppy.shelter.name)
for puppy in puppies:
	print puppy
	print "{} currently lives in {}".format(puppy[0].name, puppy[0])