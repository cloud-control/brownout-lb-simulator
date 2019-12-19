
#### Build and log into the dockerfile

The docker file is built as
```
docker build -t artifact .
```
Start up the image, run bash in interactive mode and mount shared folders.
```
docker run -it -v $(pwd)/plots:/work/plots -v $(pwd)/cloning-simulator:/work/cloning-simulator artifact /bin/bash
```

#### Run the simulator
In the artifact container, in the `/work/cloning-simulator` directory, the simulator can be run with e.g.
```
python sim_example.py
```
The result directories can be accessed through the shared folder. 

#### Compile the latex plots
In the artifact container, in the `/work/plots` directory, the plots for the paper can be compiled with
```
pdflatex main.tex
```
The pdf file can be accessed through the shared folder.

