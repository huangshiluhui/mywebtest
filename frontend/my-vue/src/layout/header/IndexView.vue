<template>
  <div class="header-container">
    <div class="header-left">
      <BreadCrumb />
    </div>
    <div class="header-right">
      <AvatarImage />
    </div>
  </div>
</template>  

<script setup>
  import AvatarImage from './components/AvatarImage.vue'
  import BreadCrumb from './components/BreadCrumb.vue'
</script>

<style lang="scss" scoped>
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    height: 100%;
    padding: 0 20px;
    box-sizing: border-box;
  }
  
  .header-left {
    display: flex;
    align-items: center;
  }
  
  .header-right {
    display: flex;
    align-items: center;
  }
  </style>