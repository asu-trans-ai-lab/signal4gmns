from signal4gmns import *


def Processing():
    # Step 0.1: Set Working Directory
    data_Set_Path = r''
    # Step 0.2: Set Working Directory
    Set_Working_Directory(data_Set_Path)
    intermediate_file_label='position'
    # Step 1: Load Data
    Read_Input_Data()
    # Step 2: Check the List of Signal Nodes (Optional)
    Display_signalNode_info()
    # Step 3: perform three modules for each Signal Node
    loggings.info('Module 1: Output Location for each Signal Node')
    
    for osmID, signal_Node in g_node_map.items():
        signal_Node.Set_Major_Apporach()
    Output_Intermediate_Files(intermediate_file_label)
    loggings.info('Module 2: Perform Left turn treatment for each Signal Node')
    Input_Intermediate_Files(intermediate_file_label)
    intermediate_file_label='volume'
    
    for osmID, signal_Node in g_node_map.items():
        signal_Node.Initialization()
    Output_Intermediate_Files(intermediate_file_label)
    loggings.info('Module 3: Perform QEM for each Signal Node')
    Input_Intermediate_Files(intermediate_file_label)

    for osmID,signal_Node in g_node_map.items():
        signal_Node.PerformQEM()

    #Step 4: Output signal_timing_phase.csv and signal_timing_phase.csv Files
    Output_Singal_Timing_Movement_Files()
    #Step 6: convert signal_timing_phase.csv and signal_timing_phase.csv to timing.csv
    Output_Timing_File()

def osm_2_gmns():
    import osm2gmns as og
    net = og.getNetFromOSMFile('map.osm', default_lanes=True, POIs=True)
    og.consolidateComplexIntersections(net)
    og.outputNetToCSV(net, output_folder='consolidated')
    og.generateMovements(net)
    og.outputNetToCSV(net)


#    og.saveFig(net)


if __name__ == '__main__':
    #convert .osm file to movement.csv etc.
    # osm_2_gmns()


    Processing()


