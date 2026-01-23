<template>
  <div>
    <el-row :gutter="20" class="header" style="margin-bottom: 20px;">
      <el-col :span="24" style="text-align: right;">
        <el-button type="success" :icon="DocumentAdd" @click="handleDialogValue()">新增</el-button>
        <el-button :icon="isExpanded ? ArrowDown : ArrowRight" @click="toggleExpandAll">
          {{ isExpanded ? '折叠' : '展开' }}
        </el-button>
      </el-col>
    </el-row>

    <el-table 
      ref="tableRef"
      :data="tableData" 
      stripe 
      border
      style="width: 100%"
      row-key="id"
      :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      :default-expand-all="isExpanded"
    >
      <el-table-column prop="name" label="菜单名称" width="200" show-overflow-tooltip>
        <template #default="scope">
          <span v-if="scope.row.icon" style="margin-right: 5px;">
            <login-icon :icon="scope.row.icon" />
          </span>
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column prop="icon" label="图标" width="100" align="center">
        <template #default="scope">
          <login-icon v-if="scope.row.icon" :icon="scope.row.icon" />
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="order_num" label="排序" width="80" align="center"/>
      <el-table-column prop="perms" label="权限标识" width="200" show-overflow-tooltip>
        <template #default="scope">
          {{ scope.row.perms || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="path" label="组件路径" width="200" show-overflow-tooltip>
        <template #default="scope">
          {{ scope.row.path || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="menu_type" label="菜单类型" width="100" align="center">
        <template #default="scope">
          <el-tag v-if="scope.row.menu_type === 'M'" type="info">目录</el-tag>
          <el-tag v-else-if="scope.row.menu_type === 'C'" type="success">菜单</el-tag>
          <el-tag v-else-if="scope.row.menu_type === 'F'" type="warning">按钮</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="120" align="center"/>
      <el-table-column prop="action" label="操作" width="200" fixed="right" align="center">
        <template v-slot="scope">
          <el-button type="primary" :icon="Edit" size="small" @click="handleDialogValue(scope.row.id)">
            编辑
          </el-button>
          <el-popconfirm 
            title="您确定要删除这条记录吗？"
            @confirm="handleDelete(scope.row.id)"
          >
            <template #reference>
              <el-button type="danger" :icon="Delete" size="small"/>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑菜单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="menuFormRef"
        :model="menuForm"
        :rules="menuFormRules"
        label-width="100px"
      >
        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="menuForm.name" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item label="父菜单" prop="parent_id">
          <el-select
            v-model="menuForm.parent_id"
            placeholder="请选择父菜单（不选则为顶级菜单）"
            clearable
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="menu in flatMenuOptions"
              :key="menu.id"
              :label="menu.label"
              :value="menu.id"
              :disabled="isEdit && menu.id === currentMenuId"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="显示顺序" prop="order_num">
          <el-input-number v-model="menuForm.order_num" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="路由地址" prop="path">
          <el-input v-model="menuForm.path" placeholder="请输入路由地址，如：/sys/user" />
        </el-form-item>
        <el-form-item label="组件路径" prop="component">
          <el-input v-model="menuForm.component" placeholder="请输入组件路径，如：sys/user/IndexView" />
        </el-form-item>
        <el-form-item label="菜单类型" prop="menu_type">
          <el-radio-group v-model="menuForm.menu_type">
            <el-radio label="M">目录</el-radio>
            <el-radio label="C">菜单</el-radio>
            <el-radio label="F">按钮</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="权限标识" prop="perms">
          <el-input v-model="menuForm.perms" placeholder="请输入权限标识，如：system:user:list" />
        </el-form-item>
        <el-form-item label="菜单图标" prop="icon">
          <el-input v-model="menuForm.icon" placeholder="请输入图标名称，如：User" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="menuForm.remark"
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
  </div>
</template>

<script setup>
  import { ref, onMounted, computed } from 'vue'
  import { DocumentAdd, Edit, Delete, ArrowDown, ArrowRight } from '@element-plus/icons-vue'
  import requestUtil from '@/util/request'
  import { ElMessage } from 'element-plus'
  import LoginIcon from '@/components/SvgIcon/LoginIcon.vue'

  const tableData = ref([])
  const tableRef = ref(null)
  const isExpanded = ref(true)
  const menuTreeOptions = ref([])
  
  // 扁平化菜单选项（用于下拉选择）
  const flatMenuOptions = computed(() => {
    const flatten = (menus, level = 0, excludeIds = []) => {
      const result = []
      menus.forEach(menu => {
        // 排除自己和自己的子菜单
        if (excludeIds.includes(menu.id)) {
          return
        }
        const prefix = '  '.repeat(level)
        result.push({
          id: menu.id,
          label: prefix + menu.name
        })
        if (menu.children && menu.children.length > 0) {
          result.push(...flatten(menu.children, level + 1, excludeIds))
        }
      })
      return result
    }
    
    // 编辑时，排除当前菜单及其所有子菜单
    const excludeIds = []
    if (isEdit.value && currentMenuId.value) {
      const findChildrenIds = (menus, targetId) => {
        const ids = []
        for (const menu of menus) {
          if (menu.id === targetId) {
            ids.push(menu.id)
            if (menu.children && menu.children.length > 0) {
              const collectChildren = (children) => {
                children.forEach(child => {
                  ids.push(child.id)
                  if (child.children && child.children.length > 0) {
                    collectChildren(child.children)
                  }
                })
              }
              collectChildren(menu.children)
            }
            break
          }
          if (menu.children && menu.children.length > 0) {
            const found = findChildrenIds(menu.children, targetId)
            if (found.length > 0) {
              ids.push(...found)
              break
            }
          }
        }
        return ids
      }
      excludeIds.push(...findChildrenIds(menuTreeOptions.value, currentMenuId.value))
    }
    
    return flatten(menuTreeOptions.value, 0, excludeIds)
  })

  // 对话框相关
  const dialogVisible = ref(false)
  const submitting = ref(false)
  const menuFormRef = ref(null)
  const isEdit = ref(false)
  const currentMenuId = ref(null)

  // 对话框标题
  const dialogTitle = computed(() => {
    return isEdit.value ? '菜单编辑' : '菜单添加'
  })

  // 菜单表单数据
  const menuForm = ref({
    name: '',
    parent_id: null,
    order_num: 0,
    path: '',
    component: '',
    menu_type: 'C',
    perms: '',
    icon: '',
    remark: ''
  })

  // 表单验证规则
  const menuFormRules = {
    name: [
      { required: true, message: '请输入菜单名称', trigger: 'blur' }
    ],
    menu_type: [
      { required: true, message: '请选择菜单类型', trigger: 'change' }
    ]
  }

  // 获取菜单列表
  const getMenuList = async () => {
    try {
      const result = await requestUtil.get('menu/search')
      if (result.data && result.data.code === 200) {
        tableData.value = result.data.menuList || []
        // 同时更新树形选择器的数据
        menuTreeOptions.value = result.data.menuList || []
      } else {
        console.error('获取菜单列表失败:', result.data?.errorInfo)
        ElMessage.error(result.data?.errorInfo || '获取菜单列表失败')
      }
    } catch (error) {
      console.error('请求失败:', error)
      ElMessage.error('获取菜单列表失败，请稍后重试')
    }
  }

  // 切换展开/折叠
  const toggleExpandAll = () => {
    isExpanded.value = !isExpanded.value
    toggleTreeExpansion(tableData.value, isExpanded.value)
  }

  // 递归展开/折叠所有节点
  const toggleTreeExpansion = (data, expand) => {
    data.forEach(row => {
      if (tableRef.value) {
        tableRef.value.toggleRowExpansion(row, expand)
        if (row.children && row.children.length > 0) {
          toggleTreeExpansion(row.children, expand)
        }
      }
    })
  }

  // 组件挂载时获取数据
  onMounted(() => {
    getMenuList()
  })

  // 重置表单
  const resetForm = () => {
    menuForm.value = {
      name: '',
      parent_id: null,
      order_num: 0,
      path: '',
      component: '',
      menu_type: 'C',
      perms: '',
      icon: '',
      remark: ''
    }
    if (menuFormRef.value) {
      menuFormRef.value.clearValidate()
    }
  }

  // 打开对话框
  const handleDialogValue = (id) => {
    if (id) {
      // 编辑模式
      isEdit.value = true
      currentMenuId.value = id
      // 从表格数据中查找菜单
      const findMenu = (menus, targetId) => {
        for (const menu of menus) {
          if (menu.id === targetId) {
            return menu
          }
          if (menu.children && menu.children.length > 0) {
            const found = findMenu(menu.children, targetId)
            if (found) return found
          }
        }
        return null
      }
      const menu = findMenu(tableData.value, id)
      if (menu) {
        menuForm.value = {
          name: menu.name || '',
          parent_id: (menu.parent_id && menu.parent_id !== 0) ? menu.parent_id : null,
          order_num: menu.order_num || 0,
          path: menu.path || '',
          component: menu.component || '',
          menu_type: menu.menu_type || 'C',
          perms: menu.perms || '',
          icon: menu.icon || '',
          remark: menu.remark || ''
        }
        // 编辑时不能选择自己作为父菜单
      }
    } else {
      // 新增模式
      isEdit.value = false
      currentMenuId.value = null
      resetForm()
    }
    dialogVisible.value = true
  }

  // 关闭对话框
  const handleDialogClose = () => {
    resetForm()
    isEdit.value = false
    currentMenuId.value = null
  }

  // 提交表单
  const handleSubmit = async () => {
    if (!menuFormRef.value) return

    await menuFormRef.value.validate(async (valid) => {
      if (!valid) {
        return false
      }

      submitting.value = true
      try {
        const formData = {
          ...menuForm.value,
          id: isEdit.value ? currentMenuId.value : -1,
          parent_id: menuForm.value.parent_id || 0
        }

        const result = await requestUtil.post('menu/save', formData)

        if (result.data && result.data.code === 200) {
          ElMessage.success(isEdit.value ? '编辑成功！' : '添加成功！')
          dialogVisible.value = false
          getMenuList()
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

  // 删除菜单
  const handleDelete = async (menuId) => {
    try {
      const result = await requestUtil.post('menu/delete', { id: menuId })
      if (result.data && result.data.code === 200) {
        ElMessage.success('删除成功！')
        getMenuList()
      } else {
        ElMessage.error(result.data?.errorInfo || '删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }
</script>

<style lang="scss" scoped>
</style>
