FROM ubuntu:18.04

ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /work

COPY cloning-simulator/requirements.txt /work/requirements.txt

RUN apt update && apt install -y texlive texlive-pictures python python-pip

RUN pip install -r /work/requirements.txt

