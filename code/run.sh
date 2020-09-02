exiftool -q -DateTimeOriginal -m -p '$Directory/$FileName|$DateTimeOriginal' \
 -r $DIR src_test/* | sort -t '|' -k 2 | cut -d'|' -f 1 |
(
xargs cat
) \
| \
ffmpeg -y -framerate 10 -f image2pipe -i - out.mkv
