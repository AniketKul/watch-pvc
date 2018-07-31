FROM ubuntu:xenial

RUN apt-get update
#RUN apt-get install -y ca-certificates
#RUN apt-get install -y libssl-dev
#RUN apt-get install -y curl unzip
#RUN curl -LO -sk https://storage.googleapis.com/kubernetes-release/release/v1.10.2/bin/linux/amd64/kubectl && chmod +x kubectl && mv kubectl /usr/local/bin/kubectl

RUN apt-get install -y python3
RUN apt-get install -y python3-pip python-dev build-essential
RUN mkdir -p /opt/exampleapp
COPY . /opt/exampleapp/
RUN chmod +x /opt/exampleapp/watch_pvc.py
RUN pip3 install --trusted-host pypi.python.org  -r /opt/exampleapp/requirements.txt

ENTRYPOINT ["python3"]
CMD ["/opt/exampleapp/watch_pvc.py"]
