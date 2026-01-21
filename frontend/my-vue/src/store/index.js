import { createStore } from 'vuex'

export default createStore({
    state: {
        editableTabsValue:'/index',
        editableTabs:[
            {
                title:'首页',
                path:'/index'
            }
        ]
    },
    getters: {
    },
    mutations: {
        ADD_TABS:(state,tab)=>{
            if(state.editableTabs.findIndex(e=>e.path===tab.path)===-1){
              state.editableTabs.push({
                title:tab.name,
                path:tab.path
              })
            }
        state.editableTabsValue=tab.path
        },

        REMOVE_TAB:(state, { targetPath, activePath })=>{
            state.editableTabs = state.editableTabs.filter(tab => tab.path !== targetPath)
            state.editableTabsValue = activePath
        },

        RESET_TAB:(state)=>{
            state.editableTabsValue='/index'
            state.editableTabs=[
                {
                    title:'首页',
                    path:'/index'
                }
            ]
        }
     },
    actions: {
    },
    modules: {
    }
})
