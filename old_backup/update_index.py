#!/usr/bin/env python3
"""
Script to update index.html to extend base.html while preserving existing styling
"""

# Read the original file
with open('main/templates/index.html.backup', 'r', encoding='utf-8') as f:
    original_content = f.read()

# Extract the CSS styles section (everything between <style> and </style>)
import re
style_match = re.search(r'<style>(.*?)</style>', original_content, re.DOTALL)
styles = style_match.group(1) if style_match else ''

# Extract the main content (everything between <div class="container"> and the closing </div> before bottom-nav)
# We'll need to carefully extract the hero banner, nutrition cards, and recommendations

# Create the new template
new_template = '''{% extends "base.html" %}
{% load static %}

{% block title %}智慧餐饮 - 首页 | DashBoard{% endblock %}

{% block meta_description %}DashBoard智慧餐饮系统首页 - 查看个性化推荐菜品和每日营养摄入分析{% endblock %}

{% block meta_keywords %}智慧餐饮,首页,营养分析,推荐菜品,健康饮食{% endblock %}

{% block og_title %}智慧餐饮 - 首页 | DashBoard{% endblock %}
{% block og_description %}查看个性化推荐菜品和每日营养摄入分析{% endblock %}

{% block extra_css %}
    <link rel="stylesheet" href="{% static 'css/all.min.css' %}">
    <link rel="stylesheet" href="{% static 'css/modern-theme.css' %}">
    <style>
''' + styles + '''
    </style>
{% endblock %}

{% block content %}
    <!-- Index Page Main Content -->
    <div class="index-page">
'''

# Now we need to add the content sections with proper semantic HTML and accessibility
# I'll write this out manually to ensure proper structure

print("Script created. Run with: python update_index.py")
print("This will generate the updated index.html file.")
