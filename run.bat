@REM Switch to Unicode as this batch file as accented characters
chcp 65001

@REM call .\venv\Scripts\activate.bat
call python auto-list.py update-cache --playlist "Noise" 
call python auto-list.py update-cache --playlist "Holiday Songs" --playlist "December Songs"
call python auto-list.py duplicates
@REM exit /b 0
@REM @REM @REM Latest Music

call python auto-list.py playlist "Genreless" --genre "NONE" 
call python auto-list.py playlist "Radio Won" --added-after "T-13" --exclude-noise --update-cache 
call python auto-list.py playlist "Radio Too" --exclude="Radio Won (A)" --exclude-noise --added-after "2024-01-30" 

call python auto-list.py playlist "Good Year" --released-after "T-365"
call python auto-list.py playlist "New Mix Takes" --released-after "T-365"  ^
    --exclude-genre "orchestra" --exclude-genre "orchestral"  --exclude-genre "symphony" ^
    --exclude-genre "string quartet" --exclude-genre "post-romantic era" ^
    --exclude-genre "classical" --exclude-genre "orchestral soundtrack" --exclude-genre "soundtrack"  ^
    --exclude-genre "guitarra clasica" --exclude-genre "classical guitar" ^
    --exclude-genre "british modern classical" --exclude-genre "german romanticism" --exclude-genre "russian romanticism" --exclude-genre "ukrainian classical"

@REM @REM @REM Decade Based Playlists
call python auto-list.py playlist "1960s" --released-before "1970-01-01" 
call python auto-list.py playlist "1970s" --released-after "1970-01-01" --released-before "1980-01-01" 
call python auto-list.py playlist "1980s" --released-after "1980-01-01" --released-before "1990-01-01" 
call python auto-list.py playlist "1990s" --released-after "1990-01-01" --released-before "2000-01-01" 
call python auto-list.py playlist "2000s" --released-after "2000-01-01" --released-before "2010-01-01" 
call python auto-list.py playlist "2010s" --released-after "2010-01-01" --released-before "2020-01-01" 
call python auto-list.py playlist "2020s" --released-after "2020-01-01" --released-before "2030-01-01" 


@REM @REM @REM Genre Playlists
call python auto-list.py playlist "Movies" --genre "orchestral soundtrack" --genre "soundtrack"  --genre "scorecore" --genre "theme"  --update-cache
call python auto-list.py playlist "Guitarra Clasica" --genre "guitarra clasica" --genre "classical guitar" --update-cache
call python auto-list.py playlist "Classical Music" --genre "orchestra" --genre "orchestral"  --genre "symphony" --genre "post-romantic era" --genre "classical" --genre "symfonicky orchestr" --genre "opera" --genre "baroque"  --exclude "Movies (A)" --exclude "Guitarra Clasica (A)" --exclude "Shaken And Stirred"
call python auto-list.py playlist "Neo Mellow" --genre "neo mellow" --genre "singer songwriter" --genre "uk singer songwriter" 
call python auto-list.py playlist "Trance" --genre "trance" --genre "rave"
call python auto-list.py playlist "Folky"  --genre "british folk" --genre "folk" --genre "chamber pop" --genre "irish folk"
call python auto-list.py playlist "Singer Songwriter" --genre "british singer-songwriter" --genre "singer-songwriter"
call python auto-list.py playlist "First Wave" --genre "new wave" --genre "new romantic" --genre "permanent wave"  --released-before "2000-01-01"
call python auto-list.py playlist "Brit-Pop" --genre "britpop" --genre "madchester"  --released-after "1990-01-01"
call python auto-list.py playlist "New Rock" --genre "rock" --released-after "2010-01-01"
call python auto-list.py playlist "Big Band" --genre "adult standards"  --genre "vocal jazz" 

@REM Artist Playlists
call python auto-list.py playlist "Radiohead" --artist "Radiohead" --artist "Thom Yorke"  --artist "Jonny Greenwood" --artist "Modeselektor" --artist "The Smile" ^
        --track "Faust Arp" --track "Fake Plastic Trees" --track  "Idioteque" --track  "Exit Music" --track  "Everything in Its Right Place" ^
        --track "True Love Waits" --track  "Exit Music (For A Film)" --track  "Weird Fishes" 
call python auto-list.py playlist "Tangerine Dream" --artist="Tangerine Dream" 
call python auto-list.py playlist "Massive Attack" --artist="Massive Attack" 
call python auto-list.py playlist "Duran Duran" --artist "Duran Duran" --artist "Arcadia" 
call python auto-list.py playlist "Doves" --artist "Doves" 
call python auto-list.py playlist "Michael Jackson" --artist "Michael Jackson" --artist "Janet Jackson" --artist "The Jacksons" --artist "The Jackson 5"
call python auto-list.py playlist "Pet Shop Boys & Erasure"  --artist "Pet Shop Boys" --artist "Tennant" --artist "Lowe" --artist "Erasure" --artist "Electronic" 
call python auto-list.py playlist "Laura Marling" --artist "Laura Marling" 
call python auto-list.py playlist "Tears For Fears"  --artist "Tears For Fears" --artist "Roland Orzabal" --artist "Curt Smith" 
call python auto-list.py playlist "Beatles" --artist "The Beatles" --artist "Paul McCartney"  --artist "John Lennon"  --artist "Ringo Starr"  --artist "George Harrison"  --artist "Wings"  --artist "George Martin" ^
        --album "Across The Universe" --album "Instant Karma" --album "Abbey Road" --album "Beatles" ^
        --track "Hard Day" --track  "Got to Get You Into My Life" --track   "Dear Prudence" --track  "Strawberry Fields" --track  "Maybe I'm Amazed" --track  "Golden Slumbers" --track  "Here Comes the Sun" --track  "A Day in the Life" 
call python auto-list.py playlist "Queen & Bowie"  --artist "Queen" --artist "Freddie Mercury" --artist "David Bowie" 
call python auto-list.py playlist "Genesis" --artist "Phil Collins" --artist "Genesis" --artist "Peter Gabriel"
call python auto-list.py playlist "Sade & Corinne" --artist "Sade" --artist "Corinne Bailey Rae" 
call python auto-list.py playlist "Depeche Mode" --artist "Depeche Mode" 
call python auto-list.py playlist "Madonna" --artist "Madonna" 
call python auto-list.py playlist "Ludovico Einaudi" --artist "Ludovico Einaudi" 
call python auto-list.py playlist "Blur vs Oasis" --artist "Oasis" --artist "Noel Gallagher" --artist "Liam Gallagher" --artist "Beady Eye" --artist "Noel Gallagher's High Flying Birds"  --artist "Blur" --artist "Gorillaz" 
call python auto-list.py playlist "Alison Moyet" --artist "Alison Moyet" --artist "Yazoo" 
call python auto-list.py playlist "Pink Floyd" --artist "Pink Floyd" 

./run-holidays.bat