# How to run Pyxel using Docker container:

https://gitlab.esa.int/sci-fv/pyxel/container_registry

* Login:

`docker login gitlab.esa.int:4567`

* Pull latest version of  Docker container:

`docker pull gitlab.esa.int:4567/sci-fv/pyxel`

* Run Pyxel Docker cont. with GUI:

`docker run -p 9999:9999 -it gitlab.esa.int:4567/sci-fv/pyxel:latest --gui True`

* Run Pyxel Docker cont. in batch mode:  

`docker run -p 9999:9999 -v C:\dev\work\docker:/data -it gitlab.esa.int:4567/sci-fv/pyxel:latest -c /data/settings_ccd.yaml -o /data/result.fits`

* List your running Docker containers:

`docker ps`

* After running Pyxel container you can access it:

`docker exec -it <CONTAINER_NAME> /bin/bash`