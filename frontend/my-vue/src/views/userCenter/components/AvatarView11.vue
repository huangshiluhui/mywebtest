<template>
    <el-form
        ref="formRef"
        :model="form"
        label-width="100px"
        style="text-align: center;padding-bottom:10px"
    >
      <el-upload
          name="avatar"
          :headers="headers"
          class="avatar-uploader"
          :action="getServerUrl() + '/user/uploadImage'"
          :show-file-list="false"
          :on-success="handleAvatarSuccess"
          :before-upload="beforeAvatarUpload"
      >
        <img v-if="imageUrl" :src="imageUrl" class="avatar" @error="handleImageError"/>
        <el-icon v-else class="avatar-uploader-icon">
          <Plus/>
        </el-icon>
      </el-upload>
      <el-button @click="handleConfirm">确认更换</el-button>
    </el-form>
  
  
  </template>
  
  <script setup>
  
  import {defineProps, ref, watch} from "vue";
  import requestUtil, {getServerUrl} from "@/util/request";
  import {ElMessage} from 'element-plus'
  import {Plus} from '@element-plus/icons-vue'
  
  
  const props = defineProps(
      {
        user: {
          type: Object,
          default: () => {
          },
          required: true
        }
      }
  )
  
  const headers = ref({
    Authorization: `Bearer ${window.sessionStorage.getItem('token') || ''}`
  })
  
  const form = ref({
    id: -1,
    avatar: ''
  })
  
  const formRef = ref(null)
  
  const imageUrl = ref("")

  // 使用 watch 监听 props 变化，避免在根作用域直接赋值导致响应式丢失
  watch(() => props.user, (newUser) => {
    if (newUser) {
      form.value = { ...newUser }
      // 只有当 avatar 字段存在且有值时才设置 imageUrl
      if (form.value.avatar) {
        imageUrl.value = getServerUrl() + '/media/userAvatar/' + form.value.avatar
      } else {
        imageUrl.value = ""
      }
    }
  }, { immediate: true })
  
  const handleAvatarSuccess = (res) => {
    imageUrl.value = getServerUrl() + '/media/userAvatar/' + res.title
    form.value.avatar = res.title;
  }

  // 处理图片加载失败的情况
  const handleImageError = () => {
    imageUrl.value = ""
  }
  
  
  const beforeAvatarUpload = (file) => {
    const isJPG = file.type === 'image/jpeg'
    const isLt2M = file.size / 1024 / 1024 < 2
  
    if (!isJPG) {
      ElMessage.error('图片必须是jpg格式')
    }
    if (!isLt2M) {
      ElMessage.error('图片大小不能超过2M!')
    }
    return isJPG && isLt2M
  }
  
  const handleConfirm = async () => {
  
    let result = await requestUtil.post("user/updateAvatar", form.value);
    let data = result.data;
    if (data.code == 200) {
      ElMessage.success("执行成功！")
    } else {
      ElMessage.error(data.errorInfo);
    }
  
  }
  
  </script>
  
  <style>
  
  .avatar-uploader .el-upload {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }
  
  .avatar-uploader .el-upload:hover {
    border-color: #409eff;
  }
  
  .el-icon.avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 178px;
    height: 178px;
    text-align: center;
  }
  
  .avatar {
    width: 120px;
    height: 120px;
    display: block;
    margin: 0 auto;
  }
  
  .avatar-uploader {
    display: flex;
    justify-content: center;
    margin-bottom: 10px;
  }
  
  .avatar-uploader .el-upload {
    margin: 0 auto;
  }
  
  :deep(.el-form-item) {
    text-align: center;
  }
  
  :deep(.el-button) {
    margin-top: 10px;
  }
  
  </style>
  