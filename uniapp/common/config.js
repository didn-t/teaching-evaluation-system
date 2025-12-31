// 环境区分：开发环境（true） / 生产环境（根据需求切换）
const isDev = true; 

// 配置各环境的接口基地址
//结尾一定不要有 ‘/’;例如：'http://127.0.0.1:8080' 不能 'http://127.0.0.1:8080/' 
export const baseUrl = isDev 
    ? 'http://127.0.0.1:8000/api/v1/teaching-eval' // 本地后端地址（开发用）
    : 'http://pingjiao.205266.xyz/api/v1/teaching-eval';  // 线上正式地址（发布用）