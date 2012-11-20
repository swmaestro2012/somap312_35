""":mod:`watermelon.web` --- Web interface using Flask
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import json
import urlparse
import urllib
import urllib2
import xml.etree.ElementTree as ET

import gdata.youtube.service
import memcache
from flask import Flask, request, render_template, redirect, url_for, session
from flask_oauth import OAuth
from sqlalchemy import create_engine

from .orm import Base, Session
from .sql import User, PlayList
from .query import ask

app = Flask(__name__)
app.secret_key = 'development key'
oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url = 'https://graph.facebook.com',
    request_token_url = None,
    access_token_url = '/oauth/access_token',
    authorize_url = 'https://www.facebook.com/dialog/oauth',
    consumer_key = '443844962317469',
    consumer_secret = '8ea10aee2e044b3fad766ef990b7c935',
    request_token_params = {'scope':'email'}
)

engine = create_engine('sqlite:///db.sq3')
Base.metadata.create_all(engine)
query = Session(bind=engine)

def get_play_list(session):
    lists = []
    if 'logged_in' in session:
        user =  query.query(User).get(int(session['id']))
        lists = query.query(PlayList).filter_by(owner=user.id).all()
    return lists

@app.route("/")
def home():
    lists = get_play_list(session)
    return render_template('home.html', lists=lists)


@app.route("/search/")
def search():
    keyword = request.args['q']
    category = request.args['c']
    lists = get_play_list(session)
    results = ask('search', category, keyword)
    if category == 'track':
        page = 'search/track.html'
    elif category == 'artist':
        page = 'search/artist.html'
    elif category == 'album':
        page = 'search/album.html'
    return render_template(page, results=results, category=category, keyword=keyword, lists=lists)


@app.route("/overview/")
def overview():
    id = request.args['q']
    category = request.args['c']
    list = get_play_list(session)
    results = ask('overview', category, id)
    if category == 'track':
        page = 'overview/track.html'
    elif category == 'artist':
        page = 'overview/artist.html'
    elif category == 'album':
        page = 'overview/album.html'
    return render_template(page, results=results, category=category, id=id, lists=list)

@app.route("/list/")
def list():
    if not 'logged_in' in session:
        return 'must be log in'
    else:
        name = request.args['n']
        lists = get_play_list(session)
        results = dict()
        for list in lists:
            if list.name == name:
                results.update(json.loads(list.play_list))
        return render_template('list.html', name=name, lists=lists, results=results)

@app.route("/add/list/")
def add_list():
    if not 'logged_in' in session:
        return 'must be log in'
    else:
        name = request.args['n'].encode('utf-8')
        pList = request.args['l'].encode('utf-8')
        user =  query.query(User).get(int(session['id']))
        try:
            current_list = query.query(PlayList).filter_by(owner=user.id).filter_by(name=name)[0].play_list
            pList = json.loads(pList)
            new_list = json.loads(current_list)
            id = pList.keys()[0]
            new_list[id] = pList[id]
            new_list = json.dumps(new_list)
            query.query(PlayList).filter_by(owner=user.id).filter_by(name=name).update({'play_list':new_list})
        except IndexError:
            query.add(PlayList(owner=user.id, name=name, play_list=pList))
        try:
            query.commit()
        except:
            pass
        return 'ok'

@app.route("/get/list/")
def get_list():
    if not 'logged_in' in session:
        return 'must be log in'
    else:
        result = []
        user = query.query(User).get(int(session['id']))
        lists = query.query(PlayList).filter_by(owner=user.id)
        for list in lists:
            result.append({list.name: list.play_list})
        return str(result)

@app.route("/get/id/")
def get_id():
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    mz_id = 'id_'+str(request.args['id'])
    if mc.get(mz_id):
        return mc.get(mz_id)
    else:
        searchValue = request.args['q'].encode('utf-8')
        client = gdata.youtube.service.YouTubeService()
        VideoUrl = "http://gdata.youtube.com/feeds/api/videos?" + "q=" + searchValue + "&" + "max-result=3" + "&" + "v=2"
        feed = client.GetYouTubeVideoFeed(VideoUrl)
        entry = feed.entry
        VideoIdUrl_data = urlparse.urlparse(entry[0].media.player.url)
        query = urlparse.parse_qs(VideoIdUrl_data.query)
        videoId = query["v"][0]
        mc.set(str(request.args['id']), videoId)
        return mc.get(str(request.args['id']))

@app.route("/get/image/")
def get_image():
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    keyword = str(request.args['keyword']).replace(' ','-')
    category = str(request.args['category'])
    if mc.get('img_'+keyword):
        return mc.get('img_'+keyword)
    else:
        url = 'http://www.maniadb.com/api/search.asp?key=3d66db45443d9fea98e26bee37952c21&target=music&v=0.4&itemtype='+category+'&query=' + urllib.quote(keyword)
        req = urllib2.Request(url)
        rsp = urllib2.urlopen(req)
        tree = ET.parse(rsp)
        root = tree.getroot()[0]
        if category == 'artist':
            try:
                image = root.findall('item')[1].find('image').text
            except IndexError:
                try:
                    image = root.findall('item')[0].find('image').text
                except IndexError:
                    image = '/static/img/default.jpg'
        else:
            try:
                image = root.findall('item')[0].find('image').text
            except IndexError:
                    image = '/static/img/default.jpg'
        mc.set('img_'+keyword, image)
        return mc.get('img_'+keyword)

@app.route("/login/")
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next='/' or request.referrer or None,
        _external=True))


@app.route("/logout/")
def logout():
    session.pop('logged_in', None)
    session.pop('id', None)
    return redirect(url_for('home'))

@app.route("/login/authorized/")
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    session['logged_in'] = True
    session['id'] = me.data['id']
    query.add(User(id=int(me.data['id']), name=me.data['name']))
    try:
        query.commit()
    except:
        pass
    return redirect(url_for('home'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404

@app.errorhandler(500)
def internal_server_error(error):
    return 'Server Error', 500
