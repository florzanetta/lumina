
Docker
======

To build the container:

    $ sudo docker build -t lumina/dev deploy/dev/

To create the container:

    $ sudo docker run --name lumina-dev -p 9922:22 lumina/dev
    $ sudo docker run --name lumina-dev -p 9922:22 \
        -v /srv/docker-lumina/var_lib_apt:/var/lib/apt \
        -v /srv/docker-lumina/var_cache_apt:/var/cache/apt \
        -v /srv/docker-lumina/home_lumina_deploy:/home/lumina/deploy \
	-d lumina/dev

To login to the container:

    $ ssh -p 9922 lumina@172.17.42.1

To deploy to the container:

    $ ansible-playbook -i deploy/dev/inventory-docker-lumina-dev.ini deploy/deploy.yml
