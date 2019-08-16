for i in $(find ./images/ | grep jpg)
do
    echo $i $(for x in $(seq 10); do printf " %d:%d" $(($RANDOM % 3500)) $(($RANDOM % 5000)); done )
done
