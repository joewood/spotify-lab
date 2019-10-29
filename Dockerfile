FROM jupyter/minimal-notebook:latest

WORKDIR /workdir
WORKDIR /workdir/ipyauth

COPY ipyauth/ipyauth /workdir/ipyauth/ipyauth
COPY ipyauth/requirements.txt /workdir/ipyauth/

RUN pip install notebook && \
  pip install -r requirements.txt & \
  cd js && \
  npm install && \
  npm run prepare && \
  cd ..\.. && \
  pip install -e . && \
  jupyter serverextension enable --py --sys-prefix ipyauth.ipyauth_callback && \
  jupyter nbextension install --py --symlink --sys-prefix ipyauth.ipyauth_widget && \
  jupyter nbextension enable --py --sys-prefix ipyauth.ipyauth_widget && \
  jupyter labextension install @jupyter-widgets/jupyterlab-manager && \
  jupyter labextension link ipyauth/js --no-build && \
  jupyter serverextension list && \
  jupyter nbextension list && \
  jupyter labextension list



