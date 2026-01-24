# server.py
import os
import decimal
import datetime
import logging
from argparse import ArgumentParser

import pymysql
import uvicorn
from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from mcp.server import Server
from mcp.server.sse import SseServerTransport

# ---------- 日志 ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------- 环境变量 ----------
load_dotenv()


class Config:
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8020))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 6666))
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")


# ---------- MCP ----------
mcp = FastMCP("file_reader")

# 内部函数实现实际逻辑
def _get_monthly_nutrition_impl(user_id: str = "default", user_name: str = None) -> dict:
    """
    获取过去 30 天用户每日饮食记录
    参数：
        user_id   – 用户ID；"default" 表示全部
        user_name – 用户名；None 表示不限
    """
    logger.info(
        f"get_monthly_nutrition called: user_id={user_id}, user_name={user_name}"
    )

    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            # 基础 SQL
            sql = """
                SELECT
                    DATE(o.order_time) AS order_date,
                    GROUP_CONCAT(DISTINCT d.name SEPARATOR ', ') AS dish_names,
                    SUM(oi.quantity * d.total_calorie) AS total_calories,
                    SUM(oi.quantity * d.total_protein) AS total_protein
                FROM orders o
                JOIN users u ON o.user_id = u.user_id
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN dishes d ON oi.dish_id = d.dish_id
                WHERE o.order_time >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            """

            # 动态条件 + 防注入
            conditions = []
            params = []
            if user_id != "default":
                conditions.append("o.user_id = %s")
                params.append(user_id)
            if user_name is not None:
                conditions.append("u.name = %s")
                params.append(user_name)

            if conditions:
                sql += " AND " + " AND ".join(conditions)

            sql += " GROUP BY DATE(o.order_time)"
            sql += " ORDER BY order_date"

            cur.execute(sql, params)
            rows = cur.fetchall()
            logger.info(f"Retrieved {len(rows)} rows")

        # 转 JSON 可序列化
        records = make_jsonable(rows)
        return {
            "text": "",
            "files": [],
            "json": [{"records": records}],
        }
    except Exception as e:
        logger.exception("Database error")
        return {
            "text": "",
            "files": [],
            "json": [{"records": []}],
        }
    finally:
        conn.close()


# MCP 工具包装器
@mcp.tool()
def get_monthly_nutrition(user_id: str = "default", user_name: str = None) -> dict:
    """
    获取过去 30 天用户每日饮食记录
    参数：
        user_id   – 用户ID；"default" 表示全部
        user_name – 用户名；None 表示不限
    """
    return _get_monthly_nutrition_impl(user_id, user_name)


# ---------- 通用：把 Decimal/date 转成 JSON 可序列化 ----------
def make_jsonable(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return str(obj)
    if isinstance(obj, dict):
        return {k: make_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_jsonable(i) for i in obj]
    return obj


# ---------- Starlette App ----------
def create_starlette_app(mcp_server: Server) -> Starlette:
    # SSE 通道
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )
        return JSONResponse({})

    # REST 接口 1：按 user_id（兼容旧）
    async def api_get_monthly_nutrition(request):
        user_id = request.query_params.get("user_id", "default")
        data = _get_monthly_nutrition_impl(user_id=user_id)
        return JSONResponse(data)

    # REST 接口 2：按 user_name
    async def api_get_monthly_nutrition_by_name(request):
        user_name = request.query_params.get("user_name", "").strip()
        if not user_name:
            return JSONResponse(
                {"error": "user_name 不能为空"}, status_code=400
            )
        data = _get_monthly_nutrition_impl(user_name=user_name)
        return JSONResponse(data)

    app = Starlette(
        debug=Config.DEBUG,
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
            Route("/get_monthly_nutrition", endpoint=api_get_monthly_nutrition),
            Route("/nutrition_by_name", endpoint=api_get_monthly_nutrition_by_name),
        ],
        on_startup=[lambda: logger.info("Server starting...")],
        on_shutdown=[lambda: logger.info("Server shutting down...")],
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


# ---------- CLI ----------
def parse_arguments():
    parser = ArgumentParser(description="MCP SSE Server")
    parser.add_argument("--host", default=Config.HOST, help="Host")
    parser.add_argument("--port", type=int, default=Config.PORT, help="Port")
    parser.add_argument("--debug", action="store_true", help="Debug")
    return parser.parse_args()


# ---------- 入口 ----------
if __name__ == "__main__":
    args = parse_arguments()
    Config.HOST = args.host
    Config.PORT = args.port
    Config.DEBUG = args.debug

    mcp_server = mcp._mcp_server
    starlette_app = create_starlette_app(mcp_server)

    logger.info(f"Starting server on {Config.HOST}:{Config.PORT}")
    uvicorn.run(
        starlette_app,
        host=Config.HOST,
        port=Config.PORT,
        log_level="debug" if Config.DEBUG else "info",
    )