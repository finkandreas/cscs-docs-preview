FROM python:3

RUN pip install aiohttp
COPY server.py /usr/bin/server.py

ENTRYPOINT ["python", "/usr/bin/server.py"]
