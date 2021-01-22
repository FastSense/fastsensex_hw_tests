SERIAL=$1
READ_DATA=""
DATA=0
SLEEP=0.5

if [ -z "$SERIAL" ]
then
    echo "The port being checked is not specified."
    exit 0
fi

while [ $DATA -lt 10 ]
do
    echo $DATA > $SERIAL
    sleep 0.01
    read -t 3 READ_DATA < $SERIAL

    if [ "$READ_DATA" == "$(($DATA + 1))" ]
    then
        echo -en "Read: ${READ_DATA}\r"
        DATA=$READ_DATA
    else
        echo "Unable to read data. Make sure the loopback cable is installed, the port is selected correctly and reader.sh is running."
        DATA=0
        #echo -en "Read:                 \r"
    fi
    sleep $SLEEP
done

echo "Verification passed. Serial: $SERIAL works correctly"
