//  Portions Copyright 2019
// Xuesong (Simon) Zhou
//   If you help write or modify the code, please also list your names here.
//   The reason of having Copyright info here is to ensure all the modified version, as a whole, under the GPL 
//   and further prevent a violation of the GPL.

// More about "How to use GNU licenses for your own software"
// http://www.gnu.org/licenses/gpl-howto.html

#pragma warning( disable : 4305 4267 4018) 
#include <iostream>
#include <fstream>
#include <list> 
#include <omp.h>
#include <algorithm>
#include <time.h>
#include <functional>
#include <stdio.h>   
#include <math.h>


#include <stack>
#include <string>
#include <vector>
#include <map>
#include <sstream>
#include <iostream>
#include <iomanip>
using namespace std;
using std::string;
using std::ifstream;
using std::vector;
using std::map;
using std::istringstream;
using std::max;
template <typename T>


// some basic parameters setting


#define sprintf_s sprintf

FILE* g_pFileOutputLog = NULL;
int g_debugging_flag = 2;


void fopen_ss(FILE **file, const char *fileName, const char *mode)
{
	*file = fopen(fileName, mode);
}


void g_ProgramStop();


//below shows where the functions used in Agentlite.cpp come from!
//Utility.cpp

#pragma warning(disable: 4244)  // stop warning: "conversion from 'int' to 'float', possible loss of data"


class CCSVParser
{
public:
	char Delimiter;
	bool IsFirstLineHeader;
	ifstream inFile;
	string mFileName;
	vector<string> LineFieldsValue;
	vector<string> Headers;
	map<string, int> FieldsIndices;

	vector<int> LineIntegerVector;

public:
	void  ConvertLineStringValueToIntegers()
	{
		LineIntegerVector.clear();
		for (unsigned i = 0; i < LineFieldsValue.size(); i++)
		{
			std::string si = LineFieldsValue[i];
			int value = atoi(si.c_str());

			if (value >= 1)
				LineIntegerVector.push_back(value);

		}
	}
	vector<string> GetHeaderVector()
	{
		return Headers;
	}

	bool m_bDataHubSingleCSVFile;
	string m_DataHubSectionName;
	bool m_bLastSectionRead;

	bool m_bSkipFirstLine;  // for DataHub CSV files

	CCSVParser(void)
	{
		Delimiter = ',';
		IsFirstLineHeader = true;
		m_bSkipFirstLine = false;
		m_bDataHubSingleCSVFile = false;
		m_bLastSectionRead = false;
	}

	~CCSVParser(void)
	{
		if (inFile.is_open()) inFile.close();
	}


	bool OpenCSVFile(string fileName, bool b_required)
	{
		mFileName = fileName;
		inFile.open(fileName.c_str());

		if (inFile.is_open())
		{
			if (IsFirstLineHeader)
			{
				string s;
				std::getline(inFile, s);
				vector<string> FieldNames = ParseLine(s);

				for (size_t i = 0;i < FieldNames.size();i++)
				{
					string tmp_str = FieldNames.at(i);
					size_t start = tmp_str.find_first_not_of(" ");

					string name;
					if (start == string::npos)
					{
						name = "";
					}
					else
					{
						name = tmp_str.substr(start);
						//			TRACE("%s,", name.c_str());
					}


					FieldsIndices[name] = (int)i;
				}
			}

			return true;
		}
		else
		{
			if (b_required)
			{

				cout << "File " << fileName << " does not exist. Please check." << endl;
				//g_ProgramStop();
			}
			return false;
		}
	}


	void CloseCSVFile(void)
	{
		inFile.close();
	}



	bool ReadRecord()
	{
		LineFieldsValue.clear();

		if (inFile.is_open())
		{
			string s;
			std::getline(inFile, s);
			if (s.length() > 0)
			{

				LineFieldsValue = ParseLine(s);

				return true;
			}
			else
			{

				return false;
			}
		}
		else
		{
			return false;
		}
	}

