const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  
  // 开发服务器配置
  devServer: {
    port: 8081, // 前端运行端口（改为 8081，避免与后端 8080 冲突）
    open: true, // 自动打开浏览器
    // Dashboard 默认运行在 8000 端口，这是独立的服务
    
    // 配置代理，解决 CORS 跨域问题（如果后端没有配置 CORS，使用代理）
    proxy: {
      '/user': {
        target: 'http://localhost:8080', // 后端 API 地址（8080 端口）
        changeOrigin: true, // 允许跨域
        // pathRewrite: {
        //   '^/user': '/user' // 如果后端路径不同，可以重写路径
        // }
      }
    }
  }
})
