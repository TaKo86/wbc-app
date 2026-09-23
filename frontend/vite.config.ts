


/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from '@vitejs/plugin-react'


export default defineConfig({
  // ...your existing config (plugins, etc.)
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom", 
    setupFiles: "./src/test-setup.ts",
  },
});