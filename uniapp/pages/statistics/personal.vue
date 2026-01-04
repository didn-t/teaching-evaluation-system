<template>
	<view class="personal-statistics-container">
		<!-- 22300417陈俫坤开发：个人统计拆分为"教师听课记录" 和 "教师被听记录" -->
		<view class="mode-tabs">
			<view class="mode-tab" :class="mode === 'listen' ? 'active' : ''" @tap="switchMode('listen')">教师听课记录</view>
			<view class="mode-tab" :class="mode === 'received' ? 'active' : ''" @tap="switchMode('received')">教师被听记录</view>
		</view>

		<!-- 教师听课记录 -->
		<view class="content-section" v-if="mode === 'listen'">
			<text class="section-title">评教统计概览</text>
			<view class="stats-grid">
				<view class="stat-item">
					<text class="stat-value">{{ listenStats.total || 0 }}</text>
					<text class="stat-label">总评教次数</text>
				</view>
				<view class="stat-item">
					<text class="stat-value">{{ Number(listenStats.avg_score || 0).toFixed(1) }}</text>
					<text class="stat-label">平均评分</text>
				</view>
			</view>

			<!-- 筛选条件 -->
			<view class="filter-section">
				<view class="filter-row">
					<view class="filter-item">
						<text class="filter-label">教师</text>
						<input class="filter-input" :value="filterTeacher" placeholder="教师姓名" @input="e => filterTeacher = e.detail.value" />
					</view>
					<view class="filter-item">
						<text class="filter-label">课程</text>
						<input class="filter-input" :value="filterCourse" placeholder="课程名称" @input="e => filterCourse = e.detail.value" />
					</view>
				</view>
				<view class="filter-row">
					<view class="filter-item" style="flex: 1;">
						<text class="filter-label">评分筛选</text>
						<picker mode="selector" :range="scoreFilterOptions" :value="filterScoreIndex" @change="handleScoreFilterChange">
							<view class="filter-picker">{{ scoreFilterOptions[filterScoreIndex] }}</view>
						</picker>
					</view>
				</view>
				<button class="query-btn" @tap="queryListenStats">查询</button>
			</view>

			<!-- 评分趋势 -->
			<view class="trend-section" v-if="listenStats.trend_data && listenStats.trend_data.length">
				<text class="section-title">评分趋势</text>
				<view class="trend-list">
					<view class="trend-item" v-for="(t, idx) in listenStats.trend_data" :key="idx">
						<text class="trend-month">{{ t.month }}</text>
						<text class="trend-score">{{ Number(t.avg_score || 0).toFixed(1) }}</text>
					</view>
				</view>
			</view>
			<view class="empty-state" v-else>
				<text class="empty-text">暂无评分趋势数据</text>
			</view>
		</view>

		<!-- 教师被听记录 -->
		<view class="content-section" v-if="mode === 'received'">
			<text class="section-title">评教统计概览</text>
			<view class="stats-grid">
				<view class="stat-item">
					<text class="stat-value">{{ receivedStats.total || 0 }}</text>
					<text class="stat-label">总评教次数</text>
				</view>
				<view class="stat-item">
					<text class="stat-value">{{ Number(receivedStats.avg_score || 0).toFixed(1) }}</text>
					<text class="stat-label">平均评分</text>
				</view>
			</view>

			<!-- 筛选条件 -->
			<view class="filter-section">
				<view class="filter-row">
					<view class="filter-item">
						<text class="filter-label">教师</text>
						<input class="filter-input" :value="filterTeacher2" placeholder="评教人姓名" @input="e => filterTeacher2 = e.detail.value" />
					</view>
					<view class="filter-item">
						<text class="filter-label">课程</text>
						<input class="filter-input" :value="filterCourse2" placeholder="课程名称" @input="e => filterCourse2 = e.detail.value" />
					</view>
				</view>
				<view class="filter-row">
					<view class="filter-item" style="flex: 1;">
						<text class="filter-label">评分筛选</text>
						<picker mode="selector" :range="scoreFilterOptions" :value="filterScoreIndex2" @change="handleScoreFilterChange2">
							<view class="filter-picker">{{ scoreFilterOptions[filterScoreIndex2] }}</view>
						</picker>
					</view>
				</view>
				<button class="query-btn" @tap="queryReceivedStats">查询</button>
			</view>

			<!-- 评分趋势 -->
			<view class="trend-section-box">
				<text class="section-title">评分趋势</text>
				<view class="trend-bar-list" v-if="receivedStats.trend_data && receivedStats.trend_data.length">
					<view class="trend-bar-item" v-for="(t, idx) in receivedStats.trend_data" :key="idx">
						<text class="trend-bar-month">{{ t.month }}</text>
						<view class="trend-bar-container">
							<view class="trend-bar" :style="{ width: (t.avg_score || 0) + '%' }"></view>
						</view>
						<text class="trend-bar-score">{{ Number(t.avg_score || 0).toFixed(0) }}分</text>
					</view>
				</view>
				<view class="empty-state" v-else>
					<text class="empty-text">暂无评分趋势数据</text>
				</view>
			</view>

			<!-- 各维度评分 -->
			<view class="dimension-section-box">
				<text class="section-title">各维度评分</text>
				<view class="dimension-bar-list" v-if="receivedStats.dimension_scores && receivedStats.dimension_scores.length">
					<view class="dimension-bar-item" v-for="(d, idx) in receivedStats.dimension_scores" :key="idx">
						<text class="dimension-bar-name">{{ d.dimension_name }}</text>
						<view class="dimension-bar-container">
							<view class="dimension-bar" :style="{ width: getDimensionPercent(d) + '%' }"></view>
						</view>
						<text class="dimension-bar-score">{{ Number(d.score || 0).toFixed(1) }}分</text>
					</view>
				</view>
				<view class="empty-state" v-else>
					<text class="empty-text">暂无维度评分数据</text>
				</view>
			</view>

			<!-- 评教记录列表 -->
			<view class="eval-list-section">
				<text class="section-title">评教记录</text>
				<view class="eval-list" v-if="receivedStats.records && receivedStats.records.length">
					<view class="eval-card" v-for="(record, idx) in receivedStats.records" :key="idx">
						<view class="eval-header">
							<text class="eval-course">{{ record.course_name }}</text>
							<text class="eval-score">{{ record.total_score }}分</text>
						</view>
						<view class="eval-info">
							<text class="eval-listener">评教人：{{ record.listen_teacher_name || '匿名' }}</text>
							<text class="eval-time">{{ record.eval_time }}</text>
						</view>
						<!-- 各维度评分详情 -->
						<view class="eval-dimensions" v-if="record.dimensions && record.dimensions.length">
							<view class="eval-dim-item" v-for="(dim, dIdx) in record.dimensions" :key="dIdx">
								<text class="dim-name">{{ dim.name }}</text>
								<text class="dim-score">{{ dim.score }}分</text>
							</view>
						</view>
						<view class="eval-comment" v-if="record.comment">
							<text class="comment-label">评语：</text>
							<text class="comment-text">{{ record.comment }}</text>
						</view>
						<view class="eval-level" v-if="record.level">
							<text class="level-tag" :class="'level-' + record.level">{{ record.level }}</text>
						</view>
					</view>
				</view>
				<view class="empty-state" v-else>
					<text class="empty-text">暂无评教记录</text>
				</view>
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
			// 22300417陈俫坤开发：统计模式 listen=教师听课记录；received=教师被听记录
			mode: 'listen',
			// 教师听课记录统计
			listenStats: {
				total: 0,
				avg_score: 0,
				trend_data: []
			},
			// 教师被听记录统计
			receivedStats: {
				total: 0,
				avg_score: 0,
				trend_data: [],
				dimension_scores: [],
				records: []
			},
			// 听课记录筛选条件
			filterTeacher: '',
			filterCourse: '',
			filterScoreIndex: 0,
			// 被听记录筛选条件
			filterTeacher2: '',
			filterCourse2: '',
			filterScoreIndex2: 0,
			// 评分筛选选项
			scoreFilterOptions: ['全部', '高分(≥80)', '低分(<60)'],
			// 加载状态
			loading: false
		};
	},
	onLoad() {
		this.queryListenStats();
	},
	computed: {
		// 获取评分筛选值
		scoreFilter() {
			if (this.filterScoreIndex === 1) return 'high';
			if (this.filterScoreIndex === 2) return 'low';
			return null;
		},
		scoreFilter2() {
			if (this.filterScoreIndex2 === 1) return 'high';
			if (this.filterScoreIndex2 === 2) return 'low';
			return null;
		}
	},
	methods: {
		switchMode(mode) {
			// 22300417陈俫坤开发：切换Tab后刷新统计
			this.mode = mode;
			if (mode === 'listen') {
				this.queryListenStats();
			} else {
				this.queryReceivedStats();
			}
		},
		handleScoreFilterChange(e) {
			this.filterScoreIndex = Number(e.detail.value);
		},
		handleScoreFilterChange2(e) {
			this.filterScoreIndex2 = Number(e.detail.value);
		},
		// 22300417陈俫坤开发：查询教师听课记录统计
		async queryListenStats() {
			this.loading = true;
			try {
				const params = {};
				if (this.filterTeacher) params.teacher_name = this.filterTeacher;
				if (this.filterCourse) params.course_name = this.filterCourse;
				if (this.scoreFilter) params.score_filter = this.scoreFilter;
				
				const res = await request({
					url: '/eval/statistics/listen/me',
					method: 'GET',
					params
				});
				
				if (res) {
					this.listenStats = {
						total: res.total_evaluations || res.total || 0,
						avg_score: res.average_score || res.avg_score || 0,
						trend_data: res.trend_data || []
					};
				}
			} catch (error) {
				console.error('获取听课统计数据失败:', error);
				uni.showToast({ title: '获取统计数据失败', icon: 'none' });
			} finally {
				this.loading = false;
			}
		},
		// 22300417陈俫坤开发：查询教师被听记录统计
		async queryReceivedStats() {
			this.loading = true;
			try {
				const params = {};
				if (this.filterTeacher2) params.listener_name = this.filterTeacher2;
				if (this.filterCourse2) params.course_name = this.filterCourse2;
				if (this.scoreFilter2) params.score_filter = this.scoreFilter2;
				
				// 获取统计数据
				const res = await request({
					url: '/eval/statistics/teacher/me',
					method: 'GET',
					params
				});
				
				// 获取评教记录列表
				const recordsRes = await request({
					url: '/eval/received/me',
					method: 'GET',
					params: { ...params, skip: 0, limit: 50 }
				});
				
				// 解析维度评分
				let dimensionScores = [];
				if (res && res.dimension_scores && Array.isArray(res.dimension_scores)) {
					dimensionScores = res.dimension_scores;
				} else if (res && res.dimension_avg_scores && typeof res.dimension_avg_scores === 'object') {
					dimensionScores = Object.keys(res.dimension_avg_scores).map(k => ({
						dimension_name: k,
						score: Number(res.dimension_avg_scores[k] || 0)
					}));
				}
				
				if (res) {
					this.receivedStats = {
						total: res.total_evaluations || res.total || 0,
						avg_score: res.average_score || res.avg_score || 0,
						trend_data: res.trend_data || [],
						dimension_scores: dimensionScores,
						records: (recordsRes && recordsRes.list) ? recordsRes.list.map(r => ({
							course_name: r.course_name || r.timetable?.course_name || '',
							total_score: r.total_score || 0,
							listen_teacher_name: r.listen_teacher_name || r.listen_teacher?.user_name || '匿名',
							eval_time: r.eval_time || r.create_time || '',
							comment: r.comment || r.overall_comment || '',
							level: r.level || '',
							dimensions: r.dimensions || []
						})) : []
					};
				}
			} catch (error) {
				console.error('获取被听统计数据失败:', error);
				uni.showToast({ title: '获取统计数据失败', icon: 'none' });
			} finally {
				this.loading = false;
			}
		},
		// 22300417陈俫坤开发：维度总分映射
		getDimensionMax(item) {
			const key = String(item?.dimension_name || item?.dimension_key || '');
			if (key.includes('教学态度')) return 20;
			if (key.includes('教学内容')) return 50;
			if (key.includes('教学方法')) return 15;
			if (key.includes('教学效果')) return 15;
			return 100;
		},
		// 22300417陈俫坤开发：计算维度进度条比例
		getDimensionPercent(item) {
			const max = this.getDimensionMax(item);
			const score = Number(item?.score || 0);
			if (!max) return 0;
			return Math.max(0, Math.min(100, (score / max) * 100));
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
.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333333;
  margin-bottom: 30rpx;
  display: block;
}
.stats-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}
.stat-item {
  flex: 1;
  min-width: 45%;
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
.filter-input {
  width: 100%;
  height: 80rpx;
  border: 2rpx solid #E4E7ED;
  border-radius: 8rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  color: #333333;
  background-color: #F5F7FA;
}
.filter-picker {
  height: 80rpx;
  line-height: 80rpx;
  border: 2rpx solid #E4E7ED;
  border-radius: 8rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  color: #333333;
  background-color: #F5F7FA;
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
.trend-section {
  background-color: #FFFFFF;
  border-radius: 12rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}
.trend-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.trend-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}
.trend-month {
  font-size: 26rpx;
  color: #666666;
}
.trend-score {
  width: 80rpx;
  font-size: 28rpx;
  font-weight: bold;
  color: #3E5C76;
  text-align: right;
}
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
.content-section {
  background-color: transparent;
}
.content-section .section-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333333;
  margin-bottom: 20rpx;
  display: block;
}
.content-section .stats-grid {
  background-color: #FFFFFF;
  border-radius: 12rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}