	vector<string> ParseLine(string line)
	{
		vector<string> SeperatedStrings;
		string subStr;

		if (line.length() == 0)
			return SeperatedStrings;

		istringstream ss(line);


		if (line.find_first_of('"') == string::npos)
		{

			while (std::getline(ss, subStr, Delimiter))
			{
				SeperatedStrings.push_back(subStr);
			}

			if (line.at(line.length() - 1) == ',')
			{
				SeperatedStrings.push_back("");
			}
		}
		else
		{
			while (line.length() > 0)
			{
				size_t n1 = line.find_first_of(',');
				size_t n2 = line.find_first_of('"');

				if (n1 == string::npos && n2 == string::npos) //last field without double quotes
				{
					subStr = line;
					SeperatedStrings.push_back(subStr);
					break;
				}

				if (n1 == string::npos && n2 != string::npos) //last field with double quotes
				{
					size_t n3 = line.find_first_of('"', n2 + 1); // second double quote

					//extract content from double quotes
					subStr = line.substr(n2 + 1, n3 - n2 - 1);
					SeperatedStrings.push_back(subStr);

					break;
				}

				if (n1 != string::npos && (n1 < n2 || n2 == string::npos))
				{
					subStr = line.substr(0, n1);
					SeperatedStrings.push_back(subStr);
					if (n1 < line.length() - 1)
					{
						line = line.substr(n1 + 1);
					}
					else // comma is the last char in the line string, push an empty string to the back of vector
					{
						SeperatedStrings.push_back("");
						break;
					}
				}

				if (n1 != string::npos && n2 != string::npos && n2 < n1)
				{
					size_t n3 = line.find_first_of('"', n2 + 1); // second double quote
					subStr = line.substr(n2 + 1, n3 - n2 - 1);
					SeperatedStrings.push_back(subStr);
					size_t idx = line.find_first_of(',', n3 + 1);

					if (idx != string::npos)
					{
						line = line.substr(idx + 1);
					}
					else
					{
						break;
					}
				}
			}

		}

		return SeperatedStrings;
	}

	template <class T> bool GetValueByFieldName(string field_name, T& value, bool NonnegativeFlag = true, bool required_field = true)
	{

		if (FieldsIndices.find(field_name) == FieldsIndices.end())
		{
			if (required_field)
			{
				cout << "Field " << field_name << " in file " << mFileName << " does not exist. Please check the file." << endl;

				g_ProgramStop();
			}
			return false;
		}
		else
		{
			if (LineFieldsValue.size() == 0)
			{
				return false;
			}

			int size = (int)(LineFieldsValue.size());
			if (FieldsIndices[field_name] >= size)
			{
				return false;
			}

			string str_value = LineFieldsValue[FieldsIndices[field_name]];

			if (str_value.length() <= 0)
			{
				return false;
			}

			istringstream ss(str_value);

			T converted_value;
			ss >> converted_value;

			if (/*!ss.eof() || */ ss.fail())
			{
				return false;
			}

			if (NonnegativeFlag && converted_value < 0)
				converted_value = 0;

			value = converted_value;
			return true;
		}
	}


	bool GetValueByFieldName(string field_name, string& value)
	{
		if (FieldsIndices.find(field_name) == FieldsIndices.end())
		{
			return false;
		}
		else
		{
			if (LineFieldsValue.size() == 0)
			{
				return false;
			}

			unsigned int index = FieldsIndices[field_name];
			if (index >= LineFieldsValue.size())
			{
				return false;
			}
			string str_value = LineFieldsValue[index];

			if (str_value.length() <= 0)
			{
				return false;
			}

			value = str_value;
			return true;
		}
	}

};


class CMainModual {
public:
	CMainModual()
	{

		g_number_of_links = 0;
		g_number_of_service_arcs = 0;
		g_number_of_nodes = 0;

		b_debug_detail_flag = 1;

		g_pFileDebugLog = NULL;
	}

	int b_debug_detail_flag;
	std::map<int, int> g_internal_node_to_seq_no_map;  // hash table, map external node number to internal node sequence no. 


	std::map<string, int> g_road_link_id_map;


	int g_number_of_links;
	int g_number_of_service_arcs;
	int g_number_of_nodes;
	int g_number_of_zones;

	int g_LoadingStartTimeInMin;
	int g_LoadingEndTimeInMin;

	FILE* g_pFileDebugLog = NULL;


};

CMainModual MainModual;


class CLink
{
public:
	CLink()  // construction 
	{

		free_flow_travel_time_in_min = 1;
	}

	~CLink()
	{
		//if (flow_volume_for_each_o != NULL)
		//	delete flow_volume_for_each_o;
	}


	// 1. based on BPR. 

	int zone_seq_no_for_outgoing_connector ;

	int m_RandomSeed;
	int link_seq_no;
	string link_id;
	int from_node_seq_no;
	int to_node_seq_no;
	int link_type;



	float fftt;
	float free_flow_travel_time_in_min;
	float lane_capacity;
	int number_of_lanes;
	int type;
	float length;

};

class CServiceArc
{
public:
	CServiceArc()  // construction 
	{
	}

	int link_seq_no;
	int starting_time_no;
	int ending_time_no;
	int time_interval_no;
	float capacity;
	int travel_time_delta;

};


class CNode
{
public:
	CNode()
	{
		node_seq_no = -1;
		//accessible_node_count = 0;
	}

	//int accessible_node_count;

	int node_seq_no;  // sequence number 
	int node_id;      //external node number 

	double x;
	double y;

	std::vector<int> m_outgoing_link_seq_no_vector;
	std::vector<int> m_incoming_link_seq_no_vector;

