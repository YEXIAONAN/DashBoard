FROM nginx:alpine

# 复制自定义配置
COPY nginx.conf /etc/nginx/nginx.conf

# 复制网站文件
COPY html /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
