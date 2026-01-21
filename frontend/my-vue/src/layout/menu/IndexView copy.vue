<template>
  <el-menu
    :default-active="activeMenu"
    class="el-menu-vertical-demo"
    background-color="#2d3a4b"
    text-color="#fff"
    active-text-color="#409eff"
    @open="handleOpen"
    @close="handleClose"
  >
    <template v-for="menu in menuList" :key="menu.id">
      <!-- 有子菜单的情况 -->
      <el-sub-menu v-if="menu.children && menu.children.length > 0" :index="String(menu.id)">
        <template #title>
          <span>{{ menu.name }}</span>
        </template>
        <!-- 递归渲染子菜单 -->
        <template v-for="child in menu.children" :key="child.id">
          <el-sub-menu v-if="child.children && child.children.length > 0" :index="String(child.id)">
            <template #title>
              <span>{{ child.name }}</span>
            </template>
            <el-menu-item
              v-for="grandChild in child.children"
              :key="grandChild.id"
              :index="String(grandChild.id)"
              @click="handleMenuClick(grandChild)"
            >
              <span>{{ grandChild.name }}</span>
            </el-menu-item>
          </el-sub-menu>
          <el-menu-item v-else :index="String(child.id)" @click="handleMenuClick(child)">
            <span>{{ child.name }}</span>
          </el-menu-item>
        </template>
      </el-sub-menu>
      <!-- 没有子菜单的情况 -->
      <el-menu-item v-else :index="String(menu.id)" @click="handleMenuClick(menu)">
        <span>{{ menu.name }}</span>
      </el-menu-item>
    </template>
  </el-menu>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const menuList = ref([])
const activeMenu = ref('')

// 从 sessionStorage 读取菜单数据
onMounted(() => {
  const menuListStr = window.sessionStorage.getItem('menuList')
  if (menuListStr) {
    try {
      menuList.value = JSON.parse(menuListStr)
      console.log('菜单数据加载成功:', menuList.value)
    } catch (error) {
      console.error('解析菜单数据失败:', error)
      menuList.value=[]
    }
  } else {
    console.warn('未找到菜单数据，请先登录')
    menuList.value=[]
  }
})

const handleOpen = (key, keyPath) => {
  console.log('菜单展开:', key, keyPath)
}

const handleClose = (key, keyPath) => {
  console.log('菜单收起:', key, keyPath)
}

const handleMenuClick = (menu) => {
  console.log('点击菜单:', menu)
  if (menu.path) {
    router.push(menu.path)
    activeMenu.value = String(menu.id)
  }
}
</script>

<style scoped>
.el-menu-vertical-demo {
  border-right: none;
  height: 100%;
}

.el-menu {
  border-right: none;
}
</style>
