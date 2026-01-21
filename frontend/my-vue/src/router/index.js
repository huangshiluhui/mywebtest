import { createRouter, createWebHashHistory } from 'vue-router'
import { isLoggedIn } from '@/util/auth.js'

// import HomeView from '@/views/HomeView.vue'
// import IndexView from '@/layout/IndexView.vue'

const routes = [
  {
    path: '/',
    name: '主页',
    component:  () => import( '@/layout/IndexView.vue'),
    redirect: '/index',
    meta:{
      requiresAuth:true
    },
    children:[
      {
        path: '/index',
        name: '首页',
        component: () => import( '@/views/index/HomeView.vue')
      },
      {
        path: '/sys/user',
        name: '用户管理',
        component: () => import( '@/views/sys/user/IndexView.vue')
      },
      {
        path: '/sys/role',
        name: '角色管理',
        component: () => import( '@/views/sys/role/IndexView.vue')
      },
      {
        path: '/sys/menu',
        name: '菜单管理',
        component: () => import( '@/views/sys/menu/IndexView.vue')
      },
      {
        path: '/bsns/department',
        name: '部门管理',
        component: () => import( '@/views/bsns/department/IndexView.vue')
      },
      {
        path: '/bsns/post',
        name: '岗位管理',
        component: () => import( '@/views/bsns/post/IndexView.vue')
      },
      {
        path: '/userCenter/info',
        name: '个人中心',
        component: () => import( '@/views/userCenter/InfoView.vue')
      }
    ]
  },

  {
    path: '/login',
    name: 'login',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import( '@/views/LoginView.vue'),
    meta:{
      requiresAuth:false
    }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})



router.beforeEach((to,from,next)=>{
  const requiresAuth = to.matched.some(record=>record.meta.requiresAuth !== false)

  if(requiresAuth){
    if (isLoggedIn()) {
      next()
    } else {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    }
  } else {
    if (isLoggedIn() && to.path === '/login') {
      next('/')
    } else {
      next()
    }
  }
})

export default router
