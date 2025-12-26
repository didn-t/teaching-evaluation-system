<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">教师端</text>
        <text class="title">我的评价记录</text>
        <text class="desc">欢迎，{{ currentUser.name }}</text>
      </view>
      <view class="header-badges">
        <text class="badge">{{ currentUser.college }}</text>
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </view>
    </view>

    <!-- 个人课表 -->
    <view class="panel">
      <view class="panel-title">
        <view>
          <text class="panel-title-text">个人课表</text>
          <text class="panel-desc">我的授课课程</text>
        </view>
      </view>
      <view v-if="myCourses.length === 0" class="empty">暂无课程</view>
      <view v-else class="course-list">
        <view v-for="course in myCourses" :key="course.id" class="course-card">
          <view class="course-info">
            <text class="course-name">{{ course.name }}</text>
            <text class="course-meta">{{ course.semester }} · {{ course.college }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <view>
          <text class="panel-title-text">评价统计</text>
          <text class="panel-desc">您的教学评价汇总</text>
        </view>
      </view>
      <view class="stats-grid">
        <view class="stat-card">
          <text class="stat-label">总评价数</text>
          <text class="stat-value">{{ evaluations.length }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">平均分</text>
          <text class="stat-value">{{ averageScore.toFixed(1) }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">当前等级</text>
          <text class="stat-value" :class="currentLevelClass">{{ currentLevel }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">各项目平均分</text>
          <view class="stat-details">
            <text>教学态度: {{ avgScores.teachingAttitude.toFixed(1) }}</text>
            <text>教学内容: {{ avgScores.content.toFixed(1) }}</text>
            <text>教学方法: {{ avgScores.method.toFixed(1) }}</text>
            <text>教学效果: {{ avgScores.effect.toFixed(1) }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 得分趋势图 -->
    <view class="panel">
      <view class="panel-title">
        <view>
          <text class="panel-title-text">得分趋势图</text>
          <text class="panel-desc">您的评教得分变化趋势</text>
        </view>
      </view>
      <view v-if="evaluations.length === 0" class="empty">暂无评价数据</view>
      <view v-else class="trend-chart">
        <view class="chart-container">
          <view class="chart-y-axis">
            <text v-for="(label, index) in yAxisLabels" :key="index" class="y-label">{{ label }}</text>
          </view>
          <view class="chart-content">
            <view class="chart-grid">
              <view v-for="(label, index) in xAxisLabels" :key="index" class="grid-line"></view>
            </view>
            <view class="chart-line-container">
              <view class="chart-line" :style="{ height: chartHeight + 'px' }">
                <view 
                  v-for="(point, index) in trendData" 
                  :key="index"
                  class="chart-point"
                  :style="{ 
                    left: (index * (100 / (trendData.length - 1 || 1))) + '%',
                    bottom: ((point.score - minScore) / (maxScore - minScore || 1) * 100) + '%'
                  }"
                >
                  <view class="point-dot"></view>
                  <view class="point-label">{{ point.score }}</view>
                </view>
              </view>
            </view>
            <view class="chart-x-axis">
              <text v-for="(label, index) in xAxisLabels" :key="index" class="x-label">{{ label }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 本院公开统计数据 -->
    <view class="panel">
      <view class="panel-title">
        <view>
          <text class="panel-title-text">本院公开统计</text>
          <text class="panel-desc">{{ currentUser.college }}的整体评价情况</text>
        </view>
      </view>
      <view class="college-stats">
        <view class="college-stat-item">
          <text class="college-stat-label">学院总平均分</text>
          <text class="college-stat-value">{{ collegeAverageScore.toFixed(1) }}</text>
        </view>
        <view class="college-stat-item">
          <text class="college-stat-label">学院总评价数</text>
          <text class="college-stat-value">{{ collegeEvaluations.length }}</text>
        </view>
        <view class="college-stat-item">
          <text class="college-stat-label">学院教师数</text>
          <text class="college-stat-value">{{ collegeTeachersCount }}</text>
        </view>
      </view>
      <view class="college-note">
        <text class="note-text">注：仅显示学院公开统计数据，不包含其他教师详细评教信息</text>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <view>
          <text class="panel-title-text">评价记录</text>
          <text class="panel-desc">查看所有评价详情</text>
        </view>
        <view class="filters">
          <input v-model="searchText" type="text" placeholder="搜索课程..." class="search-input" />
          <picker mode="selector" :range="levelOptions" @change="onLevelChange">
            <view class="picker-text">{{ selectedLevelLabel }}</view>
          </picker>
        </view>
      </view>
      <view v-if="filteredEvaluations.length === 0" class="empty">暂无评价记录</view>
      <view v-else class="list">
        <view v-for="evaluation in filteredEvaluations" :key="evaluation.id" class="card">
          <view class="card-head">
            <view>
              <text class="name">{{ evaluation.courseName }}</text>
              <text class="title">评价时间：{{ formatDate(evaluation.createdAt) }}</text>
              <view class="meta">
                <text>评价人：{{ evaluation.anonymous ? '匿名' : (evaluation.evaluatorName || '未知') }}</text>
                <text class="dot">•</text>
                <text>角色：{{ evaluation.evaluatorRole === 'supervisor' ? '督导老师' : (evaluation.evaluatorRole === 'teacher' ? '教师' : '未知') }}</text>
                <text v-if="evaluation.submitStatus" class="dot">•</text>
                <text v-if="evaluation.submitStatus" class="submit-status" :class="evaluation.submitStatus === 'during' ? 'status-during' : 'status-after'">
                  {{ evaluation.submitStatus === 'during' ? '⏱️ 课中' : '✅ 课后' }}
                </text>
              </view>
            </view>
            <view class="rating-info">
              <text class="rating-number">{{ evaluation.totalScore }}</text>
              <text class="level-badge" :class="getLevelClass(evaluation.level)">{{ evaluation.level }}</text>
            </view>
          </view>
          <view class="score-details">
            <text class="score-item">教学态度：{{ evaluation.scores.teachingAttitude }}分</text>
            <text class="score-item">教学内容：{{ evaluation.scores.content }}分</text>
            <text class="score-item">教学方法：{{ evaluation.scores.method }}分</text>
            <text class="score-item">教学效果：{{ evaluation.scores.effect }}分</text>
          </view>
          <view v-if="evaluation.suggestion || (evaluation.suggestions && (evaluation.suggestions.advantages || evaluation.suggestions.problems || evaluation.suggestions.improvements))" class="content">
            <text class="strong">文字评价建议：</text>
            <view v-if="evaluation.suggestions && (evaluation.suggestions.advantages || evaluation.suggestions.problems || evaluation.suggestions.improvements)" class="suggestions-detail">
              <view v-if="evaluation.suggestions.advantages" class="suggestion-part">
                <text class="suggestion-part-label">优点：</text>
                <text class="suggestion-part-text">{{ evaluation.suggestions.advantages }}</text>
              </view>
              <view v-if="evaluation.suggestions.problems" class="suggestion-part">
                <text class="suggestion-part-label">问题：</text>
                <text class="suggestion-part-text">{{ evaluation.suggestions.problems }}</text>
              </view>
              <view v-if="evaluation.suggestions.improvements" class="suggestion-part">
                <text class="suggestion-part-label">改进方向：</text>
                <text class="suggestion-part-text">{{ evaluation.suggestions.improvements }}</text>
              </view>
            </view>
            <view v-else-if="evaluation.suggestion" class="suggestion-text">
              <text>{{ evaluation.suggestion }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 普通老师和督导老师都可以进行评教 -->
    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">快速操作</text>
      </view>
      <view class="actions">
        <button @click="navigateTo('/pages/teacher/evaluate')" class="action-button primary">
          进行评教
        </button>
      </view>
    </view>
  </view>
</template>

<script>
import { simpleStore } from '../../utils/simpleStore';

export default {
  data() {
    return {
      currentUser: {},
      evaluations: [],
      myCourses: [],
      collegeEvaluations: [],
      searchText: '',
      filterLevel: '',
      levelOptions: ['全部等级', '优秀', '良好', '一般', '合格', '不合格'],
      selectedLevelLabel: '全部等级',
      chartHeight: 200
    };
  },
  onLoad() {
    this.loadUserData();
    this.loadEvaluations();
    this.loadMyCourses();
    this.loadCollegeStats();
  },
  computed: {
    // 检查当前用户是否有评教权限（普通老师和督导老师都可以）
    canEvaluate() {
      const userId = this.currentUser.id || this.currentUser._id;
      return simpleStore.canEvaluate(userId);
    },
    filteredEvaluations() {
      let result = this.evaluations;
      if (this.searchText) {
        result = result.filter(e => e.courseName.includes(this.searchText));
      }
      if (this.filterLevel) {
        result = result.filter(e => e.level === this.filterLevel);
      }
      return result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    },
    averageScore() {
      if (this.evaluations.length === 0) return 0;
      const sum = this.evaluations.reduce((acc, e) => acc + e.totalScore, 0);
      return sum / this.evaluations.length;
    },
    avgScores() {
      if (this.evaluations.length === 0) {
        return { teachingAttitude: 0, content: 0, method: 0, effect: 0 };
      }
      const totals = this.evaluations.reduce((acc, e) => ({
        teachingAttitude: acc.teachingAttitude + e.scores.teachingAttitude,
        content: acc.content + e.scores.content,
        method: acc.method + e.scores.method,
        effect: acc.effect + e.scores.effect
      }), { teachingAttitude: 0, content: 0, method: 0, effect: 0 });
      const count = this.evaluations.length;
      return {
        teachingAttitude: totals.teachingAttitude / count,
        content: totals.content / count,
        method: totals.method / count,
        effect: totals.effect / count
      };
    },
    currentLevel() {
      const score = this.averageScore;
      if (score >= 90) return '优秀';
      if (score >= 80) return '良好';
      if (score >= 70) return '一般';
      if (score >= 60) return '合格';
      return '不合格';
    },
    currentLevelClass() {
      const score = this.averageScore;
      if (score >= 90) return 'level-excellent';
      if (score >= 80) return 'level-good';
      if (score >= 70) return 'level-normal';
      if (score >= 60) return 'level-pass';
      return 'level-fail';
    },
    // 趋势图数据
    trendData() {
      if (this.evaluations.length === 0) return [];
      // 按时间排序
      const sorted = [...this.evaluations].sort((a, b) => 
        new Date(a.createdAt) - new Date(b.createdAt)
      );
      // 取最近10条或全部
      const recent = sorted.slice(-10);
      return recent.map((e, index) => ({
        score: e.totalScore,
        date: new Date(e.createdAt),
        index: index
      }));
    },
    minScore() {
      if (this.trendData.length === 0) return 0;
      return Math.min(...this.trendData.map(d => d.score)) - 5;
    },
    maxScore() {
      if (this.trendData.length === 0) return 100;
      return Math.max(...this.trendData.map(d => d.score)) + 5;
    },
    yAxisLabels() {
      const labels = [];
      const step = (this.maxScore - this.minScore) / 4;
      for (let i = 4; i >= 0; i--) {
        labels.push(Math.round(this.minScore + step * i));
      }
      return labels;
    },
    xAxisLabels() {
      if (this.trendData.length === 0) return [];
      return this.trendData.map((d, index) => {
        const date = d.date;
        const month = date.getMonth() + 1;
        const day = date.getDate();
        return `${month}/${day}`;
      });
    },
    // 学院统计数据
    collegeAverageScore() {
      if (this.collegeEvaluations.length === 0) return 0;
      const sum = this.collegeEvaluations.reduce((acc, e) => acc + e.totalScore, 0);
      return sum / this.collegeEvaluations.length;
    },
    collegeTeachersCount() {
      if (!this.currentUser.college) return 0;
      return simpleStore.getCollegeUsers(this.currentUser.college)
        .filter(u => u.role === 'teacher').length;
    }
  },
  methods: {
    loadUserData() {
      this.currentUser = simpleStore.state.currentUser || {};
    },
    loadEvaluations() {
      try {
        this.evaluations = simpleStore.getTeacherEvaluations(this.currentUser.id || this.currentUser._id);
      } catch (error) {
        console.error('加载评价失败:', error);
      }
    },
    loadMyCourses() {
      try {
        const allCourses = simpleStore.getCourses();
        const teacherId = this.currentUser.id || this.currentUser._id;
        this.myCourses = allCourses.filter(course => 
          course.teacherId == teacherId
        );
      } catch (error) {
        console.error('加载课程失败:', error);
      }
    },
    loadCollegeStats() {
      try {
        if (this.currentUser.college) {
          // 只获取学院的总评价数据，不包含其他教师的详细信息
          this.collegeEvaluations = simpleStore.getCollegeEvaluations(this.currentUser.college);
        }
      } catch (error) {
        console.error('加载学院统计数据失败:', error);
      }
    },
    getLevelClass(level) {
      const map = {
        '优秀': 'level-excellent',
        '良好': 'level-good',
        '一般': 'level-normal',
        '合格': 'level-pass',
        '不合格': 'level-fail'
      };
      return map[level] || '';
    },
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleString('zh-CN');
    },
    handleLogout() {
      simpleStore.logout();
      uni.redirectTo({
        url: '/pages/login/login'
      });
    },
    onLevelChange(e) {
      const selectedIndex = e.detail.value;
      this.selectedLevelLabel = this.levelOptions[selectedIndex];
      this.filterLevel = selectedIndex === 0 ? '' : this.levelOptions[selectedIndex];
    },
    navigateTo(url) {
      // 如果是 tabBar 页面，使用 switchTab，否则使用 navigateTo
      const tabBarPages = ['/pages/teacher/index', '/pages/teacher/evaluate'];
      if (tabBarPages.includes(url)) {
        uni.switchTab({
          url: url
        });
      } else {
        uni.navigateTo({
          url: url
        });
      }
    }
  }
};
</script>

<style scoped>
.page {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
}

.eyebrow {
  font-size: 14px;
  color: #4f46e5;
  display: block;
  margin-bottom: 4px;
}

.title {
  font-size: 24px;
  font-weight: bold;
  display: block;
  margin-bottom: 8px;
}

.desc {
  font-size: 14px;
  color: #666;
  display: block;
}

.badge {
  background-color: #e0e7ff;
  color: #4f46e5;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  margin-right: 10px;
}

.logout-btn {
  background-color: #ef4444;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
}

.panel {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.panel-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.panel-title-text {
  font-size: 20px;
  font-weight: bold;
  display: block;
}

.panel-desc {
  font-size: 14px;
  color: #666;
  display: block;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.stat-card {
  background: #eef2ff;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e4e9f1;
}

.stat-label {
  font-size: 14px;
  color: #1f2933;
  margin-bottom: 8px;
  display: block;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #2d3643;
  display: block;
}

.level-excellent {
  color: #10b981;
}

.level-good {
  color: #3b82f6;
}

.level-normal {
  color: #f59e0b;
}

.level-pass {
  color: #8b5cf6;
}

.level-fail {
  color: #ef4444;
}

.stat-details {
  font-size: 14px;
  color: #5d6673;
  line-height: 1.8;
}

.filters {
  display: flex;
  gap: 10px;
}

.search-input {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 14px;
}

.picker-text {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 14px;
  background: white;
}

.card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.card-head {
  display: flex;
  justify-content: space-between;
}

.name {
  font-size: 18px;
  font-weight: bold;
  display: block;
  margin-bottom: 4px;
}

.title {
  font-size: 14px;
  color: #666;
  display: block;
  margin-bottom: 8px;
}

.meta {
  display: flex;
  gap: 4px;
  font-size: 12px;
  color: #999;
}

.dot {
  margin: 0 4px;
}

.rating-info {
  text-align: right;
}

.rating-number {
  font-size: 32px;
  font-weight: 700;
  color: #4f46e5;
  display: block;
  margin-bottom: 4px;
}

.level-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
}

.score-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
  margin: 12px 0;
  padding: 12px;
  background: #eef2ff;
  border-radius: 8px;
}

.score-item {
  font-size: 14px;
  color: #5d6673;
  display: block;
}

.content {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.strong {
  font-weight: bold;
  margin-right: 8px;
}

.suggestions-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.suggestion-part {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #4f46e5;
}

.suggestion-part-label {
  font-weight: 600;
  color: #4f46e5;
  font-size: 14px;
  margin-bottom: 4px;
}

.suggestion-part-text {
  color: #333;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.suggestion-text {
  margin-top: 8px;
  color: #333;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.submit-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.status-during {
  background: #fef3c7;
  color: #d97706;
}

.status-after {
  background: #d1fae5;
  color: #059669;
}

.empty {
  text-align: center;
  padding: 40px 0;
  color: #999;
}

.actions {
  display: flex;
  gap: 12px;
}

.action-button {
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  border: none;
}

.action-button.primary {
  background: #4f46e5;
  color: #fff;
}

.action-button.ghost {
  background: #fff;
  border: 1px solid #d7deea;
  color: #1f2933;
}

/* 个人课表样式 */
.course-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.course-card {
  background: #f8f9fa;
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  padding: 16px;
}

.course-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.course-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2933;
  display: block;
}

.course-meta {
  font-size: 14px;
  color: #666;
  display: block;
}

/* 趋势图样式 */
.trend-chart {
  margin-top: 16px;
}

.chart-container {
  display: flex;
  height: 250px;
}

.chart-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 40px;
  padding-right: 8px;
  height: 200px;
}

.y-label {
  font-size: 12px;
  color: #666;
  text-align: right;
}

.chart-content {
  flex: 1;
  position: relative;
  height: 200px;
}

.chart-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: space-between;
}

.grid-line {
  width: 1px;
  background: #e4e9f1;
  height: 100%;
}

.chart-line-container {
  position: relative;
  width: 100%;
  height: 200px;
}

.chart-line {
  position: relative;
  width: 100%;
  height: 200px;
}

.chart-point {
  position: absolute;
  transform: translateX(-50%);
}

.point-dot {
  width: 8px;
  height: 8px;
  background: #4f46e5;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.point-label {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  color: #4f46e5;
  font-weight: 600;
  white-space: nowrap;
}

.chart-x-axis {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e4e9f1;
}

.x-label {
  font-size: 12px;
  color: #666;
  flex: 1;
  text-align: center;
}

/* 学院统计样式 */
.college-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.college-stat-item {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.college-stat-label {
  font-size: 14px;
  color: #666;
  display: block;
  margin-bottom: 8px;
}

.college-stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #0369a1;
  display: block;
}

.college-note {
  margin-top: 16px;
  padding: 12px;
  background: #fef3c7;
  border-radius: 8px;
  border-left: 4px solid #f59e0b;
}

.note-text {
  font-size: 12px;
  color: #92400e;
  line-height: 1.5;
}

.tip-content {
  padding: 16px;
  background: #f0f9ff;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.tip-text {
  font-size: 14px;
  color: #1e40af;
  line-height: 1.6;
  display: block;
}
</style>