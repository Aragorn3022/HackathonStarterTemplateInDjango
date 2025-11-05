make VENV or any similar environments and do the following stuff

    pip install -r requirements.txt

and then the following in the VENV and make the following changes


after installing all the requirements navigate to 
![alt text](image.png)

and make sure that this is similar to this and does not return int

![alt text](image-1.png)


this is to ensure that admin panel works


also change in this file to this
![alt text](image-2.png)

to work make  sure that ws works


# To use WebSocket use the following command

    python start_server.py

# To use Without Websocket use the following

    python manage.py runserver