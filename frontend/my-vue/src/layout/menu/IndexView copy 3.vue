<template>
      <el-menu
        active-text-color="#ffd04b"
        background-color="#2d3a4b"
        class="el-menu-vertical-demo"
        text-color="#fff"
        router
        :default-active="'/index'"
      >
      <el-menu-item index="/index">
        <el-icon><HomeFilled /></el-icon>
        <span>首页</span>
      </el-menu-item>
      <template v-for="menu in menuList" :key="menu.id">
        
      </template>
        <el-sub-menu index="1">
          <template #title>
            <login-icon icon="system" class="menu-icon" />
            <span>Navigator One</span>
          </template>
            <el-menu-item index="1-1">
                <login-icon icon="user" class="menu-icon" />
             <span>Item One</span>
            </el-menu-item>
        </el-sub-menu>      
      </el-menu>
</template>

<script setup>
</script>

<style scoped>
.menu-icon {
  margin-right: 8px;
}
</style>