.trend-section-box {
  background-color: #FFFFFF;
  border-radius: 12rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}
.trend-bar-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}
.trend-bar-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
}
.trend-bar-month {
  width: 140rpx;
  font-size: 26rpx;
  color: #666666;
  flex-shrink: 0;
}
.trend-bar-container {
  flex: 1;
  height: 24rpx;
  background-color: #F5F7FA;
  border-radius: 12rpx;
  overflow: hidden;
}
.trend-bar {
  height: 100%;
  background-color: #3E5C76;
  border-radius: 12rpx;
}
.trend-bar-score {
  width: 80rpx;
  font-size: 26rpx;
  font-weight: 600;
  color: #3E5C76;
  text-align: right;
  flex-shrink: 0;
}
.dimension-section-box {
  background-color: #FFFFFF;
  border-radius: 12rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}
.dimension-bar-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}
.dimension-bar-item {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}
.dimension-bar-name {
  font-size: 28rpx;
  color: #333333;
  font-weight: 500;
}
.dimension-bar-container {
  height: 24rpx;
  background-color: #F5F7FA;
  border-radius: 12rpx;
  overflow: hidden;
}
.dimension-bar {
  height: 100%;
  background-color: #3E5C76;
  border-radius: 12rpx;
}
.dimension-bar-score {
  font-size: 28rpx;
  font-weight: 600;
  color: #3E5C76;
  text-align: right;
}
.eval-list-section {
  margin-top: 30rpx;
}
.eval-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}
.eval-card {
  background-color: #FFFFFF;
  border-radius: 12rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}
