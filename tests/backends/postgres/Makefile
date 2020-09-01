.PHONY: up halt clean clean_all

up: docker-compose.yml
	docker-compose up -d
	sleep 2

stop:
	docker-compose stop

clean:
	docker-compose down -v

clean_all: clean
	docker-compose down --rmi all --remove-orphans
