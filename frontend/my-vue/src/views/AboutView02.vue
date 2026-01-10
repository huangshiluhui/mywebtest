<template>
    <div class="button-container">
      <div class="mb-4 button-group">
        <el-button>Default</el-button>
        <el-button type="primary">Primary</el-button>
        <el-button type="success">Success</el-button>
        <el-button type="info">Info</el-button>
        <el-button type="warning">Warning</el-button>
        <el-button type="danger">Danger</el-button>
      </div>
    
      <div class="mb-4 button-group">
        <el-button plain>Plain</el-button>
        <el-button type="primary" plain>Primary</el-button>
        <el-button type="success" plain>Success</el-button>
        <el-button type="info" plain>Info</el-button>
        <el-button type="warning" plain>Warning</el-button>
        <el-button type="danger" plain>Danger</el-button>
      </div>
    
      <div class="mb-4 button-group">
        <el-button round>Round</el-button>
        <el-button type="primary" round>Primary</el-button>
        <el-button type="success" round>Success</el-button>
        <el-button type="info" round>Info</el-button>
        <el-button type="warning" round>Warning</el-button>
        <el-button type="danger" round>Danger</el-button>
      </div>
    
      <div class="mb-4 button-group">
        <el-button :icon="Search" circle />
        <el-button type="primary" :icon="Edit" circle />
        <el-button type="success" :icon="Check" circle />
        <el-button type="info" :icon="Message" circle />
        <el-button type="warning" :icon="Star" circle />
        <el-button type="danger" :icon="Delete" circle />
      </div>
    </div>
  </template>
  
  <script setup>
  import {
    Check,
    Delete,
    Edit,
    Message,
    Search,
    Star,
  } from '@element-plus/icons-vue'
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
  