import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import { setupGlobalErrorHandler } from './plugins/errorHandler'
import { setupLazyLoad } from './directives/lazyLoad'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// Setup global error handling after router is ready
setupGlobalErrorHandler(app, router)

// Setup lazy load directive
setupLazyLoad(app)

app.mount('#app')
