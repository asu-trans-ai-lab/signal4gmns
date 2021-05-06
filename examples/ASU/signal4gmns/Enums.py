from enum import Enum

# enum
class EMovement_Index(Enum):
    EBL = 1
    EBT = 2
    EBR = 3
    WBL = 4
    WBT = 5
    WBR = 6
    NBL = 7
    NBT = 8
    NBR = 9
    SBL = 10
    SBT = 11
    SBR = 12
class EStage(Enum):
    no_stage = -1
    stage1 = 1
    stage2 = 2
    stage3 = 3
    stage4 = 4
class EDirection(Enum):
    E = 1
    W = 2
    N = 3
    S = 4
class EGroup(Enum):
    L = 1
    T_AND_R = 2
class ELeft_Turn_Treatment(Enum):
    perm = 0
    prot = 1
    no_Treatment = -1

class E_NEMA_Phase(Enum):
    Ma_SLA = 1
    Ma_SLB = 5
    Ma_STRA = 2
    Ma_STRB = 6
    Mi_SLA = 3
    Mi_SLB = 7
    Mi_STRA = 4
    Mi_STRB = 8
    nu=-1

class E_NEMA_Ring(Enum):
    Ring_1 = 1
    Ring_2 = 2
    nu=-1

class E_NEMA_Barrier(Enum):
    Barrier_1 = 1
    Barrier_2 = 2
    nu=-1

class E_Signal_Type(Enum):
    T_junction = 1
    Crossroads = 2

class E_Major_Approach(Enum):
    EW = 1
    NS = 2
    nu=-1