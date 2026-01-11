const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  
  // 开发服务器配置
  devServer: {
    port: 8081, // 前端运行端口（改为 8081，避免与后端 8000 冲突）
    open: true, // 自动打开浏览器
  }
})
