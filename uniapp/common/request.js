import {
	baseUrl
} from './config.js';

/**
 * 全局请求封装函数 - 统一处理请求和响应
 * 
 * 功能：
 * 1. 自动携带认证令牌
 * 2. 统一处理成功和失败响应
 * 3. 自动更新认证令牌
 * 4. 针对登录和获取角色请求的特殊处理
 * 5. 支持GET请求URL传参
 * 
 * @param {Object} options - 请求配置对象
 * @param {string} options.url - 请求地址
 * @param {string} [options.method='GET'] - 请求方法
 * @param {Object} [options.data={}] - 请求数据（POST/PUT请求使用）
 * @param {Object} [options.params={}] - URL查询参数（GET请求使用）
 * @param {Object} [options.header={}] - 自定义请求头
 * @returns {Promise} - 返回Promise对象
 */
export const request = (options) => {
	return new Promise((resolve, reject) => {
		// 从本地存储获取认证令牌
		const token = uni.getStorageSync('token');
		// 构造请求头，包含Content-Type和认证信息
		const header = {
			'content-type': 'application/json',
			...options.header // 合并用户传入的自定义请求头
		};
		// 如果存在认证令牌，则添加到请求头中
		if (token) {
			header.Authorization = `Bearer ${token}`;
		}

		// 处理URL查询参数
		let requestUrl = baseUrl + options.url;
		const params = options.params || {};
		const method = options.method || 'GET';
		const data = options.data || {};
		
		// 对于所有请求，将params参数转换为URL查询字符串
		const queryParams = Object.keys(params)
			.filter(key => params[key] !== undefined && params[key] !== null)
			.map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
			.join('&');
		
		if (queryParams) {
			requestUrl += (requestUrl.includes('?') ? '&' : '?') + queryParams;
		}

		console.log('请求地址：', requestUrl);
		uni.request({
			url: requestUrl,
			method: method,
			data: method.toUpperCase() === 'GET' ? {} : data,
			header: header,
			success: (res) => {
				// 解析响应数据
				// 标准响应格式：{code: number, msg: string, data: object}
				const responseData = res.data || {};
				const {
					code,
					msg
				} = responseData;
				// 业务成功：code=200，解析并返回业务数据
				if (code === 200) {
					console.log("后端返回：", responseData)
					// 检查响应头中的认证令牌
					const authHeader = res.header['authorization'] || res.header[
						'Authorization'];
					if (authHeader) {
						// 提取并保存新的认证令牌
						const token = authHeader.replace('Bearer ', '');
						uni.setStorageSync('token', token); // 更新本地存储中的令牌
					}
					// 成功时返回业务数据
					resolve(responseData.data || responseData);
				}
				// 认证失败：code=401，处理令牌过期
				else if (code === 401) {
					// 登录和获取角色请求不自动跳转，由调用方处理
					const isLoginOrRoleRequest = options.url.includes('/user/login') || options.url.includes('/user/role');
					if (isLoginOrRoleRequest) {
						reject(responseData);
					} else {
						uni.showToast({
							title: msg || '登录已过期，请重新登录',
							icon: 'none',
							duration: 2000
						});
						uni.removeStorageSync('token'); // 清除失效Token
						uni.redirectTo({
							url: '/pages/login/login'
						});
						reject(responseData);
					}
				}
				// 业务请求失败：处理非200状态码
				else {
					// 登录和获取角色请求不显示通用错误提示，由调用方处理
					const isLoginOrRoleRequest = options.url.includes('/user/login') || options.url.includes('/user/role');
					if (isLoginOrRoleRequest) {
						reject(responseData);
					} else {
						const errorMsg = msg || '接口请求失败，请稍后重试';
						uni.showToast({
							title: errorMsg,
							icon: 'none',
							duration: 2000
						});
						reject(responseData);
					}
				}
			},
			fail: (err) => {
				// 网络请求失败：断网、域名错误、超时等
				uni.showToast({
					title: '网络请求失败，请检查网络',
					icon: 'none',
					duration: 2000
				});
				// 将网络错误传递给调用方
				reject(err);
			}
		});
	});
};