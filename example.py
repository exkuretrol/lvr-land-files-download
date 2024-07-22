import json

from download_from_api import API, QuerySchema

api = API()

# load query from json, which localed in browser's local storage,
# you can get it by run `localStorage.getItem("form-data")` in browser's console
#
# NOTE: you need to filter with official website at first, then copy the json string to here.
api.query = QuerySchema.from_json(
    '{"qryType":"biz","city":"E","town":"E30","ptype":"1,2","starty":"113","startm":"2","endy":"113","endm":"2","p_build":"","ftype":"","price_s":"","price_e":"","unit_price_s":"","unit_price_e":"","area_s":"","area_e":"","build_s":"","build_e":"","buildyear_s":"","buildyear_e":"","doorno":"","pattern":"","community":"","floor":"","rent_type":"","rent_order":"","urban":"","urbantext":"","nurban":"","aa12":"","p_purpose":"","p_unusualcode":"","tmoney_unit":"1","pmoney_unit":"1","unit":"2","token":"XUV1605681637"}'
)

# or you can modify it manually
# e.g.
#
# api.query.unit = 2

res = api.get_data()

for item in res:
    print(f"交易日期：{item.get('e')} 地址：{item.get('a')}")
