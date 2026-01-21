<template>
  <el-tabs
    v-model="editableTabsValue"
    type="card"
    class="demo-tabs"
    closable
    @tab-remove="removeTab"
   @tab-click="handleTabClick"
  >
    <el-tab-pane
      v-for="item in editableTabs"
      :key="item.path"
      :label="item.title"
      :name="item.path"
    >
      <!-- <component :is="getComponent(item.name)" v-if="getComponent(item.name)" />
      <div v-else class="no-component">
        <el-empty description="该页面正在开发中..." />
      </div> -->
    </el-tab-pane>
  </el-tabs>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'

const store = useStore()
// router: Vue Router 实例，用于路由导航（push、replace、go等方法）
// route: 当前激活的路由对象，包含 path、name、params、query 等信息
const router = useRouter()
const route = useRoute()

// 初始化本地状态
const editableTabsValue = ref(store.state.editableTabsValue)
const editableTabs = ref(store.state.editableTabs)

// 监听 store 中的 tabs 状态变化
watch(
  () => [store.state.editableTabsValue, store.state.editableTabs],
  ([newValue, newTabs]) => {
    editableTabsValue.value = newValue
    editableTabs.value = newTabs
  },
  { deep: true, immediate: true }
)

// 监听路由变化，自动同步 tabs 的激活状态
// 当通过浏览器前进/后退或直接访问 URL 时，确保 tabs 状态与路由一致
watch(
  () => route.path,
  (newPath) => {
    // 如果路由变化了，但 tabs 的激活状态不一致，则同步
    if (editableTabsValue.value !== newPath) {
      editableTabsValue.value = newPath
      store.state.editableTabsValue = newPath
    }
  },
  { immediate: true }
)

const removeTab = (targetPath) => {
  const tabs = editableTabs.value
  let activePath = editableTabsValue.value
  
  if (activePath === targetPath) {
    tabs.forEach((tab, index) => {
      if (tab.path === targetPath) {
        const nextTab = tabs[index + 1] || tabs[index - 1]
        if (nextTab) {
          activePath = nextTab.path
        }
      }
    })
  }
  editableTabsValue.value = activePath
  editableTabs.value = tabs.filter((tab) => tab.path !== targetPath)

  store.state.editableTabsValue = editableTabsValue.value
  store.state.editableTabs = editableTabs.value

  // 关闭当前激活页签后，跳转到新的激活页
  if (activePath) {
    router.push(activePath)
  }
}

// 处理点击 tab，切换到对应页面
const handleTabClick = (tabPane) => {
  console.log('tabPane 对象结构:', tabPane)
  console.log('paneName (对应 el-tab-pane 的 :name 属性):', tabPane?.paneName)
  console.log('pane.props.label (对应 el-tab-pane 的 :label 属性):', tabPane?.pane?.props?.label)
  
  // 方式1: 使用 paneName (推荐，因为 name 对应路由路径)
  const targetPath = tabPane?.paneName
  if (!targetPath) return
  
  editableTabsValue.value = targetPath
  store.state.editableTabsValue = targetPath
  router.push(targetPath)
  
  // 方式2: 如果想通过 label 来路由，需要先找到对应的路由
  // const label = tabPane?.pane?.props?.label  // 例如: "用户管理"
  // const targetRoute = routes.find(r => r.name === label)
  // if (targetRoute) {
  //   router.push({ name: label })
  // }
}

</script>

<style scoped>
.demo-tabs > .el-tabs__content {
  padding: 0;
}

.no-component {
  padding: 40px;
  text-align: center;
}
</style>
