in other to run the API as a docker-compose file, you have to docker installed on your system
# docker-compose up --build #

to stop and remove existing container run
# docker-compose down #


or to run it locally,
set the environment variable to DATABASE_URL=(your desired postgres database url)

the run # python run.py # on your terminal



note the endpoint your will be fetching from are the routes.py and admin_routes.py modules respectively.
