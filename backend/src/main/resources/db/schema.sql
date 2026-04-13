CREATE DATABASE IF NOT EXISTS sa_demo DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE sa_demo;

DROP TABLE IF EXISTS sys_user_role;
DROP TABLE IF EXISTS sys_role_permission;
DROP TABLE IF EXISTS sys_permission;
DROP TABLE IF EXISTS sys_role;
DROP TABLE IF EXISTS sys_user;

CREATE TABLE sys_user (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL UNIQUE,
  password VARCHAR(128) NOT NULL,
  nickname VARCHAR(64) NOT NULL,
  enabled TINYINT NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE sys_role (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  role_code VARCHAR(64) NOT NULL UNIQUE,
  role_name VARCHAR(64) NOT NULL
);

CREATE TABLE sys_permission (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  permission_code VARCHAR(128) NOT NULL UNIQUE,
  permission_name VARCHAR(128) NOT NULL
);

CREATE TABLE sys_user_role (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  role_id BIGINT NOT NULL,
  UNIQUE KEY uk_user_role (user_id, role_id)
);

CREATE TABLE sys_role_permission (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  role_id BIGINT NOT NULL,
  permission_id BIGINT NOT NULL,
  UNIQUE KEY uk_role_permission (role_id, permission_id)
);

INSERT INTO sys_user (id, username, password, nickname, enabled) VALUES
  (1, 'admin', '123456', 'Administrator', 1),
  (2, 'viewer', '123456', 'Viewer', 1);

INSERT INTO sys_role (id, role_code, role_name) VALUES
  (1, 'admin', 'Administrator'),
  (2, 'viewer', 'Viewer');

INSERT INTO sys_permission (id, permission_code, permission_name) VALUES
  (1, 'user:read', 'Read User Data'),
  (2, 'user:write', 'Write User Data');

INSERT INTO sys_user_role (user_id, role_id) VALUES
  (1, 1),
  (2, 2);

INSERT INTO sys_role_permission (role_id, permission_id) VALUES
  (1, 1),
  (1, 2),
  (2, 1);
