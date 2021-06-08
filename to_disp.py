import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import seaborn as sns
from collections import OrderedDict
from time import sleep
import time
import pms3003
import mh_z19
import Adafruit_DHT
from GPS import GPS
import board
import busio
import adafruit_ccs811
import aqi

class FixSizeOrderedDict(OrderedDict):
    def __init__(self, *args, max=0, **kwargs):
        self._max = max
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        if self._max > 0:
            if len(self) > self._max:
                self.popitem(False)


class AQI_normal():
    color_1_good = "green"
    color_2_moderate = "yellow"
    color_3_unhealthy_sen = "orange"
    color_4_unhealthy = "red"
    color_5_unhealthy_very = "darkviolet" 
    color_6_hazardous = "maroon"

    def pm2_5_to_color(pm:int) -> str:
        if pm <= 12:
            return AQI_normal.color_1_good
        elif pm <= 35.4:
            return AQI_normal.color_2_moderate
        elif pm <= 55.4:
            return AQI_normal.color_3_unhealthy_sen
        elif pm <= 150.4:
            return AQI_normal.color_4_unhealthy
        elif pm <= 250.4:
            return AQI_normal.color_5_unhealthy_very
        else:
            return AQI_normal.color_6_hazardous

    def pm10_to_color(pm:int) -> str:
        if pm <= 54:
            return AQI_normal.color_1_good
        elif pm <= 154:
            return AQI_normal.color_2_moderate
        elif pm <= 254:
            return AQI_normal.color_3_unhealthy_sen
        elif pm <= 354:
            return AQI_normal.color_4_unhealthy
        elif pm <= 424:
            return AQI_normal.color_5_unhealthy_very
        else:
            return AQI_normal.color_6_hazardous
            
    def o3_to_color(data):
        if data <= 125:
            return AQI_normal.color_1_good
        elif data <= 164:
            return AQI_normal.color_3_unhealthy_sen
        elif data <= 204:
            return AQI_normal.color_4_unhealthy
        elif data <= 404:
            return AQI_normal.color_5_unhealthy_very
        else:
            return AQI_normal.color_6_hazardous
            
    def no2_to_color(data):
        if data <= 53:
            return AQI_normal.color_1_good
        elif data <= 100:
            return AQI_normal.color_2_moderate
        elif data <= 360:
            return AQI_normal.color_3_unhealthy_sen
        elif data <= 649:
            return AQI_normal.color_4_unhealthy
        elif data <= 1249:
            return AQI_normal.color_5_unhealthy_very
        else:
            return AQI_normal.color_6_hazardous
            
    def co_to_color(data):
        if data <= 4.4:
            return AQI_normal.color_1_good
        elif data <= 9.4:
            return AQI_normal.color_2_moderate
        elif data <= 12.4:
            return AQI_normal.color_3_unhealthy_sen
        elif data <= 15.4:
            return AQI_normal.color_4_unhealthy
        elif data <= 30.4:
            return AQI_normal.color_5_unhealthy_very
        else:
            return AQI_normal.color_6_hazardous
            
    def co2_to_color(data):
        return AQI_normal.color_1_good
            
    def voc_to_color(data):
        if data <= 35:
            return AQI_normal.color_1_good
        elif data <= 75:
            return AQI_normal.color_2_moderate
        elif data <= 185:
            return AQI_normal.color_3_unhealthy_sen
        elif data <= 304:
            return AQI_normal.color_4_unhealthy
        elif data <= 604:
            return AQI_normal.color_5_unhealthy_very
        else:
            return AQI_normal.color_6_hazardous
            
    def aqi_to_color(data):
        if data <= 50:
            return AQI_normal.color_1_good
        elif data <= 100:
            return AQI_normal.color_2_moderate
        elif data <= 150:
            return AQI_normal.color_3_unhealthy_sen
        elif data <= 200:
            return AQI_normal.color_4_unhealthy
        elif data <= 300:
            return AQI_normal.color_5_unhealthy_very
        else:
            return AQI_normal.color_6_hazardous



class sensors_data():
    def __init__(self) -> None:
        # init PMS3003
        self.pms3003_ = pms3003.PMSensor('/dev/ttyAMA2', env=1)
        self.gps = GPS("/dev/ttyAMA1")
        self.i2c_bus = busio.I2C(board.SCL, board.SDA)
        self.Adafruit_ADS1x15.ADS1115()
        self.R0 = self.adc.read_adc(3, gain=2/3)/32768*6.144


    def pms_get_pm(self):
        if len(self._raw_data_pms_) == 0:
            pm = self.pms3003_.read_pm(no_passive_mode=True, force=True)
        else:
            pm = self.pms3003_.read_pm(no_passive_mode=True)

        if pm[1] > 4000:
            print("error val")
            return self.pms_get_pm()
        return pm[1:3]

    def co2_data(self):
        return mh_z19.read()

    def temp_and_hum_data(self):
        return Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 11)
    
    def gps_loc(self):
        return self.gps.read_loc()

    def voc_data(self):
        return adafruit_ccs811.CCS811(self.i2c_bus)["tvoc"]
    
    def level_bat_data(self):
        return self.adc.read_adc(0, gain=2/3)/32768*6.144

    def co_data(self):
        co = self.adc.read_adc(1, gain=2/3)/32768*6.144
        return (co * 56000) / (3.3 - co) 

    def no2_data(self):
        no2 = self.adc.read_adc(2, gain=2/3)/32768*6.144
        return (no2 * 56000) / (3.3 - no2) 

    def o3_data(self):
        return 9.4783*pow(self.adc.read_adc(3, gain=2/3)/32768*6.144/self.R0, 2.3348)
    
        



