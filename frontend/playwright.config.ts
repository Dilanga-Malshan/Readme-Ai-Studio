import {defineConfig,devices} from '@playwright/test';
export default defineConfig({testDir:'./e2e',use:{baseURL:'http://localhost:4200'},webServer:{command:'npm start',url:'http://localhost:4200',reuseExistingServer:!process.env.CI},projects:[{name:'desktop',use:{...devices['Desktop Chrome']}},{name:'mobile',use:{...devices['Pixel 7']}}]});
