<template>
	<view class="index-container">
		<!-- 顶部欢迎区域 -->
		<view class="welcome-section">
			<view class="welcome-content">
				<text class="welcome-text">欢迎您，{{ userInfo.user_name || '用户' }}</text>
				<text class="date-text">{{ currentDate }}</text>
			</view>
			<image src="/static/logo.png" class="avatar" mode="aspectFit"></image>
		</view>

		<!-- 功能模块 -->
		<view class="module-section">
			<view class="module-grid">
				<!-- 我的课表 -->
				<view class="module-item" @tap="navigateTo('/pages/timetable/timetable')">
					<view class="module-icon timetable">
						<text class="icon-text">课</text>
					</view>
					<text class="module-title">我的课表</text>
				</view>

				<!-- 我的评教 -->
				<view class="module-item" @tap="navigateTo('/pages/evaluation/my-evaluations')">
					<view class="module-icon my-eval">
						<text class="icon-text">我的</text>
					</view>
					<text class="module-title">我的评教</text>
				</view>

				<!-- 收到的评教 -->
				<view class="module-item" @tap="navigateTo('/pages/evaluation/received-evaluations')">
					<view class="module-icon received-eval">
						<text class="icon-text">收</text>
					</view>
					<text class="module-title">收到的评教</text>
				</view>

				<!-- 个人统计 -->
				<view class="module-item" @tap="navigateTo('/pages/statistics/personal')">
					<view class="module-icon stats">
						<text class="icon-text">统</text>
					</view>
					<text class="module-title">个人统计</text>
				</view>

				<!-- 个人信息 -->
				<view class="module-item" @tap="navigateTo('/pages/profile/profile')">
					<view class="module-icon profile">
						<text class="icon-text">我</text>
					</view>
					<text class="module-title">个人信息</text>
				</view>

				<!-- 管理员功能入口 -->
				<view class="module-item" v-if="userInfo.roles_code && userInfo.roles_code.includes('school_admin')" @tap="showAdminMenu">
					<view class="module-icon admin">
						<text class="icon-text">管</text>
					</view>
					<text class="module-title">系统管理</text>
				</view>
			</view>

			<!-- 统计信息卡片 -->
			<view class="stats-section">
				<view class="stats-card">
					<view class="stats-item" @tap="navigateTo('/pages/evaluation/pending-courses')">
						<text class="stats-label">待评课程</text>
						<text class="stats-value">{{ pendingCoursesCount }}</text>
						<text class="stats-desc">需要完成的评教任务</text>
					</view>
					<view class="stats-divider"></view>
					<view class="stats-item" @tap="navigateTo('/pages/evaluation/completed-courses')">
						<text class="stats-label">已评课程</text>
						<text class="stats-value">{{ completedCoursesCount }}</text>
						<text class="stats-desc">已完成的评教任务</text>
					</view>
					<view class="stats-divider"></view>
					<view class="stats-item">
						<text class="stats-label">总评教数</text>
						<text class="stats-value">{{ pendingCoursesCount + completedCoursesCount }}</text>
						<text class="stats-desc">本学期总评教任务</text>
					</view>
				</view>
			</view>

			<!-- 最新评教记录 -->
			<view class="latest-evaluations-section">
				<view class="section-header">
					<text class="section-title">最新评教记录</text>
					<text class="more" @tap="navigateTo('/pages/evaluation/my-evaluations')">查看更多 ></text>
				</view>
				<view class="evaluations-list">
					<view v-if="latestEvaluations.length === 0" class="empty-text">
						暂无评教记录
					</view>
					<view v-for="evaluation in latestEvaluations" :key="evaluation.id" class="evaluation-item">
						<view class="evaluation-header">
							<text class="evaluation-no">评教编号: {{ evaluation.evaluation_no || 'N/A' }}</text>
							<text class="evaluation-score">{{ evaluation.total_score || 0 }} 分</text>
						</view>
						<view class="evaluation-info">
							<text class="evaluation-date">
								{{ evaluation.listen_date ? new Date(evaluation.listen_date).toLocaleDateString() : 'N/A' }}
							</text>
							<text
								class="evaluation-status"
								:class="{
									'status-valid': evaluation.status === 1,
									'status-pending': evaluation.status === 2,
									'status-rejected': evaluation.status === 3
								}"
							>
								{{
									evaluation.status === 1
										? '有效'
										: evaluation.status === 2
											? '待审核'
											: evaluation.status === 3
												? '已驳回'
												: '未知'
								}}
							</text>
						</view>
					</view>
				</view>
			</view>
		</view>

		<!-- 管理员菜单弹窗 -->
		<view class="admin-menu-modal" v-if="showAdminMenuModal" @tap="hideAdminMenu">
			<view class="admin-menu-content" @tap.stop>
				<view class="menu-header">
					<text class="menu-title">系统管理</text>
					<text class="menu-close" @tap="hideAdminMenu">×</text>
				</view>
				<view class="menu-list">
					<view class="menu-item" @tap="navigateToAdmin('/pages/admin/user-management')">
						<text class="menu-text">用户管理</text>
						<text class="arrow">></text>
					</view>
					<view class="menu-item" @tap="navigateToAdmin('/pages/admin/evaluation-review')">
						<text class="menu-text">评教审核</text>
						<text class="arrow">></text>
					</view>
					<view class="menu-item" @tap="navigateToAdmin('/pages/admin/statistics')">
						<text class="menu-text">数据统计</text>
						<text class="arrow">></text>
					</view>
					<view class="menu-item" @tap="navigateToAdmin('/pages/admin/college-management')">
						<text class="menu-text">学院管理</text>
						<text class="arrow">></text>
					</view>
					<view class="menu-item" @tap="navigateToAdmin('/pages/admin/course-status-management')">
						<text class="menu-text">课程状态管理</text>
						<text class="arrow">></text>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { request } from '../../common/request.js';

