import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import installIcons from './icons'
import store from './store'

const app = createApp(App)
app.use(store)
app.use(router)
app.use(ElementPlus)
installIcons(app)
app.mount('#app')
