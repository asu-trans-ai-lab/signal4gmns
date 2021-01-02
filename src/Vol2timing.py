"""  Portions Copyright 2019
 Xuesong (Simon) Zhou
   If you help write or modify the code, please also list your names here.
   The reason of having Copyright info here is to ensure all the modified version, as a whole, under the GPL
   and further prevent a violation of the GPL.

 More about "How to use GNU licenses for your own software"
 http://www.gnu.org/licenses/gpl-howto.html
 """
import os
import pandas as pd
import datetime
from enum import Enum
import numpy as np
import math

os.getcwd()
os.chdir(r'Dataset\1_signal_intersection_test2')

g_node_vector = []
g_link_vector = []
g_service_arc_vector = []
g_signal_node_map = {}



#enum
class movement_Index(Enum):
    EBL=1
    EBT=2
    EBR=3
    WBL=4
    WBT=5
    WBR=6
    NBL=7
    NBT=8
    NBR=9
    SBL=10
    SBT=11
    SBR=12

class stage(Enum):
    no_stage=-1
    stage1=1
    stage2=2
    stage3=3
    stage4=4

class direction(Enum):
    E=1
    W=2
    N=3
    S=4

class group(Enum):
    L=1
    T_AND_R=2

class left_Turn_Treatment(Enum):
    perm=0
    prot=1
    no_business=-1

#array size, for constructing matirx or array
laneColumnSize = 32
movementSize = 12
directionSize = 4
NEMA_PhaseSize = 32 # temp enable=false
stageSize = 4
ringSize = 3

groupSize = 5


#global parameters
l = 12
x_c_Input = 0.9
PHF = 1
f_1 = 1
f_2 = 1
t_L = 4
t_Yellow = 4
t_AR = 2
minGreenTime = 5

class CMainModual:
    def __init__(self):
        self.g_number_of_links = 0
        self.g_number_of_service_arcs = 0
        self.g_number_of_nodes = 0
        self.b_debug_detail_flag = 1
        self.g_pFileDebugLog = None
        self.g_informationCount = 0
        self.g_internal_node_to_seq_no_map = {}
        self.g_road_link_id_map = {}
        self.g_number_of_zones = 0
        self.g_LoadingStartTimeInMin = 0
        self.g_LoadingEndTimeInMin = 0
        print('Logging Time:', datetime.datetime.now(), '---------------------')

class SMovementData:
    def __init__(self):
        self.Enable = False
        self.LinkSeqNo=None
        self.PhaseNo=None
        self.StageNo_in_Order = []
        self.Volume=0
        self.Lanes=None
        self.SharedLanes=None
        self.GroupNo=None
        self.DirectionNo=None
        self.Assignment_Order=None
        self.left_Turn_Treatment=None


