-- Hotel Manager Database Schema
-- Run: mysql -u root -p hotel_manager < schema.sql

CREATE DATABASE IF NOT EXISTS hotel_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hotel_manager;

-- Users
CREATE TABLE users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('employee', 'finance', 'admin') NOT NULL DEFAULT 'employee',
    display_name VARCHAR(100) NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Orders
CREATE TABLE orders (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_platform VARCHAR(50) NOT NULL,
    order_number VARCHAR(100) NOT NULL,
    room_name VARCHAR(200) NOT NULL,
    guest_name VARCHAR(100) NOT NULL,
    salesperson VARCHAR(100) NOT NULL,
    hotel_name VARCHAR(200) NOT NULL,
    guest_count INT NOT NULL DEFAULT 1,
    booking_date DATE NOT NULL,
    confirmation_number VARCHAR(100),
    order_status ENUM('未处理', '已确认', '已入住', '已取消') NOT NULL DEFAULT '未处理',
    other_remarks TEXT,
    created_by INT UNSIGNED NOT NULL,
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    deleted_at DATETIME,
    deleted_by INT UNSIGNED,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (deleted_by) REFERENCES users(id),
    INDEX idx_created_by_deleted (created_by, is_deleted),
    INDEX idx_booking_date (booking_date),
    INDEX idx_deleted_created (is_deleted, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Order Items
CREATE TABLE order_items (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id INT UNSIGNED NOT NULL,
    date DATE NOT NULL,
    room_count INT NOT NULL,
    cost_price DECIMAL(10,2) NOT NULL,
    sale_price DECIMAL(10,2) NOT NULL,
    gross_profit DECIMAL(10,2) NOT NULL DEFAULT 0,
    profit_margin DECIMAL(5,2) NOT NULL DEFAULT 0,
    salesperson VARCHAR(100),
    confirmation_number VARCHAR(100),
    remarks TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Operation Logs
CREATE TABLE operation_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    action ENUM('create', 'update', 'delete', 'login', 'export', 'user_create', 'user_disable', 'user_enable', 'user_delete') NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT UNSIGNED,
    details JSON,
    ip_address VARCHAR(45),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_entity (entity_type, entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