	std::vector<int> m_to_node_seq_no_vector;
	std::map<int, int> m_to_node_2_link_seq_no_map;

};


struct SMovementData
{
	//SMovementData()
	//{

	//}
	bool Enable = false;//no value->false
	int LinkSeqNo;
	int PhaseNo;
	enum stage StageNo;
	int Volume;
	int Lanes;
	enum group GroupNo;//L->1;T/R->2
	enum direction DirectionNo;
};


#pragma endregion

#pragma region Method_Declarations

//SMovementData getMovementData_from_PhaseID_and_RingID(enum movement_Index type);//enable=false

#pragma endregion


#pragma region Fields

//enum
enum movement_Index { EBL = 1, EBT = 2, EBR = 3, WBL = 4, WBT = 5, WBR = 6, NBL = 7, NBT = 8, NBR = 9, SBL = 10, SBT = 11, SBR = 12 };
enum stage { stage1 = 1, stage2 = 2, stage3 = 3 };
enum direction { E = 1, W = 2, N = 3, S = 4 };
enum group { L = 1, T_AND_R = 2 };

//array size, for constructing matirx or array
const int laneColumnSize = 32;
const int movementSize = 32;
const int NEMA_PhaseSize = 32;//temp enable=false
const int stageSize = 5;
const int ringSize = 3;
const int directionSize = 5;
const int groupSize = 5;

//index range, for indexing, from 1 to 0+range (including the 0+range th)

//parameters
double l = 12;
double x_c_Input = 0.9;

#pragma endregion


#pragma region Initialization_Methods


class CSignalNode
{
public:
	CSignalNode()
	{
		y_StageMax = 1;
		x_c_output = 0.9;
		c_Min = 60;

		movement_str_to_index_map["EBL"] = EBL;
		movement_str_to_index_map["EBT"] = EBT;
		movement_str_to_index_map["EBR"] = EBR;

		movement_str_to_index_map["WBL"] = WBL;
		movement_str_to_index_map["WBT"] = WBT;
		movement_str_to_index_map["WBR"] = WBR;

		movement_str_to_index_map["NBL"] = NBL;
		movement_str_to_index_map["NBT"] = NBT;
		movement_str_to_index_map["NBR"] = NBR;

		movement_str_to_index_map["SBL"] = SBL;
		movement_str_to_index_map["SBT"] = SBT;
		movement_str_to_index_map["SBR"] = SBR;

		movement_str_to_direction_map["EBL"] = E;
		movement_str_to_direction_map["EBT"] = E;
		movement_str_to_direction_map["EBR"] = E;

		movement_str_to_direction_map["WBL"] = W;
		movement_str_to_direction_map["WBT"] = W;
		movement_str_to_direction_map["WBR"] = W;

		movement_str_to_direction_map["NBL"] = N;
		movement_str_to_direction_map["NBT"] = N;
		movement_str_to_direction_map["NBR"] = N;

		movement_str_to_direction_map["SBL"] = S;
		movement_str_to_direction_map["SBT"] = S;
		movement_str_to_direction_map["SBR"] = S;

		for (int s = 0; s <= stageSize; s++)
		{
			y_Max_Stage_Array[s] = 0;

			for (int m = 0; m <= movementSize; m++)
			{
				saturation_Flow_Rate_Matrix[s][m] = 0;
			}

			for (int d = 0; d <= directionSize; d++)
				for(int g = 0; g <= groupSize; g++)
			{
					stage_Direction_Candidates_Matrix[s][d][g] = 0;

			}

		}

		Set_Movement_to_Stage_Array();   
	}
	int movement_Range = 12;
	int stage_Range = 3;

	std::map<string, movement_Index> movement_str_to_index_map;
	std::map<string, direction> movement_str_to_direction_map;


	//array
	enum stage movement_to_Stage_Array[movementSize + 1];
	SMovementData movement_Array[movementSize + 1]; //indexed by enum movement_Direction
	int green_Start_Stage_Array[stageSize + 1];
	int green_End_Stage_Array[stageSize+1];
	double y_Max_Stage_Array[stageSize+1];
	double green_Time_Stage_Array[stageSize + 1];
	double cumulative_green_start_time_Stage_Array[stageSize + 1];
	double cumulative_green_end_time_Stage_Array[stageSize + 1];


	//matrix
	int saturation_Flow_Rate_Matrix[stageSize+1][movementSize + 1];//s
	double y_Stage_Movement_Matrix[stageSize + 1][movementSize + 1];
	double stage_Direction_Candidates_Matrix[stageSize + 1][directionSize + 1][groupSize + 1];


	int NEMA_Phase_Matrix[5][3] = { 0,0,0,0,1,5,0,2,6,0,3,7,0,4,8 };//row->NEMA_phases; col->rings
	int green_Start_NEMA_Phase[5][3];

