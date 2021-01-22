SERIAL=$1
SLEEP=0.5
DATA=0

if [ -z "$SERIAL" ]
then
    echo "The port being checked is not specified."
    exit 0
fi

while [ $DATA -lt 10 ]
do
    read DATA < $SERIAL
    sleep $SLEEP
    PASS_DATA=$(($DATA + 1))
    echo -en "Incremented data: $PASS_DATA\r"
    echo "$PASS_DATA" > $SERIAL
    sleep 0.01
done
