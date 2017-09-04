# Serve the loving-ai chatbot through a web-interface

The steps required for running the chatscript web-interface for the chatbot are,
__(Note that the commands should be run from the directory containing
  this file.)__
1. Run on the host system atleast once so as to get chatscript build.
2. Build the docker image using the following command at least once,
```
bash docker.sh b
```
3. Start the server using the following command.
```
bash docker.sh r
```
4. In a browser open to `localhost:55555` and start chatting.
5. To stop the server run,
```
bash docker.sh s
```
