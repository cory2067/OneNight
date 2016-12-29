from flask import Flask, render_template, redirect, request
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
game = {'players':[]}

@app.route('/')
def main():
	#Display the main page, and inject the current list of players
	return render_template('index.html',
		players=(", ".join(game['players']) if game['players'] else 'Nobody!'))

@app.route('/join', methods=['POST'])
def new():
	name = request.form["name"]
	game['players'].append(name)
	return redirect('/lobby/' + name)

@app.route('/lobby/<name>')
def lobby(name):
	return render_template('lobby.html', name=name)

@app.route('/start')
def start():
	return render_template('start.html')

app.run(host="127.0.0.1", port=5000)
