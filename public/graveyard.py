from flask import Flask, request, render_template, redirect, jsonify, abort
from werkzeug.datastructures import ImmutableMultiDict
import graph
import urlparse

app = Flask(__name__)
app.config.from_object('settings')
if not app.debug:
    import logging
    from logging import FileHandler
    handler = FileHandler(app.config['APP_ROOT'] + '/log/app.log')
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

@app.route('/', methods=['GET'])
def show_form():
    locations = sorted(graph.get_locations())
    return render_template('form.html', locations=locations)

@app.route('/route/', methods=['POST'])
def route():
    data = ImmutableMultiDict(urlparse.parse_qs(request.data))
    errors = validate(data)
    if errors['errors']:
        return jsonify(errors), 400
    target_node_ids = data.getlist('target_node_ids')
    speed = data.get('speed')
    bonuses = get_bonuses(data)
    return jsonify(graph.run(target_node_ids, bonuses, speed))

def validate(data):
    errors = { 'errors': [] }
    if data.get('target_node_ids') is None:
        errors['errors'].append('Select at least one waypoint')
    if data.get('speed') is None:
        errors['errors'].append('Enter a speed')
    return errors

def get_bonuses(data):
    bonuses = {}
    for key, value in [t for t in data.lists() if t[0].startswith('bonus')]:
        location = key.split('|')[1]
        bonus = data.get(key)
        bonuses[location] = bonus
    return bonuses

if __name__ == '__main__':
    app.run(host='0.0.0.0')
