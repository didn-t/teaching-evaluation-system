import requests
import base64
import time
import os
from bs4 import BeautifulSoup
import json
import re

"""
# spider = JWXTSpider()
# spider.crawl(
#     current_semester="",
#     username="",
#     password="",
#     API_KEY="",
#     SECRET_KEY=""
# )
"""
class JWXTSpider:

    def __init__(self):
        # -------------------- 用户配置 --------------------
        self.TOKEN_FILE = "baidu_token.txt"

        # -------------------- 会话 & 请求头 --------------------
        self.session = requests.Session()

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        # -------------------- 课程表解析工具 --------------------
        self.section_map = {
            "0102": "第一大节",
            "0304": "第二大节",
            "0506": "第三大节",
            "0708": "第四大节",
            "0910": "第五大节",
            "1112": "第六大节"
        }
        self.college_map = {
            "商学院": [
                "工商", "电商", "旅游", "国贸", "财管", "会计",
                "金融科技", "跨境电商", "数字经济"
            ],
            "土木与工程学院": [
                "造价", "地信", "建筑", "土木（工民建）",
                "土木（交通土建）", "土木（岩土工程）",
                "智造", "遥感"
            ],
            "艺术与传媒学院": [
                "广告", "视传", "环境", "艺术", "编导",
                "播音", "数媒", "表演", "摄影", "艺术与科技"
            ],
            "信息工程学院": [
                "计算机", "电信", "通信", "网络", "电气"
            ],
            "文理学院": [
                "英语", "商英", "体育", "汉语言",
                "学前", "心理学", "体教"
            ],
            "马克思主义学院": [
                "马克思主义"
            ],
            "大数据与人工智能学院": [
                "网媒", "人工智能", "大数据技术", "机器人工程"
            ]
        }
        # -------------------- 专业简称 → 专业全称 --------------------
        self.major_map = {
            "工商": "工商管理",
            "电商": "电子商务",
            "旅游": "旅游管理",
            "国贸": "国家经济与贸易",
            "金融科技": "金融科技",
            "跨境电商": "跨境电子商务",
            "数字经济": "数字经济",

            "造价": "工程造价",
            "地信": "地理信息科学",
            "土木（工民建）": "土木工程（工民建）",
            "土木（交通土建）": "土木工程（交通土建）",
            "土木（岩土工程）": "土木工程（岩土工程）",
            "智造": "智能建造",
            "遥感": "遥感科学与技术",

            "广告": "广告学",
            "视传": "视觉传达设计",
            "环境": "环境设计",
            "艺术": "艺术设计学",
            "编导": "广播电视编导",
            "播音": "播音与主持艺术",
            "数媒": "数字媒体艺术",
            "摄影": "摄影",
            "艺术与科技": "艺术与科技",

            "计算机": "计算机科学与技术",
            "电信": "电子信息工程",
            "通信": "通信工程",
            "电气": "电气工程及其自动化",

            "英语": "英语",
            "商英": "商务英语",
            "体育": "社会体育指导与管理",
            "汉语言": "汉语言文学",
            "学前": "学前教育",
            "心理学": "应用心理学",
            "体教": "体育教育",

            "网媒": "网络与新媒体",
            "人工智能": "人工智能",
            "大数据技术": "数据科学与大数据技术",
            "机器人工程": "机器人工程"
        }

    def identify_grade(self, text):
        """
        """
        # 1️⃣ 先找完整 4 位年级
        match_4 = re.search(r"(20\d{2})", text)
        if match_4:
            return match_4.group(1)

        # 2️⃣ 再从开头取前 2 位作为年级
        match_2 = re.match(r"(\d{2})", text)
        if match_2:
            return "20" + match_2.group(1)

        return "未知年级"

    def identify_major(self, text):
        """
        从班级名中识别专业并转换为专业全称
        """
        for short, full in self.major_map.items():
            if short in text:
                return full
        return "未知专业"

    def identify_college(self, text):
        """
        根据 班级名 / 专业名 / 课程相关文本 识别学院
        """
        for college, majors in self.college_map.items():
            for m in majors:
                if m in text:
                    return college
        return "未知学院"

    def expand_weeks(self, week_str):
        weeks = []
        parts = week_str.split(",")
        for part in parts:
            if "-" in part:
                start, end = part.split("-")
                weeks.extend([str(i) for i in range(int(start), int(end) + 1)])
            else:
                weeks.append(part)
        return ",".join(weeks)

    def parse_course_info(self, text):
        lines = text.split("\n")
        course_name = lines[0].strip() if len(lines) > 0 else ""
        teacher = lines[1].strip() if len(lines) > 1 else ""
        classes_line = lines[2].strip() if len(lines) > 2 else ""
        classroom = lines[3].strip() if len(lines) > 3 else ""

        classes_match = re.match(r"([^\s\(]+)", classes_line)
        classes = classes_match.group(1) if classes_match else ""

        week_match = re.search(r"\(([\d\-,]+)周\)", classes_line)
        week_info = self.expand_weeks(week_match.group(1)) if week_match else ""

        section_match = re.search(r"\(([\d\-]+)节\)", classes_line)
        section_time = section_match.group(1) if section_match else ""

        return {
            "course": course_name,
            "teacher": teacher,
            "class_code": classes,
            "week_info": week_info,
            "section_time": section_time,
            "classroom": classroom
        }

    def get_encryption_params(self):
        try:
            response = self.session.get(
                "http://qzjw.bwgl.cn/gllgdxbwglxy/Logon.do?method=logon&flag=sess",
                headers=self.headers
            )
            dataStr = response.text
            scode, sxh = dataStr.split("#")
            return scode, sxh
        except Exception as e:
            print("获取加密参数失败:", str(e))
            return None, None

    def encode_credentials(self, username, password, scode, sxh):
        code = f"{username}%%%{password}"
        encoded = ""
        for i in range(min(20, len(code))):
            encoded += code[i] + scode[:int(sxh[i])]
            scode = scode[int(sxh[i]):]
        if len(code) > 20:
            encoded += code[20:]
        return encoded

    def get_access_token(self, API_KEY, SECRET_KEY):
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, "r") as f:
                token = f.read().strip()
                if token:
                    return token

        token_url = (
            "https://aip.baidubce.com/oauth/2.0/token"
            f"?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}"
        )
        try:
            token_res = requests.get(token_url).json()
            access_token = token_res.get("access_token")
            if access_token:
                with open(self.TOKEN_FILE, "w") as f:
                    f.write(access_token)
                return access_token
            else:
                print("获取 access_token 失败:", token_res)
                return None
        except Exception as e:
            print("获取 access_token 异常:", e)
            return None

    def get_captcha_cloud(self, image_bytes, API_KEY, SECRET_KEY, retries=5):
        access_token = self.get_access_token(API_KEY, SECRET_KEY)
        if not access_token:
            return None

        for attempt in range(1, retries + 1):
            try:
                img_base64 = base64.b64encode(image_bytes).decode()
                ocr_url = (
                    "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
                    f"?access_token={access_token}"
                )
                headers_ocr = {"Content-Type": "application/x-www-form-urlencoded"}
                data = {"image": img_base64}

                resp = requests.post(ocr_url, data=data, headers=headers_ocr, timeout=10)
                result = resp.json()

                words_result = result.get("words_result", [])
                if not words_result:
                    time.sleep(1)
                    continue

                captcha_text = "".join(w["words"] for w in words_result)
                captcha_text = re.sub(r"[^A-Za-z0-9]", "", captcha_text)

                if len(captcha_text) == 4:
                    return captcha_text

            except Exception:
                time.sleep(1)

        return None

    def get_captcha(self, API_KEY, SECRET_KEY):
        try:
            response = self.session.get(
                "http://qzjw.bwgl.cn/gllgdxbwglxy/verifycode.servlet",
                headers=self.headers
            )
            if response.status_code == 200:
                return self.get_captcha_cloud(response.content, API_KEY, SECRET_KEY)
            else:
                return None
        except Exception:
            return None

    def login(self, encoded, captcha_text):
        login_data = {
            "method": "logon",
            "view": "0",
            "useDogCode": "",
            "encoded": encoded,
            "RANDOMCODE": captcha_text
        }
        try:
            self.session.post(
                "http://qzjw.bwgl.cn/gllgdxbwglxy/Logon.do",
                data=login_data,
                headers=self.headers,
                allow_redirects=True
            )
            return True
        except Exception:
            return False

    def fetch_full_timetable(self, current_semester):
        table_url = "http://qzjw.bwgl.cn/gllgdxbwglxy/zcbqueryAction.do?method=goQueryZKbByXzbj"
        post_data = {
            "lb": "queryzkb.jsp",
            "xnxqh": current_semester,
            "xq": "",
            "kkyx": "",
            "skyx": "",
            "sknj": "",
            "skzy": "",
            "zc1": "",
            "zc2": "",
            "jc1": "",
            "jc2": "",
            "kc": ""
        }
        try:
            resp = self.session.post(table_url, data=post_data, headers=self.headers, timeout=20)
            resp.encoding = "utf-8"
            time.sleep(2)
            if "<table" in resp.text and len(resp.text) > 5000:
                with open(f"{current_semester}.html", "w", encoding="utf-8") as f:
                    f.write(resp.text)
                return True
            else:
                return False
        except Exception:
            return False

    def parse_timetable_html(self, current_semester):
        with open(f"{current_semester}.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table", {"id": "kbtable"})
        if not table:
            return False

        header_rows = table.find_all("tr")[:2]
        days = []
        for td in header_rows[0].find_all("td")[1:]:
            colspan = int(td.get("colspan", 1))
            days.extend([td.get_text(strip=True)] * colspan)

        sections = [td.get_text(strip=True) for td in header_rows[1].find_all("td")[1:]]

        data = []
        for row in table.find_all("tr")[2:]:
            cells = row.find_all("td")
            class_name = cells[0].get_text(strip=True)
            for i, cell in enumerate(cells[1:]):
                content = cell.get_text(separator="\n", strip=True)
                if content:
                    course_info = self.parse_course_info(content)
                    data.append({
                        "班级": class_name,
                        "学院": self.identify_college(class_name),
                        "专业": self.identify_major(class_name),
                        "年级": self.identify_grade(class_name),
                        "星期": days[i],
                        "节次": self.section_map.get(sections[i], sections[i]),
                        **course_info
                    })

        with open(f"{current_semester}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return True

    # -------------------- 主流程 --------------------
    def crawl(self, current_semester, username, password, API_KEY, SECRET_KEY):
        scode, sxh = self.get_encryption_params()
        if not scode:
            return False

        encoded = self.encode_credentials(username, password, scode, sxh)
        captcha_text = self.get_captcha(API_KEY, SECRET_KEY)
        if not captcha_text:
            return False

        if not self.login(encoded, captcha_text):
            return False

        if not self.fetch_full_timetable(current_semester):
            return False

        if not self.parse_timetable_html(current_semester):
            return False

        return True




