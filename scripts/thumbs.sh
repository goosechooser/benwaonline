#!/bin/bash

folder=/home/cg/docker_benwa/watched
echo "$(date) - $folder" >> /home/cg/thumb_log

for filename in $folder/*; do
    thumb_output=/home/cg/docker_benwa/media/thumbs/
    {
        echo "running thumb.py on $filename"
        echo "thumbnail output path $thumb_output"
        echo "python3.6 /home/cg/bin/thumb.py $filename $thumb_output" >> /home/cg/thumb_log
    } >> /home/cg/thumb_log

    python3.6 /home/cg/bin/thumb.py "$filename" "$thumb_output"

    ret=$?
    if [ $ret -ne 0 ]; then
        echo "thumb.py failed" >> /home/cg/thumb_log
    else
        echo "moved $filename" to "/docker_benwa/static/imgs/" >> /home/cg/thumb_log
        mv "$filename" /home/cg/docker_benwa/media/imgs/
    fi
done
