SLEEP=0.5
DATA=0

while getopts s:b: flag 
do
    case "${flag}" in
        s) SERIAL=${OPTARG};;
        b) BAUDRATE=${OPTARG};;
    esac
done

if [ -z "$SERIAL" ]
then
    echo "The port being checked is not specified."
    exit 0
fi

if [ -z "$BAUDRATE" ]
then
    echo "Port baudrate is not set. Set default: 9600"
    BAUDRATE=9600
fi

stty -F $SERIAL $BAUDRATE
if [ $? -eq 0 ]
then
    echo "$SERIAL speed success set to: $BAUDRATE"
fi

while [ $DATA -lt 9 ]
do
    read DATA < $SERIAL
    sleep $SLEEP
    PASS_DATA=$(($DATA + 1))
    echo -en "Incremented data: $PASS_DATA\r"
    echo "$PASS_DATA" > $SERIAL
    sleep 0.01
done
