# encoding: utf-8

import functools
import os
import hashlib

import pymongo
from flask import (render_template, session, url_for,
    redirect, flash, request, abort, current_app, make_response, jsonify)
from flask_oauthlib.client import OAuth, OAuthException


from base import app, csrf


mongoclient = pymongo.MongoClient()
db = mongoclient.feusal

oauth = OAuth()

#FIXME: Find a way to unify both auth methods
alumnos_usm = oauth.remote_app('google.alumnosusm',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        access_token_url='https://www.googleapis.com/oauth2/v3/token',
        base_url='https://www.googleapis.com/oauth2/v3/',
        request_token_url=None,
        access_token_method='POST',
        consumer_key=app.config['OAUTH2_CLIENT_ID'],
        consumer_secret=app.config['OAUTH2_CLIENT_SECRET'],
        request_token_params={
            'scope': ['https://www.googleapis.com/auth/userinfo.email'],
            'hd': 'alumnos.usm.cl',
            'access_type': 'online'
        }
    )

sansano_usm = oauth.remote_app('google.sansanousm',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        access_token_url='https://www.googleapis.com/oauth2/v3/token',
        base_url='https://www.googleapis.com/oauth2/v3/',
        request_token_url=None,
        access_token_method='POST',
        consumer_key=app.config['OAUTH2_CLIENT_ID'],
        consumer_secret=app.config['OAUTH2_CLIENT_SECRET'],
        request_token_params={
            'scope': ['https://www.googleapis.com/auth/userinfo.email'],
            'hd': 'sansano.usm.cl',
            'access_type': 'online'
        }
    )

@alumnos_usm.tokengetter
def alumnos_usm_tokengetter(token=None):
    return session.get('oauth2_token')

@sansano_usm.tokengetter
def sansano_usm_tokengetter(token=None):
    return session.get('oauth2_token')

#Decorators

def requires_login(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not session._get_current_object().get('oauth2_token', False):
            return redirect(url_for('login'))
        elif not session._get_current_object().get('campus', False):
            return redirect(url_for('set_campus'))
        return f(*args, **kwargs)
    return wrapper

def requires_sudo(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not session._get_current_object().get('sudo', False):
            abort(403)
        elif not session._get_current_object().get('oauth2_token', False):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


#Login and campus set functions.
#F DRY
@app.route('/login/alumnosusm')
def login_alumnos():
    if 'oauth2_token' not in session:
        return alumnos_usm.authorize(callback=url_for('login_alumnosusm_complete', _external=True))
    else:
        return redirect(url_for('index'))

@app.route('/login/sansanousm')
def login_sansano():
    if 'oauth2_token' not in session:
        return sansano_usm.authorize(callback=url_for('login_sansanousm_complete', _external=True))
    else:
        return redirect(url_for('index'))

def finish_login_request(realm):
    resp = None
    if realm == 'alumnosusm':
        resp = alumnos_usm.authorized_response()
    elif realm == 'sansanousm':
        resp = sansano_usm.authorized_response()
    else:
        flash(u'El proceso de autenticación no terminó en los puntos determinados')

    if resp is None:
        flash(u'No se aceptaron los permisos necesarios para ingresar al sistema.')
        return redirect(url_for('login'))

    session['oauth2_token'] = (resp['access_token'],'')

    userdata = None

    if realm == 'alumnosusm':
        userdata = alumnos_usm.get('userinfo')
    elif realm == 'sansanousm':
        userdata = sansano_usm.get('userinfo')

    if userdata.data['hd'] not in ['alumnos.usm.cl', 'sansano.usm.cl']:
        session.pop('oauth2_token', None)
        flash(u'La cuenta de correo ingresada no es válida.')
        return redirect(url_for('login'))

    email = hashlib.sha512(userdata.data['email']).hexdigest()

    session['email_address'] = email

    if userdata.data['email'] in app.config['SUDOERS']:
        session['sudo'] = True

    voter = db.voters.find_one({'email': email})
    if voter is not None:
        session['campus'] = voter['campus']
        return redirect(url_for('index'))
    else:
        return redirect(url_for('set_campus'))


@app.route('/login/alumnosusm/complete')
def login_alumnosusm_complete():
    return finish_login_request('alumnosusm')

@app.route('/login/sansanousm/complete')
def login_sansanousm_complete():
    return finish_login_request('sansanousm')

@app.route('/login/')
def login():
    if 'oauth2_token' in session:
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout/')
def logout():
    session.pop('oauth2_token', None)
    session.pop('email_address', None)
    session.pop('campus', None)
    session.pop('sudo', None)
    return redirect(url_for('login'))

@app.route('/login/set_campus', methods=['GET', 'POST'])
def set_campus():
    if session.get('campus', False) is not False:
        return redirect(url_for('index'))

    if request.method == 'POST' and request.is_xhr:
        response = make_response()
        campus_response = request.get_json()
        if 'selectedCampus' not in campus_response:
            response.status_code = 400
        else:
            is_campus_set = db.administration.find({'value.value': campus_response['selectedCampus']}).count() == 1
            if not is_campus_set:
                response.status_code = 400
            else:
                try:
                    db.voters.insert_one({
                        'email': session.get('email_address', None),
                        'campus': campus_response['selectedCampus']
                    })
                    session['campus'] = campus_response['selectedCampus']
                except pymongo.errors.WriteError:
                    response.status_code = 500
                response.status_code
        return response
    else:
        return render_template('set_campus.html')

@app.route('/login/get_campus_list')
def get_campus_list():
    if not session.get('email_address', False):
        resp = make_response()
        resp.status_code = 403
        return resp
    else:
        campus_list = db.administration.find_one({'param': u'campus_list'})
        return jsonify({'campuses': [] if campus_list is None \
                    else campus_list['value']})
