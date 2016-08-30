from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine("sqlite:///restaurantmenu.db")

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

session = DBSession()

myFirstRestaurant = Restaurant(name="Pizza Palace")
session.add(myFirstRestaurant)
session.commit()
print session.query(Restaurant).all()

cheesePizza = MenuItem(name = "Cheese Pizza",
	description = "Made with all natural ingredients and fresh mozarella",
	course = "Entree",
	price = "$8.99",
	restaurant = myFirstRestaurant)
session.add(cheesePizza)
session.commit()
print session.query(MenuItem).all()

firstResult = session.query(Restaurant).first()
print firstResult.name

# items = session.query(MenuItem).all()
# for item in items:
# 	print item.name
# 	print item.restaurant.name



veggieBurgers = session.query(MenuItem).filter_by(name="Veggie Burger")
for veggieBurger in veggieBurgers:
	print veggieBurger.id
	print veggieBurger.price
	print veggieBurger.restaurant.name
	print "\n"

urbanVeggieBurger = session.query(MenuItem).filter_by(id=12).one()
print urbanVeggieBurger.price
urbanVeggieBurger.price = "$2.99"
session.add(urbanVeggieBurger)
session.commit()

veggieBurgers = session.query(MenuItem).filter_by(name="Veggie Burger")
for veggieBurger in veggieBurgers:
	if veggieBurger.price != "$2.99":
		veggieBurger.price = "$2.99"
		session.add(veggieBurger)
		session.commit()