class CSignalNode:
    def __init__(self):
        self.y_StageMax = 1
        self.x_c_output = 0.9
        self.c_Min = 60

        # [None] * (stageSize + 1)
        self.green_Start_Stage_Array = [0] * (stageSize+1)
        self.green_End_Stage_Array = [0] * (stageSize+1)
        self.y_Max_Stage_Array = [0] * (stageSize+1)
        self.green_Time_Stage_Array = [0] * (stageSize+1)
        self.cumulative_Green_Start_Time_Stage_Array = [0] * (stageSize+1)
        self.cumulative_Green_End_Time_Stage_Array = [0] * (stageSize+1)
        self.effective_Green_Time_Stage_Array = [0] * (stageSize+1)
        self.cumulative_Effective_Green_Start_Time_Stage_Array = [0] * (stageSize+1)
        self.cumulative_Effective_Green_End_Time_Stage_Array = [0] * (stageSize+1)
        self.ratio_of_Effective_Green_Time_to_Cycle_Length_Array = [0] * (stageSize+1)
        self.approach_Average_Delay_Array = [0] * (directionSize+1)
        self.approach_Total_Delay_Array = [0] * (directionSize+1)
        self.approach_Total_Volume_Array = [0] * (directionSize+1)

        self.saturation_Flow_Rate_Matrix = np.empty([stageSize + 1, movementSize + 1])
        self.stage_Direction_Candidates_Matrix = np.empty([stageSize + 1, directionSize + 1, groupSize + 1])
        self.y_Stage_Movement_Matrix = np.empty([stageSize + 1, movementSize + 1])
        self.capacity_by_Stage_and_Movement_Matrix = np.empty([stageSize + 1, movementSize + 1])
        self.v_over_C_by_Stage_and_Movement_Matrix = np.empty([stageSize + 1, movementSize + 1])
        self.average_Uniform_Delay_Matrix = np.empty([stageSize + 1, movementSize + 1])
        self.NEMA_Phase_Matrix = [[0, 0, 0, 0, 1], [5, 0, 2, 6, 0], [3, 7, 0, 4, 8]]
        self.green_Start_NEMA_Phase = np.empty([5, 3])
        self.Stage_Ring_Movement_Matrix = {}
        for a in range(ringSize + 1):
            for b in range(stageSize + 1):
                self.Stage_Ring_Movement_Matrix[ringSize + 1, stageSize + 1] = SMovementData()

        self.movement_str_to_index_map={}
        self.movement_str_to_index_map["EBL"] = movement_Index.EBL
        self.movement_str_to_index_map["EBT"] = movement_Index.EBT
        self.movement_str_to_index_map["EBR"] = movement_Index.EBR

        self.movement_str_to_index_map["WBL"] = movement_Index.WBL
        self.movement_str_to_index_map["WBT"] = movement_Index.WBT
        self.movement_str_to_index_map["WBR"] = movement_Index.WBR

        self.movement_str_to_index_map["NBL"] = movement_Index.NBL
        self.movement_str_to_index_map["NBT"] = movement_Index.NBT
        self.movement_str_to_index_map["NBR"] = movement_Index.NBR

        self.movement_str_to_index_map["SBL"] = movement_Index.SBL
        self.movement_str_to_index_map["SBT"] = movement_Index.SBT
        self.movement_str_to_index_map["SBR"] = movement_Index.SBR

        self.movement_str_array={}
        self.movement_str_array[movement_Index.EBL] = "EBL"
        self.movement_str_array[movement_Index.EBT] = "EBT"
        self.movement_str_array[movement_Index.EBR] = "EBR"
        self.movement_str_array[movement_Index.WBL] = "WBL"
        self.movement_str_array[movement_Index.WBT] = "WBT"
        self.movement_str_array[movement_Index.WBR] = "WBR"
        self.movement_str_array[movement_Index.NBL] = "NBL"
        self.movement_str_array[movement_Index.NBT] = "NBT"
        self.movement_str_array[movement_Index.NBR] = "NBR"
        self.movement_str_array[movement_Index.SBL] = "SBL"
        self.movement_str_array[movement_Index.SBT] = "SBT"
        self.movement_str_array[movement_Index.SBR] = "SBR"

        self.movement_str_to_direction_map={}
        self.movement_str_to_direction_map["EBL"] = direction.E
        self.movement_str_to_direction_map["EBT"] = direction.E
        self.movement_str_to_direction_map["EBR"] = direction.E

        self.movement_str_to_direction_map["WBL"] = direction.W
        self.movement_str_to_direction_map["WBT"] = direction.W
        self.movement_str_to_direction_map["WBR"] = direction.W

        self.movement_str_to_direction_map["NBL"] = direction.N
        self.movement_str_to_direction_map["NBT"] = direction.N
        self.movement_str_to_direction_map["NBR"] = direction.N

        self.movement_str_to_direction_map["SBL"] = direction.S
        self.movement_str_to_direction_map["SBT"] = direction.S
        self.movement_str_to_direction_map["SBR"] = direction.S

        self.left_Movement_Opposing_Index_Map={}
        self.left_Movement_Opposing_Index_Map[movement_Index.EBL] = movement_Index.WBT
        self.left_Movement_Opposing_Index_Map[movement_Index.WBL] = movement_Index.EBT
        self.left_Movement_Opposing_Index_Map[movement_Index.NBL] = movement_Index.SBT
        self.left_Movement_Opposing_Index_Map[movement_Index.SBL] = movement_Index.NBT

        self.left_Movement_Counterpart_Index_Map={}
        self.left_Movement_Counterpart_Index_Map[movement_Index.EBL] = movement_Index.EBT
        self.left_Movement_Counterpart_Index_Map[movement_Index.WBL] = movement_Index.WBT
        self.left_Movement_Counterpart_Index_Map[movement_Index.NBL] = movement_Index.NBT
        self.left_Movement_Counterpart_Index_Map[movement_Index.SBL] = movement_Index.SBT

        self.left_Movement_Counterpart_Right_Trun_Index_Map={}
        self.left_Movement_Counterpart_Right_Trun_Index_Map[movement_Index.EBL] = movement_Index.EBR
        self.left_Movement_Counterpart_Right_Trun_Index_Map[movement_Index.WBL] = movement_Index.WBR
        self.left_Movement_Counterpart_Right_Trun_Index_Map[movement_Index.NBL] = movement_Index.NBR
        self.left_Movement_Counterpart_Right_Trun_Index_Map[movement_Index.SBL] = movement_Index.SBR

        self.movement_Index_to_Group_Map={}
        self.movement_Index_to_Group_Map[movement_Index.EBL] = group(1)
        self.movement_Index_to_Group_Map[movement_Index.EBT] = group(2)
        self.movement_Index_to_Group_Map[movement_Index.EBR] = group(2)
        self.movement_Index_to_Group_Map[movement_Index.WBL] = group(1)
        self.movement_Index_to_Group_Map[movement_Index.WBT] = group(2)
        self.movement_Index_to_Group_Map[movement_Index.WBR] = group(2)
        self.movement_Index_to_Group_Map[movement_Index.NBL] = group(1)
        self.movement_Index_to_Group_Map[movement_Index.NBT] = group(2)
        self.movement_Index_to_Group_Map[movement_Index.NBR] = group(2)
        self.movement_Index_to_Group_Map[movement_Index.SBL] = group(1)
        self.movement_Index_to_Group_Map[movement_Index.SBT] = group(2)
        self.movement_Index_to_Group_Map[movement_Index.SBR] = group(2)

        self.direction_index_to_str_map={}
        self.direction_index_to_str_map[direction.E] = "E"
        self.direction_index_to_str_map[direction.W] = "W"
        self.direction_index_to_str_map[direction.N] = "N"
        self.direction_index_to_str_map[direction.S] = "S"

        self.intersection_Average_Delay = 0
        self.intersection_Total_Delay = 0
        self.intersection_Total_Volume = 0

        self.left_Turn_Treatment_index_to_str_map={}
        self.left_Turn_Treatment_index_to_str_map[left_Turn_Treatment.prot] = "Protected"
        self.left_Turn_Treatment_index_to_str_map[left_Turn_Treatment.perm] = "Permissive"
        self.left_Turn_Treatment_index_to_str_map[left_Turn_Treatment.no_business] = "Null"

        for s in range(stageSize+1):
            self.y_Max_Stage_Array[s] = 0

            for m in range(movementSize+1):
                self.saturation_Flow_Rate_Matrix[s][m] = 0
                self.capacity_by_Stage_and_Movement_Matrix[s][m] = 0

            for d in range(directionSize+1):
                for g in range(groupSize+1):
                    self.stage_Direction_Candidates_Matrix[s][d][g] = 0
                self.approach_Average_Delay_Array[d] = 0
                self.approach_Total_Delay_Array[d] = 0
                self.approach_Total_Volume_Array[d] = 0

        self.movement_Array=[]
        for m in range(movementSize+1):
            self.movement_Array.append(SMovementData())


    def PerformQEM(self,nodeID):
        self.Set_Left_Turn_Treatment()
        self.Set_StageNo_for_Movements()
        self.Set_Saturation_Flow_Rate_Matrix()
        self.Calculate_Flow_of_Ratio_Max()
        self.Calculate_Total_Cycle_Lost_Time()
        self.Calculate_the_Minimum_And_Optimal_Cycle_Length()
        self.Calculate_the_x_c_Output()
        self.Calculate_Green_Time_for_Stages()
        self.Printing_Green_Time_for_Stages()
        self.Calculate_Capacity_And_Ratio_V_over_C()
        self.Calculate_Signal_Delay(nodeID)
        self.Judge_Signal_LOS(nodeID)

    def AddMovementVolume(self, link_seq_no, str_movement, volume, lanes, sharedLanes):
        mi = self.movement_str_to_index_map[str_movement]
        di = direction(self.movement_str_to_direction_map[str_movement])
        self.movement_Array[mi.value].Enable = True
        self.movement_Array[mi.value].LinkSeqNo = link_seq_no
        self.movement_Array[mi.value].Volume = volume
        self.movement_Array[mi.value].GroupNo = self.movement_Index_to_Group_Map[mi]
        self.movement_Array[mi.value].DirectionNo = di
        self.movement_Array[mi.value].left_Turn_Treatment = left_Turn_Treatment.no_business
        self.movement_Array[mi.value].Lanes = lanes
        self.movement_Array[mi.value].SharedLanes = sharedLanes

    def Set_Left_Turn_Treatment(self):
        for m in range(1, movementSize+1):
            if self.movement_Array[m].GroupNo.value == 1:
                final_decision = 0
                #(1)Left-turn Lane Check
                if self.movement_Array[m].Lanes > 1:
                    final_decision = 1
                #(2)Minimum Volume Check
                if self.movement_Array[m].Volume >= 240:
                    final_decision = 1
                #(3)Opposing Through Lanes Check
                op_Movement_Index = self.left_Movement_Opposing_Index_Map[movement_Index(m)]
                if (self.movement_Array[op_Movement_Index.value].Lanes >= 4):
                    final_decision = 1
                #(4)Opposing Traffic Speed Check

				#(5)Minimum Cross-Product Check
                co_Movement_Index = self.left_Movement_Opposing_Index_Map[movement_Index(m)]
                if (self.movement_Array[co_Movement_Index.value].Lanes > 1):
                    if self.movement_Array[co_Movement_Index.value].Volume * self.movement_Array[m].Volume >= 100000:
                        final_decision = 1
                else:
                    if self.movement_Array[co_Movement_Index.value].Volume * self.movement_Array[m].Volume >= 50000:
                        final_decision = 1
                #(6)if there is no T movement, then the left movement should be protected'''
                if self.movement_Array[self.left_Movement_Counterpart_Index_Map[movement_Index(m)].value].Enable == False:
                    final_decision = 1
            else:
                final_decision = -1

            self.movement_Array[m].Left_Turn_Treatment = left_Turn_Treatment(final_decision)


    def Set_StageNo_for_Movements(self):
        east_And_West_Volume = self.movement_Array[movement_Index.EBL.value].Volume + self.movement_Array[movement_Index.EBT.value].Volume + self.movement_Array[movement_Index.EBR.value].Volume + self.movement_Array[movement_Index.WBL.value].Volume + self.movement_Array[movement_Index.WBT.value].Volume + self.movement_Array[movement_Index.WBR.value].Volume
        north_And_South_Volume = self.movement_Array[movement_Index.NBL.value].Volume + self.movement_Array[movement_Index.NBT.value].Volume + self.movement_Array[movement_Index.NBR.value].Volume + self.movement_Array[movement_Index.SBL.value].Volume + self.movement_Array[movement_Index.SBT.value].Volume + self.movement_Array[movement_Index.SBR.value].Volume
        self.stage_Actual_Size = 2


        east_And_West_Flag = False
        north_And_South_Flag = False
        if self.movement_Array[movement_Index.EBL.value].left_Turn_Treatment.name == 'prot':
            self.stage_Actual_Size += 1
            east_And_West_Flag = True
        elif self.movement_Array[movement_Index.WBL.value].left_Turn_Treatment.name == 'prot':
            self.stage_Actual_Size += 1
            east_And_West_Flag = True
        if self.movement_Array[movement_Index.NBL.value].left_Turn_Treatment.name == 'prot':
            self.stage_Actual_Size += 1
            north_And_South_Flag = True
        elif self.movement_Array[movement_Index.SBL.value].left_Turn_Treatment.name == 'prot':
            self.stage_Actual_Size += 1
            north_And_South_Flag = True

        # firstL = movement_Index
        # firstT = movement_Index
        # firstR = movement_Index
        # secondL = movement_Index
        # secondT = movement_Index
        # secondR = movement_Index
        # thridL = movement_Index
        # thridT = movement_Index
        # thridR = movement_Index
        # fouthL = movement_Index
        # fouthT = movement_Index
        # fouthR = movement_Index
        if (east_And_West_Volume >= north_And_South_Volume):
            firstL = movement_Index.EBL.value
            firstT = movement_Index.EBT.value
            firstR = movement_Index.EBR.value
            secondL = movement_Index.WBL.value
            secondT = movement_Index.WBT.value
            secondR = movement_Index.WBR.value
            thridL = movement_Index.NBL.value
            thridT = movement_Index.NBT.value
            thridR = movement_Index.NBR.value
            fouthL = movement_Index.SBL.value
            fouthT = movement_Index.SBT.value
            fouthR = movement_Index.SBR.value
        else:
            firstL = movement_Index.NBL.value
            firstT = movement_Index.NBT.value
            firstR = movement_Index.NBR.value
            secondL = movement_Index.SBL.value
            secondT = movement_Index.SBT.value
            secondR = movement_Index.SBR.value
            thridL = movement_Index.EBL.value
            thridT = movement_Index.EBT.value
            thridR = movement_Index.EBR.value
            fouthL = movement_Index.WBL.value
            fouthT = movement_Index.WBT.value
            fouthR = movement_Index.WBR.value

        if east_And_West_Flag:
            self.movement_Array[firstL].StageNo_in_Order.append(stage.stage1)
            self.movement_Array[firstT].StageNo_in_Order.append(stage.stage2)
            self.movement_Array[firstR].StageNo_in_Order.append(stage.stage2)
            self.movement_Array[secondL].StageNo_in_Order.append(stage.stage1)
            self.movement_Array[secondT].StageNo_in_Order.append(stage.stage2)
            self.movement_Array[secondR].StageNo_in_Order.append(stage.stage2)
            if (north_And_South_Flag):
                self.movement_Array[thridL].StageNo_in_Order.append(stage.stage3)
                self.movement_Array[thridT].StageNo_in_Order.append(stage.stage4)
                self.movement_Array[thridR].StageNo_in_Order.append(stage.stage4)
                self.movement_Array[fouthL].StageNo_in_Order.append(stage.stage3)
                self.movement_Array[fouthT].StageNo_in_Order.append(stage.stage4)
                self.movement_Array[fouthR].StageNo_in_Order.append(stage.stage4)
            else:
                self.movement_Array[thridL].StageNo_in_Order.append(stage.stage3)
                self.movement_Array[thridT].StageNo_in_Order.append(stage.stage3)
                self.movement_Array[thridR].StageNo_in_Order.append(stage.stage3)
                self.movement_Array[fouthL].StageNo_in_Order.append(stage.stage3)
                self.movement_Array[fouthT].StageNo_in_Order.append(stage.stage3)
                self.movement_Array[fouthR].StageNo_in_Order.append(stage.stage3)
        else:
            self.movement_Array[firstL].StageNo_in_Order.append(stage.stage1)
            self.movement_Array[firstT].StageNo_in_Order.append(stage.stage1)
            self.movement_Array[firstR].StageNo_in_Order.append(stage.stage1)
            self.movement_Array[secondL].StageNo_in_Order.append(stage.stage1)
            self.movement_Array[secondT].StageNo_in_Order.append(stage.stage1)
            self.movement_Array[secondR].StageNo_in_Order.append(stage.stage1)
            if north_And_South_Flag:
                self.movement_Array[thridL].StageNo_in_Order.append(stage.stage2)
                self.movement_Array[thridT].StageNo_in_Order.append(stage.stage3)
                self.movement_Array[thridR].StageNo_in_Order.append(stage.stage3)
                self.movement_Array[fouthL].StageNo_in_Order.append(stage.stage2)
                self.movement_Array[fouthT].StageNo_in_Order.append(stage.stage3)
                self.movement_Array[fouthR].StageNo_in_Order.append(stage.stage3)
            else:
                self.movement_Array[thridL].StageNo_in_Order.append(stage.stage2)
                self.movement_Array[thridT].StageNo_in_Order.append(stage.stage2)
                self.movement_Array[thridR].StageNo_in_Order.append(stage.stage2)
                self.movement_Array[fouthL].StageNo_in_Order.append(stage.stage2)
                self.movement_Array[fouthT].StageNo_in_Order.append(stage.stage2)
                self.movement_Array[fouthR].StageNo_in_Order.append(stage.stage2)

        initialStage_Range = self.stage_Actual_Size
        criticalStage = -1

        for s in range(initialStage_Range,1,-1):
            checkNumber = 0
            if criticalStage != -1:
                for m in range(1,movementSize+1):
                    for so in range(len(self.movement_Array[m].StageNo_in_Order)):
                        if self.movement_Array[m].StageNo_in_Order[so].value > criticalStage and self.movement_Array[m].Enable ==True:
                            self.movement_Array[m].StageNo_in_Order[so] = stage(self.movement_Array[m].StageNo_in_Order[so].value - 1)
            for m in range(1, movementSize+1):
                for so in range(len(self.movement_Array[m].StageNo_in_Order)):
                    if self.movement_Array[m].Enable == True and  self.movement_Array[m].StageNo_in_Order[so].value ==s:
                        checkNumber += 1
            if checkNumber == 0:
                self.stage_Actual_Size -= 1
                criticalStage = s
            else:
                criticalStage = -1
        for m in range(1, movementSize+1):
            if (self.movement_Array[m].Enable == False):
                self.movement_Array[m].StageNo_in_Order[0] == stage(-1)
        for m in range(1, movementSize+1):
            if self.movement_Array[m].Enable == True and self.movement_Array[m].GroupNo.value == 1:
                if self.movement_Array[self.left_Movement_Counterpart_Right_Trun_Index_Map[movement_Index(m)].value].Enable == True:
                    self.movement_Array[self.left_Movement_Counterpart_Right_Trun_Index_Map[movement_Index(m)].value].StageNo_in_Order.insert(self.movement_Array[self.left_Movement_Counterpart_Right_Trun_Index_Map[movement_Index(m)].value].StageNo_in_Order[0].value-1,self.movement_Array[m].StageNo_in_Order[0])
    def Set_Saturation_Flow_Rate_Matrix(self):
        for m in range(1,movementSize+1):
            if self.movement_Array[m].Enable == False:
                continue
            for so in range(len(self.movement_Array[m].StageNo_in_Order)):
                if self.movement_Array[m].Left_Turn_Treatment.name == 'prot':
                    self.saturation_Flow_Rate_Matrix[self.movement_Array[m].StageNo_in_Order[so].value][m] = 1530 * self.movement_Array[m].Lanes * PHF
                elif self.movement_Array[m].Left_Turn_Treatment.name == 'perm':
                    op_Movement_Index = self.left_Movement_Opposing_Index_Map[movement_Index(m)]
                    op_volume = self.movement_Array[op_Movement_Index].Volume
                    self.saturation_Flow_Rate_Matrix[self.movement_Array[m].StageNo_in_Order[so].value][m] = f_1 * f_2 * op_volume * math.exp((-op_volume * 4.5 / 3600)) / (1 - math.exp(op_volume *2.5 / 3600))
                else:
                    self.saturation_Flow_Rate_Matrix[self.movement_Array[m].StageNo_in_Order[so].value][m] = 1530 * self.movement_Array[m].Lanes

    def Calculate_Flow_of_Ratio_Max(self):

        for s in range(1, self.stage_Actual_Size+1):
            self.y_Max_Stage_Array[s] = 0
            for m in range(1, movementSize+1):
                for so in range(len(self.movement_Array[m].StageNo_in_Order)):
                    if self.saturation_Flow_Rate_Matrix[s][m] != 0 and self.movement_Array[m].Enable and self.movement_Array[m].StageNo_in_Order[so].value == s:
                        self.y_Stage_Movement_Matrix[s][m] = self.movement_Array[m].Volume / self.saturation_Flow_Rate_Matrix[s][m]
                        self.stage_Direction_Candidates_Matrix[s][self.movement_Array[m].DirectionNo.value][self.movement_Array[m].GroupNo.value] += self.y_Stage_Movement_Matrix[s][m]
                        if self.stage_Direction_Candidates_Matrix[s][self.movement_Array[m].DirectionNo.value][self.movement_Array[m].GroupNo.value] >= self.y_Max_Stage_Array[s]:
                            self.y_Max_Stage_Array[s] = self.stage_Direction_Candidates_Matrix[s][self.movement_Array[m].DirectionNo.value][self.movement_Array[m].GroupNo.value]
        self.y_StageMax = 0
        for i in (1, self.stage_Actual_Size+1):
            self.y_StageMax += self.y_Max_Stage_Array[i]

    def Calculate_Total_Cycle_Lost_Time(self):
        l = t_L * self.stage_Actual_Size

    def Calculate_the_Minimum_And_Optimal_Cycle_Length(self):
        self.c_Min = max(60, (l - x_c_Input) / (x_c_Input - self.y_StageMax))
        self.c_Optimal = max(60, (1.5 * l + 5) / (1 - self.y_StageMax) if self.y_StageMax!=1 else (1.5 * l + 5))

    def Calculate_the_x_c_Output(self):
        self.x_c_output = (self.y_StageMax * self.c_Min) / (self.c_Min - l)

    def Calculate_Green_Time_for_Stages(self):
        for s in range(1, self.stage_Actual_Size+1):
            self.green_Time_Stage_Array[s] = max(minGreenTime, self.y_Max_Stage_Array[s] * self.c_Min / self.y_StageMax)
            self.effective_Green_Time_Stage_Array[s] = self.green_Time_Stage_Array[s] - t_L + t_Yellow + t_AR
            self.ratio_of_Effective_Green_Time_to_Cycle_Length_Array[s] = self.effective_Green_Time_Stage_Array[s] / self.c_Min

    def Printing_Green_Time_for_Stages(self):
        self.cumulative_Green_Start_Time_Stage_Array[1] = 0
        self.cumulative_Green_End_Time_Stage_Array[1] = self.green_Time_Stage_Array[1]
        for i in range(2,self.stage_Actual_Size+1):
            self.cumulative_Green_Start_Time_Stage_Array[i] = self.cumulative_Green_End_Time_Stage_Array[i - 1]
            self.cumulative_Green_End_Time_Stage_Array[i] = self.cumulative_Green_Start_Time_Stage_Array[i] + self.green_Time_Stage_Array[i]

        self.cumulative_Effective_Green_Start_Time_Stage_Array[1] = 0
        self.cumulative_Effective_Green_End_Time_Stage_Array[1] = self.effective_Green_Time_Stage_Array[1]
        for i in range(2,self.stage_Actual_Size+1):
            self.cumulative_Effective_Green_Start_Time_Stage_Array[i] = self.cumulative_Effective_Green_End_Time_Stage_Array[i - 1]
            self.cumulative_Effective_Green_End_Time_Stage_Array[i] = self.cumulative_Effective_Green_Start_Time_Stage_Array[i] + self.effective_Green_Time_Stage_Array[i]

    def Calculate_Capacity_And_Ratio_V_over_C(self):
        for s in range(1, self.stage_Actual_Size+1):
            for m in range(1, movementSize+1):
                for so in range(len(self.movement_Array[m].StageNo_in_Order)):
                    if self.saturation_Flow_Rate_Matrix[s][m] != 0 and self.movement_Array[m].Enable and self.movement_Array[m].StageNo_in_Order[so].value == s:
                        self.capacity_by_Stage_and_Movement_Matrix[s][m] = self.saturation_Flow_Rate_Matrix[s][m] * self.ratio_of_Effective_Green_Time_to_Cycle_Length_Array[s]
                        self.v_over_C_by_Stage_and_Movement_Matrix[s][m] = self.movement_Array[m].Volume / self.capacity_by_Stage_and_Movement_Matrix[s][m]

    def Calculate_Signal_Delay(self,nodeID):
        for s in range(1, self.stage_Actual_Size+1):
            for m in range(1, movementSize+1):
                for so in range(len(self.movement_Array[m].StageNo_in_Order)):
                    if self.saturation_Flow_Rate_Matrix[s][m] != 0 and self.movement_Array[m].Enable and self.movement_Array[m].StageNo_in_Order[so].value == s:
                        self.average_Uniform_Delay_Matrix[s][m] = (0.5 * self.capacity_by_Stage_and_Movement_Matrix[s][m] * pow((1 - self.ratio_of_Effective_Green_Time_to_Cycle_Length_Array[s]), 2)) / (1 - self.v_over_C_by_Stage_and_Movement_Matrix[s][m] *self.ratio_of_Effective_Green_Time_to_Cycle_Length_Array[s])
                        self.approach_Total_Delay_Array[self.movement_Array[m].DirectionNo.value] += self.movement_Array[m].Volume * self.average_Uniform_Delay_Matrix[s][m]
                        self.approach_Total_Volume_Array[self.movement_Array[m].DirectionNo.value] += self.movement_Array[m].Volume
        for d in range(1,directionSize+1):
            if self.approach_Total_Volume_Array[d] == 0:
                continue
            self.approach_Average_Delay_Array[d] = self.approach_Total_Delay_Array[d] / self.approach_Total_Volume_Array[d]
            self.intersection_Total_Delay += self.approach_Average_Delay_Array[d] * self.approach_Total_Volume_Array[d]
            self.intersection_Total_Volume += self.approach_Total_Volume_Array[d]
        self.intersection_Average_Delay = self.intersection_Total_Delay / self.intersection_Total_Volume


    def Judge_Signal_LOS(self,nodeID):
        if self.intersection_Total_Delay <= 10:
            self.LOS = 'A'
        elif self.intersection_Total_Delay <= 20:
            self.LOS = 'B'
        elif self.intersection_Total_Delay <= 35:
            self.LOS = 'C'
        elif self.intersection_Total_Delay <= 55:
            self.LOS = 'D'
        elif self.intersection_Total_Delay <= 80:
            self.LOS = 'E'
        else:
            self.LOS = 'F'

