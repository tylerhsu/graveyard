from flask import Flask, request, render_template
import graph, json

app = Flask(__name__)

@app.route('/', method='GET')
def show_form():
    return render_template('form.html')

@app.route('/route/', method='POST')
def route():
    start_node_id = request.form['start_node_id']
    target_node_ids = request.form['target_node_ids']
    bonuses = request.form['bonuses']
    speed = request.form['speed']

    return json.dumps(graph.run(start_node_id, target_node_ids, bonuses, speed))

if __name__ == '__main__':
    app.run(host='0.0.0.0')
