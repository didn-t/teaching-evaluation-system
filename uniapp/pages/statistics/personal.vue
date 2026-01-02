<template>
	<view class="personal-statistics-container">
		<!-- 22300417陈俫坤开发：个人统计拆分为“我收到的评教”(授课被评) 和 “我提交的评教”(听课评教) -->
		<view class="mode-tabs">
			<view class="mode-tab" :class="mode === 'received' ? 'active' : ''" @tap="switchMode('received')">我收到的评教</view>
			<view class="mode-tab" :class="mode === 'submitted' ? 'active' : ''" @tap="switchMode('submitted')">我提交的评教</view>
		</view>

		<!-- 统计概览 -->
		<view class="overview-section">
			<text class="section-title">评教统计概览</text>
			
			<view class="stats-grid">
				<view class="stat-item">
					<text class="stat-value">{{ stats.total_evaluations }}</text>
					<text class="stat-label">总评教次数</text>
				</view>
				
				<view class="stat-item">
					<!-- 22300417陈俫坤开发：average_score 可能为 undefined/null，避免 toFixed 报错 -->
					<text class="stat-value">{{ Number(stats.average_score || 0).toFixed(1) }}</text>
					<text class="stat-label">平均评分</text>
				</view>
				
				<view class="stat-item">
					<text class="stat-value">{{ stats.valid_evaluations }}</text>
					<text class="stat-label">有效评教</text>
				</view>
				
				<view class="stat-item">
					<text class="stat-value">{{ stats.pending_evaluations }}</text>
					<text class="stat-label">待审核</text>
				</view>
			</view>
		</view>
		
		<!-- 筛选条件 -->
		<view class="filter-section">
			<view class="filter-row">
				<view class="filter-item">
					<text class="filter-label">学年</text>
					<view class="filter-input">
						<input 
							:value="filter.academic_year" 
							placeholder="如：2024-2025" 
							class="input"
							placeholder-class="placeholder"
							@input="handleAcademicYearInput"
						/>
					</view>
				</view>
				
				<view class="filter-item">
					<text class="filter-label">学期</text>
					<view class="filter-select">
						<picker 
							:value="getSemesterIndex()" 
							:range="semesterOptions" 
							:range-key="'label'"
							@change="handleSemesterChange"
						>
							<view class="picker-text">
								{{ getSelectedSemesterLabel() }}
							</view>
						</picker>
					</view>
				</view>
			</view>
			
			<button @tap="getStatistics" class="query-btn">
				查询
			</button>
		</view>
		
		<!-- 评分趋势 -->
		<view class="trend-section">
			<text class="section-title">评分趋势</text>
			
			<view class="trend-chart" v-if="stats.trend_data && stats.trend_data.length > 0">
				<!-- 这里可以根据需要实现评分趋势图，目前用简单的列表展示 -->
				<view class="trend-item" v-for="(item, index) in stats.trend_data" :key="index">
					<text class="trend-label">{{ item.label }}</text>
					<view class="trend-bar-container">
						<view class="trend-bar" :style="{ width: getBarWidth(item.score) + '%' }"></view>
					</view>
					<text class="trend-score">{{ item.score }}分</text>
				</view>
			</view>
			
			<view class="empty-state" v-else>
				<text class="empty-text">暂无评分趋势数据</text>
			</view>
		</view>
		
		<!-- 各维度评分 -->
		<view class="dimensions-section">
			<text class="section-title">各维度评分</text>
			
			<view class="dimension-scores" v-if="stats.dimension_scores && stats.dimension_scores.length > 0">
				<view class="dimension-item" v-for="(item, index) in stats.dimension_scores" :key="index">
					<text class="dimension-name">{{ item.dimension_name }}</text>
					<view class="dimension-bar-container">
						<view class="dimension-bar" :style="{ width: item.score + '%' }"></view>
					</view>
					<text class="dimension-score">{{ item.score }}分</text>
				</view>
			</view>
			
			<view class="empty-state" v-else>
				<text class="empty-text">暂无维度评分数据</text>
			</view>
		</view>
	</view>