	SMovementData Stage_Ring_Movement_Matrix[ringSize + 1][stageSize + 1];

	//variables

	double y_StageMax;
	double x_c_output;
	double c_Min;

	void AddMovementVolume(int link_seq_no, string str, float volume)
	{
		movement_Index mi = movement_str_to_index_map[str];
		direction di = movement_str_to_direction_map[str];

			movement_Array[mi].Enable = true;
			movement_Array[mi].LinkSeqNo = link_seq_no;
			movement_Array[mi].Volume = volume;
			movement_Array[mi].StageNo = stage(movement_to_Stage_Array[mi]);
			movement_Array[mi].GroupNo = group(mi);
			movement_Array[mi].DirectionNo = di;
		
	}

	void PerformQEM()
	{
		// step 1: input movement volume


		Set_Saturation_Flow_Rate_Matrix(); // to do:

		//step 2: Calculating Flow Ratio
		cout << "Calculating Flow Ratio \n";
		Calculating_Flow_of_Ratio_Max();
		cout << y_StageMax << endl;

		cout << "Calculating the Minimum Cycle Length \n";
		Calculating_the_Minimum_Cycle_Length();
		cout << c_Min << endl;

		cout << "ReCalculating xc \n";
		Calculating_the_x_c_Output();
		cout << x_c_output << endl;

		cout << "Timing for Stages \n";
		Calculating_Green_Time_for_Stages();
		Printing_Green_Time_for_Stages();

	}

	void Set_Movement_to_Stage_Array()
	{
		//movement_Array
		movement_to_Stage_Array[EBL] = stage1;
		movement_to_Stage_Array[EBT] = stage2;
		movement_to_Stage_Array[EBR] = stage2;
		movement_to_Stage_Array[WBL] = stage1;
		movement_to_Stage_Array[WBT] = stage2;
		movement_to_Stage_Array[WBR] = stage2;
		movement_to_Stage_Array[NBL] = stage3;
		movement_to_Stage_Array[NBT] = stage3;
		movement_to_Stage_Array[NBR] = stage3;
		movement_to_Stage_Array[SBL] = stage3;
		movement_to_Stage_Array[SBT] = stage3;
		movement_to_Stage_Array[SBR] = stage3;
	}


	void Set_Movement_Array()
	{
		//movement_Array 
		movement_Array[1].Enable = true;
		movement_Array[1].Volume = 300;
		movement_Array[1].StageNo = stage(movement_to_Stage_Array[1]);
		movement_Array[1].GroupNo = group(1);
		movement_Array[1].DirectionNo = E;

		movement_Array[2].Enable = true;
		movement_Array[2].Volume = 900;
		movement_Array[2].StageNo = stage(movement_to_Stage_Array[2]);
		movement_Array[2].GroupNo = group(2);
		movement_Array[2].DirectionNo = E;

		movement_Array[3].Enable = true;
		movement_Array[3].Volume = 200;
		movement_Array[3].StageNo = stage(movement_to_Stage_Array[3]);
		movement_Array[3].GroupNo = group(2);
		movement_Array[3].DirectionNo = E;

		movement_Array[4].Enable = true;
		movement_Array[4].Volume = 250;
		movement_Array[4].StageNo = stage(movement_to_Stage_Array[4]);
		movement_Array[4].GroupNo = group(1);
		movement_Array[4].DirectionNo = W;

		movement_Array[5].Enable = true;
		movement_Array[5].Volume = 1000;
		movement_Array[5].StageNo = stage(movement_to_Stage_Array[5]);
		movement_Array[5].GroupNo = group(2);
		movement_Array[5].DirectionNo = W;

		movement_Array[6].Enable = true;
		movement_Array[6].Volume = 150;
		movement_Array[6].StageNo = stage(movement_to_Stage_Array[6]);
		movement_Array[6].GroupNo = group(2);
		movement_Array[6].DirectionNo = W;

		movement_Array[7].Enable = true;
		movement_Array[7].Volume = 70;
		movement_Array[7].StageNo = stage(movement_to_Stage_Array[7]);
		movement_Array[7].GroupNo = group(1);
		movement_Array[7].DirectionNo = N;

		movement_Array[8].Enable = true;
		movement_Array[8].Volume = 310;
		movement_Array[8].StageNo = stage(movement_to_Stage_Array[8]);
		movement_Array[8].GroupNo = group(2);
		movement_Array[8].DirectionNo = N;

		movement_Array[9].Enable = true;
		movement_Array[9].Volume = 60;
		movement_Array[9].StageNo = stage(movement_to_Stage_Array[9]);
		movement_Array[9].GroupNo = group(2);
		movement_Array[9].DirectionNo = N;

		movement_Array[10].Enable = true;
		movement_Array[10].Volume = 90;
		movement_Array[10].StageNo = stage(movement_to_Stage_Array[10]);
		movement_Array[10].GroupNo = group(1);
		movement_Array[10].DirectionNo = S;

		movement_Array[11].Enable = true;
		movement_Array[11].Volume = 340;
		movement_Array[11].StageNo = stage(movement_to_Stage_Array[11]);
		movement_Array[11].GroupNo = group(2);
		movement_Array[11].DirectionNo = S;

		movement_Array[12].Enable = true;
		movement_Array[12].Volume = 50;
		movement_Array[12].StageNo = stage(movement_to_Stage_Array[12]);
		movement_Array[12].GroupNo = group(2);
		movement_Array[12].DirectionNo = S;

	}

