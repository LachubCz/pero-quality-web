for i in $(cat ids.data )
do
    wget https://kramerius.mzk.cz/search/iiif/uuid:$i/full/full/0/default.jpg -O ./images/$i.jpg
done
