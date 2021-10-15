# Flask Fitness Centre  -  __Stripe-Customer-Portal-API__


## Introduction
This project is live on Heroku Server at [Fitness Centre](https://kb-the-trainer.herokuapp.com/), written in flask with Mongo-DB. 

## ScreenShot

<table align="center">
    <tr>
        <td align="center">
            <a href="https://raw.githubusercontent.com/UsamaChattha/Stripe-Customer-Portal-API/main/ScreenShot/img1.JPG">
                <img src="ScreenShot/img1.JPG" alt="Screenshot Home" width="450px" />
            </a>
        </td>
        <td align="center">
            <a href="https://raw.githubusercontent.com/UsamaChattha/Stripe-Customer-Portal-API/main/ScreenShot/img2.JPG">
                <img src="ScreenShot/img2.JPG" alt="Screenshot Category" width="450px" />
            </a>
        </td>
    </tr>
    <tr>
        <td align="center">
            <a href="https://raw.githubusercontent.com/UsamaChattha/Stripe-Customer-Portal-API/main/ScreenShot/img3.JPG">
                <img src="ScreenShot/img3.JPG" alt="Screenshot Admin Panel" width="450px" />
            </a>
        </td>
        <td align="center">
            <a href="https://raw.githubusercontent.com/UsamaChattha/Stripe-Customer-Portal-API/main/ScreenShot/img4.JPG">
                <img src="ScreenShot/img4.JPG" alt="Screenshot Site Configuration" width="450px" />
            </a>
        </td>
    </tr>
</table>


## Quickstart

### Use python virtual environment
**First, Clone and Install dependence**
```
git clone https://github.com/UsamaChattha/Stripe-Customer-Portal-API.git
cd Fitness Centre
python3 -m venv .venv
# on windows, you should run .venv\Scripts\activate.bat 
source .venv/bin/activate
pip3 install -r requirements.txt
```

<!-- **Second, Init db and run**
```
# modify .flaskenv and flaskshop/setting.py
flask createdb
flask seed
flask run
``` -->

### Use Pycharm 
**First, Create New Prject and Install Dependencies Using the follwoing Command inside terminal**
```
pip3 install -r requirements.txt
```
<!-- **Second, enter container and add fake data**
```
docker-compose exec web sh
flask createdb
flask seed
``` -->
### About Config of Database and stripe
```
Add database connection string in the configuration
Add stripe public key at front end
Add stripe secrete key in the configuration
```
<!-- If the js files has been modified, you need to:


Redis and Elasticsearch is unabled by default, You can enable them for good performence and search ablitity. -->