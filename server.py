from flask import Flask, render_template, redirect, request
from random import shuffle
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
players = {}

#this variable was breaking, so making it global as lazy fix
global host
host = ''

#Home page where people join the game
@app.route('/')
def main():
	#Display the main page, and inject the current list of players
	return render_template('index.html',
		players=(", ".join(list(players)) if list(players) else 'Nobody!'))

#Submit to the server that the user wants to join
@app.route('/join', methods=['POST'])
def new():
	name = request.form["name"]
	players[name] = None
	return redirect('/lobby/' + name)

#Users placed here until the game begins
@app.route('/lobby/<name>')
def lobby(name):
	return render_template('lobby.html', name=name)

#Here, the host initates the game and chooses roles
@app.route('/start/<name>')
def start(name):
	global host
	host = name
	return render_template('start.html',
	 	name=name, players=len(players))

#Submit the host's choices and initiate game
@app.route('/start_submit', methods=['POST'])
def start_submit():
	settings = request.form
	p = list(players)
	shuffle(p)
	for index,role in enumerate(settings):
		players[p[index]] = role
	return redirect('/lobby/' + host)

#Lobby pings here every once in a while to check status
@app.route('/check/<name>')
def check(name):
	return ('{"players": '+str(len(players))+', "role":"'+str(players[name])+'"}')

app.run(host="127.0.0.1", port=5000)
