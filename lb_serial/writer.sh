SERIAL=$1
READ_DATA=""
DATA=0
SLEEP=0.02

if [ -z "$SERIAL" ]
then
    echo "The port being checked is not specified."
    exit 0
fi

while [ $DATA -lt 100 ]
do
    echo $DATA > $SERIAL
    read -t 5 READ_DATA < $SERIAL
    echo $READ_DATA

    if [ "$READ_DATA" == "$(($DATA + 1))" ]
    then
        echo -en "Read: ${READ_DATA}\r"
    else
        if [ $DATA != 0 ]
        then
            echo "Verification serial: $SERIAL read failure"
            echo "Passed data: $DATA, readed data: $READ_DATA"
        else
            echo "Unable to read data. Make sure the loopback cable is installed, the port is selected correctly and reader.sh is running."
        fi
        DATA=0
        echo -en "Read:                 \r"
    fi
    sleep $SLEEP
done

echo "Verification passed. Serial: $SERIAL works correctly"
