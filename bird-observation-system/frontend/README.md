# Frontend

## 技术栈

- Vue 3
- Vite
- Element Plus
- Axios
- ECharts
- Vue Router

## 启动方式

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

默认开发地址：`http://127.0.0.1:5173`

## FastAPI 对接

前端默认请求 `/api`，开发模式会通过 `vite.config.js` 自动代理到：

- `http://127.0.0.1:8000`

如果后端地址变化，可以修改：

- `.env` 中的 `VITE_API_BASE_URL`
- 或 `vite.config.js` 中的代理目标

## 首页数据来源

- `/api/stats/overview`
- `/api/stats/species-frequency?days=7`
- `/api/stats/daily-trend?days=7`
- `/api/stats/rare-birds?days=7`
- `/api/alerts/latest`
