from .Enums import *
class CSignal_Link_Inter():
    def __init__(self):
        pass

class CSignal_Node_Inter():
    def __init__(self, signalCode:str,osmID, x_coord, y_coord):
        self.signalCode=signalCode
        self.osm_Node_ID=osmID
        self.x_coord=x_coord
        self.y_coord=y_coord

class CSignal_Movement_Inter():
    def __init__(self, movementCode:str, signal_Node:CSignal_Node_Inter, stageNo_in_Order:list, groupNo:EGroup, directionNo:EDirection, ib_Link_id, ob_Link_id, ib_osm_node_id, ob_osm_node_id, lanes:int, movement_str:str, osm_node_id, node_id, volume, geometry):
        self.movementCode= movementCode
        self.osm_node_id=osm_node_id
        self.node_id=node_id
        self.signal_Node=signal_Node
        self.signal_link=None
        stageNo_in_Order_value_str=[str(x.value) for x in stageNo_in_Order]
        self.stageNo_in_Order=",".join(stageNo_in_Order_value_str)
        self.groupNo=groupNo.value
        self.directionNo=directionNo.value
        self.ib_Link_id=ib_Link_id
        self.ob_Link_id=ob_Link_id
        self.ib_osm_node_id=ib_osm_node_id
        self.ob_osm_node_id=ob_osm_node_id
        self.lanes=lanes
        self.movement_str=movement_str
        self.volume=volume
        self.geometry=geometry

class CSignal_Node_Interm_List():
    def __init__(self):
        self.signal_Node_List = []

    def Add_Signal_Node(self,node):
        self.signal_Node_List.append(node)

    def Output_Signal_Node_Info(self):
        sequence=[]
        for node in self.signal_Node_List:
            sequence.append([
                node.signalCode,
                node.osm_Node_ID,
                node.x_coord,
                node.y_coord
            ])
        return sequence

class CSignal_Movement_Interm_List():
    def __init__(self):
        self.signal_Movement_List=[]

    def Add_Signal_Movement(self,movement):
        self.signal_Movement_List.append(movement)

    def Output_Signal_Movement_Info(self):
        sequence=[]
        for movement in self.signal_Movement_List:
            sequence.append([
                movement.movementCode,
                movement.signal_Node.signalCode,
                movement.signal_link,
                movement.stageNo_in_Order,
                movement.osm_node_id,
                movement.node_id,
                movement.groupNo,
                movement.directionNo,
                movement.ib_Link_id,
                movement.ob_Link_id,
                movement.ib_osm_node_id,
                movement.ob_osm_node_id,
                movement.lanes,
                movement.movement_str,
                movement.volume,
                movement.geometry,
            ])
        return sequence
