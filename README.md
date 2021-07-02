# The Medium Crawler

The following project crawls medium.com for the blogs for the tag searched for.

Tech Stack Used:
* Python - FastAPI
* Postgres - Database
* Redis - Caching
* Docker - Containers

How to use?
* Clone the repo on your local machine.
* To use Docker, you need to install `docker` and `docker-compose` on your system.
* Simply run, `./docker-start.sh start` in the working directory.
* The script will handle everything on its own.
* Once, started open `http://localhost:8000/docs/swagger` in your browser - Here you can see the swagger doc of all the api's
* To, start crawling open `http://localhost:8000/blogs/` in your browser.
* Enter the tag you want to search for in search box and press Enter.
* After that you can see all the crawled blogs on the page.
* Clicking on a particular blog will redirect to a new page and crawl the blog details in that page.

Also, to make database work you will need to upgrade the migrations
* Once you start your server, execute into the container using `docker exec -it crawler-medium bash`
* Simply type, `alembic upgrade head` 
* All migrations will be updated.
* To locally check your database you can use the following connection string. 
* `postgresql+psycopg2://gocomet_read_write:goCometCrawler123@postgresql/gocomet_crawler`
