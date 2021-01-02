import Vol2timing as v2

def g_time_parser(inputstring):
    output_global_minute=[]
    for k in list(inputstring):
        sub_string = k.split('_')
        for i in sub_string:
            hh1=i[0]
            hh2 = i[1]
            mm1 = i[2]
            mm2 = i[3]
            hhf1 = (float(hh1) - 48)
            hhf2 = (float(hh2) - 48)
            mmf1 = (float(mm1) - 48)
            mmf2 = (float(mm2) - 48)
            hh = hhf1 * 10 * 60 + hhf2 * 60
            mm = mmf1 * 10 + mmf2
            global_mm_temp = hh + mm
            output_global_minute.append(global_mm_temp)
    return output_global_minute  # transform hhmm to minutes


if __name__ == '__main__':
    # g_time_parser(["0700_0800","0800_0900"])
    v2.Vol2timing(1,1,1)

