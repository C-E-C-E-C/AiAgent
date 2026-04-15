# Vue 3 + Spring Boot Full Stack Starter
# 项目的介绍图片在images目录下 
This workspace contains two applications:

- `frontend`: Vue 3 + Vue Router + TypeScript
- `backend`: Spring Boot + MySQL + Knife4j + Sa-Token + MyBatis-Plus

## Features

- Frontend route-based layout with login and dashboard pages
- Backend login/logout/profile APIs
- MySQL data model for users, roles, and permissions
- Sa-Token permission checks via `@SaCheckLogin` and `@SaCheckPermission`
- Knife4j API documentation
- Vite proxy configured for local development

## Prerequisites

- Node.js 18+
- Java 17+
- Maven 3.9+
- MySQL 8+

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Backend

1. Create a MySQL database named `sa_demo`.
2. Import `backend/src/main/resources/db/schema.sql`.
3. Update `backend/src/main/resources/application.yml` with your database credentials.
4. Run the application:

```bash
cd backend
mvn spring-boot:run
```

## Default Demo Accounts

The SQL seed file contains sample accounts. Update them before production use.

- `admin / 123456`
- `viewer / 123456`

## Notes

- Frontend requests are proxied from `/api` to `http://localhost:8080`.
- Knife4j documentation is available after the backend starts.
