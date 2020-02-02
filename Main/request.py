import time,json,requests
import numpy as np
import matplotlib
import matplotlib.figure
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.rcParams['font.sans-serif'] = ['FangSong']  # 设置默认字体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时'-'显示为方块的问题
def getProvinceList():
    "获取城市列表"
    url = "https://lab.isaaclin.cn/nCoV/api/provinceName"
    data = requests.get(url=url)
    return data.json()['results']
def catchLatestCount(provienceList):    # api from https://github.com/BlankerL/DXY-2019-nCoV-Crawler
    "抓取各省市死亡人数 治愈人数 确诊人数"
    print(provienceList)
    deadLatestCountList = []
    curedLatestCountList =[]
    confirmLatestCountList = []
    #suspectedLatestCountList = []
    url_ = 'https://lab.isaaclin.cn/nCoV/api/area?latest=1&province='
    for item in provienceList:
        url = url_+item
        data = requests.get(url=url)
        results = data.json()['results'][0]
        deadLatestCountList.append(results['deadCount'])
        curedLatestCountList.append(results['curedCount'])
        confirmLatestCountList.append(results['confirmedCount'])
        #suspectedLatestCountList.append(results['suspectedCount'])
    return deadLatestCountList,curedLatestCountList,confirmLatestCountList
def catchDailyCount(provienceList):
    deadDailyCountList = []
    curedDailyCountList = []
    confirmDailyCountList = []
    #suspectedDailyCountList = []
    for item in provienceList:
        url = 'https://lab.isaaclin.cn/nCoV/api/area?latest=0&province='+item
        data = requests.get(url=url)
        results = data.json()['results']
        temp_deadDailyCountList = []
        temp_curedDailyCountList = []
        temp_confirmDailyCountList = []
        #temp_suspectedDailyCountList = []
        for j in results:
            temp_deadDailyCountList.append(j['deadCount'])
            temp_curedDailyCountList.append(j['curedCount'])
            temp_confirmDailyCountList.append(j['confirmedCount'])
        deadDailyCountList.append(temp_deadDailyCountList)
        curedDailyCountList.append(temp_curedDailyCountList)
        confirmDailyCountList.append(temp_confirmDailyCountList)
    print(len(deadDailyCountList[44]))
    for i in confirmDailyCountList[44]:
        print(i)
    return deadDailyCountList,curedDailyCountList,confirmDailyCountList
def plotDailyChart(provience,provienceList):
    """绘制数据曲线图"""
    index = provienceList.index(provience)
    deadDailyCountList,curedDailyCountList,confirmDailyCountList = catchDailyCount(provienceList)
    plt.figure('2019-nCoV疫情统计图表', facecolor='#f4f4f4', figsize=(10, 8))
    plt.title('2019-nCoV疫情曲线', fontsize=20)
    dataList = range(0,len(deadDailyCountList[index]))
    deadDailyCountList[index].reverse()
    curedDailyCountList[index].reverse()
    confirmDailyCountList[index].reverse()
    plt.plot(dataList,deadDailyCountList[index],label = '死亡')
    plt.plot(dataList,curedDailyCountList[index],label = '治愈')
    plt.plot(dataList,confirmDailyCountList[index],label = '确诊')
    plt.gcf().autofmt_xdate()  # 优化标注（自动倾斜）
    plt.grid(linestyle=':')  # 显示网格
    plt.legend(loc='best')  # 显示图例
    plt.show()
def plotDistributionMap(provienceList):
    "绘制确诊人数分布图"
    _, __, confirmLatestCountList = catchLatestCount(provienceList)
    font = FontProperties(fname='E:/python_project/demoWuhan/res/simkai.ttf', size=14)
    lat_min = 0
    lat_max = 60
    lon_min = 70
    lon_max = 140
    handles = [
        matplotlib.patches.Patch(color='#f0f0f0', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#6B238E', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#ff7b69', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#bf2121', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#7f1818', alpha=1, linewidth=0),
    ]
    labels = ['0人','1-9人', '10-99人', '100-999人', '>1000人']
    fig = matplotlib.figure.Figure()
    fig.set_size_inches(10, 8)  # 设置绘图板尺寸
    axes = fig.add_axes((0.1, 0.12, 0.8, 0.8))  # rect = l,b,w,h
    m = Basemap(llcrnrlon=lon_min, urcrnrlon=lon_max, llcrnrlat=lat_min, urcrnrlat=lat_max, resolution='l', ax=axes)
    m.readshapefile('E:/python_project/demoWuhan/res/china-shapefiles/china', 'province', drawbounds=True)
    m.readshapefile('E:/python_project/demoWuhan/res/china-shapefiles/china_nine_dotted_line', 'section', drawbounds=True)
    m.drawcoastlines(color='black')  # 洲际线
    m.drawcountries(color='black')  # 国界线
    m.drawparallels(np.arange(lat_min, lat_max, 10), labels=[1, 0, 0, 0])  # 画经度线
    m.drawmeridians(np.arange(lon_min, lon_max, 10), labels=[0, 0, 0, 1])  # 画纬度线
    print(m.province_info)
    for info, shape in  zip(m.province_info,m.province):
        #pname = info['OWNER'].strip('\x00')
        fcname = info['FCNAME'].strip('\x00')
        print(fcname)
        if fcname in provienceList:
            pos = provienceList.index(fcname)
            if confirmLatestCountList[pos] == 0:
                color = '#f0f0f0'
            elif confirmLatestCountList[pos] < 10:
                color = '#6B238E'
            elif confirmLatestCountList[pos] < 100:
                color = '#ff7b69'
            elif confirmLatestCountList[pos] < 1000:
                color = '#bf2121'
            else:
                color = '#7f1818'
            poly = Polygon(shape, facecolor=color, edgecolor=color)
            axes.add_patch(poly)
    axes.set_title("2019-nCoV疫情地图", fontproperties=font)
    axes.legend(handles, labels, bbox_to_anchor=(0.5, -0.11), loc='lower center', ncol=4, prop=font)
    FigureCanvasAgg(fig)
    fig.savefig('2019-nCoV疫情地图1.png')
if __name__ == '__main__':
    provienceList = getProvinceList()
    #plotDailyChart('湖北省',provienceList)
    plotDistributionMap(provienceList)