class To_display():
    def __init__(self) -> None:
        self.init_plt()
        self.sensors = sensors_data()
        self.next_time_upd = int(time.time())
        # count sec. pause
        self.time_to_upd = 10
        self.data_plt = FixSizeOrderedDict(max=90)
        self.data_plt[int(time.time())] = {"pm2.5":{"data": 0, "color": AQI_normal.color_1_good},
                                "pm10": {"data": 0, "color": AQI_normal.color_1_good},
                                "o3":   {"data": 0, "color": AQI_normal.color_1_good},
                                "no2":  {"data": 0, "color": AQI_normal.color_1_good},
                                "co":   {"data": 0, "color": AQI_normal.color_1_good},
                                "co2":  {"data": 0, "color": AQI_normal.color_1_good},
                                "voc":  {"data": 0, "color": AQI_normal.color_1_good},
                                "aqi":  {"data": 0, "color": AQI_normal.color_1_good},
                                "temp": {"data": 0},
                                "hum":  {"data": 0},
                                "loc":  {"lat": 0, "lon": 0},
                                "bat_l":{"data":0}}
        self.last_pm2_5 = 0
        self.last_pm10  = 0
        self.last_o3   = 0.0
        self.last_no2  = 0.0
        self.last_co   = 0.0
        self.last_co2  = 0.0
        self.last_voc  = 0.0
        self.last_aqi  = 0.0
        self.last_temp = 0.0
        self.last_hum  = 0.0
        self.last_lat  = 0.0
        self.last_lon  = 0.0
        self.last_bat_l= 0.0



    def init_plt(self):
        plt.ion()
        large = 22; med = 16; small = 12
        params = {'axes.titlesize': large,
                'legend.fontsize': med,
                'figure.figsize': (16, 10),
                'axes.labelsize': med,
                'axes.titlesize': med,
                'xtick.labelsize': med,
                'ytick.labelsize': med,
                'figure.titlesize': large}
        plt.rcParams.update(params)
        plt.style.use('seaborn-whitegrid')
        sns.set_style("white")
        self.fig, self.axs = plt.subplots(2, 4, figsize=(25, 15), dpi= 80, facecolor='w', edgecolor='k')
        plt.subplots_adjust(wspace=1, hspace=1)
    def upd_plot(self):
        while True:
            if self.upd_sensors():
                last_num = max(self.data_plt)
                first_num = min(self.data_plt)
                # 0 0
                parametr = "pm2.5"
                formatter = matplotlib.ticker.FuncFormatter(lambda s, x: time.strftime('%H:%M:%S', time.gmtime(s)))
                self.axs[0, 0].xaxis.set_major_formatter(formatter)
                self.axs[0, 0].tick_params('x', labelrotation=45)
                self.axs[0, 0].scatter(x=last_num, y=self.data_plt[last_num]["pm2.5"]["data"], s=20, c=self.data_plt[last_num]["pm2.5"]["color"])
                self.axs[0, 0].set(xlim=(first_num-5, last_num+5), ylim=(0, 20), ylabel='PM, ug/m3')
                self.axs[0, 0].title.set_text(parametr)

                # 0 1
                parametr = "pm10"
                self.axs[0, 1].xaxis.set_major_formatter(formatter)
                self.axs[0, 1].tick_params('x', labelrotation=45)
                self.axs[0, 1].scatter(x=last_num, y=self.data_plt[last_num]["pm10"]["data"], s=20, c=self.data_plt[last_num]["pm10"]["color"])
                self.axs[0, 1].set(xlim=(first_num-5, last_num+5), ylim=(0, 30), ylabel='PM, ug/m3')
                self.axs[0, 1].title.set_text(parametr)

                # 0 2
                parametr = "co2"
                self.axs[0, 2].xaxis.set_major_formatter(formatter)
                self.axs[0, 2].tick_params('x', labelrotation=45)
                self.axs[0, 2].scatter(x=last_num, y=self.data_plt[last_num][parametr]["data"], s=20, c=self.data_plt[last_num][parametr]["color"])
                self.axs[0, 2].set(xlim=(first_num-5, last_num+5), ylim=(0, 1000), ylabel='ppm')
                self.axs[0, 2].title.set_text(parametr)

                # 0 3
                parametr = "aqi"
                self.axs[0, 3].xaxis.set_major_formatter(formatter)
                self.axs[0, 3].tick_params('x', labelrotation=45)
                self.axs[0, 3].scatter(x=last_num, y=self.data_plt[last_num][parametr]["data"], s=20, c=self.data_plt[last_num][parametr]["color"])
                self.axs[0, 3].set(xlim=(first_num-5, last_num+5), ylim=(0, 70), ylabel='ppm')
                self.axs[0, 3].title.set_text(parametr)

                # 1 0
                parametr = "o3"
                self.axs[1, 0].xaxis.set_major_formatter(formatter)
                self.axs[1, 0].tick_params('x', labelrotation=45)
                self.axs[1, 0].scatter(x=last_num, y=self.data_plt[last_num][parametr]["data"], s=20, c=self.data_plt[last_num][parametr]["color"])
                self.axs[1, 0].set(xlim=(first_num-5, last_num+5), ylim=(0, 35), ylabel='ppm')
                self.axs[1, 0].title.set_text(parametr)
                
                # 1 1
                parametr = "no2"
                self.axs[1, 1].xaxis.set_major_formatter(formatter)
                self.axs[1, 1].tick_params('x', labelrotation=45)
                self.axs[1, 1].scatter(x=last_num, y=self.data_plt[last_num][parametr]["data"], s=20, c=self.data_plt[last_num][parametr]["color"])
                self.axs[1, 1].set(xlim=(first_num-5, last_num+5), ylim=(0, 35), ylabel='ppm')
                self.axs[1, 1].title.set_text(parametr)
                
                # 1 2
                parametr = "co"
                self.axs[1, 2].xaxis.set_major_formatter(formatter)
                self.axs[1, 2].tick_params('x', labelrotation=45)
                self.axs[1, 2].scatter(x=last_num, y=self.data_plt[last_num][parametr]["data"], s=20, c=self.data_plt[last_num][parametr]["color"])
                self.axs[1, 2].set(xlim=(first_num-5, last_num+5), ylim=(0, 1.6), ylabel='ppm')
                self.axs[1, 2].title.set_text(parametr)
                
                # 1 3
                parametr = "voc"
                self.axs[1, 3].xaxis.set_major_formatter(formatter)
                self.axs[1, 3].tick_params('x', labelrotation=45)
                self.axs[1, 3].scatter(x=last_num, y=self.data_plt[last_num][parametr]["data"], s=20, c=self.data_plt[last_num][parametr]["color"])
                self.axs[1, 3].set(xlim=(first_num-5, last_num+5), ylim=(0, 40), ylabel='ppm')
                self.axs[1, 3].title.set_text(parametr)

                plt.show()
                plt.pause(10)
    
    def upd_sensors(self) -> bool:
        to_return = False
        if int(time.time()) >= self.next_time_upd:
            time_ = int(time.time()) 
            self.next_time_upd = time_ + self.time_to_upd
            # upd data
            self.data_plt[time_] = {"pm2.5":{"data": self.last_pm2_5, "color": AQI_normal.pm2_5_to_color(self.last_pm2_5)},
                                    "pm10": {"data": self.last_pm10,  "color": AQI_normal.pm10_to_color(self.last_pm10)},
                                    "o3":   {"data": self.last_o3,    "color": AQI_normal.o3_to_color(self.last_o3)},
                                    "no2":  {"data": self.last_no2,   "color": AQI_normal.no2_to_color(self.last_no2)},
                                    "co":   {"data": self.last_co,    "color": AQI_normal.co_to_color(self.last_co)},
                                    "co2":  {"data": self.last_co2,   "color": AQI_normal.co2_to_color(self.last_co2)},
                                    "voc":  {"data": self.last_voc,   "color": AQI_normal.voc_to_color(self.last_voc)},
                                    "aqi":  {"data": self.last_aqi,   "color": AQI_normal.aqi_to_color(self.last_voc)},
                                    "temp": {"data": self.last_temp},
                                    "hum":  {"data": self.last_hum},
                                    "loc":  {"lat": self.last_lat, "lon": self.last_lon},
                                    "bat_l":{"data":self.last_bat_l}}
            print(self.data_plt[time_])
            to_return = True

        # upd sensor data
        self.last_pm2_5, self.last_pm10 =self.sensors.pms_get_pm()
        self.last_co2 = self.sensors.co2_data()
        self.temp, self.hum = self.sensors.temp_and_hum_data()
        self.last_o3  = self.sensors.o3_data()
        self.last_no2 = self.sensors.no2_data()
        self.last_co = self.sensors.co_data()
        self.last_voc = self.sensors.voc_data()
        self.last_bat_l = self.sensors.level_bat_data()
        self.lat, self.lon = self.sensors.gps_loc()
        self.last_aqi = aqi.to_aqi([
                (aqi.POLLUTANT_PM25, str(self.last_pm2_5)),
                (aqi.POLLUTANT_PM10, str(self.last_pm10)),
                (aqi.POLLUTANT_O3_1H, str(self.last_o3)),
                (aqi.POLLUTANT_CO_1H, str(self.last_co)),
                (aqi.POLLUTANT_NO2_1H, str(self.last_no2))
            ])

        return to_return

            



if __name__ == "__main__":
    "Start this file"
    print("start")
    d = To_display()
    d.upd_plot()
