# Spotify Lab

A Jupyter Notebook / Lab for generating playlists by analyzing your library.

This notebook is packaged in a Docker Image and built using Github Actions. If you have docker installed you can run the notebook server using the command below:

```bash
$ docker run -i -p 8888:8888 -v $PWD:/home/jovyan/work docker.pkg.github.com/joewood/spotify-lab/lab:7b7d9043d71b
```

Then browse to http://localhost:8888/?token=vscode
