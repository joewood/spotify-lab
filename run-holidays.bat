@REM Switch to Unicode as this batch file as accented characters
chcp 65001
call .\venv\Scripts\activate.bat
call python auto-list.py update-cache --playlist "Noise" 
call python auto-list.py update-cache --playlist "Holiday Songs" --playlist "December Songs"


python auto-list.py playlist "December" --include "December Songs"  --include "Holiday Songs" --include-holidays --update-cache
python auto-list.py playlist "December Classical" --include "December Songs"  --include "Holiday Songs" ^
    --genre "orchestra" --genre "orchestral"  --genre "symphony" --genre "post-romantic era" ^
    --genre "classical" --genre "orchestral soundtrack" --genre "soundtrack"  --genre "guitarra clasica" ^
    --genre "post-romantic era" --genre "british modern classical" --genre "german romanticism" ^
    --genre "string quartet" --genre "russian romanticism" ^
    --genre "ukrainian classical" ^
    --genre "classical guitar"  --include-holidays --update-cache
python auto-list.py playlist "December Party" --include "December Songs"  --include "Holiday Songs" --min-energy 0.55 --include-holidays --exclude "December Classical"
python auto-list.py playlist "Holly Jolly" --include "December Songs"  --include "Holiday Songs" --min-energy 0.25 --include-holidays  --exclude "December Classical"
python auto-list.py playlist "December Chill" --include "December Songs"  --include "Holiday Songs" --max-energy 0.25 --include-holidays
python auto-list.py playlist "Silent Night" --include "December Songs"  --include "Holiday Songs" --max-danceability 0.4 --max-energy 0.4 --min-instrumentalness 0.15 --include-holidays
python auto-list.py playlist "December Work" --include "December Songs"  --include "Holiday Songs"  --min-energy 0.2 --min-instrumentalness 0.15 --include-holidays
python auto-list.py playlist "December Instrumental" --include "December Songs"  --include "Holiday Songs" --min-instrumentalness 0.15 --include-holidays
python auto-list.py playlist "December 3M" --include "December Songs" --added-after=T-90 --include "Holiday Songs" --include-holidays
python auto-list.py playlist "December This Year" --include "December Songs" --added-after=T-450 --include "Holiday Songs" --include-holidays
python auto-list.py playlist "December New" --include "December Songs" --released-after=T-365 --include "Holiday Songs"  --include-holidays
python auto-list.py playlist "December Classics" --include "December Songs" --released-before="1990-01-01" --include "Holiday Songs" --exclude "December Classical" --include-holidays
python auto-list.py playlist "December Pop" --include "December Songs"  --include "Holiday Songs" --exclude "December Classical" --include-holidays
