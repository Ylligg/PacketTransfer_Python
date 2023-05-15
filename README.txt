How to use application.py
_________________________

you have to choose a server and a client side with arguments.

example:
python3 application.py -s
or 
python3 application.py -c -f "filename"

when you run client remember to specify what file you want to transfer.

reliable methods
----------------

to use reliable methods use agrument -r and then you can choose between stop and wait with (sw) or Go Back N with (gbn)
make sure you run the same on both server and client.

example:
python3 application.py -s -r sw

ip address
----------

to choose a spesific ip adress you can run

python3 application.py -s -r sw -i "ip adress"

port
----

python3 application.py -s -r sw -i "ip adress" -p "port"

filetransfer
------------

to choose what file you want to send use -f, it can only be used on client side.

python3 application.py -c -r sw -i "ip adress" -p "port" -f "filename"