class CNode:
    node_seq_no = -1
    node_seq_no = 0
    node_id = 0
    x = 0.0001
    y = 0.0001
    m_outgoing_link_seq_no_vector = []
    m_incoming_link_seq_no_vector = []
    m_to_node_seq_no_vector = []
    m_to_node_2_link_seq_no_map = {}

class CLink:
    free_flow_travel_time_in_min = 1
    zone_seq_no_for_outgoing_connector = 0
    m_RandomSeed = 0
    link_seq_no = 0
    link_id = ''
    from_node_seq_no = 0
    to_node_seq_no = 0
    link_type = 0
    fftt = 0.001
    free_flow_travel_time_in_min = 0.001
    lane_capacity = 0.001
    number_of_lanes = 0
    type = 0
    length = 0.001


def g_ReadInputData(MainModual):
    MainModual.g_LoadingStartTimeInMin = 420
    MainModual.g_LoadingEndTimeInMin = 480
    # step 0:read demand period file
    print("Step 1: Reading file demand_period.csv...")
    #g_LogFile << "Step 7.1: Reading file input_agent_type.csv..." << g_GetUsedMemoryDataInMB() << endl
    parser_demand_period = pd.read_csv('demand_period.csv')
    time_period_List=list(parser_demand_period['time_period'])

    for time_period in time_period_List:
        timeList=str(time_period).split('_')
        time1 = timeList[0]
        time2 = timeList[1]
        MainModual.g_LoadingStartTimeInMin=int(time1[0])*60*10+int(time1[1])*60+int(time1[2])*10+int(time1[3])
        MainModual.g_LoadingEndTimeInMin=int(time2[0])*60*10+int(time2[1])*60+int(time2[2])*10+int(time2[3])


    MainModual.g_number_of_nodes = 0
    MainModual.g_number_of_links = 0
    internal_node_seq_no = 0
    #step 3: read node file
    parser = pd.read_csv('node.csv')
    for i in range(len(parser['node_id'])):
        node_id = parser['node_id'][i]
        MainModual.g_internal_node_to_seq_no_map[node_id] = internal_node_seq_no
        node = CNode()
        node.node_id = node_id
        node.node_seq_no = internal_node_seq_no
        internal_node_seq_no += 1
        g_node_vector.append(node)
        MainModual.g_number_of_nodes += 1


    g_info_String = "Number of Nodes = "
    g_info_String += str(MainModual.g_number_of_nodes)
    print(g_info_String)

    # step 4: read link file
    parser_link = pd.read_csv('road_link.csv')
    for i in range(len(parser_link['from_node_id'])):
        from_node_id = parser_link['from_node_id'][i]
        to_node_id = parser_link['to_node_id'][i]
        linkID = parser_link['road_link_id'][i]
        #add the to node id into the outbound (adjacent) node list
        internal_from_node_seq_no = MainModual.g_internal_node_to_seq_no_map[from_node_id]
        internal_to_node_seq_no = MainModual.g_internal_node_to_seq_no_map[to_node_id]
        link = CLink() #create a link object
        link.from_node_seq_no = internal_from_node_seq_no
        link.to_node_seq_no = internal_to_node_seq_no
        link.link_seq_no = MainModual.g_number_of_links
        link.to_node_seq_no = internal_to_node_seq_no
        link.link_id = linkID

        MainModual.g_road_link_id_map[link.link_id] = 1
        link.type = parser_link['facility_type'][i]
        link.link_type = parser_link['link_type'][i]
        length = 1.0
        free_speed = 1.0
        lane_capacity = 1800
        length = parser_link['length'][i]
        free_speed = parser_link['free_speed'][i]
        free_speed = max(0.1, free_speed)
        number_of_lanes = 1
        number_of_lanes = parser_link['lanes'][i]
        lane_capacity = parser_link['capacity'][i]
        default_cap = 1000
        default_BaseTT = 1
        link.number_of_lanes = number_of_lanes
        link.lane_capacity = lane_capacity
        link.length = length
        link.free_flow_travel_time_in_min = length / free_speed * 60
        g_node_vector[internal_from_node_seq_no].m_outgoing_link_seq_no_vector.append(link.link_seq_no)
        g_node_vector[internal_to_node_seq_no].m_incoming_link_seq_no_vector.append(link.link_seq_no)
        g_node_vector[internal_from_node_seq_no].m_to_node_seq_no_vector.append(link.to_node_seq_no)
        g_node_vector[internal_from_node_seq_no].m_to_node_2_link_seq_no_map[link.to_node_seq_no] = link.link_seq_no
        g_link_vector.append(link)
        MainModual.g_number_of_links += 1
        movement_str = parser_link['movement_str'][i]
        if len(str(movement_str))>0 and str(movement_str)!='nan':
            main_node_id = -1
            main_node_id = parser_link['main_node_id'][i]
            # NEMA_phase_number = parser_link['NEMA_phase_number'][i] #KeyError: 'NEMA_phase_number'
            initial_volume = parser_link['volume'][i]
            lanes = parser_link['lanes'][i]
            sharedLanes = parser_link['sharedLanes'][i]
            if main_node_id >= 1:
                if main_node_id not in g_signal_node_map.keys() :
                    g_signal_node_map[main_node_id] = CSignalNode()
                g_signal_node_map[main_node_id].AddMovementVolume(link.link_seq_no, movement_str, initial_volume, lanes, sharedLanes)
    g_info_String = "Number of Links = "
    g_info_String += str(MainModual.g_number_of_links)
    print(g_info_String)