.eval-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}
.eval-course {
  font-size: 30rpx;
  font-weight: 600;
  color: #333333;
}
.eval-score {
  font-size: 32rpx;
  font-weight: bold;
  color: #3E5C76;
}
.eval-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}
.eval-listener {
  font-size: 26rpx;
  color: #666666;
}
.eval-time {
  font-size: 24rpx;
  color: #999999;
}
.eval-dimensions {
  background-color: #F5F7FA;
  border-radius: 8rpx;
  padding: 16rpx;
  margin-bottom: 12rpx;
}
.eval-dim-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8rpx 0;
  border-bottom: 1rpx solid #E4E7ED;
}
.eval-dim-item:last-child {
  border-bottom: none;
}
.dim-name {
  font-size: 26rpx;
  color: #666666;
}
.dim-score {
  font-size: 26rpx;
  font-weight: 600;
  color: #3E5C76;
}
.eval-comment {
  background-color: #F5F7FA;
  border-radius: 8rpx;
  padding: 16rpx;
  margin-bottom: 12rpx;
}
.comment-label {
  font-size: 26rpx;
  color: #666666;
  font-weight: 500;
}
.comment-text {
  font-size: 26rpx;
  color: #333333;
  line-height: 1.6;
}
.eval-level {
  display: flex;
  justify-content: flex-end;
}
.level-tag {
  font-size: 24rpx;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  background-color: #E8F4FD;
  color: #3E5C76;
}
</style>