</template>

<script>
import { request } from '../../common/request.js';

export default {
	name: 'personal-statistics',
	data() {
		return {
			// 22300417陈俫坤开发：统计模式 received=我收到的评教（授课被评）；submitted=我提交的评教（听课评教）
			mode: 'received',
			// 统计数据
			stats: {
				total_evaluations: 0,
				average_score: 0,
				valid_evaluations: 0,
				pending_evaluations: 0,
				trend_data: [],
				dimension_scores: []
			},
			// 筛选条件
			filter: {
				academic_year: '',
				semester: null
			},
			// 学期选项
			semesterOptions: [
				{ label: '全部', value: null },
				{ label: '春季', value: 1 },
				{ label: '秋季', value: 2 }
			],
			// 加载状态
			loading: false
		};
	},
	onLoad() {
		this.getStatistics();
	},
	methods: {
		switchMode(mode) {
			// 22300417陈俫坤开发：切换“我收到的/我提交的”后刷新统计
			this.mode = mode;
			this.getStatistics();
		},
		// 兼容 web 和微信小程序的输入处理
		handleAcademicYearInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.filter.academic_year = value;
		},
		getSemesterIndex() {
			const index = this.semesterOptions.findIndex(opt => opt.value === this.filter.semester);
			return index >= 0 ? index : 0;
		},
		// 获取个人统计数据
		async getStatistics() {
			this.loading = true;
			try {
				const url = this.mode === 'submitted' ? '/eval/statistics/listen/me' : '/eval/statistics/teacher/me';
				const res = await request({
					url,
					method: 'GET',
					params: {
						academic_year: this.filter.academic_year || undefined,
						semester: this.filter.semester || undefined
					}
				});
				
				// 22300417陈俫坤开发：对齐后端增强统计字段（trend_data + dimension_scores(含dimension_name) + pending/valid/total）
				// 这里做一层兼容转换，避免不同版本字段不一致导致 undefined。
				if (res) {
					const total = Number(res.total_evaluations ?? res.total_evaluation_num ?? 0);
					const valid = Number(res.valid_evaluation_num ?? res.valid_evaluations ?? res.total_evaluation_num ?? 0);
					const pending = Number(res.pending_evaluation_num ?? res.pending_evaluations ?? 0);
					const avg = Number(res.avg_total_score ?? res.average_score ?? 0);
					
					// trend_data：后端增强字段，按月份聚合；没提供则保持空数组
					const trendData = Array.isArray(res.trend_data) ? res.trend_data : [];
					
					// dimension_scores：优先使用后端增强字段（含 dimension_name）；否则兼容旧的 dimension_avg_scores
					let dimensionScores = Array.isArray(res.dimension_scores) ? res.dimension_scores : [];
					if (!dimensionScores.length && res.dimension_avg_scores && typeof res.dimension_avg_scores === 'object') {
						dimensionScores = Object.keys(res.dimension_avg_scores).map(k => ({
							dimension_name: k,
							score: Number(res.dimension_avg_scores[k] ?? 0)
						}));
					}
					
					this.stats = {
						total_evaluations: total,
						average_score: avg,
						valid_evaluations: valid,
						pending_evaluations: pending,
						trend_data: trendData,
						dimension_scores: dimensionScores
					};
				}
			} catch (error) {
				console.error('获取个人统计数据失败:', error);
				uni.showToast({
					title: '获取统计数据失败，请重试',
					icon: 'none',
					duration: 2000
				});
			} finally {
				this.loading = false;
			}
		},
		
		// 处理学期选择变化
		handleSemesterChange(e) {
			// 兼容 web 和微信小程序
			const index = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e ? e : 0);
			if (this.semesterOptions && this.semesterOptions[index]) {
				this.filter.semester = this.semesterOptions[index].value;
			}
		},
		
		// 获取选中的学期标签
		getSelectedSemesterLabel() {
			const selected = this.semesterOptions.find(item => item.value === this.filter.semester);
			return selected ? selected.label : '全部';
		},
		
		// 获取评分趋势图的bar宽度
		getBarWidth(score) {
			// 假设满分是100分，将评分转换为0-100%的宽度
			return Math.min(score, 100);
		}
	}
};
</script>

