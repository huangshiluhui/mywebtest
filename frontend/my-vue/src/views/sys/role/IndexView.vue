<template>
  <div>
    <el-row :gutter="20" class="header" style="margin-bottom: 20px;">
      <el-col :span="7">
        <el-input 
          placeholder="请输入角色名称..." 
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
      <el-table-column prop="name" label="角色名" width="150" align="center"/>
      <el-table-column prop="code" label="权限字符" width="150" align="center"/>
      <el-table-column prop="create_time" label="创建时间" width="200" align="center"/>
      <el-table-column prop="remark" label="备注"/>
      <el-table-column prop="action" label="操作" width="300" fixed="right" align="center">
        <template v-slot="scope">
          <el-button type="primary" :icon="Tools" @click="handlePermissionDialogValue(scope.row.id)">
            分配权限
          </el-button>
          <el-button type="primary" :icon="Edit" @click="handleDialogValue(scope.row.id)">
            编辑
          </el-button>
          <el-popconfirm 
            v-if="scope.row.name !== '超级管理员'"
            title="您确定要删除这条记录吗？"
            @confirm="handleDelete(scope.row.id)"
          >
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

    <!-- 新增/编辑角色对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      @close="handleDialogClose"
    >
      <el-form
        ref="roleFormRef"
        :model="roleForm"
        :rules="roleFormRules"
        label-width="100px"
      >
        <el-form-item label="角色名" prop="name">
          <el-input v-model="roleForm.name" placeholder="请输入角色名" />
        </el-form-item>
        <el-form-item label="权限字符" prop="code">
          <el-input v-model="roleForm.code" placeholder="请输入权限字符" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="roleForm.remark"
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

    <!-- 分配权限对话框 -->
    <el-dialog
      v-model="dialogPermissionVisible"
      :title="dialogPermissionTitle"
      width="600px"
      @close="handlePermissionDialogClose"
    >
      <el-form
        ref="permissionFormRef"
        :model="permissionForm"
        label-width="100px"
      >
        <el-form-item label="菜单权限">
          <el-tree
            ref="treeRef"
            :data="menuTreeData"
            :props="{ children: 'children', label: 'name' }"
            :default-expanded-all="true"
            show-checkbox
            node-key="id"
            check-strictly
          />
          <div v-if="menuTreeData.length === 0" style="color: #909399; font-size: 12px; margin-top: 10px;">
            暂无可用菜单
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogPermissionVisible = false">取消</el-button>
          <el-button type="primary" @click="handlePermissionSubmit" :loading="submittingPermission">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
  import { ref, onMounted, nextTick, computed, watch } from 'vue'
  import { Search, DocumentAdd, Tools, Edit, Delete } from '@element-plus/icons-vue'
  import requestUtil from '@/util/request'
  import { ElMessage, ElMessageBox } from 'element-plus'

  const tableData = ref([])
  const tableRef = ref(null)
  const selectedRows = ref([])
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
  const roleFormRef = ref(null)
  const isEdit = ref(false)
  const currentRoleId = ref(null)

  // 对话框标题
  const dialogTitle = computed(() => {
    return isEdit.value ? '角色编辑' : '角色添加'
  })

  // 角色表单数据
  const roleForm = ref({
    name: '',
    code: '',
    remark: ''
  })

  // 表单验证规则
  const roleFormRules = {
    name: [
      { required: true, message: '请输入角色名', trigger: 'blur' },
      { min: 2, max: 30, message: '角色名长度在 2 到 30 个字符', trigger: 'blur' }
    ],
    code: [
      { required: true, message: '请输入权限字符', trigger: 'blur' }
    ]
  }

  // 获取角色列表
  const getRoleList = async () => {
    try {
      const result = await requestUtil.post('role/search', queryForm.value)
      if (result.data && result.data.code === 200) {
        await nextTick()
        tableData.value = result.data.roleList || []
        total.value = result.data.total || 0
      } else {
        // 如果返回页码超出范围的错误，自动调整页码
        if (result.data?.errorInfo && result.data.errorInfo.includes('页码超出范围')) {
          // 计算总页数
          const totalPages = Math.ceil((total.value || 0) / queryForm.value.pageSize)
          if (totalPages > 0 && queryForm.value.pageNum > totalPages) {
            // 如果当前页超出范围，重置为最后一页
            queryForm.value.pageNum = totalPages
            // 重新请求
            return getRoleList()
          } else if (totalPages === 0) {
            // 如果没有数据了，重置为第一页
            queryForm.value.pageNum = 1
            tableData.value = []
            total.value = 0
            return
          }
        }
        console.error('获取角色列表失败:', result.data?.errorInfo)
        ElMessage.error(result.data?.errorInfo || '获取角色列表失败')
      }
    } catch (error) {
      console.error('请求失败:', error)
      ElMessage.error('获取角色列表失败，请稍后重试')
    }
  }

  // 搜索时重置页码
  const handleSearch = () => {
    queryForm.value.pageNum = 1
    getRoleList()
  }

  // 组件挂载时获取数据
  onMounted(() => {
    getRoleList()
  })

  const handleSizeChange = (pageSize) => {
    queryForm.value.pageSize = pageSize
    queryForm.value.pageNum = 1
    getRoleList()
  }

  const handleCurrentChange = (pageNum) => {
    queryForm.value.pageNum = pageNum
    getRoleList()
  }

  // 重置表单
  const resetForm = () => {
    roleForm.value = {
      name: '',
      code: '',
      remark: ''
    }
    if (roleFormRef.value) {
      roleFormRef.value.clearValidate()
    }
  }

  // 打开对话框
  const handleDialogValue = (id) => {
    if (id) {
      // 编辑模式
      isEdit.value = true
      currentRoleId.value = id
      const role = tableData.value.find(r => r.id === id)
      if (role) {
        roleForm.value = {
          name: role.name || '',
          code: role.code || '',
          remark: role.remark || ''
        }
      }
    } else {
      // 新增模式
      isEdit.value = false
      currentRoleId.value = null
      resetForm()
    }
    dialogVisible.value = true
  }

  // 关闭对话框
  const handleDialogClose = () => {
    resetForm()
    isEdit.value = false
    currentRoleId.value = null
  }

  // 提交表单
  const handleSubmit = async () => {
    if (!roleFormRef.value) return

    await roleFormRef.value.validate(async (valid) => {
      if (!valid) {
        return false
      }

      submitting.value = true
      try {
        const formData = {
          ...roleForm.value,
          id: isEdit.value ? currentRoleId.value : -1
        }

        const result = await requestUtil.post('role/save', formData)

        if (result.data && result.data.code === 200) {
          ElMessage.success(isEdit.value ? '编辑成功！' : '添加成功！')
          dialogVisible.value = false
          getRoleList()
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

  // 处理表格选中变化
  const handleSelectionChange = (selection) => {
    selectedRows.value = selection
  }

  // 批量删除
  const handleBatchDelete = async () => {
    if (!selectedRows.value || selectedRows.value.length === 0) {
      ElMessage.warning('请先选择要删除的角色')
      return
    }

    // 检查是否包含超级管理员
    const hasSuperAdmin = selectedRows.value.some(row => row.name === '超级管理员')
    if (hasSuperAdmin) {
      ElMessage.warning('不能删除超级管理员！')
      return
    }

    try {
      await ElMessageBox.confirm(
        `确定要删除选中的 ${selectedRows.value.length} 个角色吗？`,
        '批量删除确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )

      const roleIds = selectedRows.value.map(row => row.id)
      let successCount = 0
      let failCount = 0

      for (const roleId of roleIds) {
        try {
          const result = await requestUtil.post('role/delete', { id: roleId })
          if (result.data && result.data.code === 200) {
            successCount++
          } else {
            failCount++
            console.error(`删除角色 ${roleId} 失败:`, result.data?.errorInfo)
          }
        } catch (error) {
          failCount++
          console.error(`删除角色 ${roleId} 异常:`, error)
        }
      }

      if (successCount > 0) {
        ElMessage.success(`成功删除 ${successCount} 个角色`)
      }

      if (failCount > 0) {
        ElMessage.warning(`${failCount} 个角色删除失败`)
      }

      if (tableRef.value) {
        tableRef.value.clearSelection()
      }
      
      // 批量删除后，计算删除后的总数据量和总页数
      const remainingTotal = total.value - successCount
      const totalPages = Math.ceil(remainingTotal / queryForm.value.pageSize)
      
      // 如果删除后没有数据了，重置为第一页
      if (remainingTotal === 0) {
        queryForm.value.pageNum = 1
      } else if (queryForm.value.pageNum > totalPages) {
        // 如果当前页超出范围，重置为最后一页
        queryForm.value.pageNum = totalPages
      }
      
      await getRoleList()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('批量删除失败:', error)
        ElMessage.error('批量删除失败，请稍后重试')
      }
    }
  }

  // 删除角色
  const handleDelete = async (roleId) => {
    try {
      const result = await requestUtil.post('role/delete', { id: roleId })
      if (result.data && result.data.code === 200) {
        ElMessage.success('删除成功！')
        
        // 删除后检查当前页是否还有数据
        const currentPageDataCount = tableData.value.length
        if (currentPageDataCount === 1 && queryForm.value.pageNum > 1) {
          // 如果当前页只剩一条数据且不是第一页，跳转到上一页
          queryForm.value.pageNum = queryForm.value.pageNum - 1
        } else if (currentPageDataCount === 1 && queryForm.value.pageNum === 1) {
          // 如果第一页只剩一条数据，删除后重置页码
          queryForm.value.pageNum = 1
        }
        
        getRoleList()
      } else {
        ElMessage.error(result.data?.errorInfo || '删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }

  // 分配权限相关
  const dialogPermissionVisible = ref(false)
  const submittingPermission = ref(false)
  const permissionFormRef = ref(null)
  const treeRef = ref(null)
  const currentPermissionRoleId = ref(null)
  const menuTreeData = ref([])

  const dialogPermissionTitle = computed(() => {
    const role = tableData.value.find(r => r.id === currentPermissionRoleId.value)
    return role ? `为 ${role.name} 分配权限` : '分配权限'
  })

  const permissionForm = ref({
    menuIds: []
  })

  // 构建菜单树
  const buildMenuTree = (menuList) => {
    const menuMap = {}
    const rootMenus = []

    // 先创建所有菜单的映射
    menuList.forEach(menu => {
      menuMap[menu.id] = {
        id: menu.id,
        name: menu.name,
        icon: menu.icon,
        path: menu.path,
        children: []
      }
    })

    // 构建树结构
    menuList.forEach(menu => {
      const menuNode = menuMap[menu.id]
      if (menu.parent_id === 0 || !menu.parent_id) {
        rootMenus.push(menuNode)
      } else if (menuMap[menu.parent_id]) {
        menuMap[menu.parent_id].children.push(menuNode)
      }
    })

    return rootMenus
  }

  // 展开所有节点的函数
  const expandAllNodes = () => {
    if (!treeRef.value || !menuTreeData.value.length) return
    
    try {
      // 收集所有节点的 key
      const allNodeKeys = []
      const collectNodeKeys = (nodes) => {
        nodes.forEach(node => {
          allNodeKeys.push(node.id)
          if (node.children && node.children.length > 0) {
            collectNodeKeys(node.children)
          }
        })
      }
      collectNodeKeys(menuTreeData.value)
      
      if (allNodeKeys.length > 0) {
        // 方法1: 使用 setExpandedKeys
        if (treeRef.value.setExpandedKeys) {
          treeRef.value.setExpandedKeys(allNodeKeys)
        }
        
        // 方法2: 直接操作 store（如果 setExpandedKeys 不生效）
        if (treeRef.value.store && treeRef.value.store.nodesMap) {
          allNodeKeys.forEach(key => {
            const node = treeRef.value.store.nodesMap[key]
            if (node && !node.expanded) {
              node.expand()
            }
          })
        }
      }
    } catch (error) {
      console.error('展开节点失败:', error)
    }
  }

  // 监听 menuTreeData 变化，当数据加载完成后自动展开
  watch([menuTreeData, dialogPermissionVisible], ([newData, isVisible]) => {
    if (isVisible && newData && newData.length > 0) {
      nextTick(() => {
        setTimeout(() => {
          expandAllNodes()
        }, 200)
      })
    }
  }, { deep: true })

  // 打开分配权限对话框
  const handlePermissionDialogValue = async (roleId) => {
    try {
      currentPermissionRoleId.value = roleId

      // 获取所有菜单
      const menuResult = await requestUtil.get('menu/searchAllMenu')
      if (menuResult.data && menuResult.data.code === 200) {
        const allMenus = menuResult.data.allMenus || []
        menuTreeData.value = buildMenuTree(allMenus)
      } else {
        ElMessage.error(menuResult.data?.errorInfo || '获取菜单列表失败')
        return
      }

      // 获取当前角色已分配的菜单
      const roleMenuResult = await requestUtil.get('role/getRoleMenus', { roleId: roleId })
      if (roleMenuResult.data && roleMenuResult.data.code === 200) {
        permissionForm.value.menuIds = roleMenuResult.data.menuIds || []
      } else {
        permissionForm.value.menuIds = []
      }

      // 打开对话框（watch 会自动触发展开）
      dialogPermissionVisible.value = true
      
      // 等待DOM更新后设置选中状态和展开节点
      await nextTick()
      await nextTick()
      
      // 多次尝试展开和设置选中状态，确保成功
      const setTreeState = () => {
        if (treeRef.value && menuTreeData.value.length > 0) {
          try {
            // 展开所有节点
            expandAllNodes()
            
            // 设置选中状态
            if (permissionForm.value.menuIds.length > 0 && treeRef.value.setCheckedKeys) {
              treeRef.value.setCheckedKeys(permissionForm.value.menuIds)
            }
          } catch (error) {
            console.error('设置树节点状态失败:', error)
          }
        }
      }
      
      // 立即尝试
      setTreeState()
      
      // 延迟尝试，确保组件完全渲染
      setTimeout(() => {
        setTreeState()
      }, 100)
      
      setTimeout(() => {
        setTreeState()
      }, 300)
    } catch (error) {
      console.error('打开分配权限对话框失败:', error)
      ElMessage.error('获取菜单列表失败，请稍后重试')
    }
  }

  // 提交权限分配
  const handlePermissionSubmit = async () => {
    submittingPermission.value = true
    try {
      // 获取选中的菜单ID
      const checkedKeys = treeRef.value.getCheckedKeys()
      const halfCheckedKeys = treeRef.value.getHalfCheckedKeys()
      const allMenuIds = [...checkedKeys, ...halfCheckedKeys]

      const formData = {
        roleId: currentPermissionRoleId.value,
        menuIds: allMenuIds
      }

      const result = await requestUtil.post('role/assignPermission', formData)

      if (result.data && result.data.code === 200) {
        ElMessage.success('权限分配成功！')
        dialogPermissionVisible.value = false
        getRoleList()
      } else {
        ElMessage.error(result.data?.errorInfo || '权限分配失败')
      }
    } catch (error) {
      console.error('提交权限分配失败:', error)
      ElMessage.error('权限分配失败，请稍后重试')
    } finally {
      submittingPermission.value = false
    }
  }

  // 关闭分配权限对话框
  const handlePermissionDialogClose = () => {
    permissionForm.value.menuIds = []
    currentPermissionRoleId.value = null
    menuTreeData.value = []
  }
</script>

<style lang="scss" scoped>
</style>
