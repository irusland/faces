exiftool -q -DateTimeOriginal -m -p '$Directory/$FileName|$DateTimeOriginal' \
 -r $DIR src_test/* | sort -t '|' -k 2 | cut -d'|' -f 1 |
(
while read -r line || [[ -n "$line" ]]; do
  echo processing "$line";
  cat $line | python -u code/modules/starter.py
  break
done
)\
| open -a Preview.app -f