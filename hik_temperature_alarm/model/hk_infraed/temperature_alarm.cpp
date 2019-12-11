#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include "HCNetSDK.h"
#include "iniFile.h"
#include <stdlib.h>
#include <sys/io.h>
#include <iostream>
#include <iconv.h>
#include <memory.h>
#include <time.h>
#include<typeinfo>
#include<fstream>
#include<string>
#include<iostream>
#include <vector>
#include <sys/stat.h>
#include <sys/types.h>
using namespace std;
#ifdef _WIN32
#elif defined(__linux__) || defined(__APPLE__)
#include <unistd.h>
#endif

//时间解释宏定义
#define GET_YEAR(_time_) (((_time_) >> 26) + 2000)
#define GET_MONTH(_time_) (((_time_) >> 22) & 15)
#define GET_DAY(_time_) (((_time_) >> 17) & 31)
#define GET_HOUR(_time_) (((_time_) >> 12) & 31)
#define GET_MINUTE(_time_) (((_time_) >> 6) & 63)
#define GET_SECOND(_time_) (((_time_) >> 0) & 63)
#define HPR_OK 0
#define HPR_ERROR -1



BOOL CALLBACK MessageCallback(LONG lCommand, NET_DVR_ALARMER *pAlarmer, char *pAlarmInfo, DWORD dwBufLen, void* pUser)
{
    
    char *img_save_path=(char *)pUser;
    NET_DVR_THERMOMETRY_ALARM struThermometryAlarm = {0};
    memcpy(&struThermometryAlarm, pAlarmInfo, sizeof(NET_DVR_THERMOMETRY_ALARM));

    switch(lCommand) 
    {
        case COMM_THERMOMETRY_ALARM: //温度预警或者温度报警
        {
            // NET_DVR_TIME struAbsTime = {0};	
            
			// struAbsTime.dwYear = GET_YEAR(struThermometryAlarm.dwAbsTime);
			// struAbsTime.dwMonth = GET_MONTH(struThermometryAlarm.dwAbsTime);
			// struAbsTime.dwDay = GET_DAY(struThermometryAlarm.dwAbsTime);
			// struAbsTime.dwHour = GET_HOUR(struThermometryAlarm.dwAbsTime);
			// struAbsTime.dwMinute = GET_MINUTE(struThermometryAlarm.dwAbsTime);
			// struAbsTime.dwSecond = GET_SECOND(struThermometryAlarm.dwAbsTime);

            // if (0 == struThermometryAlarm.byRuleCalibType)
            // {
            //     printf("点测温:  PresetNo:%d, RuleTemperature:%.1f, \
            //     CurrTemperature:%.1f, PTZ Info[Pan:%f, Tilt:%f, Zoom:%f], AlarmLevel:%d, \
            //     AlarmType:%d, AlarmRule:%d, RuleCalibType:%d,  Point[x:%f, y:%f]", 
            //     struThermometryAlarm.wPresetNo, struThermometryAlarm.fRuleTemperature, \
            //     struThermometryAlarm.fCurrTemperature, struThermometryAlarm.struPtzInfo.fPan, \
            //     struThermometryAlarm.struPtzInfo.fTilt, struThermometryAlarm.struPtzInfo.fZoom, \
            //     struThermometryAlarm.byAlarmLevel, struThermometryAlarm.byAlarmType, \
            //     struThermometryAlarm.byAlarmRule, struThermometryAlarm.byRuleCalibType, \
            //     struThermometryAlarm.struPoint.fX, struThermometryAlarm.struPoint.fY);
            // }

            if (1 == struThermometryAlarm.byRuleCalibType || 2 == struThermometryAlarm.byRuleCalibType)
            {
                int iPointNum = struThermometryAlarm.struRegion.dwPointNum;
                for (int i = 0; i < iPointNum; i++)
                {
                    float fX = struThermometryAlarm.struRegion.struPos[i].fX;
                    float fY = struThermometryAlarm.struRegion.struPos[i].fY;
                }
                 // 判断是否为报警情况，报警才输出.
                int AlarmLevel = struThermometryAlarm.byAlarmLevel;
                if(AlarmLevel == 1)
                {
                    if (struThermometryAlarm.dwThermalPicLen > 0 && struThermometryAlarm.pThermalPicBuff!= NULL)
                    {
                        char CurrTemperature[10]={0};
                        char RuleTemperature[10]={0};
                        char PresetNo[10]={0};
                        char HighestPointX[10]={0};
                        char HighestPointY[10]={0};
                        char PtzInfoPan[10]={0};
                        char PtzInfoTilt[10]={0};
                        char PtzInfoZoom[10]={0};

                        char chFile_temperature[256] = {0};
                        char cFilename_up_load[256] = {0};
                        char chFilePWD_back[256] = {0};

                        char chFile_origin[256] = {0};
                        char chFilePWD_origin[256] = {0};

                        sprintf(RuleTemperature, "%1.2f", struThermometryAlarm.fRuleTemperature);
                        sprintf(CurrTemperature, "%1.2f", struThermometryAlarm.fCurrTemperature);
                        sprintf(PresetNo, "%d", struThermometryAlarm.wPresetNo);
                        sprintf(HighestPointX, "%1.2f", struThermometryAlarm.struHighestPoint.fX);
                        sprintf(HighestPointY, "%1.2f", struThermometryAlarm.struHighestPoint.fY);
                        sprintf(PtzInfoPan, "%1.2f",struThermometryAlarm.struPtzInfo.fPan);
                        sprintf(PtzInfoTilt, "%1.2f",struThermometryAlarm.struPtzInfo.fTilt);
                        sprintf(PtzInfoZoom, "%1.2f",struThermometryAlarm.struPtzInfo.fZoom);


                        sprintf(chFile_temperature, "%s/infraed_temperature",img_save_path);
                        sprintf(chFile_origin, "%s/infraed_origin",img_save_path);
                        sprintf(cFilename_up_load, "%s_%s_%s_%s_%s_%s_%s_%s.jpg",HighestPointX,HighestPointY,PtzInfoPan,PtzInfoTilt,PtzInfoZoom,PresetNo,RuleTemperature,CurrTemperature);
                        sprintf(chFilePWD_back, "%s/infraed_temperature/%s",img_save_path,cFilename_up_load);
                        sprintf(chFilePWD_origin, "%s/infraed_origin/%s",img_save_path,cFilename_up_load);


                        if (access(chFile_temperature, 0) == -1){
                                int flag_snap = mkdir(chFile_temperature,S_IRUSR | S_IWUSR | S_IXUSR | S_IRWXG | S_IRWXO);
                        }

                        if (access(chFile_origin, 0) == -1){
                                int flag_snap = mkdir(chFile_origin,S_IRUSR | S_IWUSR | S_IXUSR | S_IRWXG | S_IRWXO);
                        }

                        FILE *fpThermal;
                        fpThermal = fopen(chFilePWD_back, "wb");
                        fwrite(
                            struThermometryAlarm.pThermalPicBuff,
                            sizeof(char),
                            struThermometryAlarm.dwThermalPicLen,
                            fpThermal
                        );
                        fclose(fpThermal);

                        FILE *fpOrigin;
                        fpOrigin = fopen(chFilePWD_origin, "wb");
                        fwrite(
                            struThermometryAlarm.pPicBuff,
                            sizeof(char),
                            struThermometryAlarm.dwPicLen,
                            fpThermal
                        );
                        fclose(fpOrigin);

                        if (access(chFilePWD_back, 0) != -1 && access(chFilePWD_origin, 0) != -1){
                                cout << "CPP CurrTemperature:"<< cFilename_up_load<< endl;
                            }
                    }
                }
            }
            break;
        }
   
        default:
            //printf("其他报警，报警信息类型: %d\n", lCommand);
            break;
    }

    return TRUE;
}

