SERIAL=$1
SLEEP=0.01

if [ -z "$SERIAL" ]
then
    echo "The port being checked is not specified."
    exit 0
fi

while true
do
    read DATA < $SERIAL
    sleep $SLEEP
    echo "$(($DATA + 1))" > $SERIAL
    sleep $SLEEP
done
