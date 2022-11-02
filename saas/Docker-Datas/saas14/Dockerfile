FROM ubuntu:20.04

LABEL maintainer="Tele"

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN set -x; \
        apt-get update \
        && apt-get install -y --no-install-recommends \
            ca-certificates \
            curl \
            dirmngr \
            node-less \
            python3-pip  \
	    python3-setuptools \
	    gnupg \
        && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb \
        && apt install ./wkhtmltox.deb -y \
        && apt-get -y install -f --no-install-recommends \
        && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false -o APT::AutoRemove::SuggestsImportant=false \
        && rm -rf /var/lib/apt/lists/* wkhtmltox.deb \
        && pip3 install psycogreen==1.0

# install latest postgresql-client
RUN set -x; \
        echo 'deb http://apt.postgresql.org/pub/repos/apt/ focal-pgdg main' > etc/apt/sources.list.d/pgdg.list \
        && export GNUPGHOME="$(mktemp -d)" \
        && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
        && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
        && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
        && gpgconf --kill all \
        && rm -rf "$GNUPGHOME" \
        && apt-get update  \
        && apt-get install -y postgresql-client \
        && rm -rf /var/lib/apt/lists/* \
	&& apt update && apt-get install -y npm \
	&& npm install -g less less-plugin-clean-css \
	&& apt-get install -y node-less

# Install Tele
ENV TELE_VERSION 14.0

#This binds to service file.So, take care
ARG TELE_USER=tele
ARG TELE_USER_UID=XXXX
ARG TELE_USER_GID=XXXX

RUN set -x; \
        groupadd -r -g ${TELE_USER_GID} ${TELE_USER} \
        && adduser --system --home=/opt/${TELE_USER} ${TELE_USER} --uid ${TELE_USER_UID} --gid ${TELE_USER_GID} \
        && apt update && apt-get install -y git libpq-dev libxml2-dev libxslt-dev libffi-dev gcc python3-dev libsasl2-dev python-dev libldap2-dev libssl-dev libjpeg-dev \
        && su - ${TELE_USER} -s /bin/bash -c "git clone https://www.github.com/tele/tele --depth 1 --branch ${TELE_VERSION} --single-branch ." \
        && mkdir /var/log/tele \
        && chown ${TELE_USER}:root /var/log/tele


COPY ./tele-server.conf /etc/tele/
RUN set -x; \
	chown -R ${TELE_USER} /etc/tele/ \
	&& chmod 640 /etc/tele/tele-server.conf \
        && pip3 install wheel
Run set -x; \
	pip3 install -r /opt/tele/requirements.txt \
    && pip3 install gevent==20.9.0



#Mount /var/lib/tele to allow restoring filestore and /mnt/extra-addons for users addons
RUN mkdir -p /mnt/extra-addons \
        && mkdir -p /opt/data_dir \
        && chown -R tele /opt/data_dir \
        && chown -R tele /mnt/extra-addons

COPY ./entrypoint.sh /
COPY ./run_tele.sh /

# Install rtlcss (on Debian buster)
RUN npm install -g rtlcss

# Expose Tele services
EXPOSE 8069 8071

# Set default user when running the container
USER ${TELE_USER}


ENTRYPOINT ["/entrypoint.sh"]


