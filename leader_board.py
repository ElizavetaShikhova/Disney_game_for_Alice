def create_leader_board(data,user_id):
    a = []
    for i in data:
        a.append((i,(data[i]["name"]).title(),data[i]["points"]))
    a.sort(key=lambda x:x[2],reverse=True)
    res=''
    ind = -1
    for i in range(len(a)):
        if i<10:
            res += f"{i+1}. {a[i][1]}, {a[i][2]}\n"
        if user_id in a[i]:
            ind = i
        if ind!=-1 and i>=10:
            break
    res += "     ...     \n"
    res += f"{ind+1}. {data[user_id]['name'].title()}, {data[user_id]['points']}"
    return res