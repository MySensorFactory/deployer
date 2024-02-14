FROM python:3.10-bullseye

WORKDIR /home

RUN apt update && \
      apt install -y curl && \
      curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl && \
      chmod +x ./kubectl && \
      mv ./kubectl /usr/local/bin/kubectl

RUN apt install python3 -y
RUN apt install python3-pip -y

COPY . .

RUN pip install $(find . -type f -name 'pythoncommons*' -print -quit)

ENTRYPOINT ["python", "deployer.py"]

