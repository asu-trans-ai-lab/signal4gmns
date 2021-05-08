from .Enums import *

def GetSignalCode(majorApproach:E_Major_Approach, approach_Existed_Movement_Matrix:{}, OSM_ID:str):
    # approach_Vacant_Movement_Matrix:
    # EWNS
    # 0100 L
    # 0010 T
    # 0100 R
    type=E_Signal_Type.Crossroads
    existed_Code=""
    column_No=[0,0,0,0]
    for approach, LTR_List in approach_Existed_Movement_Matrix.items():
        approach_existed=""
        for column_Index in range(len(LTR_List)):
            if LTR_List[column_Index]==1: # it means that this approach (e.g., E is existed)
                approach_existed+=EDirection(column_Index+1).name
                column_No[column_Index]+=1
        if approach_existed=="EWNS":
            approach_existed="A"
        if approach_existed=="":
            approach_existed="Nu"
        if 0 in column_No:
            type=E_Signal_Type.T_junction
        else:
            pass
        existed_Code+=f"{approach}_{approach_existed}|"
    signal_Code=f"{'T' if type==E_Signal_Type.T_junction else '#'}|Ma_{'EW' if majorApproach==E_Major_Approach.EW else 'NS'}|" \
                  f"{existed_Code}"#OSMID_{OSM_ID}
    return signal_Code

def GetMovementCode(movement_Index:EMovement_Index,left_Turn_Treatment:ELeft_Turn_Treatment,NEMA_Phase:E_NEMA_Phase,ring:E_NEMA_Ring,barrier:E_NEMA_Barrier):
    movement_Code=f"{movement_Index.name}|{left_Turn_Treatment.name}|NEMA_Phase_{NEMA_Phase.value}|Ring_{ring.value}|Barrier_{barrier.value}"
    return movement_Code


if __name__=="__main__":
    matrix={"L":[1,0,1,0],"R":[1,0,1,0],"T":[1,1,1,1]}
    print(GetSignalCode(E_Major_Approach.EW,matrix,"123123"))