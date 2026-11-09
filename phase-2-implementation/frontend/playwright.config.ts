import { defineConfig } from '@playwright/test';
export default defineConfig({ testDir:'./e2e', use: { baseURL: process.env.DEALDESK_E2E_BASE_URL || 'http://127.0.0.1:3000', trace:'retain-on-failure' }, timeout:120000, expect:{timeout:60000}, workers:1 });
