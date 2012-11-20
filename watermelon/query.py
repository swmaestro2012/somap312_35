""":mod:`watermelon.query` --- Query to get metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import random

import musicbrainz2.model as m
import musicbrainz2.webservice as ws

query = ws.Query()

track_inc = ws.TrackIncludes(artist=True, releases=True)
artist_inc = ws.ArtistIncludes(releases=(m.Release.TYPE_OFFICIAL, m.Release.TYPE_ALBUM), tags=True, releaseGroups=True)
release_inc = ws.ReleaseIncludes(artist=True, releaseEvents=True, labels=True, discs=True, tracks=True, releaseGroup=True)


def get_track(keyword, id=False):
    if id == True:
        result = query.getTrackById(keyword, track_inc)
    else:
        f = ws.TrackFilter(title=keyword)
        result = query.getTracks(f)
    return result

def get_artist(keyword, id=False):
    if id == True:
        result = query.getArtistById(keyword, artist_inc)
    else:
        f = ws.ArtistFilter(name=keyword)
        result = query.getArtists(f)
    return result
    
def get_album(keyword, id=False, artist=False):
    if id == True:
        result = query.getReleaseById(keyword, release_inc)
    else:
        if artist == True:
            f = ws.ReleaseFilter(artistName=keyword)
        else:
            f = ws.ReleaseFilter(title=keyword)
        result = query.getReleases(f)
    return result


def search(keyword, category):
    metadata = dict()
    
    if category == "track":
        track = get_track(keyword)
        metadata.update({"main": track[0], "another": {"tracks": track[1:]}})
    
    elif category == "artist":
        artist = get_artist(keyword)
        albums = get_album(artist[0].artist.name, artist=True)
        try:
            album_id = albums[random.randint(0,len(albums))].release.id[-36:]
            tracks = get_album(album_id, True)
        except IndexError:
            tracks = None
        metadata.update({"main": artist[0], "another": {"albums": albums, \
                                                        "tracks": tracks, \
                                                        "artists": artist[1:]}})
    
    elif category == "album":
        try:
            album = get_album(keyword)
            album_id = album[0].release.id[-36:]
            tracks = get_album(album_id, True)
        except IndexError:
            album = None
            tracks = None
        metadata.update({"main": album[0], "another": {"albums": album[1:], \
                                                       "tracks": tracks}})
    
    return metadata


def overview(keyword, category):
    metadata = dict()
    
    if category == "track":
        metadata.update({"main": get_track(keyword, True)})
    
    elif category == "artist":
        artist = get_artist(keyword, True)
        albums = artist.releases
        try:
            album_id = albums[random.randint(0,len(albums))].id[-36:]
            tracks = get_album(album_id, True)
        except IndexError:
            tracks = None
        metadata.update({"main": artist, "another": {"albums": albums, \
                                                     "tracks": tracks}})
    
    elif category == "album":
        album = get_album(keyword, True)
        metadata.update({"main": album, "another": {"tracks": album.tracks}})
    
    return metadata


def ask(type, category, keyword):
    if type == "search":
        return search(keyword, category)
    
    elif type == "overview":
        return overview(keyword, category)
    
    else:
        raise SystemExit(1)