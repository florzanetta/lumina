#
# Creates an Ubuntu 14.04 LTS based container to deploy Lumina, including:
# - creates lumina user
# - setup ssh keys for passwordless login
# - setup passwordless sudo
# - setup supervisord
#
# Based on: https://docs.docker.com/v1.5/examples/running_ssh_service/
#

FROM ubuntu:14.04
MAINTAINER Sven Dowideit <SvenDowideit@docker.com>

RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd
RUN echo 'root:root' | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22

RUN useradd --create-home --password lumina --user-group lumina
RUN mkdir /home/lumina/.ssh

COPY authorized_keys /home/lumina/.ssh/authorized_keys

RUN chown -R lumina.lumina /home/lumina/.ssh && chmod 0700 /home/lumina/.ssh && chmod 0600 /home/lumina/.ssh/authorized_keys

RUN echo 'lumina ALL=(ALL:ALL) NOPASSWD: ALL' > /etc/sudoers.d/lumina

RUN rm /etc/apt/apt.conf.d/docker-clean

VOLUME /var/lib/apt
VOLUME /var/cache/apt
VOLUME /home/lumina/deploy

RUN apt-get install -y supervisor
COPY supervisor-sshd.conf /etc/supervisor/conf.d/sshd.conf

RUN apt-get install --reinstall locales
RUN locale-gen en_US.UTF-8 && \
    echo 'LANGUAGE="en_US.UTF-8"' >> /etc/environment && \
    echo 'LC_ALL="en_US.UTF-8"' >> /etc/environment

ENV LANGUAGE "en_US.UTF-8"

CMD ["/usr/bin/supervisord", "--nodaemon", "-c", "/etc/supervisor/supervisord.conf"]
