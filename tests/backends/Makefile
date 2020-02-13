.PHONY: up stop clean clean_all

up:
	(cd mongo; make up)
	(cd postgres; make up)
	(cd redis; make up)

stop:
	(cd mongo; make stop)
	(cd mongo; make clean)
	(cd postgres; make stop)
	(cd postgres; make clean)
	(cd redis; make stop)
	(cd redis; make clean)

clean:
	(cd mongo; make clean)
	(cd postgres; make clean)
	(cd redis; make clean)

clean_all:
	(cd mongo; make clean_all)
	(cd postgres; make clean_all)
	(cd redis; make clean_all)
