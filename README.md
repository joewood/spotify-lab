# Spotify Lab

A Jupyter Notebook / Lab letting you generate playlists based on audio features of tracks in your library.


## Installation

This notebook is packaged in a Docker Image and built using Github Actions. If you have docker installed you can run the notebook server using the command below. Note - you will need to login to Github's Docker registry first using `docker login docker.pkg.github.com`.

```bash
$ docker run -i -p 8888:8888 docker.pkg.github.com/joewood/spotify-lab/main:latest
```

Then browse to http://localhost:8888/?token=vscode.

You can optionally map additional notebooks through a mounted volume:

```bash
$ docker run -i -p 8888:8888 -v $PWD:/home/jovyan/work docker.pkg.github.com/joewood/spotify-lab/main:latest
```


## How to use

Once initialized with your account using OAuth2 (via the Jupyter Notebook), your library can fetched from Spotify as a Panda DataFrame. This is done as follows:

```python
spot = Spotify(auth)
lib = spot.fetchLibraryDataFrame( cache=True )
```

The `DataFrame` contains the list of tracks in the library, related album information, audio features and artist information. This data can be used to filter and create or update playlists using the `updatePlaylist` function.

For example, a dinner party playlist would contain all music in your playlist with a high **acoustic** value and low _energy_. Given that `lib` is a `DataFrame` it can be filtered easily:

```python
  dinnerPlaylist = lib[(lib.acousticness>0.9) & (lib.energy<0.6)]
```

Using the `updatePlaylist` function our **Dinner Party** playlist can be created or updated as follows:

```python
  spot.updatePlaylist("Dinner Party",dinnerPlaylist)
```

Other examples, updating playlists in one line:

```python
spot.updatePlaylist("Night Nights",lib[(lib.acousticness>0.9) & (lib.energy<0.3) & (lib.danceability<0.3)])
spot.updatePlaylist("To Work To", lib[(lib.instrumentalness>0.9) & (lib.energy>0.6)])
spot.updatePlaylist("Quiet Work", lib[(lib.instrumentalness>0.9) & (lib.danceability<0.6)  (lib.energy>0.3) ])
```

Other fields can be used like `popularity`, `released` or `added_at`:

```python
spot.updatePlaylist("Unpopular Songs",lib[lib.track_popularity<0.10])
spot.updatePlaylist("1980s Music",lib[(lib.released>datetime(1980,1,1)) & (lib.released<datetime(1990,1,1))])
spot.updatePlaylist("Added Recently",lib[lib.added_at>(datetime.now()-timedelta(days=60)).isoformat()])
```

Note that playlists are updated with minimal changes. This means you should be able to sort by date added to the playlist in the Spotify UI (useful for tracking changes over time).

## Fields

The set of queryable fields can be found by examining the return DataFrame. A list of what's included includes:

| Field            | Description                                                                   |
| ---------------- | ----------------------------------------------------------------------------- |
| added_at         | ISO Datetime string when the track was added to the library                   |
| track_album_name | Name of the album the track belongs to                                        |
| track_name       | Name of the track                                                             |
| track_popularity | Popularity of the track (0...1)                                               |
| released         | `dateime` field when the track was released                                   |
| artist           | Name of the first artist listed                                               |
| acousticness     | Audio feature (0...1) of how acoustic the track is                            |
| danceability     | Audio feature (0...1) of how danceable the track is, including a regular beat |
| duration_ms      | Duration in Milliseconds                                                      |
| energy           | Audio feature (0...1) of how much energy the track has                        |
| instrumentalness | Audio feature (0...1) of how instrumental the track is - without singing      |
| liveness         | Audio feature (0...1) of detection of crowd (live performance)                |
| loudness         | Audio feature in decibels (-15db to -5db) of how loud the track is            |
| speechiness      | Audio feature (0...1) of how much singing / rapping in track                  |
| tempo            | Detected beats per minute in the track                                        |
| time_signature   | Detected time signature                                                       |
| valence          | Audio feature in the range (0...1) of how positive the track is               |

## Authentication

Authentication is done using OAuth2. A special Jupyter Widget is used to (using [ipyauth](https://oscar6echo.gitlab.io/ipyauth/)). To authenticate is simple, use a dedicated cell in the Notebook:

```python
from ipyauth import ParamsSpotify, Auth
auth = Auth(ParamsSpotify(
    redirect_uri='http://localhost:8888/callback',
    client_id="9e4657eefbac41afa98c61f590d8fd51"))
auth
```

After running this cell click **Sign In**. After logging into Spotify the `auth` variable will be set and can be used to initiatlize the library.

## Caching

Local _Pickle_ files are used to cache contents of the library. These can safely be removed (and git ignored) - they're purely used to reduce the load on the Spotify API.
