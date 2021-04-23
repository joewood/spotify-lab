ARG BASE_IMAGE=jupyter/minimal-notebook:latest
FROM $BASE_IMAGE

WORKDIR /home/$NB_USER
USER $NB_USER

COPY jupyterhub_config.py ./
COPY *.py ./
COPY *.ipynb ./
COPY *.txt ./

RUN pip3 install -r requirements.txt
CMD ["jupyterhub","--port","8000","--config","./jupyterhub_config.py"]

