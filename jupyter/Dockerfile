FROM jupyter/scipy-notebook:latest

USER root

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

USER ${NB_UID}

# Copy example notebooks
COPY notebooks/ /home/jovyan/work/notebooks/

EXPOSE 8888

CMD ["start-notebook.py", "--NotebookApp.token=${JUPYTER_TOKEN}", "--NotebookApp.allow_origin='*'"]
