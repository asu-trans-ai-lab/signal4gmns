from signal4gmns import *


def Processing():
    # Step 0.1: Set Working Directory
    data_Set_Path = r''
    # Step 0.2: Set Working Directory
    Set_Working_Directory(data_Set_Path)
    inter='--check_position'
    # Step 1: Load Data
    Read_Input_Data()
    # Step 2: Check the List of Signal Nodes (Optional)
    Display_signalNode_info()
    # Step 3: perform three modules for each Signal Node
    loggings.info('Module 1: Output Location for each Signal Node')
    for osmID, signal_Node in g_node_map.items():
        signal_Node.Set_Major_Apporach()
    Output_Intermediate_Files(inter)
    loggings.info('Module 2: Perform Left turn treatment for each Signal Node')
    Input_Intermediate_Files(inter)
    inter='--set_volume'
    for osmID, signal_Node in g_node_map.items():
        signal_Node.Initialization()
    Output_Intermediate_Files(inter)
    loggings.info('Module 3: Perform QEM for each Signal Node')
    Input_Intermediate_Files(inter)

    for osmID,signal_Node in g_node_map.items():
        signal_Node.PerformQEM()

    #Step 4: Output two signal_timing_phase Files
    # obtain the two jump-two files
    Output_Singal_Timing_Movement_Files()
    #Step 6: jump-three, convert the two files to timing.csv
    Output_Timing_File()

if __name__ == '__main__':

    import osm2gmns as og
    net = og.getNetFromOSMFile('map.osm', default_lanes=True, POIs=True)
    og.connectPOIWithNet(net)
    og.generateNodeActivityInfo(net)
    og.consolidateComplexIntersections(net)
    og.outputNetToCSV(net, output_folder='consolidated')
    og.generateMovements(net)
    og.outputNetToCSV(net)
    og.show(net)
#    og.saveFig(net)

    Processing()


    # for testing
    # datasetPath_multi_level = r'Dataset\3_ASU_0314'
    # datasetPath_root = r''
    # signal4gmns(datasetPath_root)

