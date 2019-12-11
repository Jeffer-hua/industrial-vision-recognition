#include <stdio.h>
#include <iostream>
#include "HCNetSDK.h"
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
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
//时间解析宏定义
#define GET_YEAR(_time_)      (((_time_)>>26) + 2000) 
#define GET_MONTH(_time_)     (((_time_)>>22) & 15)
#define GET_DAY(_time_)       (((_time_)>>17) & 31)
#define GET_HOUR(_time_)      (((_time_)>>12) & 31) 
#define GET_MINUTE(_time_)    (((_time_)>>6)  & 63)
#define GET_SECOND(_time_)    (((_time_)>>0)  & 63)

int iNum=0;
#define ISAPI_OUT_LEN	3 * 1024 * 1024
#define ISAPI_STATUS_LEN  8*1024

void CALLBACK GetThermInfoCallback(DWORD dwType, void* lpBuffer, DWORD dwBufLen, void* pUserData)
{
    if (dwType == NET_SDK_CALLBACK_TYPE_DATA)
    {
        LPNET_DVR_THERMOMETRY_UPLOAD lpThermometry = new NET_DVR_THERMOMETRY_UPLOAD;
        memcpy(lpThermometry, lpBuffer, sizeof(*lpThermometry));

        NET_DVR_TIME struAbsTime = {0};
        struAbsTime.dwYear = GET_YEAR(lpThermometry->dwAbsTime);
        struAbsTime.dwMonth = GET_MONTH(lpThermometry->dwAbsTime);
        struAbsTime.dwDay = GET_DAY(lpThermometry->dwAbsTime);
        struAbsTime.dwHour = GET_HOUR(lpThermometry->dwAbsTime);
        struAbsTime.dwMinute = GET_MINUTE(lpThermometry->dwAbsTime);
        struAbsTime.dwSecond = GET_SECOND(lpThermometry->dwAbsTime);

//         printf("实时测温结果:byRuleID[%d]wPresetNo[%d]byRuleCalibType[%d]byThermometryUnit[%d]byDataType[%d]"
//             "dwAbsTime[%4.4d%2.2d%2.2d%2.2d%2.2d%2.2d]\n", lpThermometry->byRuleID, lpThermometry->wPresetNo,
//             lpThermometry->byRuleCalibType,lpThermometry->byThermometryUnit, lpThermometry->byDataType,
//             struAbsTime.dwYear, struAbsTime.dwMonth, struAbsTime.dwDay,
//             struAbsTime.dwHour, struAbsTime.dwMinute, struAbsTime.dwSecond);

        if(lpThermometry->byRuleCalibType==0) //点测温
        {
            printf("点测温信息:fTemperature[%1.3f]\n", lpThermometry->struPointThermCfg.fTemperature);
        } 
        cout << "can not find"<< endl;
        if((lpThermometry->byRuleCalibType==1)||(lpThermometry->byRuleCalibType==2)) //框/线测温
        {
            char infrared_info[1024] = {0};
            char chTime_back[256]={0};
            char max_temperature[128]={0};
            char aver_temperature[128]={0};
            char min_temperature[128]={0};
            sprintf(max_temperature, "%1.3f", lpThermometry->struLinePolygonThermCfg.fMaxTemperature);
            sprintf(aver_temperature, "%1.3f", lpThermometry->struLinePolygonThermCfg.fAverageTemperature);
            sprintf(min_temperature, "%1.3f", lpThermometry->struLinePolygonThermCfg.fMinTemperature);
            sprintf(chTime_back, "%4.4d-%2.2d-%2.2d %2.2d:%2.2d:%2.2d", struAbsTime.dwYear, struAbsTime.dwMonth, struAbsTime.dwDay, struAbsTime.dwHour, struAbsTime.dwMinute, struAbsTime.dwSecond);
            sprintf(infrared_info, "%s_%s_%s_%s",chTime_back,max_temperature, aver_temperature,min_temperature);

            cout << "CPP match infrared_info:"<< infrared_info<< endl;
        }       

        if (lpThermometry != NULL)
        {
            delete lpThermometry;
            lpThermometry = NULL;
        }
    }
    else if (dwType == NET_SDK_CALLBACK_TYPE_STATUS)
    {
        DWORD dwStatus = *(DWORD*)lpBuffer;
        if (dwStatus == NET_SDK_CALLBACK_STATUS_SUCCESS)
        {
            printf("dwStatus:NET_SDK_CALLBACK_STATUS_SUCCESS\n");            
        }
        else if (dwStatus == NET_SDK_CALLBACK_STATUS_FAILED)
        {
            DWORD dwErrCode = *(DWORD*)((char *)lpBuffer + 4);
            printf("NET_DVR_GET_MANUALTHERM_INFO failed, Error code %d\n", dwErrCode);
        }
    }
}

int Demo_AlarmFortify(char *DeviceIP, int port, char *userName, char *password)
{
    DWORD dwChannel = 2;  //热成像通道
    //---------------------------------------
    //初始化
    NET_DVR_Init();

    //设置连接时间与重连时间
    NET_DVR_SetConnectTime(2000, 1);
    NET_DVR_SetReconnect(10000, true);

    //---------------------------------------
    //注册设备(监听报警可以不注册)
    LONG lUserID;
    NET_DVR_DEVICEINFO_V30 struDeviceInfo;
    lUserID = NET_DVR_Login_V30(DeviceIP, port, userName, password, &struDeviceInfo);
    if (lUserID < 0)
    {
        printf("Login error, %d \n", NET_DVR_GetLastError());
        NET_DVR_Cleanup();
//        return 0;
    }

    //启动实时温度检测
    NET_DVR_REALTIME_THERMOMETRY_COND struThermCond = {0};
    struThermCond.dwSize = sizeof(struThermCond);
    struThermCond.byRuleID = 1;       //规则ID，0代表获取全部规则，具体规则ID从1开始
    struThermCond.dwChan = dwChannel; //从1开始，0xffffffff代表获取全部通道

    LONG lHandle = NET_DVR_StartRemoteConfig(lUserID, NET_DVR_GET_REALTIME_THERMOMETRY, &struThermCond, sizeof(struThermCond), GetThermInfoCallback, NULL);
    if (lHandle < 0)
    {
        cout << "NET_DVR_GET_REALTIME_THERMOMETRY failed!"<< endl;
        printf("NET_DVR_GET_REALTIME_THERMOMETRY failed, error code: %d\n", NET_DVR_GetLastError());
    }
    else
    {
        cout << "NET_DVR_GET_REALTIME_THERMOMETRY is successful!"<< endl;
        printf("NET_DVR_GET_REALTIME_THERMOMETRY is successful!");
    }

    sleep(5000);  //等待一段时间，接收实时测温结果

    //关闭长连接配置接口所创建的句柄，释放资源
    if(!NET_DVR_StopRemoteConfig(lHandle))
    {
        printf("NET_DVR_StopRemoteConfig failed, error code: %d\n", NET_DVR_GetLastError());
    }

    //注销用户，如果前面没有登录，该步骤则不需要
    NET_DVR_Logout(lUserID);

    //释放SDK资源
    NET_DVR_Cleanup();

    return 0;
}

extern "C" {

	int InfraedTemperature(char *DeviceIP, int port, char *userName, char *password)
	{
		Demo_AlarmFortify(DeviceIP, port, userName, password);
		return 0;
	}

}
