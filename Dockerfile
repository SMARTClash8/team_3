FROM python:latest

WORKDIR /team_3
ADD . /team_3
COPY . /team_3

RUN pip install -r requirements.txt


ENTRYPOINT ["python"]
CMD ["app.py"]