# encoding: utf-8

import pymongo
from flask import (render_template, redirect, request,
            url_for, jsonify, make_response)
from slugify import slugify

from login import requires_login, requires_sudo
from base import app, csrf
from forms.sudo import CampusForm, NewElectionForm


connection = pymongo.MongoClient()
db = connection.feusal
admin = db.administration
elections = db.elections

#sudo index
@app.route('/sudo/')
@requires_sudo
def sudo_index():
    return render_template('sudo/index.html')

#Campus management
@app.route('/sudo/campuses', methods=['GET', 'POST'])
@requires_sudo
def manage_campuses():
    if request.method == 'POST' and request.is_xhr:
        form = CampusForm.from_json(request.get_json())
        if form.validate():
            resp = make_response()
            try:
                admin.update_one({'param': u'campus_list'},
                    {'$set' :
                        {'value': [{'pretty': name, 'value': slugify(name)} for \
                         name in form.data['campuses']]}
                    },
                    upsert=True)
                resp.status_code = 200
            except pymongo.errors.WriteError:
                resp.status_code = 500
            return resp
        else:
            return u'Denunciado, troesma', 400
    elif request.method == 'GET':
        return render_template('sudo/manage_campuses.html')


@app.route('/sudo/campuses/list')
@requires_sudo
def get_campuses_list():
    campus_list = admin.find_one({'param': u'campus_list'})
    return jsonify({'campuses': [] if campus_list is None \
                    else campus_list['value']})

#Election management

@app.route('/sudo/elections/new', methods=['GET', 'POST'])
@requires_sudo
def new_election():
    if request.method == 'POST' and request.is_xhr:
        form = NewElectionForm.from_json(request.get_json(),
            skip_unknown_keys=True)
        if form.validate():
            resp = make_response()
            try:
                if elections.find(form.data).count() == 0:
                    elections.insert_one(form.data)
                    resp.status_code = 200
                else:
                    resp.status_code = 400
            except pymongo.errors.WriteError:
                resp.status_code = 500
            return resp
        else:
            resp = make_response()
            resp.status_code = 400
            return resp
    elif request.method == 'GET':
        return render_template('sudo/new_election.html')