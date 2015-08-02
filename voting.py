# encoding: utf-8

from datetime import datetime
from flask import (render_template, request, session, make_response, abort, flash, redirect, url_for)
import pymongo
from bson import json_util, ObjectId, SON
from flask_wtf import csrf


from base import app
from login import requires_login

connection = pymongo.MongoClient()
db = connection.feusal

@app.route('/')
@requires_login
def index():
    return render_template('elections/index.html')

@app.route('/elections/list')
@requires_login
def votelist():
    page = int(request.args.get('page') or 0)
    now = datetime.now()

    elections = db.elections.find(
        {'selectedCampus': session.get('campus', None),
        'date_from': {'$lte': now },
        'date_until': {'$gt': now }
        },
        projection=['date_from', 'date_until', 'reason'])\
    .skip(20*page).limit(20).sort([('date_from', 1), ('date_until', -1)])


    response = make_response(json_util.dumps({'elections': list(elections)}))
    response.mimetype = 'application/json'
    return response

@app.route('/elections/vote/<election_id>', methods=['GET', 'POST'])
@requires_login
def votepage(election_id):
    if request.method == 'GET':
        if db.elections.find({'_id': ObjectId(election_id),
            'voters': session.get('email_address', None)}).count() > 0:
            flash(u'Usted ya votó en ésta elección')
            return redirect(url_for('index'))

        selected_election = db.elections.find_one({
                '_id': ObjectId(election_id),
                'selectedCampus': session.get('campus', None)
                },
            projection=['date_from', 'date_until', 'reason', 'electionOptions'],)

        if selected_election is None:
            abort(404)
        else:
            return render_template('elections/vote.html', election=selected_election)
    elif request.method == 'POST' and request.is_xhr:
        if db.elections.find({'_id': ObjectId(election_id),
            'voters': session.get('email_address', None)}).count() > 0:
            return u'Ya votó en dicha elección', 403
        if not csrf.validate_csrf(request.headers['X-CSRF-Token'], None):
            return u'Falta token CSRF', 401
        else:
            vote = request.get_json()
            election_options = db.elections.find_one({
                '_id': ObjectId(election_id),
                'electionOptions.name': unicode(vote.get('selectedOption', None)),
                'selectedCampus': session.get('campus', None)
                }, projection=['electionOptions.name'])

            if election_options is None:
                return u'La opción para la votación no existe o no existe la votación', 404

            db.elections.update_one({'_id': ObjectId(election_id)},
                {
                    '$inc': {'totalVoters': 1},
                    '$push': {
                        'voters': session.get('email_address', None),
                        'votes': {
                                'election': vote['selectedOption'],
                                'date': datetime.now()
                        }
                    }
                }, upsert=True
            )

            return u'Exito', 200
    else:
        return u'No se puede procesar respuesta', 405

@app.route('/elections/detail/<election_id>')
@requires_login
def electiondetail(election_id):
    election_data = db.elections.find_one({'_id': ObjectId(election_id)},
        projection=['reason', 'date_from', 'date_until', 'electionOptions', 'totalVoters', 'selectedCampus'])

    if election_data is None:
        abort(404)

    user_campus = session.get('campus', None)

    #FIXME: Find a MongoDB solution for this
    campus_data = db.administration.find_one({
            'param': 'campus_list'
        }, projection={'_id': False, 'value.value': True, 'value.pretty': True})


    campus = filter(lambda x: x['value'] == election_data['selectedCampus'],
                     campus_data['value'])[0]['pretty']
    #ENDFIXME

    print campus

    election_summary = db.elections.aggregate([
        { '$match': { '_id': ObjectId(election_id) } },
        { '$project': { 'votes': 1 } },
        { '$unwind': '$votes' },
        { '$group' : {
                '_id': { 'election': '$votes.election'},
                'results': { '$sum': 1 }
            }
        },
        { '$sort': {'results': -1 } }
    ])

    return render_template('elections/detail.html',
        election=election_data,
        campus_name=campus,
        summary=list(election_summary))

@app.route('/elections/history/<int:page>')
@app.route('/elections/history/', defaults={'page': 0})
@requires_login
def election_history(page):
    per_page = 20

    results = db.elections.find(
        { 'date_from' : { '$lte' : datetime.now() }},
        projection=['reason', 'date_from', 'date_until', 'selectedCampus'])\
    .skip(per_page*page).limit(per_page).sort([('date_from', -1), ('date_until', -1)])


    campuses_data = db.administration.find_one({
        'param': 'campus_list'
        }, projection={'_id': False, 'value.value': True, 'value.pretty': True})

    campuses = {}
    for campus in campuses_data['value']:
        campuses[campus['value']] = campus['pretty']

    return render_template('elections/history.html',
        campus_data=campuses, elections=list(results), current_page=page)