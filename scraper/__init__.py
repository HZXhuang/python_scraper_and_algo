import os

base_path = os.path.dirname(os.path.abspath(__file__))

nameMap = {
    "Afghanistan": "阿富汗",
    "Åland Islands": "奥兰",
    "Albania": "阿尔巴尼亚",
    "Algeria": "阿尔及利亚",
    "American Samoa": "美属萨摩亚",
    "Andorra": "安道尔",
    "Angola": "安哥拉",
    "Anguilla": "安圭拉",
    "Antarctica": "南极洲",
    "Antigua and Barbuda": "安地卡及巴布达",
    "Argentina": "阿根廷",
    "Armenia": "亚美尼亚",
    "Aruba": "阿鲁巴",
    "Australia": "澳大利亚",
    "Austria": "奥地利",
    "Azerbaijan": "阿塞拜疆",
    "Bahamas": "巴哈马",
    "Bahrain": "巴林",
    "Bangladesh": "孟加拉国",
    "Barbados": "巴巴多斯",
    "Belarus": "白俄罗斯",
    "Belgium": "比利时",
    "Belize": "伯利兹",
    "Benin": "贝宁",
    "Bermuda": "百慕大",
    "Bhutan": "不丹",
    "Bolivia, Plurinational State of": "玻利维亚",
    "Bonaire, Sint Eustatius and Saba": "荷兰加勒比区",
    "Bosnia and Herzegovina": "波黑",
    "Botswana": "博茨瓦纳",
    "Bouvet Island": "布韦岛",
    "Brazil": "巴西",
    "British Indian Ocean Territory": "英属印度洋领地",
    "Brunei Darussalam": "文莱",
    "Bulgaria": "保加利亚",
    "Burkina Faso": "布吉纳法索",
    "Burundi": "布隆迪",
    "Cabo Verde": "佛得角",
    "Cambodia": "柬埔寨",
    "Cameroon": "喀麦隆",
    "Canada": "加拿大",
    "Cayman Islands": "开曼群岛",
    "Central African Republic": "中非",
    "Chad": "乍得",
    "Chile": "智利",
    "China": "中国",
    "Christmas Island": "圣诞岛",
    "Cocos (Keeling) Islands": "科科斯（基林）群岛",
    "Colombia": "哥伦比亚",
    "Comoros": "科摩罗",
    "Congo": "刚果共和国",
    "Congo, The Democratic Republic of the": "刚果民主共和国",
    "Cook Islands": "库克群岛",
    "Costa Rica": "哥斯达黎加",
    "Côte d'Ivoire": "科特迪瓦",
    "Croatia": "克罗地亚",
    "Cuba": "古巴",
    "Curaçao": "库拉索",
    "Cyprus": "赛普勒斯",
    "Czechia": "捷克",
    "Denmark": "丹麦",
    "Djibouti": "吉布提",
    "Dominica": "多米尼克",
    "Dominican Republic": "多米尼加",
    "Ecuador": "厄瓜多尔",
    "Egypt": "埃及",
    "El Salvador": "萨尔瓦多",
    "Equatorial Guinea": "赤道几内亚",
    "Eritrea": "厄立特里亚",
    "Estonia": "爱沙尼亚",
    "Eswatini": "斯威士兰",
    "Ethiopia": "衣索比亚",
    "Falkland Islands (Malvinas)": "福克兰群岛",
    "Faroe Islands": "法罗群岛",
    "Fiji": "斐济",
    "Finland": "芬兰",
    "France": "法国",
    "French Guiana": "法属圭亚那",
    "French Polynesia": "法属玻里尼西亚",
    "French Southern Territories": "法属南部和南极领地",
    "Gabon": "加彭",
    "Gambia": "冈比亚",
    "Georgia": "格鲁吉亚",
    "Germany": "德国",
    "Ghana": "加纳",
    "Gibraltar": "直布罗陀",
    "Greece": "希腊",
    "Greenland": "格陵兰",
    "Grenada": "格瑞那达",
    "Guadeloupe": "瓜德罗普",
    "Guam": "关岛",
    "Guatemala": "危地马拉",
    "Guernsey": "根西",
    "Guinea": "几内亚",
    "Guinea-Bissau": "几内亚比绍",
    "Guyana": "圭亚那",
    "Haiti": "海地",
    "Heard Island and McDonald Islands": "赫德岛和麦克唐纳群岛",
    "Holy See (Vatican City State)": "梵蒂冈",
    "Honduras": "洪都拉斯",
    "Hong Kong": "中国香港",
    "Hungary": "匈牙利",
    "Iceland": "冰岛",
    "India": "印度",
    "Indonesia": "印度尼西亚",
    "Iran, Islamic Republic of": "伊朗",
    "Iraq": "伊拉克",
    "Ireland": "爱尔兰",
    "Isle of Man": "马恩岛",
    "Israel": "以色列",
    "Italy": "意大利",
    "Jamaica": "牙买加",
    "Japan": "日本",
    "Jersey": "泽西",
    "Jordan": "约旦",
    "Kazakhstan": "哈萨克斯坦",
    "Kenya": "肯尼亚",
    "Kiribati": "基里巴斯",
    "Korea, Democratic People's Republic of": "朝鲜",
    "Korea, Republic of": "韩国",
    "Kuwait": "科威特",
    "Kyrgyzstan": "吉尔吉斯斯坦",
    "Lao People's Democratic Republic": "老挝",
    "Latvia": "拉脱维亚",
    "Lebanon": "黎巴嫩",
    "Lesotho": "赖索托",
    "Liberia": "利比里亚",
    "Libya": "利比亚",
    "Liechtenstein": "列支敦斯登",
    "Lithuania": "立陶宛",
    "Luxembourg": "卢森堡",
    "Macao": "中国澳门",
    "Madagascar": "马达加斯加",
    "Malawi": "马拉维",
    "Malaysia": "马来西亚",
    "Maldives": "马尔地夫",
    "Mali": "马里",
    "Malta": "马耳他",
    "Marshall Islands": "马绍尔群岛",
    "Martinique": "马提尼克",
    "Mauritania": "毛里塔尼亚",
    "Mauritius": "模里西斯",
    "Mayotte": "马约特",
    "Mexico": "墨西哥",
    "Micronesia, Federated States of": "密克罗尼西亚联邦",
    "Moldova, Republic of": "摩尔多瓦",
    "Monaco": "摩纳哥",
    "Mongolia": "蒙古",
    "Montenegro": "蒙特内哥罗",
    "Montserrat": "蒙特塞拉特",
    "Morocco": "摩洛哥",
    "Mozambique": "莫桑比克",
    "Myanmar": "缅甸",
    "Namibia": "纳米比亚",
    "Nauru": "瑙鲁",
    "Nepal": "尼泊尔",
    "Netherlands": "荷兰",
    "New Caledonia": "新喀里多尼亚",
    "New Zealand": "新西兰",
    "Nicaragua": "尼加拉瓜",
    "Niger": "尼日尔",
    "Nigeria": "奈及利亚",
    "Niue": "纽埃",
    "Norfolk Island": "诺福克岛",
    "North Macedonia": "北马其顿",
    "Northern Mariana Islands": "北马里亚纳群岛",
    "Norway": "挪威",
    "Oman": "阿曼",
    "Pakistan": "巴基斯坦",
    "Palau": "帛琉",
    "Palestine, State of": "巴勒斯坦",
    "Panama": "巴拿马",
    "Papua New Guinea": "巴布亚新几内亚",
    "Paraguay": "巴拉圭",
    "Peru": "秘鲁",
    "Philippines": "菲律宾",
    "Pitcairn": "皮特凯恩群岛",
    "Poland": "波兰",
    "Portugal": "葡萄牙",
    "Puerto Rico": "波多黎各",
    "Qatar": "卡塔尔",
    "Réunion": "留尼汪",
    "Romania": "罗马尼亚",
    "Russian Federation": "俄罗斯",
    "Rwanda": "卢旺达",
    "Saint Barthélemy": "圣巴泰勒米",
    "Saint Helena, Ascension and Tristan da Cunha": "圣赫勒拿、阿森松和特里斯坦-达库尼亚",
    "Saint Kitts and Nevis": "圣基茨和尼维斯",
    "Saint Lucia": "圣卢西亚",
    "Saint Martin (French part)": "法属圣马丁",
    "Saint Pierre and Miquelon": "圣皮埃尔和密克隆",
    "Saint Vincent and the Grenadines": "圣文森特和格林纳丁斯",
    "Samoa": "萨摩亚",
    "San Marino": "圣马力诺",
    "Sao Tome and Principe": "圣多美和普林西比",
    "Saudi Arabia": "沙乌地阿拉伯",
    "Senegal": "塞内加尔",
    "Serbia": "塞尔维亚",
    "Seychelles": "塞舌尔",
    "Sierra Leone": "塞拉利昂",
    "Singapore": "新加坡",
    "Sint Maarten (Dutch part)": "荷属圣马丁",
    "Slovakia": "斯洛伐克",
    "Slovenia": "斯洛维尼亚",
    "Solomon Islands": "所罗门群岛",
    "Somalia": "索马里",
    "South Africa": "南非",
    "South Georgia and the South Sandwich Islands": "南乔治亚和南桑威奇群岛",
    "South Sudan": "南苏丹",
    "Spain": "西班牙",
    "Sri Lanka": "斯里兰卡",
    "Sudan": "苏丹",
    "Suriname": "苏里南",
    "Svalbard and Jan Mayen": "斯瓦尔巴和扬马延",
    "Sweden": "瑞典",
    "Switzerland": "瑞士",
    "Syrian Arab Republic": "叙利亚",
    "Taiwan, Province of China": "中华民国中国台湾省",
    "Tajikistan": "塔吉克斯坦",
    "Tanzania, United Republic of": "坦桑尼亚",
    "Thailand": "泰国",
    "Timor-Leste": "东帝汶",
    "Togo": "多哥",
    "Tokelau": "托克劳",
    "Tonga": "汤加",
    "Trinidad and Tobago": "千里达及托巴哥",
    "Tunisia": "突尼西亚",
    "Turkey": "土耳其",
    "Turkmenistan": "土库曼斯坦",
    "Turks and Caicos Islands": "特克斯和凯科斯群岛",
    "Tuvalu": "图瓦卢",
    "Uganda": "乌干达",
    "Ukraine": "乌克兰",
    "United Arab Emirates": "阿联酋",
    "United Kingdom": "英国",
    "United States": "美国",
    "United States Minor Outlying Islands": "美国本土外小岛屿",
    "Uruguay": "乌拉圭",
    "Uzbekistan": "乌兹别克斯坦",
    "Vanuatu": "瓦努阿图",
    "Venezuela, Bolivarian Republic of": "委内瑞拉",
    "Viet Nam": "越南",
    "Virgin Islands, British": "英属维尔京群岛",
    "Virgin Islands, U.S.": "美属维尔京群岛",
    "Wallis and Futuna": "瓦利斯和富图纳",
    "Western Sahara": "西撒哈拉",
    "Yemen": "叶门",
    "Zambia": "尚比亚",
    "Zimbabwe": "辛巴威",
}

