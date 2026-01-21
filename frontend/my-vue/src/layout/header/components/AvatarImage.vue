<template>
  <el-dropdown>
    <span class="el-dropdown-link avatar-wrapper">
      <el-avatar shape="square" :size="40" :src="squareUrl" />
      &nbsp;&nbsp;{{currentUser.username}}
      <el-icon class="el-icon--right">
        <arrow-down />
      </el-icon>
    </span>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item @click="goUserCenter">个人中心</el-dropdown-item>
        <el-dropdown-item @click="logout">安全退出</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup>
  import { getServerUrl } from '@/util/request'
  import { ArrowDown } from '@element-plus/icons-vue'
  import router from '@/router'
  import store from '@/store'
  
  const currentUser=JSON.parse(sessionStorage.getItem("currentUser"))
  const squareUrl=getServerUrl()+'/media/userAvatar/'+currentUser.avatar
  
  // 跳转到个人中心，并新增tab
  const goUserCenter = () => {
    const item = { name: '个人中心', path: '/userCenter/info' }
    store.commit('ADD_TABS', item)
    router.push(item.path)
  }
  
  const logout=()=>{
  window.sessionStorage.clear()
  router.replace("/login")
  }
</script>


<style lang="scss" scoped>
.avatar-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
  
  // 移除默认的边框和轮廓
  border: none;
  outline: none;
  
  // hover 时的样式（可选：改为背景色变化而不是边框）
  &:hover {
    background-color: rgba(0, 0, 0, 0.05);
    border: none;
    outline: none;
  }
  
  // 移除 focus 时的轮廓
  &:focus {
    outline: none;
  }
}

// 如果 el-dropdown-link 有默认样式，需要深度选择器覆盖
:deep(.el-dropdown-link) {
  border: none !important;
  outline: none !important;
  
  &:hover {
    border: none !important;
    outline: none !important;
    background-color: rgba(0, 0, 0, 0.05);
  }
  &:focus {
    outline: none !important;
  }
}
</style>