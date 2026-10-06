import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In development, requests to /api are forwarded to the FastAPI backend,
// so the browser only ever talks to one address (no CORS surprises).
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // lets you open the app from your phone on the same Wi-Fi
    port: 5173,
    proxy: {
      "/api": {
        target: process.env.OFFLINE_BACKEND_URL ?? "http://127.0.0.1:8000",
        changeOrigin: true,
        // Local models can be slow; don't let the dev proxy hang up first.
        timeout: 180_000,
        proxyTimeout: 180_000,
      },
    },
  },
});
