FROM debian:bullseye-slim

RUN set -ex; \
    apt-get update &&\
    apt-get install -y wget nano &&\
    apt-get install -y --fix-missing --no-install-recommends &&\
    rm -rf /var/lib/apt/lists/* 

ENV TZ="America/Sao_Paulo"

WORKDIR /opt

COPY ./source ./source
COPY ./config ./config
COPY ./autosave ./autosave
COPY ./requirements.txt .

ENV CONDA_DIR /opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

RUN ln -sf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O \
   ~/miniconda.sh && /bin/bash ~/miniconda.sh -b -p /opt/conda && conda create -n pcaspy -c paulscherrerinstitute pcaspy -c conda-forge --file requirements.txt

ENV EPICS_CA_ADDR_LIST 127.0.0.1
ENV EPICS_CA_AUTO_ADDR_LIST NO

WORKDIR /opt/source
CMD ["/opt/conda/envs/pcaspy/bin/python", "/opt/source/ioc_main.py"]
