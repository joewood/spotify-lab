from datetime import datetime, timedelta
from spotilab import Spotilab

if __name__ == "__main__":
    spot = Spotilab()

    # Read the library into a Data Frame
    lib = spot.fetch_library()
    print(f"Running Updater with {len(lib)} tracks from library")

    # Common Time Ranges
    days1 = datetime.now() - timedelta(days=2)
    days14 = datetime.now() - timedelta(days=13)
    days90 = datetime.now() - timedelta(days=90)
    days120 = datetime.now() - timedelta(days=120)
    year1 = datetime.now() - timedelta(days=365)

    # The Decades
    date1960 = datetime(1960, 1, 1)
    date1970 = datetime(1970, 1, 1)
    date1980 = datetime(1980, 1, 1)
    date1990 = datetime(1990, 1, 1)
    date2000 = datetime(2000, 1, 1)
    date2010 = datetime(2010, 1, 1)
    date2020 = datetime(2020, 1, 1)

    # Decide to run the holiday playlist update
    HOLIDAY_TIME = False

    # dd = spot.get_library_duplicates()
    original_dupes = lib[lib.duplicated(subset=["original_uri"], keep=False)]
    print("Duplicate Originals", original_dupes)
    spot.update_playlist(
        "Duplicates Spotify ID",
        lib[lib.original_uri.isin(original_dupes["original_uri"].tolist())],
        exclude_holiday=False,
        exclude_noise=False,
    )

    def _fix_name(n) -> str:
        name = n["name"]
        if (
            " mix" in name.lower()
            or " instrumental" in name.lower()
            or " acoustic" in name.lower()
            or " remix" in name.lower()
            or " version" in name.lower()
            or "- pt." in name.lower()
            or "part " in name.lower()
            or " live" in name.lower()
            or " reprise" in name.lower()
            or " continued" in name.lower()
            or " <>" in name.lower()
            or " suite" in name.lower()
            or " bbc" in name.lower()
            or "rmx" in name.lower()
        ):
            return name
        return name.split(" - ")[0]

    # Add a column to lib with a lambda expression from the name column
    lib["name-no-remaster"] = lib.apply(_fix_name, axis=1)

    duplicates = lib[lib.duplicated(subset=["name-no-remaster", "artist"], keep=False)]
    duplicates_sorted = duplicates.sort_values(by="popularity", ascending=True)
    result_unpopular = duplicates_sorted.drop_duplicates(
        subset=["name-no-remaster", "artist"], keep="first", inplace=False
    )
    result_popular = duplicates_sorted.drop_duplicates(
        subset=["name-no-remaster", "artist"], keep="last", inplace=False
    )
    result_unpopular_uris = result_unpopular["original_uri"].tolist()
    result_popular_uris = result_popular["original_uri"].tolist()
    print(result_unpopular_uris)
    spot.update_playlist(
        "Duplicates", lib[lib.original_uri.isin(result_unpopular_uris)], exclude_holiday=False, exclude_noise=False
    )
    spot.update_playlist(
        "Duplicates To Keep",
        lib[lib.original_uri.isin(result_popular_uris)],
        exclude_holiday=False,
        exclude_noise=False,
    )

    # WORKOUT PLAYLISTS

    newPlaylist = lib[(lib.duration_ms < 1000 * 60 * 7) & (lib.energy > 0.935)]
    # # Exclude some artists from this playlist
    spot.update_playlist("Auto Run Fast", newPlaylist, released_between=(date1990, None), sort_key="energy", limit=80)
    spot.update_playlist("New Run Fast", newPlaylist, released_between=(year1, None), sort_key="energy", limit=40)

    # UNPOPUPAR PLAYLISTS

    spot.update_playlist(
        "Are You Sure", sort_ascending=True, sort_key="popularity", limit=40, released_between=(None, days120)
    )
    comp = lib[~lib.album.isin(["Love", "Ricochet (Live)"])]
    spot.update_playlist("Compilations", comp[(comp.album_type == "compilation")])

    # TEST
    spot.update_playlist("Tangerine Dream", artists=["Tangerine Dream"], artists_like=["Tangerine Dream"])
    # DECADES

    spot.update_playlist("Auto 1960s", released_between=(None, date1970))

    spot.update_playlist(
        "Auto 1970s",
        released_between=(date1970, date1980),
    )
    spot.update_playlist(
        "1970s Party",
        released_between=(date1970, date1980),
        sort_key="energy",
        limit=150,
    )
    spot.update_playlist(
        "Auto 1980s",
        released_between=(date1980, date1990),
    )
    spot.update_playlist("1980s Party", released_between=(date1980, date1990), sort_key="energy", limit=150)

    spot.update_playlist("1980s Top40", released_between=(date1980, date1990), sort_key="popularity", limit=40)
    spot.update_playlist(
        "1980s Bottom100", released_between=(date1980, date1990), sort_key="popularity", sort_ascending=True, limit=100
    )
    spot.update_playlist(
        "1990s Bottom100", released_between=(date1990, date2000), sort_key="popularity", sort_ascending=True, limit=100
    )
    spot.update_playlist("1990s Top40", released_between=(date1990, date2000), sort_key="popularity", limit=40)
    spot.update_playlist("2000s Top40", released_between=(date2000, date2010), sort_key="popularity", limit=40)
    spot.update_playlist("2010s Top40", released_between=(date2010, date2020), sort_key="popularity", limit=40)
    spot.update_playlist("2020s Top40", released_between=(date2020, None), sort_key="popularity", limit=40)
    spot.update_playlist(
        "Auto 1990s",
        released_between=(date1990, date2000),
    )
    spot.update_playlist("1990s Party", released_between=(date1990, date2000), sort_key="energy", limit=150)
    spot.update_playlist(
        "Auto 2000s",
        released_between=(date2000, date2010),
    )
    spot.update_playlist("2000s Party", released_between=(date2000, date2010), sort_key="energy", limit=150)
    spot.update_playlist("Auto 2010s", released_between=(date2010, date2020))
    spot.update_playlist("2010s Party", released_between=(date2010, date2020), sort_key="energy", limit=150)
    spot.update_playlist("Auto 2020", released_between=(date2020, None))
    spot.update_playlist("2020s Party", released_between=(date2020, None), sort_key="energy", limit=150)

    # NEW STUFF

    spot.update_playlist("Good Year", released_between=(year1, None))
    spot.update_playlist("Radio Won", added_after=days14)
    spot.update_playlist("Radio Too", added_after=days90, limit=200, exclude_playlists=["Radio Won"])
    spot.update_playlist("New Released", released_between=(days120, None))
    spot.update_playlist("New Mix Takes", released_between=(year1, None), sort_key="energy", limit=100)

    ## THE MOODS

    spot.update_playlist(
        "Dinner Party",
        lib[
            (lib.acousticness > 0.8)
            & (lib.energy < 0.55)
            & (lib.instrumentalness < 0.7)
            & (lib.duration_ms < (1000 * 360))
            & (lib.release_date > date1980)
        ],
    )
    spot.update_playlist(
        "Dinner Party Classics",
        lib[
            (lib.acousticness > 0.8)
            & (lib.energy < 0.6)
            & (lib.instrumentalness < 0.7)
            & (lib.duration_ms < (1000 * 360))
            & (lib.release_date <= date1980)
        ],
    )
    spot.update_playlist(
        "Night Nights",
        lib[
            (lib.acousticness > 0.9)
            & (lib.loudness < -15)
            & (lib.speechiness < 0.3)
            & (lib.energy < 0.2)
            & (lib.danceability < 0.3)
        ],
    )

    spot.update_playlist("Danceability", sort_key="danceability", limit=20)
    spot.update_playlist("Quiet", sort_key="loudness", limit=50, sort_ascending=True)
    spot.update_playlist("Energy", sort_key="energy", limit=50)
    spot.update_playlist("Low-Energy", sort_key="energy", limit=50, sort_ascending=True)
    spot.update_playlist("Instrumentalness", sort_key="instrumentalness", limit=20)
    spot.update_playlist("Low-Speechiness", sort_key="speechiness", sort_ascending=True, limit=20)

    workInstrumental = lib.instrumentalness > 0.65

    workDance = lib.energy > 0.7
    quietInstrumental = workInstrumental & (lib.energy < 0.3)
    quietDance = lib.danceability < 0.5

    quietEnergy = lib.loudness < -15
    loudEnergy = lib.loudness >= -15
    workFast = (lib.energy > 0.8) & workInstrumental

    spot.update_playlist("To Work To", lib[workInstrumental & workDance])
    spot.update_playlist("To Work To 4M", lib[workInstrumental], added_after=days120, limit=100)
    spot.update_playlist(
        "New Released To Work To",
        lib[workInstrumental & workDance],
        released_between=(year1, None),
    )

    spot.update_playlist(
        "Quiet Work",
        lib[quietInstrumental & quietDance & quietEnergy],
    )
    spot.update_playlist("Loud Work", lib[workInstrumental & workDance & loudEnergy])
    spot.update_playlist("Fast Work", lib[workFast])

    spot.update_playlist(
        "Duran Duran",
        artists=["Duran Duran", "Arcadia"],
    )
    spot.update_playlist("Doves", artists=["Doves"], artists_like=["Doves"])
    spot.update_playlist(
        "Classical",
        artists=[
            "Gabriel Fauré",
            "Guiseppe Verdi",
            "Wolfgang Amadeus Mozart",
            "Ludwig van Beethoven",
            "Frédéric Chopin",
            "George Friedrich Handel",
            "Johann Sebastian Bach",
            "Antonín Dvořák",
            "Franz Liszt",
            "Felix Mendelssohn",
            "Gustav Mahler",
            "Jean Sibelius",
            "Pyotr Ilyich Tchaikovsky",
        ],
        artists_like=[
            "Gabriel Fauré",
            "Guiseppe Verdi",
            "Antonín Dvořák",
            "Ludwig van Beethoven",
            "Wolfgang Amadeus Mozart",
            "Frédéric Chopin",
            "Jean Sibelius",
            "Felix Mendelssohn",
            "George Friedrich Handel",
            "Johan Sebastian Bach",
            "Franz Liszt",
            "Gustav Mahler",
            "Pyotr Ilyich Tchaikovsky",
        ],
    )
    spot.update_playlist(
        "Michael Jackson", artists=["Michael Jackson", "Janet Jackson", "The Jacksons", "The Jackson 5"]
    )
    spot.update_playlist("Pet Shop Boys", artists=["Pet Shop Boys", "Tennant", "Lowe"])
    spot.update_playlist("Laura Marling", artists=["Laura Marling"], artists_like=["Laura Marling"])
    spot.update_playlist("Tears For Fears", artists=["Tears For Fears", "Roland Orzabal", "Curt Smith"])
    spot.update_playlist(
        "Radiohead Plus",
        artists=["Radiohead", "Thom Yorke", "Jonny Greenwood", "Modeselektor", "The Smile"],
        tracks=[
            "Faust Arp",
            "Fake Plastic Trees",
            "Idioteque",
            "Exit Music",
            "Everything in Its Right Place",
            "True Love Waits",
            "Exit Music (For A Film)",
            "Weird Fishes",
        ],
    )
    spot.update_playlist(
        "Beatles Plus",
        artists=[
            "The Beatles",
            "Paul McCartney",
            "John Lennon",
            "Ringo Starr",
            "George Harrison",
            "Wings",
            "George Martin",
        ],
        albums=["Across The Universe", "Instant Karma", "Abbey Road", "Beatles"],
        tracks=[
            "Hard Day",
            "Got to Get You Into My Life",
            "Dear Prudence",
            "Strawberry Fields",
            "Maybe I'm Amazed",
            "Golden Slumbers",
            "Here Comes the Sun",
            "A Day in the Life",
        ],
    )
    spot.update_playlist(
        "Paul McCartney",
        artists=["Paul McCartney", "Wings"],
    )
    spot.update_playlist("Queen Plus", artists=["Queen", "David Bowie", "Freddie Mercury"], artists_like=["Queen"])
    spot.update_playlist(
        "Folky",
        artists=[
            "Katherine Priddy",
            "Laura Marling",
            "Dido",
            "Cerys Matthews",
            "Joni Mitchell",
            "Evan MacColl",
            "The Chieftains",
            "Clannad",
        ],
        artists_like=[
            "Katherine Priddy",
            "Laura Marling",
            "Dido",
            "Cerys Matthews",
            "Joni Mitchell",
            "Evan MacColl",
            "The Chieftains",
            "Clannad",
        ],
    )
    spot.update_playlist(
        "Movies",
        artists=[
            "Hans Zimmer",
            "Trent Reznor",
            "Trent Reznor and Atticus Ross",
            "Danny Elfman",
            "John Williams",
            "Howard Shore",
            "Ennio Morricone",
            "James Horner",
            "Steven Price",
            "Carter Burwell",
            "John Barry",
            "Vangelis",
            "Thomas Newman",
            "Philip Glass",
            "Craig Armstrong",
            "Jóhann Jóhannsson",
            "Michael Giacchino",
        ],
        artists_like=[
            "Hans Zimmer",
            "Danny Elfman",
            "John Williams",
            "Michael Giacchino",
        ]
    )
    spot.update_playlist("Seal", artists=["Seal"], artists_like=["Seal"])
    spot.update_playlist("Genesis", artists=["Phil Collins", "Genesis", "Peter Gabriel"], artists_like=["Phil Collins"])
    spot.update_playlist(
        "Orbie",
        artists=[
            "Orbital",
            "Leftfield",
            "The Orb",
            "Fluke",
            "808 State",
            "Daft Punk",
            "UNKLE",
            "The Prodigy",
            "Propellerheads",
            "Underworld",
            "The Chemical Brothers",
            "Dardust",
            "Röyksopp",
        ],
        artists_like=["Orbital"],
    )
    spot.update_playlist(
        "Sade Plus", artists=["Sade", "Oleta Adams", "Macy Gray", "Corinne Bailey Rae"], artists_like=["Sade"]
    )
    spot.update_playlist("Kate Bush", artists=["Kate Bush"])
    spot.update_playlist("Depeche Mode", artists=["Depeche Mode"])
    spot.update_playlist("Madonna", artists=["Madonna"])
    spot.update_playlist("Corinne Bailey Rae", artists=["Corinne Bailey Rae"], artists_like=["Corinne Bailey Rae"])
    spot.update_playlist(
        "Oasis",
        artists=["Oasis", "Noel Gallagher", "Liam Gallagher", "Beady Eye", "Noel Gallagher's High Flying Birds"],
    )
    spot.update_playlist(
        "Alison Moyet",
        artists_like=["Alison Moyet", "Yazoo"],
        artists=["Paul Young", "Level 42", "Howard Jones", "Yazoo"],
    )
    spot.update_playlist(
        "First Wave",
        artists=[
            "Blondie",
            "Cure",
            "U2",
            "Ramones",
            "Thompson Twins",
            "Depeche Mode",
            "The Police",
            "Pretenders",
            "New Order",
            "David Bowie",
            "Kraftwerk",
            "Velvet Underground",
            "Talking Heads",
            "Joy Division",
            "Siouxsie and the Banshees",
            "The Clash",
        ],
        artists_like=["Police"],
    )

    if HOLIDAY_TIME:
        # Debug playlists - used to exclude
        decSongs = spot.fetch_track_uris("December Songs")
        holidaySongs = spot.fetch_track_uris("Holiday Songs")
        # December Songs
        allDecember = lib[(lib.original_uri.isin(decSongs)) | (lib.original_uri.isin(holidaySongs))]
        holiday = lib[lib.original_uri.isin(holidaySongs)]

        spot.update_playlist("December", allDecember, exclude_holiday=False)
        spot.update_playlist("December Party", allDecember[(allDecember.energy > 0.55)], exclude_holiday=False)
        spot.update_playlist("Holly Jolly", allDecember[(allDecember.energy > 0.25)], exclude_holiday=False)
        spot.update_playlist("December Chill", allDecember[(allDecember.energy <= 0.25)], exclude_holiday=False)
        spot.update_playlist(
            "Silent Night",
            allDecember[
                (allDecember.danceability < 0.4) & (allDecember.energy < 0.4) & (allDecember.instrumentalness > 0.15)
            ],
            exclude_holiday=False,
        )
        spot.update_playlist(
            "December Work",
            allDecember[(allDecember.instrumentalness > 0.15) & (allDecember.energy > 0.2)],
            exclude_holiday=False,
        )
        spot.update_playlist(
            "December Instrumental",
            allDecember[allDecember.instrumentalness > 0.15],
            exclude_holiday=False,
        )
        spot.update_playlist(
            "December Nonstrumental",
            allDecember[allDecember.instrumentalness <= 0.15],
            exclude_holiday=False,
        )
        spot.update_playlist(
            "December 3M",
            new_tracks_df=allDecember,
            added_after=days90,
            limit=100,
            exclude_holiday=False,
        )
        spot.update_playlist(
            "December This Year",
            new_tracks_df=allDecember,
            released_between=(year1, None),
            exclude_holiday=False,
        )
        spot.update_playlist(
            "December New",
            new_tracks_df=allDecember,
            released_between=(days90, None),
            exclude_holiday=False,
        )
        spot.update_playlist(
            "December Classics", new_tracks_df=allDecember, released_between=(None, date1990), exclude_holiday=False
        )