<style scoped>
.personal-statistics-container {
	background-color: #F5F7FA;
	min-height: 100vh;
	padding: 30rpx;
}

.mode-tabs {
	display: flex;
	background-color: #FFFFFF;
	border-radius: 12rpx;
	overflow: hidden;
	margin-bottom: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.mode-tab {
	flex: 1;
	text-align: center;
	padding: 22rpx 10rpx;
	font-size: 28rpx;
	color: #666666;
	background-color: #FFFFFF;
}

.mode-tab.active {
	color: #FFFFFF;
	background-color: #3E5C76;
	font-weight: 600;
}

/* 公共样式 */
.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 30rpx;
	display: block;
}

/* 统计概览 */
.overview-section {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.stats-grid {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 20rpx;
}

.stat-item {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 30rpx;
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
}

.stat-value {
	font-size: 48rpx;
	font-weight: bold;
	color: #3E5C76;
	margin-bottom: 10rpx;
}

.stat-label {
	font-size: 24rpx;
	color: #666666;
}

/* 筛选条件 */
.filter-section {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.filter-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 20rpx;
	margin-bottom: 30rpx;
}

.filter-item {
	flex: 1;
}

.filter-label {
	display: block;
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
	margin-bottom: 15rpx;
}

.filter-input .input {
	width: 100%;
	height: 80rpx;
	border: 2rpx solid #E4E7ED;
	border-radius: 8rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
	color: #333333;
	background-color: #F5F7FA;
}

.placeholder {
	color: #C0C4CC;
}

.filter-select {
	height: 80rpx;
	border: 2rpx solid #E4E7ED;
	border-radius: 8rpx;
	padding: 0 20rpx;
	background-color: #F5F7FA;
	display: flex;
	justify-content: center;
	align-items: center;
}

.picker-text {
	font-size: 28rpx;
	color: #333333;
}

.query-btn {
	width: 100%;
	height: 88rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
	font-size: 32rpx;
	font-weight: bold;
	border-radius: 44rpx;
}

.query-btn::after {
	border: none;
}

.query-btn:active {
	background-color: #2D455A;
}

/* 评分趋势 */
.trend-section {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.trend-chart {
	/* 趋势图容器 */
}

.trend-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.trend-item:last-child {
	margin-bottom: 0;
}

.trend-label {
	width: 120rpx;
	font-size: 26rpx;
	color: #666666;
}

.trend-bar-container {
	flex: 1;
	height: 20rpx;
	background-color: #F5F7FA;
	border-radius: 10rpx;
	margin: 0 20rpx;
	overflow: hidden;
}

.trend-bar {
	height: 100%;
	background-color: #3E5C76;
	border-radius: 10rpx;
}

.trend-score {
	width: 80rpx;
	font-size: 28rpx;
	font-weight: bold;
	color: #3E5C76;
	text-align: right;
}

/* 各维度评分 */
.dimensions-section {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.dimension-item {
	margin-bottom: 30rpx;
}

.dimension-item:last-child {
	margin-bottom: 0;
}

.dimension-name {
	display: block;
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
	margin-bottom: 15rpx;
}

.dimension-bar-container {
	height: 30rpx;
	background-color: #F5F7FA;
	border-radius: 15rpx;
	margin-bottom: 10rpx;
	overflow: hidden;
}

.dimension-bar {
	height: 100%;
	background-color: #3E5C76;
	border-radius: 15rpx;
}

.dimension-score {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #3E5C76;
	text-align: right;
}

/* 空状态 */
.empty-state {
	display: flex;
	justify-content: center;
	align-items: center;
	padding: 80rpx 0;
	color: #999999;
}

.empty-text {
	font-size: 28rpx;
}
</style>