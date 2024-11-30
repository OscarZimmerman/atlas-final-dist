# atlas-final


To run this container, simply export the file to your local files, and run in your linux enivironment the setup shell file (e.g. ./setup.sh). This should set up the container, the rabbitMQ site, run the code, and export the final graph. Results have been ommitted from the final repository, so they can be reproduced for marking, but the final graph produced in testing can be seen in the report. 

To increase the scale of the data accessed, simply edit the producer and aggregator python files, and edit the lines files = ["data_A", "data_B", etc...] to increase and decrease the data as much as desired. 

To increase the number of workers, enter the shell script to the line:
docker run --rm --name worker1 --network="host" rabbitmq_analysis python worker.py 

Edit it to:
docker run --rm --name worker1 --network="host" rabbitmq_analysis python worker.py &
docker run --rm --name worker2 --network="host" rabbitmq_analysis python worker.py &
wait

if you wanted to run two workers e.g.

