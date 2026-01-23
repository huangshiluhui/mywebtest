<template>
    <el-form
        ref="formRef"
        :model="form"
        label-width="100px"
        style="text-align: center;padding-bottom:10px"
    >
      <el-upload
          name="avatar"
          class="avatar-uploader"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleFileChange"
          :before-upload="beforeAvatarUpload"
      >
        <img v-if="previewUrl" :src="previewUrl" class="avatar" @error="handleImageError"/>
        <img v-else-if="imageUrl" :src="imageUrl" class="avatar" @error="handleImageError"/>
        <el-icon v-else class="avatar-uploader-icon">
          <Plus/>
        </el-icon>
      </el-upload>
      <el-button @click="handleConfirm" :loading="uploading">确认更换</el-button>
    </el-form>
  
  
  </template>
  
  <script setup>
  
  import {defineProps, ref, watch, onBeforeUnmount} from "vue";
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
  
  // const headers = ref({
  //   Authorization: `Bearer ${window.sessionStorage.getItem('token') || ''}`
  // })
  
  const form = ref({
    id: -1,
    avatar: ''
  })
  
  const formRef = ref(null)
  
  const imageUrl = ref("")  // 当前服务器上的头像URL
  const previewUrl = ref("")  // 新选择图片的预览URL（本地预览，未上传）
  const selectedFile = ref(null)  // 新选择的文件对象
  const uploading = ref(false)  // 上传状态

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
      // 重置预览和选择的文件
      if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value)
        previewUrl.value = ""
      }
      selectedFile.value = null
    }
  }, { immediate: true })

  // 处理图片加载失败的情况
  const handleImageError = () => {
    imageUrl.value = ""
  }
  
  // 处理文件选择（不立即上传，只预览）
  const handleFileChange = (file) => {
    // 释放之前的预览URL（如果存在）
    if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value)
    }
    // 创建新的预览URL
    previewUrl.value = URL.createObjectURL(file.raw)
    selectedFile.value = file.raw
  }
  
  const beforeAvatarUpload = (file) => {
    const isJPG = file.type === 'image/jpeg'
    const isLt2M = file.size / 1024 / 1024 < 2
    
    if (!isJPG) {
      ElMessage.error('图片必须是jpg格式')
      return false
    }
    if (!isLt2M) {
      ElMessage.error('图片大小不能超过2M!')
      return false
    }
    return false  // 返回 false 阻止自动上传
  }
  
  // 确认更换：先上传文件，再更新数据库
  const handleConfirm = async () => {
    // 如果没有选择新文件，直接更新数据库（使用现有头像）
    if (!selectedFile.value) {
      if (!form.value.avatar) {
        ElMessage.warning('请先选择要更换的头像')
        return
      }
      // 直接更新数据库
      uploading.value = true
      try {
        let result = await requestUtil.post("user/updateAvatar", form.value);
        let data = result.data;
        if (data.code == 200) {
          ElMessage.success("执行成功！")
          // 更新 sessionStorage 中的用户信息
          const currentUser = JSON.parse(sessionStorage.getItem("currentUser"))
          if (currentUser) {
            currentUser.avatar = form.value.avatar
            sessionStorage.setItem("currentUser", JSON.stringify(currentUser))
          }
        } else {
          ElMessage.error(data.errorInfo);
        }
      } catch (error) {
        ElMessage.error('更新失败，请稍后重试')
      } finally {
        uploading.value = false
      }
      return
    }

    // 有新文件，先上传文件
    uploading.value = true
    try {
      // 创建 FormData 上传文件
      const formData = new FormData()
      formData.append('avatar', selectedFile.value)
      
      // 上传文件
      const uploadResult = await requestUtil.fileUpload("user/uploadImage", formData)
      const uploadData = uploadResult.data
      
      if (uploadData.code !== 200) {
        ElMessage.error(uploadData.errorInfo || '上传失败')
        return
      }
      
      // 上传成功，更新数据库
      form.value.avatar = uploadData.title
      const updateResult = await requestUtil.post("user/updateAvatar", form.value)
      const updateData = updateResult.data
      
      if (updateData.code == 200) {
        ElMessage.success("头像更换成功！")
        // 更新预览URL为服务器URL
        if (previewUrl.value) {
          URL.revokeObjectURL(previewUrl.value)
          previewUrl.value = ""
        }
        imageUrl.value = getServerUrl() + '/media/userAvatar/' + form.value.avatar
        selectedFile.value = null
        
        // 更新 sessionStorage 中的用户信息
        const currentUser = JSON.parse(sessionStorage.getItem("currentUser"))
        if (currentUser) {
          currentUser.avatar = form.value.avatar
          sessionStorage.setItem("currentUser", JSON.stringify(currentUser))
        }
      } else {
        ElMessage.error(updateData.errorInfo || '更新失败')
      }
    } catch (error) {
      console.error('上传或更新失败:', error)
      ElMessage.error('操作失败，请稍后重试')
    } finally {
      uploading.value = false
    }
  }

  // 组件卸载时释放预览URL，避免内存泄漏
  onBeforeUnmount(() => {
    if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value)
    }
  })
  
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
  