MainModual = CMainModual()

def Vol2timing(iteration_number, MainModual_mode, column_updating_iterations):
    #step 1: read input data
    g_ReadInputData(MainModual)

    #step 2: PerformQEM
    g_pFileServiceArc_list = []
    for it in g_signal_node_map:
        g_signal_node_map[it].PerformQEM(it)

    # step 2: Output data
    for it in g_signal_node_map:
        sn = g_signal_node_map[it]
        cycle_time_in_sec = max(10, sn.c_Min)
        number_of_cycles = (MainModual.g_LoadingEndTimeInMin - MainModual.g_LoadingStartTimeInMin) * 60 / cycle_time_in_sec
        offset_in_sec = 0
        g_loading_start_time_in_sec = int(MainModual.g_LoadingStartTimeInMin * 60 + offset_in_sec)
        ci = 0

        for m in range(1, movementSize+1):
            if sn.movement_Array[m].Enable:
                for so in range(len(sn.movement_Array[m].StageNo_in_Order)):
                    StageNo = sn.movement_Array[m].StageNo_in_Order[so]
                    global_start_time_in_sec = sn.cumulative_Green_Start_Time_Stage_Array[
                                                   StageNo.value] + cycle_time_in_sec * ci + g_loading_start_time_in_sec
                    global_end_time_in_sec = sn.cumulative_Green_End_Time_Stage_Array[
                                                 StageNo.value] + cycle_time_in_sec * ci + g_loading_start_time_in_sec
                    start_hour = int(global_start_time_in_sec / 3600)
                    start_min = int(global_start_time_in_sec / 60 - start_hour * 60)
                    start_sec = int(global_start_time_in_sec % 60)
                    end_hour = int(global_end_time_in_sec / 3600)
                    end_min = int(global_end_time_in_sec / 60 - end_hour * 60)
                    end_sec = int(global_end_time_in_sec % 60)

                    from_node_id = g_node_vector[g_link_vector[sn.movement_Array[m].LinkSeqNo].from_node_seq_no].node_id
                    to_node_id = g_node_vector[g_link_vector[sn.movement_Array[m].LinkSeqNo].to_node_seq_no].node_id
                    capacity = int(sn.green_Time_Stage_Array[StageNo.value] * 1800.0 / 3600.0)
                    greenTime = int(sn.green_Time_Stage_Array[StageNo.value])
                    redTime = int(cycle_time_in_sec - sn.green_Time_Stage_Array[StageNo.value])

                g_pFileServiceArc_list.append([
                g_link_vector[sn.movement_Array[m].LinkSeqNo].link_id,#1 road_link_id
                from_node_id,#2 from_node_id
                to_node_id,#3 to_node_id
                str(start_hour)+':'+str(start_min)+':'+str(start_sec)+'_'+str(end_hour)+':'+str(end_min)+':'+str(end_sec),#4 time_window
                -1, #5 time_interval
                -1, #6 travel_time_delta
                capacity, #7 capacity
                ci, #8 cycle_no
                cycle_time_in_sec, #9 cycle_length
                greenTime, #10 green_time
                redTime, #11 red_time
                int(it), #12 main_node_id
                StageNo.value, # 14 stage
                movement_Index(m).name  # 15 movement_str
                ])

    g_pFileServiceArc_list_df=pd.DataFrame(g_pFileServiceArc_list,columns=['road_link_id','from_node_id','to_node_id','time_window',
                                                                           'time_interval','travel_time_delta','capacity','cycle_no',
                                                                           'cycle_length','green_time',
                                                                           'red_time','main_node_id','stage','movement_str'])
    g_pFileServiceArc_list_df.to_csv('service_arc.csv', index=False)