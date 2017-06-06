from flask import Flask, render_template, redirect, request
from random import shuffle
from gevent.wsgi import WSGIServer
import time
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
players = {}
center = []
swap = [None]*3
ready = []
#these variable are breaking, so making it global as lazy fix
#i kind of get why, but not sure how to write a better fix
global host
host = ''
global insomniac
insomniac = ''
global stopwatch
stopwatch = None
global delet
delet = {}

#Home page where people join the game
@app.route('/')
def main():
	global delet
	if delet: #if a game has already been started
		return render_template('new.html')

	#Display the main page, and inject the current list of players
	return render_template('index.html',
		players=(", ".join(list(players)) if list(players) else 'Nobody!'))

@app.route('/new')
def new():
	#clear EVERYTHING
	players.clear()
	center.clear()
	ready.clear()
	swap[0]=None;swap[1]=None;swap[2]=None
	global host
	host = ''
	global insomniac
	insomniac = ''
	global stopwatch
	stopwatch = None
	global delet
	delet = {}
	return redirect('/')


#Submit to the server that the user wants to join
@app.route('/join', methods=['POST'])
def join():
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
	global delet
	delet = {n:0 for n in players} #num of votes to kill
	return redirect('/lobby/' + host)

#Lobby pings here every once in a while to check what role you have
@app.route('/check/<name>')
def check(name):
	if not name in players:
 		return '' #this typically shouldn't happen
	return ('{"players": '+str(len(players))+', "role":"'+str(players[name])+'"}')

#Send out forms to the users to take actions
@app.route('/action/<name>')
def action(name):
	role = players[name]
	if 'werewolf' in role or role == 'minion':
		return render_template('roles/werewolf.html',
			wolf=", ".join([p for p in players if 'werewolf' in players[p]]),
			name=name)
	if role in ('tanner', 'hunter', 'robber', 'insomniac') :
		if role == 'insomniac':
			global insomniac
			insomniac = name
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
		if not pair:
			continue
		temp = players[pair[0]]
		players[pair[0]] = players[pair[1]]
		players[pair[1]] = temp

	#the drunk is weird because of center cards
	if swap[2]:
		ind = center.index(swap[2][1])
		players[swap[2][0]] = swap[2][1]
		center[ind] = 'drunk'

#Countdown to the end of the game
@app.route('/timer/<name>')
def timer(name):
	ready.append(name)
	if len(ready) == len(players):
		swap_all()
		print(players)
		global stopwatch
		stopwatch = time.time() #begin daytime
	return render_template('timer.html', name=name)

@app.route('/timer_check/<name>')
def timer_check(name):
	global stopwatch
	if not stopwatch:
		return "wait"

	msg = ''
	if insomniac == name:
		msg = 'You are now: ' + players[name]
	return '{"time": '+str(int(300-time.time()+stopwatch))+', "msg": "'+msg+'"}'

@app.route('/vote')
def vote():
	return render_template('vote.html', players=players)

@app.route('/kill', methods=['POST'])
def kill():
	global delet
	delet[tuple(request.form)[0]] += 1
	return render_template('results.html', n=len(players), players=players)

@app.route('/fetchvote')
def fetch_vote():
	return str(delet).replace("'",'"')

@app.route('/fetchroles')
def fetch_roles():
	return str(players).replace("'",'"')

port = int(os.environ.get('PORT', 33507))
serv = WSGIServer(port, app)
serv.serve_forever()
