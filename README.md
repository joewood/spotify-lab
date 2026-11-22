# **Spotify Lab:** Auto Playlists in Spotify

A Jupyter Notebook / Lab letting you generate playlists based on audio features of tracks in your library.

## To Run

You'll need a Spotify Client ID exported for the Sptotipy library:

```bash
export SPOTIPY_CLIENT_ID=<SPOTIFY CLIENT ID>
```


## Creating Playlists

Check run.py for examples of how to use auto playlist features.


## Install and Develop on Windows

```cmd
rem if necessary
winget install -e --id git.git
winget install -e --id Python.Python.3.13
winget install -e --id astral-sh.uv

rem install/update dependencies from pyproject.toml + uv.lock
uv sync

rem run without activating .venv
uv run python auto-list.py duplicates
uv run python auto-list.py playlist "Genreless" --genre "NONE"
```

## Dependency Management

- Dependencies are managed in `pyproject.toml`.
- Exact resolved versions are locked in `uv.lock`.
- To add or update packages:

```cmd
uv add <package>
uv lock
uv sync
```