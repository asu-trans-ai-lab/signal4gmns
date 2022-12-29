from EnumClass import NodeEnum as noe
from EnumClass import LinkEnum as lie
from EnumClass import LinkSecondEnum as lise
from EnumClass import LaneEnum as lae
from EnumClass import LaneSecondEnum as lase
from EnumClass import TimeplanEnum as tpe
from EnumClass import TimeplanSecondEnum as tpse
from EnumClass import PhaseEnum as pe
from EnumClass import PhaseSecondEnum as pse
from backup.Functions import *
import pickle

import pandas as pd

# importPath= r"data/Combined_File.csv"
importPath= r"UTDF.csv"
settingPath=r"setting.csv"

exportPath= r"export"
dataList=[]
sectionNameList=[]
presetSectionNameList=['[Network]', '[Nodes]', '[Links]', '[Lanes]', '[Timeplans]', '[Phases]']
presetSectionShortNameList=["net","nod","lin","lan","tim","pha"]
presetSectionNameShortDic=dict(zip(presetSectionShortNameList,presetSectionNameList))
presetElementIndexofSection="INTID"
presetParameterIndexofSection="RECORDNAME"
positionElementIndexofSectionDic={}
positionParameterIndexofSectionDic={}
sectionLocationDic={}
subSectionDic={}
sectionElementIndexDic={}
rowIndex=0
currentSectionNameStr=""
globalHashDic = {}  # table key, element key, perameter(second) key, direction(first) key



presetExportFileNameList=["LAYOUT","LANES","TIMING","PHASING"]
presetExportFileShortNameList=["lay","lan","tim","pha"]
presetExportFileShortDic=dict(zip(presetExportFileShortNameList,presetExportFileNameList))
exportKeywordDic=dict(zip(presetExportFileShortNameList, ["Layout Data","Lane Group Data","Timing Plans","Phasing Data"]))
exportColumnList= [["INTID","INTNAME","TYPE","X","Y","Z","NID","SID","EID","WID","NEID","NWID","SEID","SWID","NNAME","SNAME","ENAME","WNAME","NENAME","NWNAME","SENAME","SWNAME","Inside Radius","Outside Radius","Roundabout Lanes","Circle Speed"],
                                                          ["RECORDNAME","INTID","NBL","NBT","NBR","SBL","SBT","SBR","EBL","EBT","EBR","WBL","WBT","WBR","NEL","NET","NER","NWL","NWT","NWR","SEL","SET","SER","SWL","SWT","SWR","PED","HOLD"],
                                                          ["PLANID","INTID","S1","S2","S3","S4","S5","S6","S7","S8","CL","OFF","LD","REF","CLR"],
                                                          ["RECORDNAME","INTID","D1","D2","D3","D4","D5","D6","D7","D8"]]
exportColumnDic=dict(zip(presetExportFileShortNameList,exportColumnList))
exportColumnFlattenList=[x for x in flatten(exportColumnList)]
#output variable,table name,
# two steps, find first, and obtain variables second. thus, we have a target element and a target key(parameter) with some selections(directions)
exportVariableFromVariableDic={"INTID":"INTID",
                               "INTNAME":""}

exportColumnForIntersection=["full_name", "city_name", "synchro_INTID", "file_name","intersection_id"]

#exportKeywordDic=dict(zip(presetExportFileShortNameList, [['[Nodes]', '[Links]'],['[Lanes]'],['[Timeplans]'],['[Phases]']]))
# 1. each export file has a section dimension determined by a variable of import file
# 2. build a mapping between the first dimension variable and variable in import file

def exractElementData(sectionName:str, subSectionList:list):
    flagRecroding=False
    elementDataDic={}
    positionOfDirectionKeyDic={}
    for line in subSectionList:
        if line=="":
            continue
        if presetElementIndexofSection in line:
            positionElementIndexofSectionDic[sectionName]=line.split(",").index(presetElementIndexofSection)
            if sectionName != '[Nodes]':
                positionParameterIndexofSectionDic[sectionName]=line.split(",").index(presetParameterIndexofSection)

            if sectionName=='[Nodes]':
                en=noe
            elif sectionName=='[Links]':
                en=lie
                esn=lise
            elif sectionName=='[Lanes]':
                en=lae
                esn=lase
            elif sectionName == '[Timeplans]':
                en=tpe
                esn=tpse
            else:
                en=pe
                esn=pse
            for i in en:
                nam=i.name
                if "_" in nam:
                    nam=str.replace(nam,"_"," ")
                lineArray=line.split(",")
                if nam in lineArray:
                    positionOfDirectionKeyDic[nam]=line.split(",").index(nam)
            flagRecroding=True
            continue
        if flagRecroding:
            lineList=line.split(",")
            elementName= lineList[positionElementIndexofSectionDic[sectionName]]
            if elementName not in sectionElementIndexDic[sectionName]:
                sectionElementIndexDic[sectionName].append(elementName)

            if elementName not in elementDataDic.keys():
                elementDataDic[elementName]={}
            parameterList=[]
            if sectionName!='[Nodes]':
                for i in esn:
                    nam = i.name
                    if "_" in nam:
                        nam = str.replace(nam, "_", " ")
                    parameterList.append(nam)
                    if nam not in elementDataDic[elementName].keys():
                        elementDataDic[elementName][nam] = {}
            else:
                if "null" not in elementDataDic[elementName].keys():
                    elementDataDic[elementName]["null"]={}
                    parameterList.append("null")

            for i in positionOfDirectionKeyDic.keys():
                for j in parameterList:
                    if sectionName=='[Nodes]' or j==lineList[positionParameterIndexofSectionDic[sectionName]]:
                        elementDataDic[elementName][j][i] = lineList[positionOfDirectionKeyDic[i]]
    return elementDataDic

