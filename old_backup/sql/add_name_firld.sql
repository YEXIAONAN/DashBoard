-- 为users表添加name字段
ALTER TABLE users ADD COLUMN name VARCHAR(50) NULL COMMENT '姓名';

-- 可选：为现有用户添加默认姓名（示例）
-- UPDATE users SET name = CONCAT('用户', user_id) WHERE name IS NULL;