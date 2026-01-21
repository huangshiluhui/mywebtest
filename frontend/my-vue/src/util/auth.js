/**
 * 检查用户是否已登录
 * @returns {boolean}
 */
export function isLoggedIn() {
    const token = window.sessionStorage.getItem('token')
    return !!token
  }
  
  /**
   * 获取当前用户信息
   * @returns {Object|null}
   */
  export function getCurrentUser() {
    const userStr = window.sessionStorage.getItem('currentUser')
    if (userStr) {
      try {
        return JSON.parse(userStr)
      } catch (error) {
        console.error('解析用户信息失败:', error)
        return null
      }
    }
    return null
  }
  
  /**
   * 退出登录
   */
  export function logout() {
    window.sessionStorage.removeItem('token')
    window.sessionStorage.removeItem('currentUser')
    window.sessionStorage.removeItem('menuList')
  }
  