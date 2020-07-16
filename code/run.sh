exiftool -q -DateTimeOriginal -m -p '$Directory/$FileName|$DateTimeOriginal' \
-r $PWD  * | sort -t '|' -k 2 | cut -d'|' -f | \
(
cat
) \
| \



