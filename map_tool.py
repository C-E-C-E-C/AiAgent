import requests 

from config import AMAP_KEY


# 统一把请求文本做一次清洗，避免中文或特殊字符在接口参数里出问题。
def clean_text(text):
    return text.encode("utf-8", "ignore").decode("utf-8", "ignore")


class MapTool:
    def __init__(self):
        # 这里直接读取高德 Key，后续所有地图请求都复用它。
        self.key = AMAP_KEY
    
    def get_location(self,city,keywords):
        # 按城市 + 关键字搜索 POI，拿到景点、餐饮、酒店等位置数据。
        url = "https://restapi.amap.com/v3/place/text"
        paras = {
            "key" : self.key,
            "keywords" : clean_text(keywords),
            "city" : clean_text(city),
            "output" : "JSON"
        }
        res = requests.get(url,params=paras)
        return res.json()
    
    def get_route(self,origin,destination):
        # 步行路线查询，通常用于两个点位之间的导航或路线展示。
        url = "https://restapi.amap.com/v3/direction/walking"
        paras = {
            "key" : self.key,
            "origin" : clean_text(origin),
            "destination" : clean_text(destination),
        }
        res = requests.get(url,params=paras)
        return res.json()