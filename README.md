## OVDPs website (Flask framework)

+ **ovdp/**
  + **static/**
    + **reports/**
  + **templates/**
  + __init__.py
  + views.py
  + utils_app.py
  + *default_settings.py*
  + *auctions.db*

+ **instance/**
  + **logs/**
    + app.log
    + debug.log  <-- MODE_DEBUG=True (**load_data.py**)
  + *local_settings.py*  <-- DEBUG / DATABASE / **SECRET_KEY**
  + *auctions.db*  <-- For testing and debugging.

+ **venv/**

+ run_server.py
+ load_data.py
+ utils_load.py


![Screenshot](screenshot-flask_ovdp__index.png)
![Screenshot](screenshot-flask_ovdp__stats.png)
![Screenshot](screenshot-flask_ovdp__year.png)
![Screenshot](screenshot-flask_ovdp__auctions.png)
