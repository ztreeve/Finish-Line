import sys
def intToTime(timeInt):
    timeStr = str(timeInt)
    time = ""
    
    if timeInt <= 999: time = str(timeInt%1000-timeInt%10)
    elif timeInt <= 9999 and timeInt > 999: time = "{}:{}".format(timeStr[0],timeStr[1:3])
    elif timeInt <= 99999 and timeInt > 9999: time = "{}:{}".format(timeStr[0:2],timeStr[2:4])
    elif timeInt <= 99999 and timeInt > 9999: time = "{}:{}".format(timeStr[0:2],timeStr[2:4])
    elif timeInt <= 999999 and timeInt > 99999: time = "{}:{}:{}".format(timeStr[0],timeStr[1:3],timeStr[3:4])
    
    if timeInt % 10 != 0:
        time = time + ".{}".format(timeInt%10)
    return time

print(intToTime(int(sys.argv[1])))