code_country_map = {
    "af": "南非",
    "am": "埃塞俄比亚",
    "an": "西班牙",
    "ar": "坦桑尼亚",
    "as": "印度",
    "az": "阿塞拜疆",
    "be": "白俄罗斯",
    "bg": "保加利亚",
    "bn": "印度",
    "br": "法国",
    "bs": "波斯尼亚",
    "ca": "西班牙",
    "cs": "捷克",
    "cy": "威尔士",
    "da": "丹麦",
    "de": ["德国", "奥地利", "瑞士", "比利时", "意大利", "卢森堡"],
    "dz": "不丹",
    "el": "希腊",
    "en": ["英国", "美国", "加拿大", "澳大利亚", "新西兰", "牙买加", "新加坡", "马来西亚", "爱尔兰"],
    "eo": "中国",
    "es": "西班牙",
    "et": "爱沙尼亚",
    "eu": "西班牙",
    "fa": ["伊朗", "塔吉克斯坦", "阿富汗"],
    "fi": "芬兰",
    "fo": "法罗群岛",
    "fr": "法国",
    "ga": "爱尔兰",
    "gl": "西班牙",
    "gu": ["印度", "巴基斯坦", "肯尼亚"],
    "he": "以色列",
    "hi": "印度",
    "hr": "克罗地亚",
    "ht": ["加拿大", "美国", "法国", "古巴", "巴哈马"],
    "hu": "匈牙利",
    "hy": "亚美尼亚",
    "id": "印度尼西亚",
    "is": "冰岛",
    "it": ["意大利", "瑞士"],
    "ja": "日本",
    "jv": "印度尼西亚",
    "ka": "格鲁吉亚",
    "kk": "哈萨克斯坦",
    "km": "柬埔寨",
    "kn": "卡纳塔克邦",
    "ko": ["朝鲜", "韩国"],
    "ku": ["伊朗", "伊拉克", "叙利亚", "土耳其"],
    "ky": "吉尔吉斯斯坦",
    "la": ["美国", "中国"],
    "lb": "卢森堡",
    "lo": "老挝",
    "lt": "立陶宛",
    "lv": "拉脱维亚",
    "mg": "马达加斯加",
    "mk": "北马其顿",
    "ml": "印度",
    "mn": "蒙古",
    "mr": "印度",
    "ms": ["马来西亚", "文莱", "新加坡"],
    "mt": "马耳他",
    "nb": "挪威",
    "ne": "尼泊尔",
    "nl": "荷兰",
    "nn": "挪威",
    "no": "挪威",
    "oc": "法国",
    "or": "印度",
    "pa": ["印度", "巴基斯坦"],
    "pl": "波兰",
    "ps": "阿富汗",
    "pt": "葡萄牙",
    "qu": "未知国家",
    "ro": "罗马尼亚",
    "ru": "俄罗斯",
    "rw": "卢旺达",
    "se": ["挪威", "瑞典", "芬兰"],
    "si": "斯里兰卡",
    "sk": "斯洛伐克",
    "sl": "斯洛维尼亚",
    "sq": "阿尔巴尼亚",
    "sr": "塞尔维亚",
    "sv": "瑞典",
    "sw": ["坦桑尼亚", "肯尼亚", "乌干达", "刚果民主共和国"],
    "ta": "印度",
    "te": "印度",
    "th": "泰国",
    "tl": "菲律宾",
    "tr": "土耳其",
    "ug": "中国",
    "uk": "乌克兰",
    "ur": "巴基斯坦",
    "vi": "越南",
    "vo": "未知国家",
    "wa": "未知国家",
    "xh": "南非",
    "zh": "中国",
    "zu": "南非"
}