export default {
	name: 'index',
	data() {
		return {
			userInfo: {},
			currentDate: '',
			pendingCoursesCount: 0,
			completedCoursesCount: 0,
			latestEvaluations: [],
			showAdminMenuModal: false,

			// ===== 方案A关键：首次进入时，onShow 紧跟 onLoad 会重复请求，这里用标记跳过一次 =====
			skipFirstShowRefresh: true,

			// ===== 额外：防止 getEvaluationStats 在短时间内被多次触发导致并发重复请求 =====
			statsLoading: false
		};
	},
	onLoad() {
		// 首次进入：在 onLoad 里请求一次
		this.getUserInfo();
		this.setCurrentDate();
		this.getEvaluationStats();
	},
	onShow() {
		// 首次进入时 onShow 会紧跟 onLoad 触发一次，这里跳过，避免重复请求
		if (this.skipFirstShowRefresh) {
			this.skipFirstShowRefresh = false;
			return;
		}

		// 之后每次页面显示时刷新数据
		this.getUserInfo();
		this.getEvaluationStats();
	},
	methods: {
		// 获取用户信息
		async getUserInfo() {
			try {
				const res = await request({
					url: '/user/me',
					method: 'GET'
				});

				// 提取用户信息，包括roles_code等字段
				const userInfo = {
					...(res.user || {}),
					roles_code: res.roles_code || [],
					roles_name: res.roles_name || [],
					permissions: res.permissions || []
				};

				// 保存到本地
				uni.setStorageSync('userInfo', userInfo);
				this.userInfo = userInfo;
			} catch (error) {
				console.error('获取用户信息失败:', error);

				// 如果获取失败，可能是登录过期，跳转到登录页面
				if (error.code === 401) {
					uni.removeStorageSync('token');
					uni.removeStorageSync('userInfo');
					uni.navigateTo({
						url: '/pages/login/login'
					});
				}
			}
		},

		// 设置当前日期
		setCurrentDate() {
			const now = new Date();
			const year = now.getFullYear();
			const month = String(now.getMonth() + 1).padStart(2, '0');
			const day = String(now.getDate()).padStart(2, '0');
			const week = ['日', '一', '二', '三', '四', '五', '六'][now.getDay()];
			this.currentDate = `${year}-${month}-${day} 星期${week}`;
		},

		// 跳转到指定页面
		navigateTo(url) {
			// 定义tabBar页面列表
			const tabBarPages = [
				'/pages/index/index',
				'/pages/timetable/timetable',
				'/pages/evaluation/my-evaluations',
				'/pages/statistics/personal',
				'/pages/profile/profile'
			];
			
			// 判断是否为tabBar页面
			if (tabBarPages.includes(url)) {
				// 使用switchTab跳转tabBar页面
				uni.switchTab({
					url
				});
			} else {
				// 使用navigateTo跳转普通页面
				uni.navigateTo({
					url
				});
			}
		},

		// 显示管理员菜单
		showAdminMenu() {
			this.showAdminMenuModal = true;
		},

		// 隐藏管理员菜单
		hideAdminMenu() {
			this.showAdminMenuModal = false;
		},

		// 导航到管理员页面
		navigateToAdmin(url) {
			// 关闭菜单
			this.hideAdminMenu();
			// 跳转到指定页面
			uni.navigateTo({
				url
			});
		},

		// 获取评教相关统计数据
		async getEvaluationStats() {
			// 防止短时间内重复触发导致并发重复请求
			if (this.statsLoading) return;
			this.statsLoading = true;

			try {
				// 并发请求所有数据
				const [pendingCourses, completedCourses, latestEvaluations] = await Promise.all([
					this.getPendingCourses(),
					this.getCompletedCourses(),
					this.getLatestEvaluations()
				]);

				// 更新数据
				this.pendingCoursesCount = pendingCourses.total || 0;
				this.completedCoursesCount = completedCourses.total || 0;
				this.latestEvaluations = latestEvaluations.list || [];
			} catch (error) {
				console.error('获取评教统计数据失败:', error);
			} finally {
				this.statsLoading = false;
			}
		},

		// 获取待评课程数量
		async getPendingCourses() {
			try {
				const res = await request({
					url: '/eval/pending-courses',
					method: 'GET',
					params: {
						page: 1,
						page_size: 1
					}
				});
				return res || { total: 0 };
			} catch (error) {
				console.error('获取待评课程失败:', error);
				return { total: 0 };
			}
		},

		// 获取已评课程数量
		async getCompletedCourses() {
			try {
				const res = await request({
					url: '/eval/completed-courses',
					method: 'GET',
					params: {
						page: 1,
						page_size: 1
					}
				});
				return res || { total: 0 };
			} catch (error) {
				console.error('获取已评课程失败:', error);
				return { total: 0 };
			}
		},

		// 获取最新的评教记录
		async getLatestEvaluations() {
			try {
				const res = await request({
					url: '/eval/mine',
					method: 'GET',
					params: {
						page: 1,
						page_size: 3
					}
				});
				return res || { list: [] };
			} catch (error) {
				console.error('获取最新评教记录失败:', error);
				return { list: [] };
			}
		}
	}
};
</script>