	void Set_Saturation_Flow_Rate_Matrix()
	{
		//movement_Array left turn movement
		// we need to use the saturation flow rate values based on protected and permitted

		saturation_Flow_Rate_Matrix[1][EBL] = 1750;
		saturation_Flow_Rate_Matrix[1][WBL] = 1750;
		saturation_Flow_Rate_Matrix[2][EBT] = 3400;
		saturation_Flow_Rate_Matrix[2][EBR] = 3400;
		saturation_Flow_Rate_Matrix[2][WBT] = 3400;
		saturation_Flow_Rate_Matrix[2][WBR] = 3400;
		saturation_Flow_Rate_Matrix[3][NBL] = 475;
		saturation_Flow_Rate_Matrix[3][NBT] = 1800;
		saturation_Flow_Rate_Matrix[3][NBR] = 1800;
		saturation_Flow_Rate_Matrix[3][SBL] = 450;
		saturation_Flow_Rate_Matrix[3][SBT] = 1800;
		saturation_Flow_Rate_Matrix[3][SBR] = 1800;
	}
#pragma endregion

#pragma region Private_Methods

	void Calculating_Flow_of_Ratio_Max()
	{
		//y_Stage_Movement_Matrix
		//y_StageMax
		for (size_t i = 1; i <= stage_Range; i++)
		{
			y_Max_Stage_Array[i] = 0;

			for (size_t m = 1; m <= movement_Range; m++)
			{
				if (saturation_Flow_Rate_Matrix[i][m] != 0 && movement_Array[m].Enable && movement_Array[m].StageNo == i)
				{
					y_Stage_Movement_Matrix[i][m] = double(movement_Array[m].Volume) / double(saturation_Flow_Rate_Matrix[i][m]);

					//double stage_Direction_Candidates_Matrix[stageSize][directionSize][groupSize]
					stage_Direction_Candidates_Matrix[i][movement_Array[m].DirectionNo][movement_Array[m].GroupNo] += y_Stage_Movement_Matrix[i][m];

					// we tally the movement matrix from this direction and this group number, so we can distingush movements belonging to different directions 
					if (stage_Direction_Candidates_Matrix[i][movement_Array[m].DirectionNo][movement_Array[m].GroupNo] >= y_Max_Stage_Array[i])
					{
						y_Max_Stage_Array[i] = stage_Direction_Candidates_Matrix[i][movement_Array[m].DirectionNo][movement_Array[m].GroupNo];
					}
				}
			}
		}

		y_StageMax = 0;
		for (size_t i = 1; i <= stageSize; i++)
		{
			y_StageMax += y_Max_Stage_Array[i];
		}

	}


	void Calculating_the_Minimum_Cycle_Length()
	{
		c_Min = max(60, (l - x_c_Input) / (x_c_Input - y_StageMax));
	}

	void Calculating_the_x_c_Output()
	{
		x_c_output = (y_StageMax * c_Min) / (c_Min - l);
	}


	void Calculating_Green_Time_for_Stages()
	{
		for (size_t i = 1; i <= stage_Range; i++)
		{
//			green_Time_Stage_Array[i] = y_Max_Stage_Array[i] * c_Min / x_c_output;
			green_Time_Stage_Array[i] = y_Max_Stage_Array[i] * c_Min / y_StageMax;

			
		}
	}

	void Printing_Green_Time_for_Stages()
	{
		cumulative_green_start_time_Stage_Array[1] = 0;
		cumulative_green_end_time_Stage_Array[1] = green_Time_Stage_Array[1];


		for (size_t i = 2; i <= stage_Range; i++)
		{
			cout << green_Time_Stage_Array[i] << endl;
			cumulative_green_start_time_Stage_Array[i] = cumulative_green_end_time_Stage_Array[i - 1];
			cumulative_green_end_time_Stage_Array[i] = cumulative_green_start_time_Stage_Array[i] + green_Time_Stage_Array[i];
		}
	}


	int signal_node_seq_no;  // sequence number 
	int main_node_id;      //external node number 

	std::vector<int> m_movement_link_seq_no_vector;

};


extern std::vector<CNode> g_node_vector;
extern std::vector<CLink> g_link_vector;
extern std::vector<CServiceArc> g_service_arc_vector;


