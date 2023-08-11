# Utility Functions
# the packet will be organized in this way:
# T/F TID
# packet packet


def isLast(header):
    last = header.split(" ")[0]
    # print("is the last?: " + last)
    if last == "T":
        return True
    else:
        return False
    
def getTid(header):
    tid = header.split(" ")[1]
    return int(tid)


def narray_to_string(packet):
    string = ""
    for s in packet:
        string = string + " " + str(s)
    return string[1:]

def unique(_list):
    unique_list = []
    # traverse for all elements
    for x in _list:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list