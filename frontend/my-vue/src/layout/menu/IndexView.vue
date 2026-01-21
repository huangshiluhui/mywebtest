<template>
  <el-menu
    active-text-color="#ffd04b"
    background-color="#2d3a4b"
    class="el-menu-vertical-demo"
    text-color="#fff"
    router
    :default-active="'/index'"
  >
    <el-menu-item index="/index" @click="openTab({name:'首页',path:'/index'})">
      <el-icon><HomeFilled /></el-icon>
      <span>首页</span>
    </el-menu-item>

    <template v-for="menu in menuList" :key="menu.id">
      <!-- 有子菜单的情况 -->
      <el-sub-menu v-if="menu.children && menu.children.length > 0" :index="String(menu.id)">
        <template #title>
          <login-icon :icon="menu.icon" class="menu-icon" />
          <span>{{ menu.name }}</span>
        </template>
        <!-- 循环子菜单的孩子节点情况 -->
        <el-menu-item v-for="child in menu.children" :key="child.id"  @click="openTab(child)">
            <login-icon :icon="child.icon" class="menu-icon" />
            <span>{{ child.name }}</span>
          </el-menu-item>
      </el-sub-menu>

      <!-- 没有子菜单的情况 -->
      <el-menu-item v-else :index="menu.path || String(menu.id)" @click="openTab(menu)">
        <login-icon :icon="menu.icon" class="menu-icon" />
        <span>{{ menu.name }}</span>
      </el-menu-item>
    </template>
  </el-menu>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { HomeFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import store from '@/store'

const menuList = ref([])
const router = useRouter()

onMounted(() => {
  const menuListStr = window.sessionStorage.getItem('menuList')
  if (menuListStr) {
    try {
      menuList.value = JSON.parse(menuListStr)
    } catch (error) {
      console.error('解析菜单数据失败:', error)
      menuList.value = []
    }
  }
})

const openTab = (item) => {
  if (!item?.path) return
  store.commit('ADD_TABS', item)
  router.push(item.path)
}
</script>

<style scoped>
.menu-icon {
  margin-right: 8px;
}
</style>