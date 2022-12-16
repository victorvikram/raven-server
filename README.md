# Raven editor
The RAVEN editor has two parts: a flask server (raven-server) and a front end (either raven-app or raven-site). The front end sends requests to the flask server specifying the criteria for generating the RAVEN problem. Then the server generates the problem. This guide will instruct you on how to install both.

## Installation
### If you are using raven-app (more involved setup, requiring nodejs, but allows you to edit the front-end)
1. Clone the RAVEN app from [here](https://github.com/victorvikram/raven-app): `git clone <url>`
2. If you don't already have node.js, install it [here](https://nodejs.org/en/).
3. Run `npm install` in the root directory of the RAVEN app. This installs the necessary react packages.

### If you are using raven-site (simply a static html page with linked javascript)
Clone the RAVEN app from [here](https://github.com/victorvikram/raven-site): `git clone <url>`


### Either way, you will need to set up the server:
1. Clone the RAVEN server from [here](https://github.com/victorvikram/raven-server): `git clone <url>`
2. If you don't already have python and `pip`, you can install it [here](https://www.python.org/). Alternatively, you can install [Anaconda](http://anaconda.com/) which comes with many data science packages preinstalled. 
3. You may need to add `pip` and `python` to the system path if the installer didn't do that automatically. This allows you to run `pip` and `python` commands from the command line without specifying the full path ([here](https://datatofish.com/add-python-to-windows-path/) are example instructions for Windows, a google search will provide instructions for other OSes).
4. From the root directory of the RAVEN server, run `pip install -r requirements.txt`. This installs the necessary python packages.

## To run
1. If you are using raven-app, from the RAVEN app root directory, run `npm start`. If you are using raven-site, simply open `index.html`.
2. From the RAVEN server root directory, first you need to set an environment variable. Different systems accomplish this differently:
*Powershell*: `$env:FLASK_APP = "app"`
*Cmd*: `set FLASK_APP=app`
*Bash*: `export FLASK_APP=app`
Then, run `flask run`.
And that's all!

## When the app is not reaching the server,
it may be that the request URL is incorrect.
### If you are using raven-app
Ensure that the line `let url = <url>` at the top of `app.js` in the RAVEN app root directory matches with the URL of the flask server (it will tell you the URL it is running on after you run `flask run`). Note that `localhost` and `127.0.0.1` are equivalent.

### If you are using raven-site
We recommend you simply make sure the flask server is running on `localhost:5000`. If you must change the address of the server (not recommended) you will need to change all instances of the string `localhost:5000` in the file `static/js/main.39a7fb9c.js` to the new server address `<ADDRESS>:<PORT>`.
