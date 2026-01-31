# 本地知识库

下载ragflow  `git clone https://github.com/infiniflow/ragflow.git`

需要安装docker

> [在国内 Windows 平台上安装 Docker 的详细教程_docker windows intel-CSDN博客](https://blog.csdn.net/HYP_Coder/article/details/141753300)

![image-20250626211056992](https://picture-01-1316374204.cos.ap-beijing.myqcloud.com/lenovo-picture/202506262110274.png)

换一下可以使用的镜像源

```
"registry-mirrors": [
    "https://docker.xuanyuan.me",
    "https://mirror.ccs.tencentyun.com"
]
```

我这里使用的是上面两个

```bash
docker compose -f docker-compose.yml up -d
```

可以在127.0.0.1访问

![image-20250626220806018](https://picture-01-1316374204.cos.ap-beijing.myqcloud.com/lenovo-picture/202506262208176.png)

![image-20250626220825169](https://picture-01-1316374204.cos.ap-beijing.myqcloud.com/lenovo-picture/202506262208379.png)

![image-20250626222920966](https://picture-01-1316374204.cos.ap-beijing.myqcloud.com/lenovo-picture/202506262229177.png)

```
docker compose down
docker compose up -d
```

> 以上的测试失败, 下边使用API的方式

## MCP

在使用ragflow的时候, 他默认是有一个MCP接口的, 但是还在试用阶段, 我测试了一下没有成功, 这里使用自己实现的方式达成MCP调用

MCP的注册工具使用另一个UP**[闪电蘑菇](https://space.bilibili.com/24615859?spm_id_from=333.788.upinfo.detail.click)**开发的工具[小智MCP自由了！我开源了个命令行神器实现多MCP聚合](https://www.bilibili.com/video/BV1hxMbzqEzU/?spm_id_from=333.1387.favlist.content.click), 开源地址在[这里](https://github.com/shenjingnan/xiaozhi-client)

下面摘抄一下他的手册

```bash
## 安装
npm i -g xiaozhi-client

## 创建项目
xiaozhi create my-app --template hello-world

## 进入项目
cd my-app

## 安装依赖（主要是示例代码中mcp服务所使用的依赖）
pnpm install

# 修改 xiaozhi.config.json 中的 mcpEndpoint 为你的接入点地址（需要自行前往xiaozhi.me获取）
# 小智AI配置MCP接入点使用说明：https://ccnphfhqs21z.feishu.cn/wiki/HiPEwZ37XiitnwktX13cEM5KnSb

## 运行
xiaozhi start
```

> 这里使用的npm是Node.js的一部分, 放一个网上找的文档[node（npm） 安装及其环境配置完整教程_npm安装及环境配置-CSDN博客](https://blog.csdn.net/qq_45824320/article/details/136601535), 出现问题可以问一下AI

配置好以后打开文件xiaozhi.config.json, 填入python路径以及我写的mcp工具即可

我写的MCP工具需要填入API和知识库的id

