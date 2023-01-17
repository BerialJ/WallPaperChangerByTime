import datetime
import os
import signal
import time
import win32api
import win32con
import win32gui
import astral
from astral.location import Location
from astral.sun import sun
import wallpaper_change_cron


def get_sunset_ime(date):
    city = astral.LocationInfo('beijing', 'China', 'Asia/Shanghai', 39.54, 116.23)
    # print((
    #     f"Information for {city.name}/{city.region}\n"
    #     f"Timezone: {city.timezone}\n"
    #     f"Latitude: {city.latitude:.02f}; Longitude: {city.longitude:.02f}\n"
    # ))
    beijing = Location(city)
    sun_times = sun(city.observer, date, tzinfo=beijing.timezone)
    # print((
    #     f'Dawn:    {sun_times["dawn"]}\n'
    #     f'Sunrise: {sun_times["sunrise"]}\n'
    #     f'Noon:    {sun_times["noon"]}\n'
    #     f'Sunset:  {sun_times["sunset"]}\n'
    #     f'Dusk:    {sun_times["dusk"]}\n'
    # ))

    sunset_time = f'Sunset:  {sun_times["sunset"]}'.split(' ')[3].split('.')[0][:-3]

    return sunset_time


def start_timer(time_list):
    time_now = time.strftime('%H:%M', time.localtime())
    sunset_time = get_sunset_ime(date=datetime.date.today())
    time_latest = ''
    for time_num in time_list:

        if time_num == 'sunset_time':
            time_num = sunset_time
            print(time_latest)
        if time_now > time_num:
            time_latest = time_num
            print(time_latest)
    print("现在时间%s，仅在%s之后，更换%s壁纸" % (time_now, time_latest, time_latest))
    if time_latest == sunset_time:
        change_wallpaper(time_list['sunset_time'])
    else:
        change_wallpaper(time_list[time_latest])

    while True:
        time_now = time.strftime('%H:%M', time.localtime())
        if time_now == wallpaper_change_cron.check_sunset_time:
            sunset_time = get_sunset_ime(date=datetime.date.today())
            time_list[sunset_time] = time_list['sunset_time']

        if time_now in time_list:
            # print(pairs[time_now])
            change_wallpaper(time_list[time_now])
        # if time_now == sunset_time:
        #     change_wallpaper(time_list[sunset_time])

        time.sleep(58)


def change_wallpaper(path):
    # 切换时要检查一下图片是否存在
    if os.path.exists(path):
        # 打开指定注册表路径
        reg_key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
        # 最后的参数:2拉伸,0居中,6适应,10填充,0平铺
        win32api.RegSetValueEx(reg_key, "WallpaperStyle", 0, win32con.REG_SZ, "10")
        # 最后的参数:1表示平铺,拉伸居中等都是0
        win32api.RegSetValueEx(reg_key, "TileWallpaper", 0, win32con.REG_SZ, "0")
        # 刷新桌面与设置壁纸
        win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, path, win32con.SPIF_SENDWININICHANGE)

    else:
        print('图片不存在，切换失败')
        pass


def get_pairs(time_list):
    # print(cron)
    # table = {}
    # time_now = time.strftime('%H:%M', time.localtime())
    # table[time_now] = 'C:\\Users\\admin\\Desktop\\tools\\wallpaper_changer\\wallpapers\\0179.jpg'
    # return table
    return time_list


def control_pid(path):
    if os.path.exists(path):
        path = open(pid_path, "r")
        pid = path.readline()
        path.close()
        try:
            os.kill(int(pid), signal.SIGINT)
            print('# killed:', pid)
        except OSError:
            print('无相关进程，是否由编译器启动？')

    pid = os.getpid()
    print('# New:', pid)
    path = open(pid_path, "wt")
    path.write("%d" % pid)
    path.close()


if __name__ == '__main__':
    pid_path = "WallPaperChanger.pid"
    cron = wallpaper_change_cron.table

    control_pid(pid_path)
    pairs = get_pairs(cron)
    start_timer(pairs)

    os.remove(pid_path)
