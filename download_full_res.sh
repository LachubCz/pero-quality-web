for i in $(cat id.rnd )
do
    wget https://kramerius.mzk.cz/search/iiif/uuid:$i/full/full/0/default.jpg -O ./images/$i.jpg
done
