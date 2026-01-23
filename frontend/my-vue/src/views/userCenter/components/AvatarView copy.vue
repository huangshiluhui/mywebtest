<template>
  <div class="avatar-container">
    <el-avatar shape="square" :size="60" :src="squareUrl" />
  </div>
</template>

<script setup>
import { getServerUrl } from '@/util/request'
const currentUser=JSON.parse(sessionStorage.getItem("currentUser"))
const squareUrl=getServerUrl()+'/media/userAvatar/'+currentUser.avatar
</script>

<style lang="scss" scoped>
.avatar-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: 20px 0;
}
</style>
