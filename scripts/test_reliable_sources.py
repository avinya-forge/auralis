import urllib.request
import urllib.parse
import json

def query_itunes(query):
    url = 'https://itunes.apple.com/search?' + urllib.parse.urlencode({'term': query, 'entity': 'song', 'limit': 1})
    req = urllib.request.Request(url, headers={'User-Agent': 'AuralisMusicApp/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data['resultCount'] > 0:
                item = data['results'][0]
                return {
                    'source': 'iTunes',
                    'title': item.get('trackName'),
                    'artist': item.get('artistName'),
                    'album': item.get('collectionName'),
                    'year': item.get('releaseDate', '')[:4],
                    'genre': item.get('primaryGenreName'),
                    'artwork_url': item.get('artworkUrl100', '').replace('100x100bb', '600x600bb')
                }
    except Exception as e:
        return {'error': str(e)}
    return None

def query_musicbrainz(recording, artist):
    query = f'recording:"{recording}" AND artist:"{artist}"'
    url = 'https://musicbrainz.org/ws/2/recording/?' + urllib.parse.urlencode({'query': query, 'fmt': 'json', 'limit': 1})
    req = urllib.request.Request(url, headers={'User-Agent': 'AuralisMusicApp/1.0 ( support@auralis.local )'})
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('recordings'):
                rec = data['recordings'][0]
                return {
                    'source': 'MusicBrainz',
                    'title': rec.get('title'),
                    'artist': rec.get('artist-credit', [{}])[0].get('name'),
                    'year': rec.get('first-release-date', '')[:4],
                    'album': rec.get('releases', [{}])[0].get('title') if rec.get('releases') else ''
                }
    except Exception as e:
        return {'error': str(e)}
    return None

if __name__ == '__main__':
    print('iTunes Queen:', query_itunes('Queen Bohemian Rhapsody'))
    print('iTunes Lata:', query_itunes('Lata Mangeshkar Lag Ja Gale'))
    print('MusicBrainz U2:', query_musicbrainz('With or Without You', 'U2'))
