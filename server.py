from flask import Flask, render_template, redirect, request
from random import shuffle
import time
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
players = {}
center = []
swap = [None]*3
ready = []
start = None
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
		if index>=len(players):
			center.append(role)
		else:
			players[p[index]] = role
	return redirect('/lobby/' + host)

#Lobby pings here every once in a while to check what role you have
@app.route('/check/<name>')
def check(name):
	return ('{"players": '+str(len(players))+', "role":"'+str(players[name])+'"}')

#Send out forms to the users to take actions
@app.route('/action/<name>')
def action(name):
	role = players[name]
	if 'werewolf' in role or role == 'minion':
		return render_template('roles/werewolf.html',
			wolf=", ".join([p for p in players if 'werewolf' in players[p]]),
			name=name)
	if role in ('tanner', 'hunter', 'robber') :
		return '<p>To continue, <a href="/timer/{name}">click here</a></p>'.format(name=name)
	if role == 'seer':
		return render_template('roles/seer.html', players=players, center=center, name=name)
	if role == 'robber':
		return render_template('roles/robber.html', players=players, name=name)
	if role == 'troublemaker':
		return render_template('roles/troublemaker.html', players=players, name=name)
	if role == 'drunk':
		return render_template('roles/drunk.html', center=center, name=name)

@app.route('/robber', methods=['POST'])
def robber():
	swap[0] = tuple(request.form)
	print(swap)
	return ""

@app.route('/troublemaker/<name>', methods=['POST'])
def troublemaker(name):
	swap[1] = tuple(request.form)
	print(swap)
	return redirect('/timer/'+name)

@app.route('/drunk/<name>', methods=['POST'])
def drunk(name):
	swap[2] = (name, tuple(request.form)[0])
	print(swap)
	return redirect('/timer/'+name)

#execute all swapping
def swap_all():
	for pair in swap[:2]:
		temp = players[pair[0]]
		players[pair[0]] = players[pair[1]]
		players[pair[1]] = temp

	#the drunk is weird because of center cards
	ind = center.index(swap[2][1])
	players[swap[2][0]] = swap[2][1]
	center[ind] = 'drunk'

#Countdown to the end of the game
@app.route('/timer/<name>')
def timer(name):
	ready.append(name)
	if len(ready) == len(players):
		swap_all()
		start = time.time() #begin daytime
	return render_template('timer.html', name=name)

@app.route
def timer_check():
	return ''

app.run(host="127.0.0.1", port=5000)
