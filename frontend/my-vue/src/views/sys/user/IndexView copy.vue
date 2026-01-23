<template>
    <div>
    <el-row :gutter="20" class="header" style="margin-bottom: 20px;">
      <el-col :span="7">
        <el-input 
          placeholder="请输入用户名..." 
          v-model="queryForm.query" 
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </el-col>
      <el-col :span="4">
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <el-button type="success" :icon="DocumentAdd" @click="handleDialogValue()">新增</el-button>
      </el-col>
    </el-row>
    <el-table :data="tableData" stripe style="width: 100%">
      <el-table-column prop="id" label="id" width="180" />
      <el-table-column prop="username" label="username" width="180" />
      <el-table-column prop="email" label="email" />
      <el-table-column prop="phonenumber" label="phonenumber" />
      <el-table-column prop="status" label="status" />
      <el-table-column prop="create_time" label="create_time" />
      <el-table-column prop="update_time" label="update_time" />
      <el-table-column prop="remark" label="remark" />
    </el-table>
    <el-pagination
      v-model:current-page="queryForm.pageNum"
      v-model:page-size="queryForm.pageSize"
      :page-sizes="[3, 5, 10]"
      :background="background"
      layout="total, sizes, prev, pager, next, jumper"
      :total="total"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      style="margin-top: 20px;"
    />
    </div>
  </template>
  
  <script setup>
    import { ref, onMounted, nextTick } from 'vue'
    import { Search, DocumentAdd } from '@element-plus/icons-vue'
    import requestUtil from '@/util/request'
    
    const tableData = ref([])
    const queryForm = ref({
        query: '',
        pageNum: 1,
        pageSize: 3
    })
    const total = ref(0)
    const background = ref(true)
    
    const getUserList = async () => {
      try {
        console.log(queryForm.value)
        const result = await requestUtil.post('user/search', queryForm.value)
        console.log(result)
        if (result.data && result.data.code === 200) {
          // 使用 nextTick 确保 DOM 更新完成后再更新数据，避免 ResizeObserver 错误
          await nextTick()
          tableData.value = result.data.userList || []
          total.value = result.data.total || 0
        } else {
          console.error('获取用户列表失败:', result.data?.errorInfo)
        }
      } catch (error) {
        console.error('请求失败:', error)
      }
    }
    
    // 搜索时重置页码
    const handleSearch = () => {
      queryForm.value.pageNum = 1
      getUserList()
    }
    
    // 组件挂载时获取数据
    onMounted(() => {
      getUserList()
    })
    
    const handleSizeChange = (pageSize) => {
        queryForm.value.pageSize = pageSize
        queryForm.value.pageNum = 1
        getUserList()
    }

    const handleCurrentChange = (pageNum) => {
        queryForm.value.pageNum = pageNum
        getUserList()
    }
    
    const handleDialogValue = () => {
      // 新增用户对话框，暂时留空
      console.log('打开新增用户对话框')
    }
  </script>
  