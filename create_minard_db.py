import sqlite3
import pandas as pd

#整理程式碼為一個類別 & 載入欄位名稱
class CreateMinardDB:
    def __init__(self) :
        with open("data/minard.txt") as f:
            lines = f.readlines()
        column_names = lines[2].split()
        #調整欄位名稱
        patterns_to_be_replaced = {"(", ")", "$", ","}
        adjusted_column_names = []
        for column_name in column_names:
            for pattern in patterns_to_be_replaced:
                if pattern in column_name:
                    column_name = column_name.replace(pattern, "")
            adjusted_column_names.append(column_name)
        #建立屬性 & 將欄位名稱分成三部分
        self.lines = lines
        self.column_names_city = adjusted_column_names[:3]
        self.column_names_temperature = adjusted_column_names[3:7]
        self.column_names_troop = adjusted_column_names[7:]
#載入城市資料
#城市資料位於第 6 列至第 25 列、第 0 欄至第 2 欄。
#定義方法 以便傳入資料庫
    def create_city_dataframe(self):
        i = 6
        longitudes, latitudes, cities = [], [], []
        while i <= 25:
            long, lat, city = self.lines[i].split()[:3]
            longitudes.append(float(long))
            latitudes.append(float(lat))
            cities.append(city)
            i += 1
        city_data = (longitudes, latitudes, cities)
        city_df = pd.DataFrame()
        for column_name, data in zip(self.column_names_city, city_data):
            city_df[column_name] = data
        return city_df
    
#載入氣溫資料
#氣溫資料位於第 6 列至第 14 列、第 3 欄至第 7 欄。
#注意第 10 列資料的日期為遺漏值。
#定義方法 以便傳入資料庫
    def create_temperature_dataframe(self):
        i = 6
        longitudes, temperatures, days, dates = [], [], [], []
        while i <= 14:
            lines_split = self.lines[i].split()
            longitudes.append(float(lines_split[3]))
            temperatures.append(int(lines_split[4]))
            days.append(int(lines_split[5]))
            if i == 10:
                dates.append("Nov 24")
            else:
                date_str = lines_split[6] + " " + lines_split[7]
                dates.append(date_str)
            i += 1
        temperature_data = (longitudes, temperatures, days, dates)
        temperature_df = pd.DataFrame()
        for column_name, data in zip(self.column_names_temperature, temperature_data):
            temperature_df[column_name] = data
        return temperature_df

#載入軍隊資料
#軍隊資料位於第 6 列至第 53 列、倒數第 1 欄至倒數第 5 欄。
#因為資料欄位數可能不同，計算擷取的欄位從右側終點來數比從左側起點來數容易。
#定義方法 以便傳入資料庫
    def create_troop_dataframe(self):
        i = 6
        longitudes, latitudes, survivals, directions, divisions = [], [], [], [], []
        while i <= 53:
            lines_split = self.lines[i].split()
            divisions.append(int(lines_split[-1]))
            directions.append(lines_split[-2])
            survivals.append(int(lines_split[-3]))
            latitudes.append(float(lines_split[-4]))
            longitudes.append(float(lines_split[-5]))
            i += 1
        troop_data = (longitudes, latitudes, survivals, directions, divisions)
        troop_df = pd.DataFrame()
        for column_name, data in zip(self.column_names_troop, troop_data):
            troop_df[column_name] = data
        return troop_df
    
#定義方法 以便傳入資料庫
    def create_datebase(self):
        connection = sqlite3.connect("data/minard.db")
        city_df = self.create_city_dataframe()
        temperature_df = self.create_temperature_dataframe()
        troop_df = self.create_troop_dataframe()
        df_dict = {
            "cities": city_df,
            "temperatures": temperature_df,
            "troops": troop_df
        }
        for k, v in df_dict.items():
            v.to_sql(name=k, con=connection, index=False, if_exists="replace")
#初始化&呼叫資料夾
create_minard_db = CreateMinardDB()
create_minard_db.create_datebase()