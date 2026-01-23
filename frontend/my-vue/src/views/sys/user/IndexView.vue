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
      <el-col :span="17">
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <el-button type="success" :icon="DocumentAdd" @click="handleDialogValue()">新增</el-button>
        <el-button type="danger" :icon="Delete" @click="handleBatchDelete">批量删除</el-button>
      </el-col>
    </el-row>

    <el-table 
      ref="tableRef"
      :data="tableData" 
      stripe 
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55"/>
      <el-table-column prop="avatar" label="头像" width="80" align="center">
        <template v-slot="scope">
          <el-avatar 
            v-if="scope.row.avatar" 
            :src="getServerUrl() + '/media/userAvatar/' + scope.row.avatar" 
            :size="50"
          />
          <el-avatar v-else :size="50">
            <el-icon><User /></el-icon>
          </el-avatar>
        </template>
      </el-table-column>
      <el-table-column prop="username" label="用户名" width="100" align="center"/>
      <el-table-column prop="roleList" label="拥有角色" width="200" align="center">
        <template v-slot="scope">
          <el-tag v-for="role in scope.row.roleList" :key="role.id" style="margin-right: 5px;">
            {{ role.name }}
          </el-tag>
          <span v-if="!scope.row.roleList || scope.row.roleList.length === 0">暂无角色</span>
        </template>
      </el-table-column>
      <el-table-column prop="email" label="邮箱" width="200" align="center"/>
      <el-table-column prop="phonenumber" label="手机号" width="120" align="center"/>
      <el-table-column prop="status" label="状态？" width="200" align="center">
        <template v-slot="{row}">
          <el-switch v-model="row.status" @change="statusChangeHandle(row)" active-text="正常"
                     inactive-text="禁用" :active-value="1" :inactive-value="0"></el-switch>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="200" align="center"/>
      <el-table-column prop="login_date" label="最后登录时间" width="200" align="center"/>
      <el-table-column prop="remark" label="备注"/>
      <el-table-column prop="action" label="操作" width="400" fixed="right" align="center">
        <template v-slot="scope">
          <el-button type="primary" :icon="Tools" @click="handleRoleDialogValue(scope.row.id,scope.row.roleList)">分配角色
          </el-button>

          <el-popconfirm v-if="scope.row.username!='python222'" title="您确定要对这个用户重置密码吗？"
                         @confirm="handleResetPassword(scope.row.id)">
            <template #reference>
              <el-button type="warning" :icon="RefreshRight">重置密码</el-button>
            </template>
          </el-popconfirm>

          <el-button type="primary" v-if="scope.row.username!='python222'" :icon="Edit"
                     @click="handleDialogValue(scope.row.id)">编辑</el-button>
          <el-popconfirm v-if="scope.row.username!='python222'" title="您确定要删除这条记录吗？"
                         @confirm="handleDelete(scope.row.id)">
            <template #reference>
              <el-button type="danger" :icon="Delete"/>
            </template>
          </el-popconfirm>


        </template>
      </el-table-column>

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

    <!-- 新增/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      @close="handleDialogClose"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">
            默认初始密码: 123456
          </div>
        </el-form-item>
        <el-form-item label="手机号" prop="phonenumber">
          <el-input v-model="userForm.phonenumber" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="userForm.status">
            <el-radio :label="1">正常</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="userForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
    <!-- 分配角色对话框 -->
    <el-dialog
      v-model="dialogRoleVisible"
      :title="dialogRoleTitle"
      width="500px"
      @close="handleRoleDialogClose"
    >
      <el-form
        ref="roleFormRef"
        :model="roleForm"
        :rules="roleFormRules"
        label-width="100px"
      >
        <el-form-item label="角色列表" prop="roleIds">
          <el-checkbox-group v-model="roleForm.roleIds">
            <el-checkbox 
              v-for="role in allRoles" 
              :key="role.id" 
              :label="role.id"
              style="display: block; margin-bottom: 10px;"
            >
              {{ role.name }}
              <span v-if="role.code" style="color: #909399; font-size: 12px; margin-left: 5px;">
                ({{ role.code }})
              </span>
            </el-checkbox>
          </el-checkbox-group>
          <div v-if="allRoles.length === 0" style="color: #909399; font-size: 12px; margin-top: 10px;">
            暂无可用角色
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogRoleVisible = false">取消</el-button>
          <el-button type="primary" @click="handleRoleSubmit" :loading="submittingRole">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
    </div>
  </template>
  
  <script setup>
    import { ref, onMounted, nextTick, computed } from 'vue'
    import { Search, DocumentAdd, Tools, RefreshRight, Edit, Delete, User } from '@element-plus/icons-vue'
    import requestUtil, { getServerUrl } from '@/util/request'
    import { ElMessage, ElMessageBox } from 'element-plus'
    
    const tableData = ref([])
    const tableRef = ref(null) // 表格引用，用于获取选中的行
    const selectedRows = ref([]) // 选中的行数据
    const queryForm = ref({
        query: '',
        pageNum: 1,
        pageSize: 3
    })
    const total = ref(0)
    const background = ref(true)
    
    // 对话框相关
    const dialogVisible = ref(false)
    const submitting = ref(false)
    const userFormRef = ref(null)
    const isEdit = ref(false) // 是否为编辑模式
    const currentUserId = ref(null) // 当前编辑的用户ID
    
    // 对话框标题
    const dialogTitle = computed(() => {
      return isEdit.value ? '用户编辑' : '用户添加'
    })
    
    // 用户表单数据
    const userForm = ref({
      username: '',
      phonenumber: '',
      email: '',
      status: 1, // 默认正常
      remark: ''
    })
    
    // 表单验证规则
    const userFormRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
      ],
      phonenumber: [
        { required: true, message: '请输入手机号', trigger: 'blur' },
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
      ]
    }
    
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
    
    // 重置表单
    const resetForm = () => {
      userForm.value = {
        username: '',
        phonenumber: '',
        email: '',
        status: 1,
        remark: ''
      }
      if (userFormRef.value) {
        userFormRef.value.clearValidate()
      }
    }
    
    // 打开对话框
    const handleDialogValue = (id) => {
      if (id) {
        // 编辑模式
        isEdit.value = true
        currentUserId.value = id
        // 从表格数据中查找用户信息
        const user = tableData.value.find(u => u.id === id)
        if (user) {
          userForm.value = {
            username: user.username || '',
            phonenumber: user.phonenumber || '',
            email: user.email || '',
            status: user.status !== undefined ? user.status : 1,
            remark: user.remark || ''
          }
        }
      } else {
        // 新增模式
        isEdit.value = false
        currentUserId.value = null
        resetForm()
      }
      //触发对话框显示
      dialogVisible.value = true
    }
    
    // 关闭对话框
    const handleDialogClose = () => {
      resetForm()
      isEdit.value = false
      currentUserId.value = null
    }
    
    // 提交表单
    const handleSubmit = async () => {
      if (!userFormRef.value) return
      
      // 表单验证
      await userFormRef.value.validate(async (valid) => {
        if (!valid) {
          return false
        }
        
        submitting.value = true
        try {
          const formData = {
            ...userForm.value,
            id: isEdit.value ? currentUserId.value : -1 // 新增时 id 为 -1
          }
          
          // 只有新增时才设置默认密码
          if (!isEdit.value) {
            formData.password = '123456'
          }
          
          const result = await requestUtil.post('user/save', formData)
          
          if (result.data && result.data.code === 200) {
            ElMessage.success(isEdit.value ? '编辑成功！' : '添加成功！')
            dialogVisible.value = false
            getUserList() // 刷新列表
          } else {
            ElMessage.error(result.data?.errorInfo || '操作失败')
          }
        } catch (error) {
          console.error('提交失败:', error)
          ElMessage.error('操作失败，请稍后重试')
        } finally {
          submitting.value = false
        }
      })
    }
    

    // 分配角色相关
    const allRoles = ref([])
    const dialogRoleVisible = ref(false)
    const dialogRoleTitle = computed(() => {
      const user = tableData.value.find(u => u.id === currentRoleUserId.value)
      return user ? `为 ${user.username} 分配角色` : '分配角色'
    })
    const roleFormRules = {
      roleIds: [
        { required: false, message: '请选择角色', trigger: 'change' }
      ]
    }
    const roleFormRef = ref(null)
    const submittingRole = ref(false)
    const currentRoleUserId = ref(null) // 当前分配角色的用户ID
    
    // 角色表单数据
    const roleForm = ref({
      roleIds: [] // 选中的角色ID数组
    })
    
    // 打开分配角色对话框
    const handleRoleDialogValue = async (userId, roleList) => {
      try {
        // 保存当前用户ID
        currentRoleUserId.value = userId
        
        // 获取所有角色列表
        const result = await requestUtil.get('role/searchAllRole')
        if (result.data && result.data.code === 200) {
          allRoles.value = result.data.allRoles || []
        } else {
          ElMessage.error(result.data?.errorInfo || '获取角色列表失败')
          return
        }
        
        // 设置当前用户已拥有的角色为选中状态
        if (roleList && Array.isArray(roleList) && roleList.length > 0) {
          roleForm.value.roleIds = roleList.map(role => role.id)
        } else {
          roleForm.value.roleIds = []
        }
        
        // 打开对话框
        dialogRoleVisible.value = true
      } catch (error) {
        console.error('打开分配角色对话框失败:', error)
        ElMessage.error('获取角色列表失败，请稍后重试')
      }
    }
    
    // 提交角色分配
    const handleRoleSubmit = async () => {
      if (!roleFormRef.value) return
      
      submittingRole.value = true
      try {
        const formData = {
          userId: currentRoleUserId.value,
          roleIds: roleForm.value.roleIds || []
        }
        
        const result = await requestUtil.post('user/assignRole', formData)
        
        if (result.data && result.data.code === 200) {
          ElMessage.success('角色分配成功！')
          dialogRoleVisible.value = false
          getUserList() // 刷新列表
        } else {
          ElMessage.error(result.data?.errorInfo || '角色分配失败')
        }
      } catch (error) {
        console.error('提交角色分配失败:', error)
        ElMessage.error('角色分配失败，请稍后重试')
      } finally {
        submittingRole.value = false
      }
    }
    
    // 关闭分配角色对话框
    const handleRoleDialogClose = () => {
      roleForm.value.roleIds = []
      currentRoleUserId.value = null
      if (roleFormRef.value) {
        roleFormRef.value.clearValidate()
      }
    }
    
    const handleResetPassword = async (userId) => {
      // 重置密码
      try {
        const result = await requestUtil.post('user/resetPassword', { id: userId })
        if (result.data && result.data.code === 200) {
          ElMessage.success('密码重置成功！')
        } else {
          ElMessage.error(result.data?.errorInfo || '重置密码失败')
        }
      } catch (error) {
        console.error('重置密码失败:', error)
        ElMessage.error('重置密码失败，请稍后重试')
      }
    }
    
    // 处理表格选中变化
    const handleSelectionChange = (selection) => {
      selectedRows.value = selection
    }
    
    // 批量删除
    const handleBatchDelete = async () => {
      if (!selectedRows.value || selectedRows.value.length === 0) {
        ElMessage.warning('请先选择要删除的用户')
        return
      }
      
      // 检查是否包含超级管理员
      const hasSuperAdmin = selectedRows.value.some(row => row.username === 'python222')
      if (hasSuperAdmin) {
        ElMessage.warning('不能删除超级管理员！')
        return
      }
      
      try {
        // 确认对话框
        await ElMessageBox.confirm(
          `确定要删除选中的 ${selectedRows.value.length} 个用户吗？`,
          '批量删除确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
          }
        )
        
        // 获取所有选中用户的ID
        const userIds = selectedRows.value.map(row => row.id)
        
        // 批量删除
        let successCount = 0
        let failCount = 0
        
        for (const userId of userIds) {
          try {
            const result = await requestUtil.post('user/delete', { id: userId })
            if (result.data && result.data.code === 200) {
              successCount++
            } else {
              failCount++
              console.error(`删除用户 ${userId} 失败:`, result.data?.errorInfo)
            }
          } catch (error) {
            failCount++
            console.error(`删除用户 ${userId} 异常:`, error)
          }
        }
        
        // 显示删除结果
        if (successCount > 0) {
          ElMessage.success(`成功删除 ${successCount} 个用户`)
        }
        
        if (failCount > 0) {
          ElMessage.warning(`${failCount} 个用户删除失败`)
        }
        
        // 无论成功或失败，都刷新列表以同步最新数据
        // 清空选中
        if (tableRef.value) {
          tableRef.value.clearSelection()
        }
        // 刷新列表
        await getUserList()
      } catch (error) {
        // 用户取消删除
        if (error !== 'cancel') {
          console.error('批量删除失败:', error)
          ElMessage.error('批量删除失败，请稍后重试')
        }
      }
    }
    
    const handleDelete = async (userId) => {
      // 删除用户
      try {
        const result = await requestUtil.post('user/delete', { id: userId })
        if (result.data && result.data.code === 200) {
          ElMessage.success('删除成功！')
          getUserList() // 刷新列表
        } else {
          ElMessage.error(result.data?.errorInfo || '删除失败')
        }
      } catch (error) {
        console.error('删除失败:', error)
        ElMessage.error('删除失败，请稍后重试')
      }
    }
    
    const statusChangeHandle = async (row) => {
      // 状态切换
      try {
        const result = await requestUtil.post('user/updateStatus', {
          id: row.id,
          status: row.status
        })
        if (result.data && result.data.code === 200) {
          ElMessage.success('状态更新成功！')
        } else {
          // 如果更新失败，恢复原状态
          row.status = row.status === 1 ? 0 : 1
          ElMessage.error(result.data?.errorInfo || '状态更新失败')
        }
      } catch (error) {
        console.error('状态更新失败:', error)
        // 恢复原状态
        row.status = row.status === 1 ? 0 : 1
        ElMessage.error('状态更新失败，请稍后重试')
      }
    }
  </script>
  