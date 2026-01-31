FROM jupyter/scipy-notebook:latest

USER root

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

USER ${NB_UID}

# Copy example notebooks
COPY notebooks/ /home/jovyan/work/notebooks/

EXPOSE 8888

CMD ["start-notebook.py", "--NotebookApp.token=${JUPYTER_TOKEN}", "--NotebookApp.allow_origin='*'"]
