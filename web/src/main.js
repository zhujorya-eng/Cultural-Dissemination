import { TheaterApp } from './TheaterApp.js';

const canvas = document.getElementById('canvas');
const loading = document.getElementById('loading');

async function bootstrap() {
  try {
    const app = new TheaterApp(canvas);
    window.kunquVR = app;
    loading.classList.add('hidden');
  } catch (err) {
    console.error(err);
    loading.querySelector('p').textContent = '加载失败，请刷新页面重试';
  }
}

bootstrap();
