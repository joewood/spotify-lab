import argparse
from datetime import datetime, timedelta
import json
import math
import numbers


from spotilab import Spotilab

feature_list = [
#     "energy",
#     "popularity",
#     "danceability",
#     "valence",
#     "acousticness",
#     "instrumentalness",
#     "liveness",
#     "speechiness",
#     "loudness",
#     "tempo",
    "duration_ms",
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spotify Auto-List")
    subparsers = parser.add_subparsers(title="subcommands", description="valid subcommands", help="additional help")

    ##### SUB-COMMAND: update cache
    parser_update_cache = subparsers.add_parser(
        "update-cache", help="Update the music library cache. Do this once before executing other commands."
    )
    parser_update_cache.add_argument("--playlist", action="append", help="The name of the playlist to update")
    parser_update_cache.set_defaults(subcommand="update_cache")

    ##### SUB-COMMAND: duplicates
    parser_duplicates = subparsers.add_parser(
        "duplicates", help="Scan for duplicates in the music library. Do this once before executing other commands."
    )
    parser_duplicates.set_defaults(subcommand="duplicates")

    #### SUB-COMMAND: to update a playlist
    parser_update_playlist = subparsers.add_parser(
        "playlist", help="Update or Create a playlist from the music library"
    )
    parser_update_playlist.add_argument("name", type=str, help="The name of the playlist to update or create")
    # add a repeating argument for "genre" that is stored into a string list
    parser_update_playlist.add_argument(
        "--limit", type=int, help="The limit on the number of tracks to include in the playlist"
    )
    parser_update_playlist.add_argument(
        "--sort",
        type=str,
        help="Sort the tracks by this feature attribute",
        choices=feature_list,
        default=None,
    )
    parser_update_playlist.add_argument(
        "--sort-ascending",
        help="If specified sorts the sort attribute in ascending order, otherwise descending order",
        action="store_true",
        default=False,
    )
    parser_update_playlist.add_argument(
        "--update-cache",
        help="Update the cached playlist after calculating (useful when the playlist is being used as an input for another playlist)",
        action="store_true",
        default=False,
    )
    parser_update_playlist.add_argument(
        "--exclude-noise",
        help='Exclude the playlist "noise"',
        action="store_true",
        default=False,
    )
    parser_update_playlist.add_argument(
        "--include-holidays",
        help="Include the holiday playlist",
        action="store_true",
        default=False,
    )

    parser_update_playlist.add_argument("--genre", action="append", help="The genre(s) to include from the playlist")
    parser_update_playlist.add_argument(
        "--exclude-genre", action="append", help="The genre(s) to exclude from the playlist"
    )
    parser_update_playlist.add_argument(
        "--artist", action="append", help="The names of the artists whose tracks will be included in the playlist"
    )
    # parser_update_playlist.add_argument(
    #     "--artist-like", action="append", help="Include some tracks from artists who are associated with these artists"
    # )
    parser_update_playlist.add_argument("--track", action="append", help="Include specific track names")
    parser_update_playlist.add_argument("--album", action="append", help="Include specific named albums")
    parser_update_playlist.add_argument(
        "--exclude",
        action="append",
        help="The names of the playlists with tracks that should be excluded from the playlist",
    )
    parser_update_playlist.add_argument(
        "--include",
        action="append",
        help="The names of the playlists with tracks that be used instead of the entire library",
    )

    for feature in feature_list:
        parser_update_playlist.add_argument(
            "--min-" + feature,
            type=float,
            help=f"The minimum value for the {feature} feature",
        )
        parser_update_playlist.add_argument(
            "--max-" + feature,
            type=float,
            help=f"The maximum value for the {feature} feature",
        )

    def parse_date(iso_date_or_relative: str) -> datetime:
        return (
            (datetime.now() - timedelta(days=int(iso_date_or_relative.replace("T-", ""))))
            if iso_date_or_relative.startswith("T-")
            else datetime.strptime(iso_date_or_relative, "%Y-%m-%d")
        )

    parser_update_playlist.add_argument(
        "--released-after",
        type=parse_date,
        default=None,
        help="The release date (YYYY-MM-DD) after which tracks should be included in the playlist",
    )
    parser_update_playlist.add_argument(
        "--released-before",
        type=parse_date,
        default=None,
        help="The release date (YYYY-MM-DD) before which tracks should be included in the playlist",
    )
    parser_update_playlist.add_argument(
        "--added-after",
        type=parse_date,
        default=None,
        help='The library added date (YYYY-MM-DD) or relative date in the form "T-14" (for 2 weeks ago), after which tracks should be included in the playlist',
    )

    # add a repeating argument for "artist" that is stored into a string list
    parser_update_playlist.set_defaults(subcommand="update_playlist")

    # sub-command to show track information
    parser_show_track_info = subparsers.add_parser("show-track-info", help="show track information")
    parser_show_track_info.add_argument(
        "track", type=str, help="Name or part name of the track to show information for"
    )
    parser_show_track_info.set_defaults(subcommand="show_track_info")

    # sub-command to show music library summary
    parser_show_library_summary = subparsers.add_parser("show-library-summary", help="show music library summary")
    parser_show_library_summary.set_defaults(subcommand="show_library_summary")

    args = parser.parse_args()

    if args.subcommand == "update_cache":
        # code to update cache
        print("Updating cache...")
        spot = Spotilab()
        new_tracks_df = spot.fetch_library(cache_only=False)
        for playlist_name in args.playlist:
            print(f"Updating Cache For {playlist_name}...")
            spot.fetch_track_uris(playlist_name, dirty_cache=True)
        print("Complete")
        exit(0)

    elif args.subcommand == "duplicates":
        # code to update cache
        print("Updating cache...")
        spot = Spotilab()
        new_tracks_df = spot.fetch_library(cache_only=True)
        # print("Columns ", spot._lib.columns)
        artist_dupe_len = spot._lib.groupby(["artist", "name", "duration_ms"]).filter(lambda x: len(x) > 1)
        print(f"DUPLICATE BY ARTIST/NAME/LENGTH: {len(artist_dupe_len)}")
        artist_dupe = spot._lib.groupby(["artist", "name"]).filter(lambda x: len(x) > 1)
        print(f"DUPLICATE BY ARTIST/NAME: {len(artist_dupe)}")
        group_uri = spot._lib.groupby(["track_uri"]).filter(lambda x: len(x) > 1)
        print(f"DUPLICTE BY URIs: {len(group_uri)}")
        # take the second top 50 rows
        original_uris = spot._lib["original_uri"].drop_duplicates(keep="last").to_list()
        original_uris = [x for x in original_uris if x is not None]
        print(f"ORIGINAL URIS: {len(original_uris)}")

        # noise_uris = list(spot._client.fetch_playlist_track_uris("Noise", dirty_cache=True))
        # print(f"NOISE URIS: {len(noise_uris)}")
        # for index in range(0, len(noise_uris), 50):
        #     chunk = [x for x in noise_uris[index : index + 50] if x is not None]
        #     spot._client._spotify.current_user_saved_tracks_add(tracks=chunk)

            # spot._client._spotify.current_user_saved_tracks_delete(tracks=chunk)

        if len(original_uris) > 0:
            for index in range(0, len(original_uris), 50):
                chunk = [x for x in original_uris[index : index + 50] if x is not None]
                # spot._client._spotify.current_user_saved_tracks_delete(tracks=chunk)
                spot._client._spotify.current_user_saved_tracks_delete(tracks=chunk)
                # spot._client._spotify.current_user_saved_tracks_add(tracks=chunk)
        exit(0)

    elif args.subcommand == "update_playlist":
        # code to update playlist
        print(f"Updating playlist {args.name}...")
        spot = Spotilab()
        new_tracks_df = spot.fetch_library(cache_only=True)
        # print the number of rows in new_tracks_df
        released_between = (
            None
            if (args.released_before is None and args.released_after is None)
            else (args.released_after, args.released_before)
        )
        for feature in feature_list:
            if args.__dict__["min_" + feature] is not None:
                new_tracks_df = new_tracks_df.loc[new_tracks_df[feature] >= args.__dict__["min_" + feature]]
            if args.__dict__["max_" + feature] is not None:
                new_tracks_df = new_tracks_df.loc[new_tracks_df[feature] <= args.__dict__["max_" + feature]]
        spot.update_playlist(
            args.name + " (A)",
            new_tracks_df=new_tracks_df,
            limit=args.limit,
            include_genres=args.genre,
            artists=args.artist,
            # artists_like=args.artist_like,
            sort_key=args.sort,
            tracks=args.track,
            albums=args.album,
            exclude_noise=args.exclude_noise,
            exclude_holiday=not args.include_holidays,
            sort_ascending=args.sort_ascending,
            exclude_playlists=args.exclude,
            exclude_genres=args.exclude_genre,
            include_playlists=args.include,
            released_between=released_between,
            added_after=args.added_after,
        )

    elif args.subcommand == "show_track_info":
        # code to show track information
        spot = Spotilab()
        new_tracks_df = spot.fetch_library(cache_only=True)
        track_df = new_tracks_df.loc[new_tracks_df["name"].str.contains(args.track, case=False)]
        print(f"Showing information for track")
        rows = track_df.to_dict(orient="records")
        genres = set[str]()
        for row in rows:
            print(f"Track: {row['name']} by {row['artist']}")
            print(f"\tEnergy: { row["energy"]}")
            print(f"\tLoudness: {row["loudness"]}")
            print(f"\tTempo: {row["tempo"]}")
            print(f"\tDanceability :${row["danceability"]}")
            print(f"\tenergy: {row["energy"]}")
            print(f"\tvalence: {row["valence"]}")
            print(f"\tacousticness: {row["acousticness"]}")
            print(f"\tinstrumentalness: {row["instrumentalness"]}")
            print(f"\tliveness: {row["liveness"]}")
            print(f"\tspeechiness: {row["speechiness"]}")
            print(f"\ttime_signature: {row["time_signature"]}")
            print(f"\tminor: {row["minor"]}")
            print(f"\tkey: {row["key"]}")

            xx = row.get("album_genres", [])
            tt = row.get("genres_artist1", [])
            genres.update(row["genres"])
            genres.update(tt if not (math.isnan) else [])
            genres.update(xx if not (math.isnan) else [])
            # for key in row:
            #     if row[key] is not None and (not isinstance(row[key],numbers.Number) or not math.isnan(row[key])):
            #         print(f"{key}: {row[key]}")
        print(f"GENRES: {genres}")

    elif args.subcommand == "show_library_summary":
        # code to show music library summary
        print("Showing music library summary...")
