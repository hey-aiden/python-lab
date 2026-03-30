# python httpx模块

import httpx

# 同步发送GET请求
response = httpx.get("https://www.baidu.com")

print(response)

# 发送POST请求
# response = requests.post("https://www.baidu.com", data={"key": "value"})
# print(response.text)

# 发送GET请求并传递参数