std::vector<CNode> g_node_vector;
std::vector<CLink> g_link_vector;
std::vector<CServiceArc> g_service_arc_vector;

std::map<int, CSignalNode> g_signal_node_map;  // first key is signal node id


//split the string by "_"
vector<string> split(const string &s, const string &seperator) {
	vector<string> result;typedef string::size_type string_size;
	string_size i = 0;

	while (i != s.size()) {
		int flag = 0;
		while (i != s.size() && flag == 0) {
			flag = 1;
			for (string_size x = 0; x < seperator.size(); ++x)
				if (s[i] == seperator[x]) {
					++i;
					flag = 0;
					break;
				}
		}

		flag = 0;
		string_size j = i;
		while (j != s.size() && flag == 0) {
			for (string_size x = 0; x < seperator.size(); ++x)
				if (s[j] == seperator[x]) {
					flag = 1;
					break;
				}
			if (flag == 0)
				++j;
		}
		if (i != j) {
			result.push_back(s.substr(i, j - i));
			i = j;
		}
	}
	return result;
}
string test_str = "0300:30:120_0600:30:140";


vector<float> g_time_parser(vector<string>& inputstring)
{
	vector<float> output_global_minute;

	for (int k = 0; k < inputstring.size(); k++)
	{
		vector<string> sub_string = split(inputstring[k], "_");

		for (int i = 0; i < sub_string.size(); i++)
		{
			//HHMM
			//012345
			char hh1 = sub_string[i].at(0);
			char hh2 = sub_string[i].at(1);
			char mm1 = sub_string[i].at(2);
			char mm2 = sub_string[i].at(3);

			float hhf1 = ((float)hh1 - 48);
			float hhf2 = ((float)hh2 - 48);
			float mmf1 = ((float)mm1 - 48);
			float mmf2 = ((float)mm2 - 48);

			float hh = hhf1 * 10 * 60 + hhf2 * 60;
			float mm = mmf1 * 10 + mmf2;
			float global_mm_temp = hh + mm;
			output_global_minute.push_back(global_mm_temp);
		}
	}

	return output_global_minute;
} // transform hhmm to minutes 


inline string g_time_coding(float time_stamp)
{
	int hour = time_stamp / 60;
	int minute = time_stamp - hour * 60;

	int second = (time_stamp - hour * 60 - minute)*60;

	ostringstream strm;
	strm.fill('0');
	strm << setw(2) << hour << setw(2) << minute << ":" << setw(2) << second;

	return strm.str();
} // transform hhmm to minutes 


void g_ProgramStop()
{

	cout << "STALite Program stops. Press any key to terminate. Thanks!" << endl;
	getchar();
	exit(0);
};



