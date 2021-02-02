from Vol2timing import Vol2timing

if __name__ == '__main__':
    # g_time_parser(["0700_0800","0800_0900"])
    datasetPath = r'Dataset\2_ASU_with_movement'
    Vol2timing(["0700_0800"], datasetPath)