<style scoped>
.index-container {
	background-color: #F5F7FA;
	min-height: 100vh;
	padding-bottom: 100rpx;
}

/* 欢迎区域 */
.welcome-section {
	background-color: #3E5C76;
	color: #FFFFFF;
	padding: 30rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.welcome-content {
	flex: 1;
}

.welcome-text {
	font-size: 36rpx;
	font-weight: bold;
	display: block;
	margin-bottom: 10rpx;
}

.date-text {
	font-size: 24rpx;
	opacity: 0.9;
}

.avatar {
	width: 100rpx;
	height: 100rpx;
	border-radius: 50rpx;
	background-color: #FFFFFF;
	padding: 10rpx;
}

/* 功能模块 */
.module-section {
	padding: 30rpx;
	background-color: #FFFFFF;
	margin-top: 20rpx;
}

.module-grid {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 30rpx;
}

.module-item {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 20rpx;
	background-color: #F5F7FA;
	border-radius: 16rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.module-item:active {
	background-color: #E9EDF2;
}

.module-icon {
	width: 100rpx;
	height: 100rpx;
	border-radius: 50rpx;
	display: flex;
	justify-content: center;
	align-items: center;
	margin-bottom: 15rpx;
}

.module-icon.submit {
	background-color: #FF6B6B;
}

.module-icon.timetable {
	background-color: #4ECDC4;
}

.module-icon.my-eval {
	background-color: #45B7D1;
}

.module-icon.received-eval {
	background-color: #96CEB4;
}

.module-icon.stats {
	background-color: #FFEAA7;
}

.module-icon.profile {
	background-color: #DDA0DD;
}

.module-icon.admin {
	background-color: #FF6B6B;
}

.icon-text {
	font-size: 40rpx;
	font-weight: bold;
	color: #FFFFFF;
}

.module-title {
	font-size: 26rpx;
	color: #333333;
	font-weight: 500;
}

/* 公共样式 */
.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

.more {
	font-size: 24rpx;
	color: #666666;
}

/* 统计信息卡片 */
.stats-section {
	padding: 0 30rpx;
	margin-top: 20rpx;
}

.stats-card {
	background-color: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	display: flex;
	justify-content: space-around;
	align-items: center;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.stats-item {
	flex: 1;
	text-align: center;
}

.stats-divider {
	width: 2rpx;
	height: 100rpx;
	background-color: #F5F7FA;
	margin: 0 20rpx;
}

.stats-label {
	font-size: 26rpx;
	color: #666666;
	display: block;
	margin-bottom: 10rpx;
}

.stats-value {
	font-size: 48rpx;
	font-weight: bold;
	color: #3E5C76;
	display: block;
	margin-bottom: 10rpx;
}

.stats-desc {
	font-size: 22rpx;
	color: #999999;
	display: block;
}

/* 最新评教记录 */
.latest-evaluations-section {
	padding: 0 30rpx;
	margin-top: 20rpx;
	background-color: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

.more {
	font-size: 24rpx;
	color: #666666;
}

.evaluations-list {
	max-height: 300rpx;
}

.evaluation-item {
	padding: 20rpx 0;
	border-bottom: 2rpx solid #F5F7FA;
}

.evaluation-item:last-child {
	border-bottom: none;
}

.evaluation-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 10rpx;
}

.evaluation-no {
	font-size: 26rpx;
	color: #333333;
}

.evaluation-score {
	font-size: 28rpx;
	font-weight: bold;
	color: #FF6B6B;
}

.evaluation-info {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.evaluation-date {
	font-size: 24rpx;
	color: #666666;
}

.evaluation-status {
	font-size: 24rpx;
	padding: 4rpx 16rpx;
	border-radius: 12rpx;
	font-weight: 500;
}

.status-valid {
	background-color: #E8F5E8;
	color: #4CAF50;
}

.status-pending {
	background-color: #FFF3E0;
	color: #FF9800;
}

.status-rejected {
	background-color: #FFEBEE;
	color: #F44336;
}

/* 空状态 */
.empty-text {
	text-align: center;
	padding: 60rpx 0;
	color: #999999;
	font-size: 26rpx;
}

/* 管理员菜单弹窗 */
.admin-menu-modal {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0.5);
	display: flex;
	justify-content: center;
	align-items: center;
	z-index: 9999;
}

.admin-menu-content {
	background-color: #FFFFFF;
	border-radius: 20rpx;
	width: 80%;
	max-width: 500rpx;
	box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.2);
}

.menu-header {
	padding: 25rpx 30rpx;
	border-bottom: 2rpx solid #F5F7FA;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.menu-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

.menu-close {
	font-size: 40rpx;
	color: #C0C4CC;
	padding: 8rpx;
}

.menu-list {
	padding: 0;
}

.menu-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	height: 110rpx;
	padding: 0 30rpx;
	border-bottom: 2rpx solid #F5F7FA;
}

.menu-item:last-child {
	border-bottom: none;
}

.menu-text {
	font-size: 28rpx;
	color: #333333;
}

.arrow {
	font-size: 32rpx;
	color: #C0C4CC;
}
</style>
