from .signal4gmns import CSignalNode
from .Enums import *


class NEMA_Frame:
    def __init__(self, signalNode: CSignalNode):
        self.Ring_Dict = {
            E_NEMA_Ring.Ring_1: [E_NEMA_Phase.Ma_SLA, E_NEMA_Phase.Ma_STRA, E_NEMA_Phase.Mi_SLA, E_NEMA_Phase.Mi_STRA],
            E_NEMA_Ring.Ring_2: [E_NEMA_Phase.Ma_SLB, E_NEMA_Phase.Ma_STRB, E_NEMA_Phase.Mi_SLB, E_NEMA_Phase.Mi_STRB]}
        self.Barrier_Dict = {E_NEMA_Barrier.Barrier_1: [E_NEMA_Phase.Ma_SLA, E_NEMA_Phase.Ma_STRA, E_NEMA_Phase.Ma_SLB,
                                                        E_NEMA_Phase.Ma_STRB],
                             E_NEMA_Barrier.Barrier_2: [E_NEMA_Phase.Mi_SLA, E_NEMA_Phase.Mi_STRA, E_NEMA_Phase.Mi_SLB,
                                                        E_NEMA_Phase.Mi_STRB]}

        self.Stage_NEMA_Dict = {
            EStage.stage1: [E_NEMA_Phase.Ma_SLA, E_NEMA_Phase.Ma_SLB],
            EStage.stage2: [E_NEMA_Phase.Ma_STRA, E_NEMA_Phase.Ma_STRB],
            EStage.stage3: [E_NEMA_Phase.Mi_SLA, E_NEMA_Phase.Mi_SLB],
            EStage.stage4: [E_NEMA_Phase.Mi_STRA, E_NEMA_Phase.Mi_STRB]
        }
        self.Stage_Movement_Dict = {}
        self.Movement_Stage_Dict = {}
        self.NEMA_MovementList_Table = {}
        self.Movement_NEMA_Table = {}
        self.signalNode = signalNode

    def __str__(self):
        return self.Movement_NEMA_Table

    def Assign_NEMA_Phase(self, EW_OR_NS):
        if EW_OR_NS:  # true for EW
            self.Movement_NEMA_Table[EMovement_Index.EBL] = E_NEMA_Phase.Ma_SLA
            self.Movement_NEMA_Table[EMovement_Index.WBL] = E_NEMA_Phase.Ma_SLB
            self.Movement_NEMA_Table[EMovement_Index.EBT] = E_NEMA_Phase.Ma_STRA
            self.Movement_NEMA_Table[EMovement_Index.WBT] = E_NEMA_Phase.Ma_STRB
            self.Movement_NEMA_Table[EMovement_Index.EBR] = E_NEMA_Phase.Ma_STRA
            self.Movement_NEMA_Table[EMovement_Index.WBR] = E_NEMA_Phase.Ma_STRB

            self.Movement_NEMA_Table[EMovement_Index.NBL] = E_NEMA_Phase.Mi_SLA
            self.Movement_NEMA_Table[EMovement_Index.SBL] = E_NEMA_Phase.Mi_SLB
            self.Movement_NEMA_Table[EMovement_Index.NBT] = E_NEMA_Phase.Mi_STRA
            self.Movement_NEMA_Table[EMovement_Index.SBT] = E_NEMA_Phase.Mi_STRB
            self.Movement_NEMA_Table[EMovement_Index.NBR] = E_NEMA_Phase.Mi_STRA
            self.Movement_NEMA_Table[EMovement_Index.SBR] = E_NEMA_Phase.Mi_STRB
        else:
            self.Movement_NEMA_Table[EMovement_Index.EBL] = E_NEMA_Phase.Mi_SLA
            self.Movement_NEMA_Table[EMovement_Index.WBL] = E_NEMA_Phase.Mi_SLB
            self.Movement_NEMA_Table[EMovement_Index.EBT] = E_NEMA_Phase.Mi_STRA
            self.Movement_NEMA_Table[EMovement_Index.WBT] = E_NEMA_Phase.Mi_STRB
            self.Movement_NEMA_Table[EMovement_Index.EBR] = E_NEMA_Phase.Mi_STRA
            self.Movement_NEMA_Table[EMovement_Index.WBR] = E_NEMA_Phase.Mi_STRB

            self.Movement_NEMA_Table[EMovement_Index.NBL] = E_NEMA_Phase.Ma_SLA
            self.Movement_NEMA_Table[EMovement_Index.SBL] = E_NEMA_Phase.Ma_SLB
            self.Movement_NEMA_Table[EMovement_Index.NBT] = E_NEMA_Phase.Ma_STRA
            self.Movement_NEMA_Table[EMovement_Index.SBT] = E_NEMA_Phase.Ma_STRB
            self.Movement_NEMA_Table[EMovement_Index.NBR] = E_NEMA_Phase.Ma_STRA
            self.Movement_NEMA_Table[EMovement_Index.SBR] = E_NEMA_Phase.Ma_STRB

        for movement, NEMA_Phase in self.Movement_NEMA_Table.items():
            if self.signalNode.movement_Array[movement.value].Enable == True:
                self.signalNode.movement_Array[movement.value].NEMA_Phase = NEMA_Phase.value
            else:
                self.Movement_NEMA_Table[movement] = None

        for Movement, NEMA_Phase in self.Movement_NEMA_Table.items():
            if NEMA_Phase==None:
                continue
            if NEMA_Phase not in self.NEMA_MovementList_Table.keys():
                self.NEMA_MovementList_Table[NEMA_Phase]=[]
            self.NEMA_MovementList_Table[NEMA_Phase].append(Movement)

        for stage, NEMA_Phase_List in self.Stage_NEMA_Dict.items():
            flatten = lambda x: [y for l in x for y in flatten(l)] if type(x) is list else [x]
            self.Stage_Movement_Dict[stage]=flatten([movement for movement in (self.NEMA_MovementList_Table[NEMA_Phase] for NEMA_Phase in NEMA_Phase_List if NEMA_Phase in self.NEMA_MovementList_Table.keys())])

        for stage, movementList in self.Stage_Movement_Dict.items():
            for movement in movementList:
                if movement not in self.Movement_Stage_Dict.keys():
                    self.Movement_Stage_Dict[movement]=None
                self.Movement_Stage_Dict[movement]=stage

    def Get_Phases_of_Rings(self):
        ring_Phase_Dict = {}
        for ring, phase_List in self.Ring_Dict.items():
            ring_Phase_Dict[ring] = [x for x in phase_List if x != None]
        return ring_Phase_Dict

    def Get_Phases_of_Barriers(self):
        ring_Barrier_Dict = {}
        for barrier, phase_List in self.Barrier_Dict.items():
            ring_Barrier_Dict[barrier] = [x for x in phase_List if x != None]
        return ring_Barrier_Dict

    def Get_Movements_of_Stages(self):
        return self.Stage_Movement_Dict
    def Get_Stage_of_Movement(self):
        return self.Movement_Stage_Dict
    def Get_Movement_NEMA_Table(self):
        return self. Movement_NEMA_Table
# stage is constrainted by barriers
