// 引入axios
import axios from 'axios';


// baseUrl 配置
// 开发：.env.development 或 默认；生产：.env.production 的 VUE_APP_BASE_API
const baseUrl = process.env.VUE_APP_BASE_API || 'http://localhost:8080'
// 创建axios实例
const httpService = axios.create({
    // url前缀-'http:xxx.xxx'
    // baseURL: process.env.BASE_API, // 需自定义
    baseURL:baseUrl,
    // 请求超时时间
    timeout: 3000 // 需自定义
});

//添加请求和响应拦截器
// 添加请求拦截器
httpService.interceptors.request.use(function (config) {
    // 在发送请求之前做些什么
    const token = window.sessionStorage.getItem('token');
    if (token) {
        // 使用标准的 Authorization 头部，格式为 Bearer token
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, function (error) {
    // 对请求错误做些什么
    return Promise.reject(error);
});

// 添加响应拦截器
httpService.interceptors.response.use(function (response) {
    // 对响应数据做点什么
    return response;
}, function (error) {
    // 对响应错误做点什么
    console.error('请求错误:', error)
    if (error.response) {
        // 服务器返回了错误状态码
        console.error('错误状态码:', error.response.status)
        console.error('错误响应数据:', error.response.data)
        
        // 如果是401错误（未授权），可能是token过期或无效
        if (error.response.status === 401) {
            console.error('认证失败，可能需要重新登录')
            // 可以在这里清除token并跳转到登录页
            // window.sessionStorage.removeItem('token')
            // window.location.href = '/login'
        }
        
        // 如果后端返回了JSON格式的错误信息，尝试解析
        if (error.response.data && typeof error.response.data === 'string') {
            try {
                const errorData = JSON.parse(error.response.data)
                error.response.data = errorData
            } catch (e) {
                // 如果不是JSON，保持原样
            }
        }
    } else if (error.request) {
        // 请求已发出，但没有收到响应
        console.error('请求超时或网络错误:', error.request)
    } else {
        // 其他错误
        console.error('请求配置错误:', error.message)
    }
    return Promise.reject(error);
});

/*网络请求部分*/

/*
 *  get请求
 *  url:请求地址
 *  params:参数
 * */
export function get(url, params = {}) {
    return new Promise((resolve, reject) => {
        httpService({
            url: url,
            method: 'get',
            params: params
        }).then(response => {
            resolve(response);
        }).catch(error => {
            reject(error);
        });
    });
}

/*
 *  post请求
 *  url:请求地址
 *  params:参数
 * */
export function post(url, params = {}) {
    return new Promise((resolve, reject) => {
        httpService({
            url: url,
            method: 'post',
            data: params
        }).then(response => {
            console.log(response)
            resolve(response);
        }).catch(error => {
            console.log(error)
            reject(error);
        });
    });
}

/*
 *  delete请求
 *  url:请求地址
 *  params:参数
 * */
export function del(url, params = {}) {
    return new Promise((resolve, reject) => {
        httpService({
            url: url,
            method: 'delete',
            data: params
        }).then(response => {
            console.log(response)
            resolve(response);
        }).catch(error => {
            console.log(error)
            reject(error);
        });
    });
}


/*
 *  文件上传
 *  url:请求地址
 *  params:参数
 * */
export function fileUpload(url, params = {}) {
    return new Promise((resolve, reject) => {
        // 当使用 FormData 时，不设置 Content-Type，让浏览器自动设置（包括边界）
        const config = {
            url: url,
            method: 'post',
            data: params
        }
        // 只有当 params 不是 FormData 时才设置 Content-Type
        if (!(params instanceof FormData)) {
            config.headers = { 'Content-Type': 'multipart/form-data' }
        }
        httpService(config).then(response => {
            resolve(response);
        }).catch(error => {
            reject(error);
        });
    });
}

export function getServerUrl(){
    return baseUrl;
}

export default {
    get,
    post,
    del,
    fileUpload,
    getServerUrl
}
