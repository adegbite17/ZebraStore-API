This is a backend api for Zebra online store, the tech stack inludes, python, flask, postgresql, docker, bcrypt and JWT authetication for secuirity, flutterwave payment gateway. It has a user and admin end point where items can be update, added, deleted, track order and delivery, it is a secured endpoint, whereby users has to be admin in order to view this endpoint, it has a login route to login existing user, signup route to register new users, search route to search for existing product, logout route to logout users, products route to list all existing products, update route profile to update users creditials, add-to-cart route to add item to route, delete-cart-items route to delete cart items, get-cart-items route to get items, order route to view orders, and also verify payment route to verify payments.



in other to run the API as a docker-compose file, you have to docker installed on your system
# docker-compose up --build #

to stop and remove existing container run
# docker-compose down #


or to run it locally,
set the environment variable to DATABASE_URL=(your desired postgres database url)

the run # python run.py # on your terminal



note the endpoint your will be fetching from are the routes.py and admin_routes.py modules respectively.
