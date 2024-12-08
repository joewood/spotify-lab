# python auto-list.py update-cache --playlist "Noise" 
# python auto-list.py update-cache --playlist "Holiday Songs" --playlist "December Songs"

python auto-list.py playlist "December" --include "December Songs"  --include "Holiday Songs" --include-holidays --update-cache
python auto-list.py playlist "December Classical" --include "December Songs"  --include "Holiday Songs" \
    --genre "orchestra" --genre "orchestral"  --genre "symphony" --genre "post-romantic era" \
    --genre "classical" --genre "orchestral soundtrack" --genre "soundtrack"  --genre "guitarra clasica" \
    --genre "post-romantic era" --genre "british modern classical" --genre "german romanticism" \
    --genre "string quartet" --genre "russian romanticism" \
    --genre "ukrainian classical" \
    --genre "classical guitar"  --include-holidays --update-cache
python auto-list.py playlist "December This Year" --include "December Songs" --added-after=T-450 --include "Holiday Songs" --include "December Songs" --include-holidays --exclude-noise 
python auto-list.py playlist "December New" --include "December Songs" --released-after=T-365 --include "Holiday Songs" --include "December Songs"  --include-holidays --exclude-noise 
python auto-list.py playlist "December Classics" --include "December Songs" --released-before="1990-01-01" --include "Holiday Songs" --exclude "December Classical (A)" --include-holidays
python auto-list.py playlist "December Pop" --include "December Songs"  --include "Holiday Songs" --exclude "December Classical (A)" --include-holidays
