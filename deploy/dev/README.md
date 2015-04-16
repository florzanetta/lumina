
Docker
======

To build the container:

    $ sudo docker build -t lumina/dev deploy/dev/

To create the container:

    $ sudo docker run --name lumina-dev -p 9922:22 lumina/dev

To login to the container:

    $ ssh -p 9922 lumina@172.17.42.1
