.PHONY: up halt clean clean_all

up: docker-compose.yml
	sudo docker-compose up -d

stop:
	sudo docker-compose stop

clean:
	sudo docker-compose down -v

clean_all: clean
	sudo docker-compose down --rmi all --remove-orphans
