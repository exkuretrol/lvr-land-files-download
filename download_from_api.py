import base64
import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from typing import List, Literal, Optional

from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger("rich")

import requests


@dataclass
class QuerySchema:
    ptype: List[int] = field(
        default_factory=lambda: [
            1,  # 房地(土地+建物)
            2,  # 房地(土地+建物)+車位
            # 3,  # 土地
            # 4,  # 建物
            # 5,  # 車位
        ]
    )
    starty: int = 113
    startm: int = 2
    endy: int = 113
    endm: int = 2
    qryType: Literal[
        "biz",  # 買賣
        "rent",  # 租賃
        "sale",  # 預售屋
        "saleRemark",  # 預售屋建案
    ] = "biz"
    city: Literal[
        "A",  #  台北市
        "B",  #  台中市
        "C",  #  基隆市
        "D",  #  台南市
        "E",  #  高雄市
        "F",  #  台北縣
        "G",  #  宜蘭縣
        "H",  #  桃園縣
        "I",  #  嘉義市
        "J",  #  新竹縣
        "K",  #  苗栗縣
        "L",  #  台中縣
        "M",  #  南投縣
        "N",  #  彰化縣
        "O",  #  新竹市
        "P",  #  雲林縣
        "Q",  #  嘉義縣
        "R",  #  台南縣
        "S",  #  高雄縣
        "T",  #  屏東縣
        "U",  #  花蓮縣
        "V",  #  台東縣
        "W",  #  金門縣
        "X",  #  澎湖縣
        "Y",  #  陽明山
        "Z",  #  連江縣
    ] = "A"
    town: str = "A01"  # if city is "A", town is "A01"
    p_build: Optional[str] = None  # 門牌 / 社區名稱
    ftype: Optional[str] = None  # 租賃類型篩選
    price_s: Optional[str] = None
    price_e: Optional[str] = None
    unit_price_s: Optional[str] = None
    unit_price_e: Optional[str] = None
    area_s: Optional[str] = None
    area_e: Optional[str] = None
    build_s: Optional[str] = None
    build_e: Optional[str] = None
    buildyear_s: Optional[str] = None
    buildyear_e: Optional[str] = None
    doorno: Optional[str] = None
    pattern: Optional[str] = None
    community: Optional[str] = None
    floor: Optional[str] = None
    rent_type: Optional[str] = None
    rent_order: Optional[str] = None
    urban: Optional[str] = None
    urbantext: Optional[str] = None
    nurban: Optional[str] = None
    aa12: Optional[str] = None
    p_purpose: Optional[str] = None
    p_unusualcode: Optional[str] = None
    tmoney_unit: Literal[
        "1",  # 萬元
        "2",  # 元
    ] = "1"
    pmoney_unit: Literal[
        "1",  # 萬元
        "2",  # 元
    ] = "1"
    unit: Literal[
        "1",  # 平方公尺
        "2",  # 坪
    ] = "2"
    token: str = ""  # get_token()

    @classmethod
    def from_json(self, json_str: str):
        d = json.loads(json_str)
        d["ptype"] = [int(i) for i in d["ptype"].split(",")]
        return QuerySchema(**d)

    def to_json(self) -> str:
        """
        Sample Input
        {
            "ptype": "1,2",
            "starty": "113",
            "startm": "2",
            "endy": "113",
            "endm": "2",
            "qryType": "biz",
            "city": "A",
            "town": "A01",
            "p_build": "",
            "ftype": "",
            "price_s": "",
            "price_e": "",
            "unit_price_s": "",
            "unit_price_e": "",
            "area_s": "",
            "area_e": "",
            "build_s": "",
            "build_e": "",
            "buildyear_s": "",
            "buildyear_e": "",
            "doorno": "",
            "pattern": "",
            "community": "",
            "floor": "",
            "rent_type": "",
            "rent_order": "",
            "urban": "",
            "urbantext": "",
            "nurban": "",
            "aa12": "",
            "p_purpose": "",
            "p_unusualcode": "",
            "tmoney_unit": "1",
            "pmoney_unit": "1",
            "unit": "2",
            "token": ""
        }
        """
        d = {}
        for k, v in self.__dict__.items():
            if v is None:
                d.update({k: ""})
            elif isinstance(v, int):
                d.update({k: str(v)})
            elif isinstance(v, list):
                d.update({k: ",".join([str(i) for i in v])})
            else:
                d.update({k: v})
        return json.dumps(d).replace(" ", "")


def aes_encrypt(data: str, key: str) -> str:
    import subprocess

    result = subprocess.run(["node", "aes.js", data, key], stdout=subprocess.PIPE)
    return result.stdout.decode().strip()


class API:
    def __init__(self, host: str = "lvr.land.moi.gov.tw"):
        self.query = QuerySchema()
        self._host = host
        self._end_point = "/SERVICE/QueryPrice"
        self.url = f"https://{self._host}{self._end_point}"

    def get_token(self) -> str:
        url = f"https://{self._host}/jsp/setToken.jsp"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["token"]

    def encrypt_query(self) -> str:
        self.query.token = self.get_token()
        log.debug(f"Query Dict: ")
        log.debug(asdict(self.query))
        query_str = self.query.to_json()

        # hash by MD5
        key1 = hashlib.md5(query_str.encode()).hexdigest()
        log.debug(f"MD5 hashed host: {key1}")

        # hash by AES, then encode by base64
        aes_encrypted_query = aes_encrypt(query_str, self._host)

        log.debug(f"AES encrypted text: {aes_encrypted_query}")
        log.debug(f"Length of AES encrypted text: {len(aes_encrypted_query)}")
        key2 = base64.b64encode(aes_encrypted_query.encode()).decode()
        log.debug(f"Base64 encoded encrypted text: {key2}")
        log.debug(f"Length of Base64 encoded encrypted text: {len(key2)}")
        return (key1, key2)

    def get_query_url(self):
        key1, key2 = self.encrypt_query()
        url = self.url + f"/{key1}?q=" + key2
        log.debug(f"Query URL: {url}")
        return url

    def get_data(self):
        response = requests.get(self.get_query_url())
        response.raise_for_status()
        return response.json()