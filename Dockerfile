FROM python:3.10-bullseye

WORKDIR /home

RUN apt update && \
      apt install -y curl && \
      curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl && \
      chmod +x ./kubectl && \
      mv ./kubectl /usr/local/bin/kubectl

COPY . .

RUN bash functions/configure_python.sh

ENTRYPOINT ["python", "deployer.py"]

