"""文件操作工具."""

from pathlib import Path

from fastapi import HTTPException


def safe_write(dir_name: str, filename: str, content: bytes) -> None:
    """安全写入文件，统一异常处理.

    把三种常见写入错误映射为 HTTP 状态码：
    - FileExistsError → 409
    - PermissionError → 500
    - OSError         → 500
    """
    target_dir = Path(dir_name)
    target_dir.mkdir(exist_ok=True)

    try:
        (target_dir / filename).write_bytes(content)
    except FileExistsError:
        raise HTTPException(status_code=409, detail=f"文件 {filename} 已存在")
    except PermissionError:
        raise HTTPException(status_code=500, detail="服务器没有写入权限")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"写入失败: {e}")