void g_ReadInputData(CMainModual& MainModual)
{

	MainModual.g_LoadingStartTimeInMin = 99999;
	MainModual.g_LoadingEndTimeInMin = 0;

	//step 0:read demand period file
	CCSVParser parser_demand_period;
	cout << "Step 1: Reading file demand_period.csv..." << endl;
	//g_LogFile << "Step 7.1: Reading file input_agent_type.csv..." << g_GetUsedMemoryDataInMB() << endl;
	if (!parser_demand_period.OpenCSVFile("demand_period.csv", true))
	{
		cout << "demand_period.csv cannot be opened. " << endl;
		g_ProgramStop();

	}

	if (parser_demand_period.inFile.is_open() || parser_demand_period.OpenCSVFile("demand_period.csv", true))
	{

		while (parser_demand_period.ReadRecord())
		{
			int demand_period_id;

			if (parser_demand_period.GetValueByFieldName("demand_period_id", demand_period_id) == false)
			{
				cout << "Error: Field demand_period_id in file demand_period cannot be read." << endl;
				g_ProgramStop();
				break;
			}


			vector<float> global_minute_vector;
			string time_period;
			if (parser_demand_period.GetValueByFieldName("time_period", time_period) == false)
			{
				cout << "Error: Field time_period in file demand_period cannot be read." << endl;
				g_ProgramStop();
				break;
			}

			vector<string> input_string;
			input_string.push_back(time_period);
			//input_string includes the start and end time of a time period with hhmm format
			global_minute_vector = g_time_parser(input_string); //global_minute_vector incldue the starting and ending time
			if (global_minute_vector.size() == 2)
			{


				if (global_minute_vector[0] < MainModual.g_LoadingStartTimeInMin)
					MainModual.g_LoadingStartTimeInMin = global_minute_vector[0];

				if (global_minute_vector[1] > MainModual.g_LoadingEndTimeInMin)
					MainModual.g_LoadingEndTimeInMin = global_minute_vector[1];



				//cout << global_minute_vector[0] << endl;
				//cout << global_minute_vector[1] << endl;
			}

		}
		parser_demand_period.CloseCSVFile();
	}

	MainModual.g_number_of_nodes = 0;
	MainModual.g_number_of_links = 0;  // initialize  the counter to 0


	int internal_node_seq_no = 0;
	// step 3: read node file 

	CCSVParser parser;
	if (parser.OpenCSVFile("node.csv", true))
	{


		while (parser.ReadRecord())  // if this line contains [] mark, then we will also read field headers.
		{

			int node_id;

			if (parser.GetValueByFieldName("node_id", node_id) == false)
				continue;

			if (MainModual.g_internal_node_to_seq_no_map.find(node_id) != MainModual.g_internal_node_to_seq_no_map.end())
			{
				continue; //has been defined
			}
			MainModual.g_internal_node_to_seq_no_map[node_id] = internal_node_seq_no;



			CNode node;  // create a node object 

			node.node_id = node_id;
			node.node_seq_no = internal_node_seq_no;

			internal_node_seq_no++;

			g_node_vector.push_back(node);  // push it to the global node vector

			MainModual.g_number_of_nodes++;
			if (MainModual.g_number_of_nodes % 5000 == 0)
				cout << "reading " << MainModual.g_number_of_nodes << " nodes.. " << endl;
		}

		cout << "number of nodes = " << MainModual.g_number_of_nodes << endl;

	//	fprintf(g_pFileOutputLog, "number of nodes =,%d\n", MainModual.g_number_of_nodes);

		parser.CloseCSVFile();
	}

	// step 4: read link file 

	CCSVParser parser_link;

	if (parser_link.OpenCSVFile("road_link.csv", true))
	{
		while (parser_link.ReadRecord())  // if this line contains [] mark, then we will also read field headers.
		{
			int from_node_id;
			int to_node_id;
			if (parser_link.GetValueByFieldName("from_node_id", from_node_id) == false)
				continue;
			if (parser_link.GetValueByFieldName("to_node_id", to_node_id) == false)
				continue;

			string linkID;
			parser_link.GetValueByFieldName("road_link_id", linkID);


			// add the to node id into the outbound (adjacent) node list

			if (MainModual.g_internal_node_to_seq_no_map.find(from_node_id) == MainModual.g_internal_node_to_seq_no_map.end())
			{
				cout << "Error: from_node_id " << from_node_id << " in file road_link.csv is not defined in node.csv." << endl;

				continue; //has not been defined
			}
			if (MainModual.g_internal_node_to_seq_no_map.find(to_node_id) == MainModual.g_internal_node_to_seq_no_map.end())
			{
				cout << "Error: to_node_id " << to_node_id << " in file road_link.csv is not defined in node.csv." << endl;
				continue; //has not been defined
			}

			if (MainModual.g_road_link_id_map.find(linkID) != MainModual.g_road_link_id_map.end())
			{
				cout << "Error: road_link_id " << linkID.c_str() << " has been defined more than once. Please check road_link.csv." << endl;
				continue; //has not been defined
			}


			int internal_from_node_seq_no = MainModual.g_internal_node_to_seq_no_map[from_node_id];  // map external node number to internal node seq no. 
			int internal_to_node_seq_no = MainModual.g_internal_node_to_seq_no_map[to_node_id];


			CLink link;  // create a link object 

			link.from_node_seq_no = internal_from_node_seq_no;
			link.to_node_seq_no = internal_to_node_seq_no;
			link.link_seq_no = MainModual.g_number_of_links;
			link.to_node_seq_no = internal_to_node_seq_no;
			link.link_id = linkID;

			MainModual.g_road_link_id_map[link.link_id] = 1;



			parser_link.GetValueByFieldName("facility_type", link.type, true, false);
			parser_link.GetValueByFieldName("link_type", link.link_type);


			float length = 1.0; // km or mile
			float free_speed = 1.0;

			float lane_capacity = 1800;
			parser_link.GetValueByFieldName("length", length);
			parser_link.GetValueByFieldName("free_speed", free_speed);
			free_speed = max(0.1, free_speed);

			int number_of_lanes = 1;
			parser_link.GetValueByFieldName("lanes", number_of_lanes);
			parser_link.GetValueByFieldName("capacity", lane_capacity);

			float default_cap = 1000;
			float default_BaseTT = 1;

			link.number_of_lanes = number_of_lanes;
			link.lane_capacity = lane_capacity;


			link.length = length;
			link.free_flow_travel_time_in_min = length / free_speed * 60;


			g_node_vector[internal_from_node_seq_no].m_outgoing_link_seq_no_vector.push_back(link.link_seq_no);  // add this link to the corresponding node as part of outgoing node/link
			g_node_vector[internal_to_node_seq_no].m_incoming_link_seq_no_vector.push_back(link.link_seq_no);  // add this link to the corresponding node as part of outgoing node/link



			g_node_vector[internal_from_node_seq_no].m_to_node_seq_no_vector.push_back(link.to_node_seq_no);  // add this link to the corresponding node as part of outgoing node/link
			g_node_vector[internal_from_node_seq_no].m_to_node_2_link_seq_no_map[link.to_node_seq_no] = link.link_seq_no;  // add this link to the corresponding node as part of outgoing node/link

			g_link_vector.push_back(link);

			MainModual.g_number_of_links++;

			// map link data to signal node map.

			string movement_str;
			parser_link.GetValueByFieldName("movement_str", movement_str);

			if (movement_str.size() > 0)  // and valid
			{
				int main_node_id = -1;

				parser_link.GetValueByFieldName("main_node_id", main_node_id, true, false);


				int NEMA_phase_number = 0;
				parser_link.GetValueByFieldName("NEMA_phase_number", NEMA_phase_number,true,false);

				int initial_volume = 200;
				parser_link.GetValueByFieldName("volume", initial_volume, true, false);

				if(main_node_id>=1)
				{
					g_signal_node_map[main_node_id].AddMovementVolume(link.link_seq_no, movement_str, initial_volume);
				}
			}


		}
		}
		parser_link.CloseCSVFile();
	// we now know the number of links
	cout << "number of links = " << MainModual.g_number_of_links << endl;

//	fprintf(g_pFileOutputLog, "number of links =,%d\n", MainModual.g_number_of_links);


};


