FROM jupyter/minimal-notebook:latest

WORKDIR /home/$NB_USER
USER $NB_USER

COPY --chown=1000:100 ./ipyauth /home/$NB_USER/ipyauth
COPY ./requirements.txt /tmp
COPY ./jupyter_notebook_config.py /home/$NB_USER
COPY --chown=1000:100 ./spotify-lab.ipynb /home/$NB_USER/auto-playlist.ipnyb

RUN pip install --requirement /tmp/requirements.txt && \
  cd ipyauth && \
  pip install --requirement ./requirements.txt && \
  cd ipyauth/js && npm ci && cd ../.. && \
  pip install -e . && \
  cd /home/$NB_USER && \
  jupyter serverextension enable --py --sys-prefix ipyauth.ipyauth_callback && \
  jupyter nbextension install --py --symlink --sys-prefix ipyauth.ipyauth_widget && \
  jupyter nbextension enable --py --sys-prefix ipyauth.ipyauth_widget && \
  jupyter labextension install @jupyter-widgets/jupyterlab-manager && \
  jupyter labextension link ipyauth/js --no-build && \
  jupyter serverextension list && \
  jupyter nbextension list && \
  jupyter labextension list
