@REM Switch to Unicode as this batch file as accented characters
chcp 65001
@REM call .\venv\Scripts\activate.bat
python auto-list.py update-cache

@REM @REM @REM Latest Music
@REM exit /b 0
python auto-list.py playlist "Genreless" --genre "NONE" 
python auto-list.py playlist "Radio Won" --added-after "T-13" --exclude-noise --update-cache
python auto-list.py playlist "Radio Too" --added-after "T-120" --limit=200 --exclude="Radio Won" --exclude-noise
python auto-list.py playlist "Good Year" --released-after "T-365"
python auto-list.py playlist "New Released" --released-after "T-120"
python auto-list.py playlist "New Mix Takes" --released-after "T-365"  ^
    --exclude-genre "orchestra" --exclude-genre "orchestral"  --exclude-genre "symphony" ^
    --exclude-genre "string quartet" --exclude-genre "post-romantic era" ^
    --exclude-genre "classical" --exclude-genre "orchestral soundtrack" --exclude-genre "soundtrack"  ^
    --exclude-genre "guitarra clasica" --exclude-genre "classical guitar" ^
    --exclude-genre "british modern classical" --exclude-genre "german romanticism" --exclude-genre "russian romanticism" --exclude-genre "ukrainian classical"

@REM @REM @REM Decade Based Playlists
python auto-list.py playlist "Auto 1960s" --released-before "1970-01-01" --exclude "Holiday Songs"
python auto-list.py playlist "Auto 1970s" --released-after "1970-01-01" --released-before "1980-01-01" --exclude "Holiday Songs"
python auto-list.py playlist "1970s Party"  --released-before "1980-01-01" --sort energy --limit 150 
python auto-list.py playlist "Auto 1980s" --released-after "1980-01-01" --released-before "1990-01-01" --exclude "Holiday Songs"
python auto-list.py playlist "1980s Party"  --released-after "1980-01-01" --released-before "1990-01-01" --sort energy --limit 150 
python auto-list.py playlist "Auto 1990s" --released-after "1990-01-01" --released-before "2000-01-01" --exclude "Holiday Songs"
python auto-list.py playlist "1990s Party"  --released-after "1990-01-01" --released-before "2000-01-01" --sort energy --limit 150
python auto-list.py playlist "Auto 2000s" --released-after "2000-01-01" --released-before "2010-01-01" --exclude "Holiday Songs"
python auto-list.py playlist "2000s Party"  --released-after "2000-01-01" --released-before "2010-01-01" --sort energy --limit 150
python auto-list.py playlist "Auto 2010s" --released-after "2010-01-01" --released-before "2020-01-01" --exclude "Holiday Songs"
python auto-list.py playlist "2010s Party"  --released-after "2010-01-01" --released-before "2020-01-01" --sort energy --limit 150
python auto-list.py playlist "Auto 2020s" --released-after "2020-01-01" --released-before "2030-01-01" --exclude "Holiday Songs"
python auto-list.py playlist "2020s Party"  --released-after "2020-01-01" --released-before "2030-01-01" --sort energy --limit 150


@REM @REM @REM Genre Playlists
python auto-list.py playlist "Movies" --genre "orchestral soundtrack" --genre "soundtrack"  --genre "scorecore" --genre "theme"  --update-cache
python auto-list.py playlist "Movies Energetic" --genre "orchestral soundtrack" --genre "soundtrack"  --genre "scorecore" --genre "theme"  --min-energy 0.5 --update-cache
python auto-list.py playlist "Guitarra Clasica" --genre "guitarra clasica" --genre "classical guitar" --update-cache
python auto-list.py playlist "Classical Music" --genre "orchestra" --genre "orchestral"  --genre "symphony" --genre "post-romantic era" --genre "classical" --genre "symfonicky orchestr"  --exclude "Movies" --exclude "Guitarra Clasica" --exclude "Shaken And Stirred"
python auto-list.py playlist "Classical Quiet" --genre "orchestra" --genre "orchestral"  --genre "symphony" --genre "post-romantic era" --genre "classical" --genre "symfonicky orchestr" --max-loudness -25
python auto-list.py playlist "Neo Mellow" --genre "neo mellow" --genre "singer songwriter" --genre "uk singer songwriter" 
python auto-list.py playlist "Trance" --genre "trance" --genre "rave"
python auto-list.py playlist "Dinner Party" --min-acousticness 0.8 --max-energy 0.5 --max-instrumentalness 0.7 --max-duration_ms 3600000 --released-after "1980-01-01" 
python auto-list.py playlist "Dinner Party Classics" --min-acousticness 0.8 --max-energy 0.5 --max-instrumentalness 0.7 --max-duration_ms 3600000 --released-before "1980-01-01"
python auto-list.py playlist "Night Nights" --min-acousticness 0.9 --max-loudness -15 --max-speechiness 0.3 --max-energy 0.2 --max-danceability 0.3
python auto-list.py playlist "Danceability"  --sort "danceability" --limit 20
python auto-list.py playlist "Quiet"  --sort "loudness" --limit 50 --sort-ascending
python auto-list.py playlist "Energy"  --sort "energy" --limit 50
python auto-list.py playlist "Low-Energy"  --sort "energy" --limit 50 --sort-ascending
python auto-list.py playlist "Instrumentalness"  --sort "instrumentalness" --limit 20
python auto-list.py playlist "Low-Speechiness"  --sort "speechiness"  --sort-ascending --limit 20
python auto-list.py playlist "To Work To" --min-instrumentalness 0.65 --min-energy 0.7
python auto-list.py playlist "To Work To 4M" --min-instrumentalness 0.65 --added-after "T-120" 
python auto-list.py playlist "New Released To Work To" --min-instrumentalness 0.65 --min-energy 0.7 --released-after "T-365"
python auto-list.py playlist "Quiet Work" --min-instrumentalness 0.65 --max-energy 0.3 --max-danceability 0.5 --max-loudness -15
python auto-list.py playlist "Loud Work"  --min-instrumentalness 0.65  --min-energy 0.7 --min-loudness -15 
python auto-list.py playlist "Folky" --min-acousticness 0.8  --genre "british folk" --genre "folk" --genre "chamber pop" --genre "irish folk"
python auto-list.py playlist "Singer Songwriter" --genre "british singer-songwriter" --genre "singer-songwriter"
python auto-list.py playlist "First Wave" --genre "new wave" --genre "new romantic" --genre "permanent wave" --min-energy 0.6 --released-before "2000-01-01"
python auto-list.py playlist "Brit-Pop" --genre "britpop" --genre "madchester"  --released-after "1990-01-01"
python auto-list.py playlist "New Rock" --genre "rock" --released-after "2010-01-01"
python auto-list.py playlist "Big Band" --genre "adult standards"  --genre "vocal jazz" 

