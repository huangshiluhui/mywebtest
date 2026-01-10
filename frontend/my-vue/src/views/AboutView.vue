<template>
   <el-button type="primary" @click="handleLogin">登录测试</el-button>
   <el-button type="success" @click="handleUserList">用户列表信息展示</el-button>
  </template>
  
<script>
import requestUtil from '@/util/request.js'
import { ElMessage } from 'element-plus'

export default {
  name: 'AboutView',
  methods: {
    async handleLogin() {
      try {
        ElMessage.info('正在发送登录测试请求...')
        let result = await requestUtil.get("user/jwt_test/")
        console.log('登录测试结果:', result)
        ElMessage.success('登录测试成功！请查看控制台')
      } catch (error) {
        console.error('登录测试失败:', error)
        ElMessage.error('登录测试失败: ' + (error.message || '请求出错'))
      }
    },
    async handleUserList() {
      try {
        ElMessage.info('正在获取用户列表...')
        let result = await requestUtil.get("user/test/")
        console.log('用户列表结果:', result)
        ElMessage.success('获取用户列表成功！请查看控制台')
      } catch (error) {
        console.error('获取用户列表失败:', error)
        ElMessage.error('获取用户列表失败: ' + (error.message || '请求出错'))
      }
    }
  }
}
</script>

<style scoped>
/* 容器：使用 Grid 布局，让所有按钮行和列都居中对齐 */
.button-container {
  display: grid;
  grid-template-columns: repeat(6, auto); /* 6列，每列自适应宽度 */
  grid-template-rows: repeat(4, auto); /* 4行 */
  gap: 24px 12px; /* 行间距 列间距 */
  justify-content: center; /* 让整个网格在页面中居中 */
  align-items: center; /* 让每一列的按钮在垂直方向上居中对齐 */
  padding: 20px;
}

/* 按钮组：让子元素直接参与 Grid 布局 */
.button-group {
  display: contents; /* 让按钮直接参与 Grid 布局，忽略按钮组容器 */
}

/* 确保每个按钮在网格单元格中居中 */
.button-group .el-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: auto; /* 让按钮根据内容自适应宽度 */
  margin: 0 auto; /* 让按钮在网格单元格中居中 */
}

/* 圆形按钮保持圆形，不被拉伸 */
.button-group .el-button.is-circle {
  width: auto; /* 保持圆形按钮的原始宽度 */
  aspect-ratio: 1; /* 保持宽高比 1:1，确保是圆形 */
}
</style>
  