def QueryValueFromTheGlobalHashTable(tableNameStr:str, elementNameStr:str, parameterName, directionNameEnum):

    if isinstance(parameterName,str):
        parameterName = parameterName
    else:
        parameterName=parameterName.name
    if "_" in parameterName:
        parameterName=str.replace(parameterName,"_"," ")

    directionName = directionNameEnum.name
    if "_" in directionName:
        directionName=str.replace(directionName, "_", " ")

    return globalHashDic[tableNameStr][elementNameStr][parameterName][directionName]

if __name__ == '__main__':
    with open(importPath, "r", encoding="utf-8") as fileHandler:
        while True:
            line=fileHandler.readline()
            if not line:
                break
            line=line.strip()
            if "[" in line:
                sectionNameList.append(line)
                currentSectionNameStr=line
                sectionLocationDic[line]=rowIndex
                subSectionDic[line]=[]
                sectionElementIndexDic[line]=[]
            subSectionDic[currentSectionNameStr].append(line)

            rowIndex+=1
    print(rowIndex)

    for tableKey in presetSectionNameList:
        if tableKey not in globalHashDic.keys():
            globalHashDic[tableKey]={}

        if tableKey=='[Network]':
            globalHashDic[tableKey]={"null":{}}
            flagRecroding = False
            for lineN in subSectionDic[tableKey]:
                if lineN=="":
                    continue
                if "RECORDNAME" in lineN:
                    flagRecroding = True
                    continue
                if flagRecroding:
                    lineArray=lineN.split(",")
                    globalHashDic[tableKey]["null"][lineArray[0]]={"DATA",lineArray[1]}
        else:
            globalHashDic[tableKey]=exractElementData(tableKey, subSectionDic[tableKey])

    df_setting=pd.read_csv(settingPath)
    city_name=df_setting["city_name"].values[0]
    print("import finished")

    # export intersection_from_synchro.csv

    tableName=presetSectionNameShortDic["lin"]
    df = pd.DataFrame()

    asequenced_intersection_id=0
    for elementID in sectionElementIndexDic[tableName]:
        flagIntersection=False
        directionList=globalHashDic[tableName][elementID][lise.Name.name]
        directionNameList=[]
        for directionID in range(3,11):
            directionName=directionList[lie(directionID).name]
            if directionName not in directionNameList and directionName!='':
                directionNameList.append(directionName)
        if len(directionNameList) >1:
            flagIntersection=True
        #     this is an intersection
        intersectionName=""
        if flagIntersection:
            intersectionName=' & '.join(directionNameList)
            intersectionID=directionList[lie.INTID.name]
            df=df.append({exportColumnForIntersection[0]: intersectionName,exportColumnForIntersection[1]:city_name,exportColumnForIntersection[2]: intersectionID,exportColumnForIntersection[3]:"",exportColumnForIntersection[4]:asequenced_intersection_id}, ignore_index=True)
            asequenced_intersection_id+=1
    df.to_csv("intersection_from_synchro.csv",index=False)

    file= open("globalHashDic.pkl","wb")
    pickle.dump(globalHashDic,file)
    file.close()
    print("export finished")








    # first, we should obtain the index of row from the globalHashDic
    # In the case of LAYOUT.csv, the index is INTID
    # tableName=presetSectionNameShortDic["nod"]
    # parameterName="null"
    # for elementNode in sectionElementIndexDic[tableName]:
    #     INTNAME
    #     TYPE =
    #     X
    #     Y
    #     Z
    #     NID
    #     SID
    #     EID
    #     WID
    #     NEID
    #     NWID
    #     SEID
    #     SWID
    #     NNAME
    #     SNAME
    #     ENAME
    #     WNAME
    #     NENAME
    #     NWNAME
    #     SENAME
    #     SWNAME
    #     InsideRadius
    #     OutsideRadius
    #     RoundaboutLanes
    #     CircleSpeed
    #
    #     row = [elementNode, ]  # we build the row driectly.
    #
    #
    #
    # for elementIndex in sectionElementIndexDic[tableName]:
    #     for directionIndex in noe:
    #         QueryValueFromTheGlobalHashTable(tableName,elementIndex,parameterName,directionIndex)


# the exprot should use pandas