@REM Artist Playlists
python auto-list.py playlist "Radiohead Plus" --artist "Radiohead" --artist "Thom Yorke"  --artist "Jonny Greenwood" --artist "Modeselektor" --artist "The Smile" ^
        --track "Faust Arp" --track "Fake Plastic Trees" --track  "Idioteque" --track  "Exit Music" --track  "Everything in Its Right Place" ^
        --track "True Love Waits" --track  "Exit Music (For A Film)" --track  "Weird Fishes" 
python auto-list.py playlist "Tangerine Dream" --artist="Tangerine Dream" --artist-like="Tangerine Dream"
python auto-list.py playlist "Duran Duran" --artist "Duran Duran" --artist "Arcadia" 
python auto-list.py playlist "Doves" --artist "Doves" --artist-like="Doves"
python auto-list.py playlist "Michael Jackson" --artist "Michael Jackson" --artist "Janet Jackson" --artist "The Jacksons" --artist "The Jackson 5"
python auto-list.py playlist "Pet Shop Boys"  --artist "Pet Shop Boys" --artist "Tennant" --artist "Lowe"
python auto-list.py playlist "Laura Marling" --artist "Laura Marling" --artist "Laura Marling"
python auto-list.py playlist "Tears For Fears"  --artist "Tears For Fears" --artist "Roland Orzabal" --artist "Curt Smith"
python auto-list.py playlist "Beatles Plus" --artist "The Beatles" --artist "Paul McCartney"  --artist "John Lennon"  --artist "Ringo Starr"  --artist "George Harrison"  --artist "Wings"  --artist "George Martin" ^
        --album "Across The Universe" --album "Instant Karma" --album "Abbey Road" --album "Beatles" ^
        --track "Hard Day" --track  "Got to Get You Into My Life" --track   "Dear Prudence" --track  "Strawberry Fields" --track  "Maybe I'm Amazed" --track  "Golden Slumbers" --track  "Here Comes the Sun" --track  "A Day in the Life" 
python auto-list.py playlist "Paul McCartney" --artist "Paul McCartney" --artist "Wings"
python auto-list.py playlist "Queen Plus"  --artist "Queen" --artist "Freddie Mercury" --artist-like "Queen"
python auto-list.py playlist "Seal" --artist "Seal" --artist-like "Seal"
python auto-list.py playlist "Genesis" --artist "Phil Collins" --artist "Genesis" --artist "Peter Gabriel"
python auto-list.py playlist "Sade Plus" --artist "Sade" --artist-like "Sade" 
python auto-list.py playlist "Kate Bush" --artist "Kate Bush"
python auto-list.py playlist "Depeche Mode" --artist "Depeche Mode"
python auto-list.py playlist "Madonna" --artist "Madonna"
python auto-list.py playlist "Corinne Bailey Rae"  --artist "Corinne Bailey Rae" --artist-like "Corinne Bailey Rae"
python auto-list.py playlist "Oasis" --artist "Oasis" --artist "Noel Gallagher" --artist "Liam Gallagher" --artist "Beady Eye" --artist "Noel Gallagher's High Flying Birds"
python auto-list.py playlist "Alison Moyet" --artist "Alison Moyet" --artist "Yazoo" --artist-like "Alison Moyet"

@REM ./run-holidays.bat