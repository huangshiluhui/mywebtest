const { defineConfig } = require('@vue/cli-service')
const path = require('path')

function resolve(dir) {
  return path.join(__dirname, dir)
}

module.exports = defineConfig({
  transpileDependencies: true,
  
  // 开发服务器配置
  devServer: {
    port: 8081, // 前端运行端口（改为 8081，避免与后端 8000 冲突）
    open: true, // 自动打开浏览器
    host: '0.0.0.0', // 绑定到所有网络接口，允许局域网访问
    allowedHosts: 'all', // 允许所有主机访问（有助于显示 Network 地址）
    // 或者使用 client: { webSocketURL: 'auto://0.0.0.0:0/ws' } 来强制显示
  },
  
  // 配置 webpack
  chainWebpack(config) {
    // 设置 svg-sprite-loader
    config.module
      .rule('svg')
      .exclude.add(resolve('src/icons/svg'))
      .end()
    config.module
      .rule('icons')
      .test(/\.svg$/)
      .include.add(resolve('src/icons/svg'))
      .end()
      .use('svg-sprite-loader')
      .loader('svg-sprite-loader')
      .options({
        symbolId: 'icon-[name]'
      })
      .end()
  }
})
