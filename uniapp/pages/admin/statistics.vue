<template>
	<view class="admin-container">
		<view class="page-header">
			<text class="page-title">数据统计</text>
		</view>

		<view class="tabs">
			<view class="tab" :class="activeTab === 'school' ? 'active' : ''" @tap="switchTab('school')" v-if="isSchoolAdmin">全校</view>
			<view class="tab" :class="activeTab === 'college' ? 'active' : ''" @tap="switchTab('college')">学院</view>
			<view class="tab" :class="activeTab === 'ranking' ? 'active' : ''" @tap="switchTab('ranking')">教师排名</view>
			<!-- 22300417陈俫坤开发：学院管理员/学校管理员专用统计Tab -->
			<view class="tab" :class="activeTab === 'listen_stat' ? 'active' : ''" @tap="switchTab('listen_stat')" v-if="isCollegeAdmin || isSchoolAdmin">听课统计</view>
			<view class="tab" :class="activeTab === 'received_stat' ? 'active' : ''" @tap="switchTab('received_stat')" v-if="isCollegeAdmin || isSchoolAdmin">被听统计</view>
		</view>

		<view class="filter-section">
			<view class="filter-row">
				<view class="filter-item">
					<text class="filter-label">学年</text>
					<input :value="filters.academic_year" placeholder="如 2024-2025" class="filter-input" placeholder-class="placeholder" @input="onYearInput" />
				</view>
				<view class="filter-item">
					<text class="filter-label">学期</text>
					<picker mode="selector" :range="['全部', '1', '2']" :value="semesterIndex" @change="onSemesterChange">
						<view class="picker">{{ filters.semester ? String(filters.semester) : '全部' }}</view>
					</picker>
				</view>
			</view>

			<view class="filter-row" v-if="activeTab !== 'school'">
				<view class="filter-item" style="flex: 1;">
					<text class="filter-label">学院</text>
					<picker mode="selector" :range="collegePickerNames" :value="collegeIndex" @change="onCollegeChange">
						<view class="picker">{{ currentCollegeName }}</view>
					</picker>
				</view>
			</view>

			<view class="filter-actions">
				<button class="reset-btn" @tap="reset">重置</button>
				<button class="search-btn" @tap="refresh">查询</button>
			</view>
		</view>

		<view class="content-section">
			<!-- 全校统计 -->
			<view v-if="activeTab === 'school'" class="card" v-show="!loading">
				<view v-if="schoolStat" class="stat-block">
					<view class="stat-row">
						<text class="stat-label">总评教次数</text>
						<text class="stat-value">{{ schoolStat.total_evaluations ?? 0 }}</text>
					</view>
					<view class="stat-row">
						<text class="stat-label">全校平均分</text>
						<text class="stat-value">{{ formatScore(schoolStat.school_avg_score) }}</text>
					</view>
				</view>
				<view v-else class="empty-state">
					<text class="empty-icon">📊</text>
					<text class="empty-text">暂无数据</text>
					<text class="empty-hint">如提示无权限，请使用 school_admin 账号</text>
				</view>
			</view>

			<!-- 学院统计 -->
			<view v-if="activeTab === 'college'" class="card" v-show="!loading">
				<view v-if="collegeStat" class="stat-block">
					<view class="stat-row">
						<text class="stat-label">学院</text>
						<text class="stat-value">{{ collegeStat.college_name || '-' }}</text>
					</view>
					<view class="stat-row">
						<text class="stat-label">总评教次数</text>
						<text class="stat-value">{{ collegeStat.total_evaluations ?? 0 }}</text>
					</view>
					<view class="stat-row">
						<text class="stat-label">学院平均分</text>
						<text class="stat-value">{{ formatScore(collegeStat.college_avg_score) }}</text>
					</view>
					<view class="stat-subtitle">得分分布</view>
					<view class="tags">
						<text class="tag">优秀 {{ collegeStat.score_distribution?.优秀 ?? 0 }}</text>
						<text class="tag">良好 {{ collegeStat.score_distribution?.良好 ?? 0 }}</text>
						<text class="tag">合格 {{ collegeStat.score_distribution?.合格 ?? 0 }}</text>
						<text class="tag">不合格 {{ collegeStat.score_distribution?.不合格 ?? 0 }}</text>
					</view>
				</view>
				<view v-else class="empty-state">
					<text class="empty-icon">🏫</text>
					<text class="empty-text">暂无数据</text>
					<text class="empty-hint">请选择学院后点击查询</text>
				</view>
			</view>

			<!-- 教师排名 -->
			<view v-if="activeTab === 'ranking'" class="card" v-show="!loading">
				<view v-if="ranking.length" class="rank-list">
					<view class="rank-item" v-for="(r, idx) in ranking" :key="r.teacher_id">
						<view class="rank-header">
							<text class="rank-no">#{{ idx + 1 }}</text>
							<text class="rank-name">{{ r.teacher_name }}</text>
							<text class="rank-score">{{ formatScore(r.avg_score) }}</text>
						</view>
						<view class="rank-info">
							<text class="info-text">学院：{{ r.college_name }}</text>
							<text class="info-text">次数：{{ r.evaluation_count }}</text>
						</view>
					</view>
				</view>
				<view v-else class="empty-state">
					<text class="empty-icon">🏅</text>
					<text class="empty-text">暂无排名数据</text>
					<text class="empty-hint">点击查询获取教师排名</text>
				</view>
			</view>

			<!-- 22300417陈俫坤开发：学院管理员 - 教师听课统计 -->
			<view v-if="activeTab === 'listen_stat'" class="card" v-show="!loading">
				<view v-if="listenStat" class="stat-block">
					<view class="stat-row">
						<text class="stat-label">本院教师总数</text>
						<text class="stat-value">{{ listenStat.total_teachers ?? 0 }}</text>
					</view>
					<view class="stat-row">
						<text class="stat-label">已完成听课任务</text>
						<text class="stat-value">{{ listenStat.completed_count ?? 0 }}</text>
					</view>
					<view class="stat-row">
						<text class="stat-label">未完成听课任务</text>
						<text class="stat-value">{{ listenStat.incomplete_count ?? 0 }}</text>
					</view>
					<view class="stat-subtitle">教师听课详情</view>
					<view class="teacher-list">
						<view class="teacher-item" v-for="t in listenStat.teachers" :key="t.teacher_id">
							<text class="teacher-name">{{ t.teacher_name }}</text>
							<text class="teacher-count">已听 {{ t.listen_count }} 次</text>
							<text class="teacher-status" :class="t.listen_count >= (listenStat.required_count || 1) ? 'status-ok' : 'status-warn'">{{ t.listen_count >= (listenStat.required_count || 1) ? '已完成' : '未完成' }}</text>
						</view>
					</view>
				</view>
				<view v-else class="empty-state">
					<text class="empty-icon">📋</text>
					<text class="empty-text">暂无数据</text>
				</view>
			</view>

			<!-- 22300417陈俫坤开发：学院管理员 - 教师被听统计 -->
			<view v-if="activeTab === 'received_stat'" class="card" v-show="!loading">
				<view v-if="receivedStat" class="stat-block">
					<view class="stat-row">
						<text class="stat-label">本院被评教总次数</text>
						<text class="stat-value">{{ receivedStat.total_received ?? 0 }}</text>
					</view>
					<view class="stat-row">
						<text class="stat-label">本院平均分</text>
						<text class="stat-value">{{ formatScore(receivedStat.avg_score) }}</text>
					</view>
					<view class="stat-subtitle">得分分布</view>
					<view class="tags">
						<text class="tag">优秀 {{ receivedStat.score_distribution?.优秀 ?? 0 }}</text>
						<text class="tag">良好 {{ receivedStat.score_distribution?.良好 ?? 0 }}</text>
						<text class="tag">一般 {{ receivedStat.score_distribution?.一般 ?? 0 }}</text>
						<text class="tag">合格 {{ receivedStat.score_distribution?.合格 ?? 0 }}</text>
						<text class="tag">不合格 {{ receivedStat.score_distribution?.不合格 ?? 0 }}</text>
					</view>
					<view class="stat-subtitle">教师被评排名</view>
					<view class="teacher-list">
						<view class="teacher-item" v-for="(t, idx) in receivedStat.teacher_ranking" :key="t.teacher_id">
							<text class="rank-badge">#{{ idx + 1 }}</text>
							<text class="teacher-name">{{ t.teacher_name }}</text>
							<text class="teacher-score">{{ formatScore(t.avg_score) }}分</text>
							<text class="teacher-count">{{ t.received_count }}次</text>
						</view>
					</view>
				</view>
				<view v-else class="empty-state">
					<text class="empty-icon">📊</text>
					<text class="empty-text">暂无数据</text>
				</view>
			</view>

			<view v-if="loading" class="loading">加载中...</view>
		</view>
	</view>
