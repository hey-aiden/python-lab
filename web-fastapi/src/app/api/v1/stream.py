import asyncio
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

message = """
Rick: (stumbles in drunkenly, and turns on the lights) Morty! You gotta come on. You got--... you gotta come with me.
Morty: (rubs his eyes) What, Rick? What's going on?
Rick: I got a surprise for you, Morty.
Morty: It's the middle of the night. What are you talking about?
Rick: (spills alcohol on Morty's bed) Come on, I got a surprise for you. (drags Morty by the ankle) Come on, hurry up. (pulls Morty out of his bed and into the hall)
Morty: Ow! Ow! You're tugging me too hard!
Rick: We gotta go, gotta get outta here, come on. Got a surprise for you Morty.
"""


@router.get("/stream_data")
async def handleStreamData() -> StreamingResponse:
    """方式 1：text/plain 流 — TCP 层面逐 chunk 传输，但浏览器/curl 默认缓冲.

    验证方式（Python 客户端逐 chunk 读才能看到流式）：
      import httpx
      with httpx.stream("GET", url, headers={"Cookie": "session=abc"}) as r:
          for line in r.iter_lines():
              print(line)
    """

    async def generate() -> AsyncGenerator[str, None]:
        for line in message.splitlines():
            if not line.strip():
                continue
            yield line + "\n"
            await asyncio.sleep(1.5)

    return StreamingResponse(generate(), media_type="text/plain")


@router.get(
    "/stream_sse", dependencies=[]
)  # dependencies=[] 跳过 router 级 cookie 鉴权
async def handleStreamSSE() -> StreamingResponse:
    """方式 2：SSE（Server-Sent Events）— 浏览器原生支持，逐条渲染.

    SSE 格式要求每条消息以 "data: " 开头，以 "\n\n" 结尾。
    浏览器用 EventSource API 监听，每条到达后立刻回调 onmessage。

    dependencies=[] 是必要的——EventSource API 不支持自定义请求头，
    也无法携带 httponly cookie，所以 SSE 端点通常需要独立鉴权或公开。

    前端测试（在浏览器控制台粘贴）：
      const es = new EventSource("http://127.0.0.1:8000/api/v1/stream_sse");
      es.onmessage = (e) => console.log(e.data);          // 每条台词
      es.addEventListener("done", (e) => {                // 自定义 done 事件
          console.log("流结束:", e.data);
          es.close();                                     // 主动关闭连接
      });
      es.onerror = () => console.log("连接关闭或出错");    // TCP 断开时触发
    """

    async def generate() -> AsyncGenerator[str, None]:
        for line in message.splitlines():
            if not line.strip():
                continue
            yield f"data: {line}\n\n"  # SSE 协议：data: xxx \n\n 表示一条消息结束
            await asyncio.sleep(1.5)

        # 遍历完毕，发送结束事件
        yield "event: done\ndata: 流已结束\n\n"
        # SSE 关闭流程：done 之后必须等浏览器主动 close()，再关闭连接
        # 如果不 wait 直接结束 → 连接先断开 → 浏览器触发 onerror → 自动重连 → 死循环
        await asyncio.sleep(0.5)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
