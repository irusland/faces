#!/bin/bash
timeline="/Users/irusland/LocalProjects/faces_data/timeline"
input="/Users/irusland/LocalProjects/faces/timeline.txt"
COUNTER=1
while IFS= read -r line
do
  echo "$line"
  zcounter=$(printf "%04d" $COUNTER)
  ln -sf "$line" "${timeline}/${zcounter}.jpg"
  let COUNTER++
done < "$input"

