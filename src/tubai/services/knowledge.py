"""目的地游玩知识库（离线兜底 + 行程线索）。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DestinationInfo:
    city: str
    style: str
    spots: list[str] = field(default_factory=list)
    foods: list[str] = field(default_factory=list)
    transport: str = ""
    reservation: str = ""
    risks: list[str] = field(default_factory=list)
    anti_pitfalls: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    tags: set[str] = field(default_factory=set)


DESTINATIONS: list[DestinationInfo] = [
    DestinationInfo(
        city="北京",
        style="人文古迹",
        spots=[
            "故宫博物院",
            "天坛公园",
            "颐和园",
            "八达岭长城",
            "南锣鼓巷",
            "国家博物馆",
        ],
        foods=["北京烤鸭", "炸酱面", "卤煮", "豆汁儿", "涮羊肉"],
        transport="地铁覆盖广，景点多可地铁直达；长城建议市郊铁路或包车",
        reservation="故宫需提前 7 天实名预约；国博需预约",
        risks=["节假日故宫/长城人流极大", "冬季干冷注意保湿防晒"],
        anti_pitfalls=[
            "避开王府井高价“老北京”餐馆，去本地人常去的连锁",
            "长城黑车勿信，走官方摆渡",
        ],
        alternatives=["故宫约不上可去恭王府/孔庙国子监", "八达岭人多可考虑慕田峪"],
        tags={"人文"},
    ),
    DestinationInfo(
        city="成都",
        style="城市逛吃",
        spots=["宽窄巷子", "锦里", "武侯祠", "大熊猫繁育研究基地", "青城山", "都江堰"],
        foods=["火锅", "串串香", "担担面", "钟水饺", "兔头"],
        transport="地铁+打车为主，青城山可高铁",
        reservation="熊猫基地建议早班入园；青城山需购票",
        risks=["夏季闷热潮湿", "火锅辛辣肠胃敏感者慎点"],
        anti_pitfalls=[
            "景区“免费拍照”多为收费套路",
            "宽窄巷子小吃性价比一般，建议去建设路",
        ],
        alternatives=["锦里人多可去东郊记忆/铁像寺水街"],
        tags={"美食"},
    ),
    DestinationInfo(
        city="三亚",
        style="海岛休闲",
        spots=[
            "亚龙湾",
            "天涯海角",
            "蜈支洲岛",
            "南山文化旅游区",
            "后海村",
            "呀诺达雨林",
        ],
        foods=["海鲜", "椰子鸡", "清补凉", "抱罗粉"],
        transport="打车/租车自驾为主，景点分散",
        reservation="蜈支洲岛需提前购票，风浪大可能停航",
        risks=["夏秋台风季关注船班", "紫外线极强易晒伤", "海鲜过敏/肠胃风险"],
        anti_pitfalls=["海鲜加工店选明码标价、看评分", "景区拍照/潜水二次消费提前问清"],
        alternatives=["蜈支洲岛风浪大可改分界洲岛或亚龙湾海底世界"],
        tags={"海岛", "亲子"},
    ),
    DestinationInfo(
        city="丽江",
        style="自然风光徒步",
        spots=["丽江古城", "玉龙雪山", "蓝月谷", "束河古镇", "拉市海", "虎跳峡"],
        foods=["腊排骨火锅", "鸡豆凉粉", "丽江粑粑", "三文鱼（虹鳟）"],
        transport="古城内步行，玉龙雪山建议包车/跟团",
        reservation="玉龙雪山大索道需提前抢票；蓝月谷含在雪山票内",
        risks=["高海拔可能高原反应", "昼夜温差大", "紫外线强"],
        anti_pitfalls=[
            "古城“艳遇酒托”警惕",
            "拉市海马场选正规渠道，避免低价团强制消费",
        ],
        alternatives=["玉龙雪山票紧张可去文海/白沙古镇"],
        tags={"高原", "徒步"},
    ),
    DestinationInfo(
        city="拉萨",
        style="人文古迹",
        spots=["布达拉宫", "大昭寺", "八廓街", "色拉寺", "纳木错", "药王山观景台"],
        foods=["甜茶", "藏面", "牦牛肉", "酥油茶", "藏式火锅"],
        transport="市内打车/公交，纳木错需包车",
        reservation="布达拉宫需提前预约，旺季一票难求",
        risks=["高反风险高，首日勿剧烈运动", "紫外线强，防晒必备", "昼夜温差 15°C+"],
        anti_pitfalls=[
            "八廓街购物认准正规店铺",
            "低价“高反神药”勿信，红景天提前服用更稳",
        ],
        alternatives=["布达拉宫约不上可去宗角禄康公园外观+药王山拍照"],
        tags={"高原", "人文"},
    ),
    DestinationInfo(
        city="杭州",
        style="城市逛吃",
        spots=["西湖", "灵隐寺", "西溪湿地", "河坊街", "宋城", "良渚古城遗址"],
        foods=["西湖醋鱼", "东坡肉", "片儿川", "龙井虾仁", "葱包桧"],
        transport="地铁+公交+共享单车环湖最佳",
        reservation="灵隐寺需预约；节假日西湖单双号限行",
        risks=["梅雨季闷热多雨", "暑期西湖断桥人流爆炸"],
        anti_pitfalls=["西湖边“现泡龙井”多为外地茶", "河坊街小吃偏贵"],
        alternatives=["断桥人多可走杨公堤/茅家埠"],
        tags={"人文", "亲子"},
    ),
    DestinationInfo(
        city="厦门",
        style="城市逛吃",
        spots=["鼓浪屿", "南普陀寺", "厦门大学", "曾厝垵", "环岛路", "植物园"],
        foods=["沙茶面", "海蛎煎", "土笋冻", "姜母鸭", "花生汤"],
        transport="地铁+公交+轮渡上岛",
        reservation="鼓浪屿船票需提前预约；厦大需预约",
        risks=["旺季船票紧张", "台风季船班可能取消"],
        anti_pitfalls=["鼓浪屿上“现开珍珠”多假货", "曾厝垵伴手礼溢价严重"],
        alternatives=["鼓浪屿约不上可去集美学村/园博苑"],
        tags={"海岛", "美食"},
    ),
    DestinationInfo(
        city="西安",
        style="人文古迹",
        spots=[
            "秦始皇兵马俑",
            "西安城墙",
            "大雁塔",
            "陕西历史博物馆",
            "回民街",
            "华清宫",
        ],
        foods=["肉夹馍", "羊肉泡馍", "biangbiang面", "凉皮", "甑糕"],
        transport="地铁可达市区景点，兵马俑坐游 5 路/直通车",
        reservation="陕历博必须预约；兵马俑建议提前购票",
        risks=["夏季暴晒", "节假日城墙/兵马俑人流大"],
        anti_pitfalls=[
            "回民街主街偏游客价，洒金桥更地道",
            "兵马俑“黑导游”勿信，认准官方讲解",
        ],
        alternatives=["陕历博约不上可去西安博物院/碑林"],
        tags={"人文"},
    ),
    DestinationInfo(
        city="桂林",
        style="自然风光徒步",
        spots=["漓江竹筏", "阳朔西街", "遇龙河", "龙脊梯田", "象鼻山", "十里画廊"],
        foods=["桂林米粉", "啤酒鱼", "荔浦芋扣肉", "油茶"],
        transport="桂林-阳朔动车/船，阳朔租电瓶车",
        reservation="漓江竹筏/船票需提前订；龙脊梯田节假日限流",
        risks=["雨季漓江水位影响筏运", "夏季暴晒多蚊虫"],
        anti_pitfalls=["西街“特产”比价再买", "竹筏小费/拍照收费提前谈清"],
        alternatives=["漓江停航可去遇龙河骑行"],
        tags={"徒步", "亲子"},
    ),
    DestinationInfo(
        city="青岛",
        style="海岛休闲",
        spots=["栈桥", "八大关", "崂山", "啤酒博物馆", "金沙滩", "小鱼山"],
        foods=["辣炒蛤蜊", "鲅鱼水饺", "青岛啤酒+烧烤", "海菜凉粉"],
        transport="地铁+公交，崂山建议包车/跟团",
        reservation="崂山需购票；啤酒博物馆可现场买",
        risks=["海边风大早晚凉", "啤酒节人多价高"],
        anti_pitfalls=["海鲜大排档看标价，避开“论只卖”", "栈桥快照收费先问清"],
        alternatives=["金沙滩远可去第一/第二海水浴场"],
        tags={"海岛"},
    ),
    DestinationInfo(
        city="昆明",
        style="自然风光徒步",
        spots=["石林", "滇池", "翠湖", "云南民族村", "西山龙门", "斗南花市"],
        foods=["过桥米线", "汽锅鸡", "鲜花饼", "野生菌火锅", "烧饵块"],
        transport="地铁+打车，石林高铁 20 分钟",
        reservation="石林建议提前购票；野生菌火锅旺季排队",
        risks=["紫外线强", "雨季路滑", "野生菌务必煮熟"],
        anti_pitfalls=["景区银饰/玉石谨慎购买", "低价一日游隐性购物点多"],
        alternatives=["石林人多可去九乡溶洞"],
        tags={"高原", "亲子"},
    ),
    DestinationInfo(
        city="上海",
        style="城市逛吃",
        spots=["外滩", "豫园", "迪士尼乐园", "武康路", "上海博物馆", "朱家角古镇"],
        foods=["生煎", "小笼包", "本帮红烧肉", "葱油拌面", "排骨年糕"],
        transport="地铁极方便，去迪士尼有专线",
        reservation="迪士尼需购票并预约；上博需预约",
        risks=["梅雨季闷热", "节假日外滩人流量管控"],
        anti_pitfalls=["南京路伴手礼溢价", "外滩“观光隧道”性价比低"],
        alternatives=["迪士尼人多可去海昌海洋公园"],
        tags={"美食", "亲子"},
    ),
]


def find_destination(query: str) -> DestinationInfo | None:
    for d in DESTINATIONS:
        if d.city in query or query in d.city:
            return d
    for d in DESTINATIONS:
        for tag in d.tags:
            if tag in query:
                return d
    return None


def get_destination(query: str, style: str = "") -> DestinationInfo:
    found = find_destination(query)
    if found:
        return found
    # 通用兜底模板
    return DestinationInfo(
        city=query,
        style=style or "综合",
        spots=["当地核心景区", "老城步行街", "博物馆/纪念馆", "城市公园/观景台"],
        foods=["本地特色菜", "夜市小吃", "老字号早餐"],
        transport="市内地铁/公交为主，远景点建议打车或包车",
        reservation="热门景点建议提前 3-7 天预约",
        risks=["旺季人流较大", "关注天气变化"],
        anti_pitfalls=["景区周边餐饮先看评价与标价", "警惕低价强制购物团"],
        alternatives=["主景区人多可改周边小众目的地"],
    )
