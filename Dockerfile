FROM jupyter/minimal-notebook:latest AS BUILD

WORKDIR /home/$NB_USER
USER $NB_USER

COPY --chown=1000:100 ./ipyauth /home/$NB_USER/ipyauth

RUN cd /home/$NB_USER/ipyauth/ipyauth/js && \
  npm ci 


FROM jupyter/minimal-notebook:latest

WORKDIR /home/$NB_USER
USER $NB_USER

COPY --chown=1000:100 ./ipyauth /home/$NB_USER/ipyauth
COPY --from=BUILD /home/$NB_USER/ipyauth/ipyauth/js/dist /home/$NB_USER/ipyauth/ipyauth/js/dist 
COPY ./requirements.txt /tmp
COPY ./*.py /home/$NB_USER/
COPY ./spotify-lab.ipynb /home/$NB_USER/auto-playlist.ipnyb

# RUN

RUN pip install --requirement /tmp/requirements.txt && \
  cd /home/$NB_USER/ipyauth && \
  pip install --requirement ./requirements.txt 

RUN cd /home/$NB_USER/ipyauth/ipyauth/js && \
  npm install --only=production

RUN cd /home/$NB_USER/ipyauth && \
  pip install -e . && \
  jupyter serverextension enable --py --sys-prefix ipyauth.ipyauth_callback && \
  jupyter nbextension install --py --symlink --sys-prefix ipyauth.ipyauth_widget && \
  jupyter nbextension enable --py --sys-prefix ipyauth.ipyauth_widget && \
  jupyter labextension install @jupyter-widgets/jupyterlab-manager && \
  jupyter labextension link ipyauth/js --no-build && \
  jupyter serverextension list && \
  jupyter nbextension list && \
  jupyter labextension list && \
  cd /home/$NB_USER
