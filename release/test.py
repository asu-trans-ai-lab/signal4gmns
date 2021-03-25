#pip install Vol2timing --upgrade

from Vol2timing import *

def One_step_executation():
    #Step 0: Set up working directory
    datasetPath_root = r''
    Set_Working_Directory(datasetPath_root)
    #Step 1: Load data
    time_Period="0700_0800"
    Read_Input_Data(time_Period)
    #Step 2: Check the list of signal nodes (Optional)
    Display_signalNode_info()
    #Step 3: PerformQEM for each signal node
    loggings.info('Step 3: PerformQEM for each Signal Node')
    for it in g_signal_node_map:
        g_signal_node_map[it].PerformQEM(it)
    #Step 4: Calculate performance metrics
    g_pFileServiceArc_list, signal_timing_phase_list, signal_phase_mvmt_list=Calculate_Metrics()
    #Step 5: Output files
    Output_Files(g_pFileServiceArc_list,signal_timing_phase_list,signal_phase_mvmt_list)

def Step_by_step_processing_with_internallopp():
    #Step 0: Set Working Directory
    datasetPath_root = r''
    Set_Working_Directory(datasetPath_root)
    #Step 1: Load Data
    time_Period="0700_0800"
    Read_Input_Data(time_Period)
    #Step 2: Check the List of Signal Nodes (Optional)
    Display_signalNode_info()
    #Step 3: PerformQEM for each Signal Node
    loggings.info('Step 3: PerformQEM for each Signal Node')
    for it in g_signal_node_map:
        loggings.info(f"Main Node ID: {str(it)}",2)
        node=g_signal_node_map[it]
        #Step 2.1: Set Left Turn Treatment
        node.Set_Left_Turn_Treatment()
        #Step 2.2: Set Stage No. for Movements
        node.Set_StageNo_for_Movements()
        #Step 2.3: Set Saturation Flow Rate Matrix
        node.Set_Saturation_Flow_Rate_Matrix()
        #Step 2.4: Calculate Max Flow Ratio
        node.Calculate_Flow_of_Ratio_Max()
        #Step 2.5: Calculate Total Cycle Lost Time
        node.Calculate_Total_Cycle_Lost_Time()
        #Step 2.6: Calculate the Minimum and Optimal Cycle Length
        node.Calculate_the_Minimum_And_Optimal_Cycle_Length()
        #Step 2.7: Calculate x_c'
        node.Calculate_the_x_c_Output()
        #Step 2.8: Calculate Green Time for Stages
        node.Calculate_Green_Time_for_Stages()
        #Step 2.9: Print Green Time for Stages
        node.Printing_Green_Time_for_Stages()
        #Step 2.10: Calculate Capacity and V over C Ratio
        node.Calculate_Capacity_And_Ratio_V_over_C()
        #Step 2.11: Calculate Signal Delay
        node.Calculate_Signal_Delay(it)
        #Step 2.12: Judge Signal LOS
        node.Judge_Signal_LOS(it)
    #Step 4: Calculate Metrics
    g_pFileServiceArc_list, signal_timing_phase_list, signal_phase_mvmt_list=Calculate_Metrics()
    #Step 5: Output Files
    Output_Files(g_pFileServiceArc_list,signal_timing_phase_list,signal_phase_mvmt_list)

if __name__ == '__main__':

    #mode 1. If you want to learn this package step by step, use Step_by_Step_Processing()
    #Step_by_step_processing()

    #mode 2 Integrated_Processing()

    # 3. The automated processing function with two parameters, time range and path.
    # You can set your own data directory, or put data on root
    
    #mode 3
    datasetPath_root = r''
    Vol2timing("0700_0800", datasetPath_root)

