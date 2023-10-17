# Battleship

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Usage](#Usage)
* [To do](#todo)
* [License](#License)


## General info

Simple web app to play battleships with other players.

## Technologies

* Python
* Django
* Django rest framework
* Docker
* JavaScript

## Usage 

first build Docker image:
```console
docker-compose build
```
then run docker container:
```console
docker-compose up
```
which starts application that can be accessed on 'localhost:8000/battleships'

Screens from web app:

<img src="https://raw.github.com/MaciejSurowiec/battleship/master/examples/main.png" width=620 height=315>

<img src="https://raw.github.com/MaciejSurowiec/battleship/master/examples/preparation1.png" width=620 height=315>

<img src="https://raw.github.com/MaciejSurowiec/battleship/master/examples/preparation2.png" width=620 height=315>

<img src="https://raw.github.com/MaciejSurowiec/battleship/master/examples/game.png" width=620 height=315>


## To do

* Add Pygame app
* Single player mode
* Statistics

## License
The code is licensed under the MIT license.
