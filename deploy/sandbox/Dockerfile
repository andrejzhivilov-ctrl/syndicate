# Code sandbox for the agents (deploy/sandbox/server.py). No secrets, no internet (hermes_net is internal).
FROM python:3.12.10-slim
RUN pip install --no-cache-dir numpy==1.26.4 pandas==2.2.3 scipy==1.13.1 matplotlib==3.9.2 openpyxl==3.1.5 \
    && useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin sandbox
COPY server.py /srv/server.py
USER 10001
EXPOSE 8080
CMD ["python", "-I", "/srv/server.py"]