int Demo_AlarmFortify(char *DeviceIP, int port, char *userName, char *password,char *img_save_path) {
    //---------------------------------------
    // 初始化
    NET_DVR_Init();
    //设置连接时间与重连时间
    NET_DVR_SetConnectTime(2000, 1);
    NET_DVR_SetReconnect(10000, true);
    //---------------------------------------
    // 注册设备
    LONG lUserID;

    //登录参数，包括设备地址、登录用户、密码等
    NET_DVR_USER_LOGIN_INFO struLoginInfo = {0};
    struLoginInfo.bUseAsynLogin = 0; //同步登录方式
    strcpy(struLoginInfo.sDeviceAddress, DeviceIP); //设备IP地址
    struLoginInfo.wPort = port; //设备服务端口
    strcpy(struLoginInfo.sUserName, userName); //设备登录用户名
    strcpy(struLoginInfo.sPassword, password); //设备登录密码
  
    //设备信息, 输出参数
    NET_DVR_DEVICEINFO_V40 struDeviceInfoV40 = {0};

    lUserID = NET_DVR_Login_V40(&struLoginInfo, &struDeviceInfoV40);
    if (lUserID < 0)
    {
        printf("Login failed, error code: %d\n", NET_DVR_GetLastError());
        NET_DVR_Cleanup();
        return 0;
    }
  
    //设置报警回调函数
    NET_DVR_SetDVRMessageCallBack_V31(MessageCallback, img_save_path);
  
    //启用布防
    LONG lHandle;
    NET_DVR_SETUPALARM_PARAM  struAlarmParam={0};
    struAlarmParam.dwSize=sizeof(struAlarmParam);
    //温度或者温差报警不需要设置其他报警布防参数，不支持

    lHandle = NET_DVR_SetupAlarmChan_V41(lUserID, & struAlarmParam);
    if (lHandle < 0)
    {
        printf("NET_DVR_SetupAlarmChan_V41 error, %d\n", NET_DVR_GetLastError());
        NET_DVR_Logout(lUserID);
        NET_DVR_Cleanup(); 
        return 0;
    }
  
    sleep(50000); //等待过程中，如果设备上传报警信息，在报警回调函数里面接收和处理报警信息

    //撤销布防上传通道
    if (!NET_DVR_CloseAlarmChan_V30(lHandle))
    {
        printf("NET_DVR_CloseAlarmChan_V30 error, %d\n", NET_DVR_GetLastError());
        NET_DVR_Logout(lUserID);
        NET_DVR_Cleanup(); 
        return 0;
    }
  
    //注销用户
    NET_DVR_Logout(lUserID);
    //释放SDK资源
    NET_DVR_Cleanup();
    return 0;
}

extern "C" {

	int InfraedTemperature(char *DeviceIP, int port, char *userName, char *password,char *img_save_path)
	{
		Demo_AlarmFortify(DeviceIP, port, userName, password,img_save_path);
		return 0;
	}

}
