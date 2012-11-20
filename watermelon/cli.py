""":mod:`watermelon.cli` --- Command-line interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import sys

from .query import ask


def wrong_access():
    print "Usage: ", sys.argv[0], "type", "category", "keyword"
    raise SystemExit(1)


if __name__ == "__main__":
    try:
        type = sys.argv[1]
        category = sys.argv[2]
        keyword = sys.argv[3]
    except IndexError:
        wrong_access()
    
    if not type in ["search", "overview"]:
        wrong_access()
    if not category in ["track", "artist", "album"]:
        wrong_access()
    
    results = ask(type, category, keyword)
    
    if type == "search":
        if category == "track":
            print 'name:', results['main'].track.title
            print 'id:', results['main'].track.id[-36:]
            try:
                print 'album:', results['main'].track.releases[0].title
                print 'album id:', results['main'].track.releases[0].id[-36:]
            except IndexError:
                print 'album: None'
            print 'artist:', results['main'].track.artist.name
            print 'artist id:', results['main'].track.artist.id[-36:]
            print '\nAnother same name tracks'
            for track in results['another']['tracks']:
                try:
                    print 'title:', track.track.title, 'id:', track.track.id[-36:], 'album:', track.track.releases[0].title,\
                          'album id:', track.track.releases[0].id[-36:], 'artist:', track.track.artist.name.encode('utf-8'),\
                          'artist id', track.track.artist.id[-36:]
                except IndexError:
                    print 'title:', track.track.title, 'id:', track.track.id[-36:], 'album: None',\
                          'artist:', track.track.artist.name.encode('utf-8'), 'artist id', track.track.artist.id[-36:]
                
        elif category == "artist":
            print 'name:', results['main'].artist.name
            print 'type:', results['main'].artist.type
            print 'duration:', results['main'].artist.beginDate, "-", results['main'].artist.endDate
            print 'id:', results['main'].artist.id[-36:]
            print '\nAlbums'
            for album in results['another']['albums']:
                print 'title:', album.release.title, 'id:', album.release.id[-36:]
            print '\nTracks'
            for track in results['another']['tracks'].tracks:
                print 'title:', track.title, 'album:', results['another']['tracks'].title, 'time:', track.duration ,'id:', track.id[-36:]
            print '\nAnother Artists'
            for artist in results['another']['artists']:
                print 'name:', artist.artist.name, 'type:', artist.artist.type, 'id:', artist.artist.id[-36:]
                
        elif category == "album":
            print 'name:', results['main'].release.title
            print 'id:', results['main'].release.id[-36:]
            print 'artist:', results['main'].release.artist.name
            print 'artist id:', results['main'].release.artist.id[-36:]
            print '\nTracks'
            for track in results['another']['tracks'].tracks:
                print 'title:', track.title, 'time:', track.duration ,'id:', track.id[-36:]
            print '\nAnother Albums'
            for album in results['another']['albums']:
                print 'title:', album.release.title, 'id:', album.release.id[-36:], 'artist:', album.release.artist.name, 'id:', album.release.artist.id[-36:]
        
    elif type == "overview":
        print "\nOverview"
        
        if category == "track":
            print 'name:', results['main'].title
            print 'id:', results['main'].id[-36:]
            print 'artist:', results['main'].artist.name
            print 'artist id:', results['main'].artist.id[-36:]
            print '\nAlbums'
            for album in results['main'].releases:
                print 'title:', album.title, 'id:', album.id[-36:]
            
        elif category == "artist":
            print 'name:', results['main'].name
            print 'type:', results['main'].type
            print 'duration:', results['main'].beginDate, "-", results['main'].endDate
            print 'id:', results['main'].id[-36:]
            print '\nAlbums'
            for album in results['another']['albums']:
                print 'title:', album.title, 'id:', album.id[-36:]
            print '\nTracks'
            for track in results['another']['tracks'].tracks:
                print 'title:', track.title, 'album:', results['another']['tracks'].title, 'time:', track.duration ,'id:', track.id[-36:]
            
        elif category == "album":
            print 'name:', results['main'].title
            print 'id:', results['main'].id[-36:]
            print 'artist:', results['main'].artist.name
            print 'artist id:', results['main'].artist.id[-36:]
            print '\nTracks'
            for track in results['another']['tracks']:
                print 'title:', track.title, 'time:', track.duration ,'id:', track.id[-36:]