// API Configuration
// In production (Railway), use relative URLs since frontend is served from same origin
// In development, use localhost:8002

export const API_URL = import.meta.env.PROD
    ? "" // Same origin in production
    : "http://localhost:8002";
