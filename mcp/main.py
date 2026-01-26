import os
from collections import defaultdict

import uvicorn
import logging
from dotenv import load_dotenv
from argparse import ArgumentParser

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server import Server
from mcp.server.sse import SseServerTransport

import pymysql
from starlette.routing import Route, Mount



# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()


class Config:
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8020))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # MySQL
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '6666'))
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')


# 初始化MCP
mcp = FastMCP("file_reader")
@mcp.tool()
def get_weekly_nutrition() -> dict:
    """
    多表查询：orders → order_items → dishes
    统计近 7 天用户每日卡路里 & 蛋白质摄入量（按购买数量加权）
    """
    logger.info("get_weekly_nutrition (multi-table) called")
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT
                    DATE(o.order_time) AS d,
                    oi.quantity,
                    d.total_calorie,
                    d.total_protein
                FROM orders o
                JOIN order_items oi
                  ON o.order_id = oi.order_id
                JOIN dishes d
                  ON oi.dish_id = d.dish_id
                WHERE o.order_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);
            """
            cur.execute(sql)
            rows = cur.fetchall()

        if not rows:
            return {"error": "近 7 天没有订单数据"}

        # 按日期汇总
        daily = defaultdict(lambda: {"cal": 0.0, "pro": 0.0})
        for r in rows:
            day = str(r["d"])
            qty = int(r["quantity"])
            daily[day]["cal"] += float(r["total_calorie"]) * qty
            daily[day]["pro"] += float(r["total_protein"]) * qty

        # 7 日均值
        avg_cal = round(sum(v["cal"] for v in daily.values()) / 7, 1)
        avg_protein = round(sum(v["pro"] for v in daily.values()) / 7, 1)

        prompt = (
            f"我上周平均每天通过点餐摄入 {avg_cal} 千卡热量、{avg_protein} 克蛋白质。"
            "请针对我的饮食进行评估与建议。"
        )

        return {
            "daily_data": [{"date": k, "cal": v["cal"], "pro": v["pro"]}
                           for k, v in sorted(daily.items())],
            "avg_cal": avg_cal,
            "avg_protein": avg_protein,
            "prompt": prompt
        }
    finally:
        conn.close()

import decimal, datetime, json

def make_jsonable(obj):
    """递归把 Decimal / date 转成 float / str"""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, datetime.date):
        return str(obj)
    if isinstance(obj, dict):
        return {k: make_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_jsonable(i) for i in obj]
    return obj

from starlette.responses import Response   # 如已导入可忽略
from starlette.responses import JSONResponse   # 新增

def create_starlette_app(mcp_server: Server) -> Starlette:
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
        return Response(status_code=200)

    # ⬇︎ 新增：给 Dify「自定义工具」用的 REST 接口
    async def api_get_weekly_nutrition(request):
        data = get_weekly_nutrition()
        return JSONResponse(data)

    app = Starlette(
        debug=Config.DEBUG,
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
            Route("/get_weekly_nutrition", endpoint=api_get_weekly_nutrition, methods=["GET"]),  # ⬅︎ 这一行
        ],
        on_startup=[lambda: logger.info("Server starting...")],
        on_shutdown=[lambda: logger.info("Server shutting down...")],
    )

    from starlette.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

def parse_arguments():
    """解析命令行参数"""
    parser = ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default=Config.HOST, help='Host to bind to')
    parser.add_argument('--port', type=int,
                        default=Config.PORT, help='Port to listen on')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    # 更新配置
    Config.HOST = args.host
    Config.PORT = args.port
    Config.DEBUG = args.debug

    # 启动服务器
    mcp_server = mcp._mcp_server
    starlette_app = create_starlette_app(mcp_server)

    logger.info(f"Starting server on {Config.HOST}:{Config.PORT}")
    uvicorn.run(
        starlette_app,
        host=Config.HOST,
        port=Config.PORT,
        log_level="info" if not Config.DEBUG else "debug"
    )