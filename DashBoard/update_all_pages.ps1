# 批量更新所有页面为现代主题
Write-Host "🚀 开始批量更新页面..." -ForegroundColor Cyan

$pages = @(
    "main/templates/orders.html",
    "main/templates/profile.html", 
    "main/templates/repo.html",
    "main/templates/ai_health_advisor.html",
    "main/templates/MyOrder.html",
    "main/templates/Collection.html",
    "main/templates/nutrition_recipes.html",
    "main/templates/order_history.html",
    "main/templates/order_status.html",
    "main/templates/registe.html",
    "main/templates/NoComment.html"
)

foreach ($page in $pages) {
    if (Test-Path $page) {
        Write-Host "📝 处理: $page" -ForegroundColor Yellow
        
        $content = Get-Content $page -Raw -Encoding UTF8
        
        # 添加modern-theme.css引用（如果还没有）
        if ($content -notmatch 'modern-theme\.css') {
            $content = $content -replace '(<link rel="stylesheet" href="\.\./static/css/all\.min\.css">)', 
                '$1`n    <link rel="stylesheet" href="../static/css/modern-theme.css">'
        }
        
        # 更新颜色变量
        $content = $content -replace '#27ae60', '#4A90E2'  # 主绿色 -> 主蓝色
        $content = $content -replace '#1e8449', '#2E5C8A'  # 深绿色 -> 深蓝色
        $content = $content -replace '#52be80', '#7AB8F5'  # 浅绿色 -> 浅蓝色
        $content = $content -replace 'rgba\(39, 174, 96', 'rgba(74, 144, 226'  # 绿色rgba -> 蓝色rgba
        
        # 更新背景色
        $content = $content -replace '#f0f9f4', '#FAFBFC'  # 淡绿背景 -> 淡灰背景
        $content = $content -replace '#e8f8f0', '#F5F7FA'  # 浅绿背景 -> 浅灰背景
        $content = $content -replace '#f8fdf9', '#F5F7FA'  # 柔和绿背景 -> 柔和灰背景
        
        # 更新圆角（增大圆角）
        $content = $content -replace 'border-radius:\s*12px', 'border-radius: 16px'
        $content = $content -replace 'border-radius:\s*15px', 'border-radius: 20px'
        $content = $content -replace 'border-radius:\s*16px', 'border-radius: 20px'
        $content = $content -replace 'border-radius:\s*20px', 'border-radius: 24px'
        
        # 保存文件
        $content | Set-Content $page -Encoding UTF8 -NoNewline
        
        Write-Host "✅ 完成: $page" -ForegroundColor Green
    } else {
        Write-Host "⚠️  文件不存在: $page" -ForegroundColor Red
    }
}

Write-Host "`n🎉 所有页面更新完成！" -ForegroundColor Green
Write-Host "📊 已更新 $($pages.Count) 个页面" -ForegroundColor Cyan