double SignalAPI(int iteration_number, int MainModual_mode, int column_updating_iterations)
{

// step 1: read input data of network / demand tables / Toll
	g_ReadInputData(MainModual);

	for (std::map<int, CSignalNode>::iterator it = g_signal_node_map.begin(); it != g_signal_node_map.end(); ++it)
	{
		it->second.PerformQEM();
	}

	//output service_arc.csv

	FILE* g_pFileServiceArc = NULL;

	fopen_ss(&g_pFileServiceArc, "service_arc.csv", "w");

	if (g_pFileServiceArc == NULL)
	{
		cout << "File service_arc.csv cannot be opened." << endl;
		g_ProgramStop();
	}
	else
	{

		
		fprintf(g_pFileServiceArc, "from_node_id,to_node_id,time_window,time_interval,travel_time_delta,capacity\n");

		for (std::map<int, CSignalNode>::iterator it = g_signal_node_map.begin(); it != g_signal_node_map.end(); ++it)
		{
			CSignalNode sn = it->second;

			int cycle_time_in_sec = max(10,sn.c_Min);
			int number_of_cycles = (MainModual.g_LoadingEndTimeInMin - MainModual.g_LoadingStartTimeInMin) * 60 / cycle_time_in_sec;  // unit: seconds;
			int offset_in_sec = 0;
			int g_loading_start_time_in_sec = MainModual.g_LoadingStartTimeInMin * 60 + offset_in_sec;
			for (int ci = 0; ci <= number_of_cycles; ci++)
			{

				for (int m = 1; m < movementSize; m++)
				{
					if (sn.movement_Array[m].Enable)
					{

						int StageNo = sn.movement_Array[m].StageNo;
						// we should also consider offset.
						int global_start_time_in_sec = sn.cumulative_green_start_time_Stage_Array[StageNo] + cycle_time_in_sec * ci + g_loading_start_time_in_sec;
						int global_end_time_in_sec = sn.cumulative_green_end_time_Stage_Array[StageNo] + cycle_time_in_sec * ci + g_loading_start_time_in_sec;

						//0300:30
						int start_hour = global_start_time_in_sec / 3600;
						int start_min = global_start_time_in_sec / 60 - start_hour * 60;
						int start_sec = global_start_time_in_sec % 60;

						int end_hour = global_end_time_in_sec / 3600;
						int end_min = global_end_time_in_sec / 60 - end_hour * 60;
						int end_sec = global_end_time_in_sec % 60;

						int from_node_id = g_node_vector[g_link_vector[sn.movement_Array[m].LinkSeqNo].from_node_seq_no].node_id;
						int to_node_id = g_node_vector[g_link_vector[sn.movement_Array[m].LinkSeqNo].to_node_seq_no].node_id;
						float capacity = sn.green_Time_Stage_Array[StageNo] * sn.saturation_Flow_Rate_Matrix[StageNo][m] / 3600.0;
						fprintf(g_pFileServiceArc, "%d,%d,%02d%02d:%02d_%02d%02d:%02d,-1,-1,%f\n",
							from_node_id,
							to_node_id,
							start_hour,
							start_min,
							start_sec,
							end_hour,
							end_min,
							end_sec,
							capacity
						);

					}  // per movement

				}
			}  // per cycle
		}  // per signal node
	
		fclose(g_pFileServiceArc);
	}


	getchar();
	return 1;

}



