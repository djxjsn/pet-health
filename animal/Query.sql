-- 3. 使用数据库
USE `ai_pet_health`;

-- 4. 创建 users 表
CREATE TABLE `users` (
    `user_id`       CHAR(36)        NOT NULL                    COMMENT '用户 ID，UUID 主键',
    `phone`         VARCHAR(20)     NOT NULL                    COMMENT '手机号码，唯一约束',
    `email`         VARCHAR(255)    DEFAULT NULL                COMMENT '电子邮箱，唯一约束',
    `password_hash` VARCHAR(255)    NOT NULL                    COMMENT '加密后的密码',
    `is_active`     TINYINT(1)      NOT NULL DEFAULT 1          COMMENT '账户是否激活',
    `is_superuser`  TINYINT(1)      NOT NULL DEFAULT 0          COMMENT '是否为超级管理员',
    `last_login_at` DATETIME        DEFAULT NULL                COMMENT '最后登录时间',
    `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP       COMMENT '创建时间',
    `updated_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                ON UPDATE CURRENT_TIMESTAMP   COMMENT '更新时间',
    PRIMARY KEY (`user_id`),
    UNIQUE KEY `uk_users_phone` (`phone`),
    UNIQUE KEY `uk_users_email` (`email`),
    KEY `ix_users_is_active` (`is_active`),
    KEY `ix_users_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='用户基础信息表';

-- 5. 创建 user_profiles 表
CREATE TABLE `user_profiles` (
    `profile_id`    CHAR(36)        NOT NULL                    COMMENT '档案 ID，UUID 主键',
    `user_id`       CHAR(36)        NOT NULL                    COMMENT '关联用户 ID，外键 + 唯一约束',
    `full_name`     VARCHAR(100)    DEFAULT NULL                COMMENT '用户真实姓名',
    `gender`        ENUM('male', 'female', 'other', 'unspecified')
                                    NOT NULL DEFAULT 'unspecified' COMMENT '性别',
    `date_of_birth` DATE            DEFAULT NULL                COMMENT '出生日期',
    `avatar_url`    VARCHAR(500)    DEFAULT NULL                COMMENT '头像 URL 地址',
    `address`       VARCHAR(500)    DEFAULT NULL                COMMENT '联系地址',
    `bio`           TEXT            DEFAULT NULL                COMMENT '个人简介',
    `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP       COMMENT '创建时间',
    `updated_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                ON UPDATE CURRENT_TIMESTAMP   COMMENT '更新时间',
    PRIMARY KEY (`profile_id`),
    UNIQUE KEY `uk_user_profiles_user_id` (`user_id`),
    KEY `ix_user_profiles_full_name` (`full_name`),
    CONSTRAINT `fk_user_profiles_user_id`
        FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='用户扩展档案表';

-- 6. 插入初始数据
INSERT INTO `users` (`user_id`, `phone`, `email`, `password_hash`, `is_active`, `is_superuser`)
VALUES
('00000000-0000-0000-0000-000000000001', '13800000000', 'admin@aipethealth.com', '$2b$12$LJ3m4ys3Lk0TSwMCfVSLnOXLwHbONbKxHPOR3lEVbwMGF7cGfHaKa', 1, 1),
('00000000-0000-0000-0000-000000000010', '13800000001', 'test@aipethealth.com', '$2b$12$LJ3m4ys3Lk0TSwMCfVSLnOXLwHbONbKxHPOR3lEVbwMGF7cGfHaKa', 1, 0);

INSERT INTO `user_profiles` (`profile_id`, `user_id`, `full_name`, `gender`, `bio`)
VALUES
('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', '系统管理员', 'unspecified', 'AI 宠物健康助手系统管理员账户'),
('00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000010', '测试用户', 'male', '系统测试账户');

-- 7. 验证
SELECT '表创建成功！' AS message;
SHOW TABLES;
SELECT * FROM users;