</template>

<script>
import { request } from '../../common/request.js';

export default {
	name: 'statistics',
	data() {
		return {
			// 22300417陈俫坤开发：统计分析页数据
			activeTab: 'school',
			loading: false,
			filters: {
				academic_year: '',
				semester: null,
				college_id: null
			},
			me: null,
			colleges: [],
			schoolStat: null,
			collegeStat: null,
			ranking: [],
			// 22300417陈俫坤开发：学院管理员专用统计数据
			listenStat: null,
			receivedStat: null,
			isCollegeAdmin: false,
			isSchoolAdmin: false
		};
	},
	onLoad() {
		this.init();
	},
	computed: {
		semesterIndex() {
			if (!this.filters.semester) return 0;
			return this.filters.semester === 1 ? 1 : 2;
		},
		collegePickerNames() {
			const names = ['全部'];
			this.colleges.forEach(c => names.push(c.college_name));
			return names;
		},
		collegeIndex() {
			if (!this.filters.college_id) return 0;
			const idx = this.colleges.findIndex(c => c.id === this.filters.college_id);
			return idx >= 0 ? idx + 1 : 0;
		},
		currentCollegeName() {
			if (!this.filters.college_id) return '全部';
			const c = this.colleges.find(x => x.id === this.filters.college_id);
			return c ? c.college_name : '全部';
		}
	},
	methods: {
		async init() {
			await this.loadMe();
			// 22300417陈俫坤开发：判断角色
			const codes = (this.me && this.me.roles_code) ? this.me.roles_code : [];
			this.isSchoolAdmin = codes.includes('school_admin');
			this.isCollegeAdmin = codes.includes('college_admin');
			// 22300417陈俫坤开发：非 school_admin 默认展示学院统计，避免全校统计接口 403
			if (!this.isSchoolAdmin) {
				this.activeTab = this.isCollegeAdmin ? 'listen_stat' : 'college';
			}
			await this.loadColleges();
			this.refresh();
		},
		async loadMe() {
			try {
				const res = await request({ url: '/user/me', method: 'GET' });
				this.me = res;
				// 22300417陈俫坤开发：默认学院筛选为当前用户所属学院（如果有）
				const cid = res && res.user ? res.user.college_id : null;
				if (cid) this.filters.college_id = cid;
			} catch (e) {
				this.me = null;
			}
		},
		async loadColleges() {
			try {
				// 22300417陈俫坤开发：拉取学院列表用于筛选
				const res = await request({ url: '/org/colleges', method: 'GET', params: { skip: 0, limit: 200 } });
				this.colleges = (res && res.list) ? res.list : [];
				// 22300417陈俫坤开发：若当前用户 college_id 在学院表不存在，清空筛选，避免请求带错误 college_id 导致排名/统计为空
				if (this.filters.college_id) {
					const exists = this.colleges.some(c => c && c.id === this.filters.college_id);
					if (!exists) {
						this.filters.college_id = null;
					}
				}
			} catch (e) {
				this.colleges = [];
			}
		},
		switchTab(tab) {
			this.activeTab = tab;
			this.refresh();
		},
		onYearInput(e) {
			this.filters.academic_year = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		onSemesterChange(e) {
			const idx = (e && e.detail && e.detail.value !== undefined) ? Number(e.detail.value) : 0;
			if (idx === 0) this.filters.semester = null;
			if (idx === 1) this.filters.semester = 1;
			if (idx === 2) this.filters.semester = 2;
		},
		onCollegeChange(e) {
			const idx = (e && e.detail && e.detail.value !== undefined) ? Number(e.detail.value) : 0;
			if (idx === 0) {
				this.filters.college_id = null;
				return;
			}
			const c = this.colleges[idx - 1];
			this.filters.college_id = c ? c.id : null;
		},
		reset() {
			this.filters.academic_year = '';
			this.filters.semester = null;
			// 保留当前用户学院默认值
			const cid = this.me && this.me.user ? this.me.user.college_id : null;
			this.filters.college_id = cid || null;
			this.refresh();
		},
		formatScore(v) {
			if (v === null || v === undefined) return '-';
			const n = Number(v);
			if (Number.isNaN(n)) return String(v);
			return n.toFixed(2);
		},
		async refresh() {
			this.loading = true;
			try {
				const params = {
					academic_year: this.filters.academic_year || undefined,
					semester: this.filters.semester || undefined
				};
				if (this.activeTab === 'school') {
					// 22300417陈俫坤开发：获取全校统计
					this.schoolStat = await request({ url: '/eval/statistics/school', method: 'GET', params });
					this.collegeStat = null;
					this.ranking = [];
					return;
				}
				if (this.activeTab === 'college') {
					if (!this.filters.college_id) {
						this.collegeStat = null;
						return;
					}
					// 22300417陈俫坤开发：获取学院统计
					this.collegeStat = await request({
						url: `/eval/statistics/college/${this.filters.college_id}`,
						method: 'GET',
						params
					});
					this.schoolStat = null;
					this.ranking = [];
					return;
				}
				if (this.activeTab === 'ranking') {
					// 22300417陈俫坤开发：获取教师排名
					this.ranking = [];
					const res = await request({
						url: '/eval/statistics/teacher/ranking',
						method: 'GET',
						params: {
							...params,
							college_id: this.filters.college_id || undefined
						}
					});
					this.ranking = (res && res.ranking) ? res.ranking : [];
					this.schoolStat = null;
					this.collegeStat = null;
				}
				// 22300417陈俫坤开发：学院管理员 - 教师听课统计
				if (this.activeTab === 'listen_stat') {
					// school_admin必须先选择学院
					if (!this.filters.college_id) {
						this.listenStat = null;
						return;
					}
					this.listenStat = await request({
						url: '/eval/college/statistics/listen',
						method: 'GET',
						params: {
							...params,
							college_id: this.filters.college_id
						}
					});
					this.schoolStat = null;
					this.collegeStat = null;
					this.ranking = [];
					this.receivedStat = null;
				}
				// 22300417陈俫坤开发：学院管理员 - 教师被听统计
				if (this.activeTab === 'received_stat') {
					// school_admin必须先选择学院
					if (!this.filters.college_id) {
						this.receivedStat = null;
						return;
					}
					this.receivedStat = await request({
						url: '/eval/college/statistics/received',
						method: 'GET',
						params: {
							...params,
							college_id: this.filters.college_id
						}
					});
					this.schoolStat = null;
					this.collegeStat = null;
					this.ranking = [];
					this.listenStat = null;
				}
			} catch (e) {
				// 22300417陈俫坤开发：改善错误提示，显示具体错误信息
				console.error('查询统计数据失败:', e);
				this.schoolStat = null;
				this.collegeStat = null;
				this.ranking = [];
				
				let errorMsg = '查询失败，请重试';
				if (e && e.data && e.data.detail) {
					errorMsg = e.data.detail;
				} else if (e && e.message) {
					errorMsg = e.message;
				} else if (typeof e === 'string') {
					errorMsg = e;
				}
				
				uni.showToast({
					title: errorMsg,
					icon: 'none',
					duration: 3000
				});
			} finally {
				this.loading = false;
			}
		}
	}
};
</script>

<style scoped>
.admin-container {
	background-color: #F5F7FA;
	min-height: 100vh;
}

.page-header {
	background-color: #3E5C76;
	color: #FFFFFF;
	padding: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.page-title {
	font-size: 36rpx;
	font-weight: bold;
}

.tabs {
	background-color: #FFFFFF;
	padding: 0 30rpx;
	display: flex;
	gap: 16rpx;
}

.tab {
	flex: 1;
	text-align: center;
	padding: 22rpx 0;
	font-size: 28rpx;
	color: #666666;
	border-bottom: 4rpx solid transparent;
}

.tab.active {
	color: #3E5C76;
	font-weight: bold;
	border-bottom-color: #3E5C76;
}

.filter-section {
	padding: 20rpx 30rpx;
	background-color: #FFFFFF;
}

.filter-row {
	display: flex;
	gap: 20rpx;
	margin-bottom: 16rpx;
}

.filter-item {
	flex: 1;
}

.filter-label {
	font-size: 24rpx;
	color: #666666;
	margin-bottom: 10rpx;
	display: block;
}

.filter-input {
	height: 80rpx;
	border-radius: 12rpx;
	background-color: #F5F7FA;
	padding: 0 20rpx;
	font-size: 28rpx;
	color: #333333;
}

.picker {
	height: 80rpx;
	border-radius: 12rpx;
	background-color: #F5F7FA;
	padding: 0 20rpx;
	display: flex;
	align-items: center;
	font-size: 28rpx;
	color: #333333;
}

.placeholder {
	color: #C0C4CC;
}

.filter-actions {
	display: flex;
	gap: 20rpx;
}

.reset-btn,
.search-btn {
	flex: 1;
	height: 72rpx;
	line-height: 72rpx;
	border-radius: 36rpx;
	font-size: 28rpx;
}

.reset-btn {
	background-color: #FFFFFF;
	color: #3E5C76;
	border: 2rpx solid #3E5C76;
}

.search-btn {
	background-color: #3E5C76;
	color: #FFFFFF;
}

.reset-btn::after,
.search-btn::after {
	border: none;
}

.content-section {
	padding: 0 30rpx;
	margin-top: 20rpx;
}

.card {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.stat-block {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 20rpx;
}

.stat-row {
	display: flex;
	justify-content: space-between;
	margin-bottom: 16rpx;
}

.stat-label {
	font-size: 26rpx;
	color: #666666;
}

.stat-value {
	font-size: 26rpx;
	color: #333333;
	font-weight: bold;
}

.stat-subtitle {
	margin-top: 20rpx;
	margin-bottom: 10rpx;
	font-size: 26rpx;
	font-weight: bold;
	color: #333333;
}

.tags {
	display: flex;
	flex-wrap: wrap;
	gap: 12rpx;
}

.tag {
	font-size: 24rpx;
	color: #3E5C76;
	background-color: #FFFFFF;
	border-radius: 20rpx;
	padding: 8rpx 14rpx;
}

.rank-list {
	margin-top: 0;
}

.rank-item {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 20rpx;
	margin-bottom: 16rpx;
}

.rank-item:last-child {
	margin-bottom: 0;
}

.rank-header {
	display: flex;
	align-items: center;
	gap: 14rpx;
	margin-bottom: 10rpx;
}

.rank-no {
	font-size: 24rpx;
	color: #999999;
}

.rank-name {
	flex: 1;
	font-size: 28rpx;
	font-weight: bold;
	color: #333333;
}

.rank-score {
	font-size: 28rpx;
	color: #3E5C76;
	font-weight: bold;
}

.rank-info {
	display: flex;
	gap: 20rpx;
	flex-wrap: wrap;
}

.info-text {
	font-size: 24rpx;
	color: #666666;
}

.empty-state {
	padding: 100rpx 0;
	text-align: center;
	color: #999999;
}

.empty-icon {
	font-size: 80rpx;
	margin-bottom: 20rpx;
}

.empty-text {
	font-size: 32rpx;
	margin-bottom: 10rpx;
}

.empty-hint {
	font-size: 26rpx;
}

.loading {
	margin-top: 20rpx;
	text-align: center;
	font-size: 28rpx;
	color: #999999;
}

/* 22300417陈俫坤开发：学院管理员统计样式 */
.teacher-list {
	margin-top: 16rpx;
}

.teacher-item {
	display: flex;
	align-items: center;
	gap: 16rpx;
	padding: 16rpx;
	background-color: #FFFFFF;
	border-radius: 8rpx;
	margin-bottom: 12rpx;
}

.teacher-item:last-child {
	margin-bottom: 0;
}

.teacher-name {
	flex: 1;
	font-size: 26rpx;
	color: #333333;
}

.teacher-count {
	font-size: 24rpx;
	color: #666666;
}

.teacher-score {
	font-size: 26rpx;
	color: #3E5C76;
	font-weight: bold;
}

.teacher-status {
	font-size: 22rpx;
	padding: 4rpx 12rpx;
	border-radius: 20rpx;
}

.status-ok {
	background-color: #E8F5E9;
	color: #4CAF50;
}

.status-warn {
	background-color: #FFF3E0;
	color: #FF9800;
}

.rank-badge {
	font-size: 22rpx;
	color: #999999;
	min-width: 50rpx;
}
</style>