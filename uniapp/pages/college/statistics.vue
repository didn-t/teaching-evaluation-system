<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">学院管理员</text>
        <text class="title">统计分析</text>
        <text class="desc">欢迎，{{ currentUser.name }} - {{ currentUser.college }}</text>
      </view>
      <view class="header-badges">
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </view>
    </view>

    <view class="panel">
      <view class="panel-header">
        <view>
          <text class="panel-title-text">学院统计概览</text>
          <text class="panel-desc">{{ currentUser.college }}的整体评价情况</text>
        </view>
        <button @click="handleExport" class="export-btn">导出报表</button>
      </view>
      <view class="stats-grid">
        <view class="stat-card">
          <text class="stat-label">教师总数</text>
          <text class="stat-value">{{ collegeTeachers.length }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">总评价数</text>
          <text class="stat-value">{{ evaluations.length }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">学院平均分</text>
          <text class="stat-value">{{ collegeAverageScore.toFixed(1) }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">最高分</text>
          <text class="stat-value">{{ maxScore.toFixed(1) }}</text>
        </view>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">教师排名</text>
        <text class="panel-desc">按平均分排序</text>
      </view>
      <view v-if="teacherRanking.length === 0" class="empty">暂无数据</view>
      <view v-else class="ranking-list">
        <view v-for="(teacher, index) in teacherRanking" :key="teacher.id" class="ranking-item">
          <view class="rank-badge" :class="getRankClass(index + 1)">
            <text class="rank-number">{{ index + 1 }}</text>
          </view>
          <view class="teacher-info">
            <text class="teacher-name">{{ teacher.name }}</text>
            <view class="teacher-stats">
              <text class="stat-text">评价数：{{ teacher.count }}</text>
              <text class="stat-text">平均分：{{ teacher.avgScore.toFixed(1) }}</text>
              <text class="stat-text">总分：{{ teacher.totalScore.toFixed(1) }}</text>
            </view>
          </view>
          <view class="score-display">
            <text class="score-value">{{ teacher.avgScore.toFixed(1) }}</text>
            <text class="score-label">平均分</text>
          </view>
        </view>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">问题统计</text>
        <text class="panel-desc">评价中反映的主要问题</text>
      </view>
      <view class="problem-list">
        <view v-for="(problem, index) in problemStats" :key="index" class="problem-item">
          <text class="problem-text">{{ problem.text }}</text>
          <text class="problem-count">出现 {{ problem.count }} 次</text>
        </view>
        <view v-if="problemStats.length === 0" class="empty">暂无问题反馈</view>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">评教详情</text>
        <text class="panel-desc">所有评教记录</text>
      </view>
      <view class="table-container">
        <view class="table-header">
          <view class="table-cell">课程</view>
          <view class="table-cell">任课教师</view>
          <view class="table-cell">评价人</view>
          <view class="table-cell">总分</view>
          <view class="table-cell">等级</view>
        </view>
        <view v-for="evaluation in (evaluations || []).slice(0, 20)" :key="evaluation.id" class="table-row">
          <view class="table-cell">{{ evaluation.courseName || '-' }}</view>
          <view class="table-cell">{{ evaluation.teacherName || '-' }}</view>
          <view class="table-cell">{{ evaluation.anonymous ? '匿名' : (evaluation.evaluatorName || '未知') }}</view>
          <view class="table-cell">{{ evaluation.totalScore || 0 }}</view>
          <view class="table-cell">
            <text class="level-badge" :class="getLevelClass(evaluation.level)">{{ evaluation.level || '-' }}</text>
          </view>
        </view>
        <view v-if="evaluations.length === 0" class="empty">暂无评价记录</view>
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
      listenRecords: [],
      collegeTeachers: []
    };
  },
  onLoad() {
    // 页面加载时直接加载数据，不进行服务器连接检测
    // 与其他账号（如教师端、督导端）使用相同的登录逻辑
    this.loadUserData();
    this.loadData();
  },
  onShow() {
    // 页面显示时刷新数据（如果需要），但不进行服务器连接检测
    // 确保与其他账号逻辑一致
    try {
      if (this.currentUser && this.currentUser.college) {
        this.loadData();
      }
    } catch (error) {
      console.error('页面显示时加载数据失败:', error);
      // 静默处理错误，不影响页面显示
    }
  },
  computed: {
    collegeAverageScore() {
      try {
        if (!this.evaluations || !Array.isArray(this.evaluations) || this.evaluations.length === 0) {
          return 0;
        }
        const validScores = this.evaluations.filter(e => e && e.totalScore && typeof e.totalScore === 'number');
        if (validScores.length === 0) return 0;
        const sum = validScores.reduce((acc, e) => acc + e.totalScore, 0);
        return sum / validScores.length;
      } catch (error) {
        console.error('计算学院平均分失败:', error);
        return 0;
      }
    },
    maxScore() {
      try {
        if (!this.evaluations || !Array.isArray(this.evaluations) || this.evaluations.length === 0) {
          return 0;
        }
        const validScores = this.evaluations
          .filter(e => e && e.totalScore && typeof e.totalScore === 'number')
          .map(e => e.totalScore);
        return validScores.length > 0 ? Math.max(...validScores) : 0;
      } catch (error) {
        console.error('计算最高分失败:', error);
        return 0;
      }
    },
    teacherRanking() {
      try {
        if (!this.collegeTeachers || !Array.isArray(this.collegeTeachers) || this.collegeTeachers.length === 0) {
          return [];
        }
        if (!this.evaluations || !Array.isArray(this.evaluations)) {
          return [];
        }
        const teacherStats = this.collegeTeachers.map(teacher => {
          if (!teacher || !teacher.id) return null;
          const teacherEvals = this.evaluations.filter(e => e && e.teacherId == teacher.id);
          const validEvals = teacherEvals.filter(e => e.totalScore && typeof e.totalScore === 'number');
          const count = validEvals.length;
          const totalScore = validEvals.reduce((acc, e) => acc + e.totalScore, 0);
          const avgScore = count > 0 ? totalScore / count : 0;
          const level = avgScore >= 90 ? '优秀' : avgScore >= 80 ? '良好' : avgScore >= 70 ? '一般' : avgScore >= 60 ? '合格' : '不合格';
          return {
            id: teacher.id,
            name: teacher.name || '未知',
            count,
            totalScore,
            avgScore,
            level
          };
        }).filter(t => t !== null && t.count > 0);
        return teacherStats.sort((a, b) => b.avgScore - a.avgScore);
      } catch (error) {
        console.error('计算教师排名失败:', error);
        return [];
      }
    },
    problemStats() {
      try {
        if (!this.evaluations || !Array.isArray(this.evaluations) || this.evaluations.length === 0) {
          return [];
        }
        const problemKeywords = ['问题', '不足', '建议', '改进', '需要', '希望'];
        const problemMap = {};
        
        this.evaluations.forEach(evaluation => {
          if (!evaluation) return;
          let suggestionText = '';
          if (evaluation.suggestions) {
            const parts = [];
            if (evaluation.suggestions.problems) parts.push(evaluation.suggestions.problems);
            if (evaluation.suggestions.improvements) parts.push(evaluation.suggestions.improvements);
            suggestionText = parts.join(' ');
          } else if (evaluation.suggestion) {
            suggestionText = evaluation.suggestion;
          }
          
          if (suggestionText) {
            problemKeywords.forEach(keyword => {
              if (suggestionText.includes(keyword)) {
                problemMap[keyword] = (problemMap[keyword] || 0) + 1;
              }
            });
          }
        });
        
        return Object.entries(problemMap)
          .map(([text, count]) => ({ text, count }))
          .sort((a, b) => b.count - a.count)
          .slice(0, 10);
      } catch (error) {
        console.error('计算问题统计失败:', error);
        return [];
      }
    }
  },
  methods: {
    loadUserData() {
      this.currentUser = simpleStore.state.currentUser || {};
    },
    loadData() {
      // 直接从本地存储加载数据，不进行服务器连接检测
      // 与其他账号（如教师端、督导端）使用相同的登录逻辑，直接从本地存储获取数据
      // TODO: 后期接入后端接口时，可在此处调用API获取数据
      // 示例：
      // try {
      //   const response = await uni.request({ 
      //     url: `/api/college/evaluations?college=${this.currentUser.college}`,
      //     timeout: 10000
      //   });
      //   this.evaluations = response.data;
      // } catch (error) {
      //   console.error('获取评价数据失败:', error);
      //   // 失败时使用本地数据作为降级方案
      //   this.evaluations = simpleStore.getCollegeEvaluations(this.currentUser.college) || [];
      // }
      
      // 确保用户数据存在
      if (!this.currentUser || !this.currentUser.college) {
        console.warn('用户数据或学院信息不存在，无法加载数据');
        this.evaluations = [];
        this.listenRecords = [];
        this.collegeTeachers = [];
        return;
      }
      
      try {
        const collegeName = this.currentUser.college;
        
        // 使用本地存储数据，不进行网络请求，与其他账号逻辑一致
        const evaluations = simpleStore.getCollegeEvaluations(collegeName);
        const listenRecords = simpleStore.getCollegeListenRecords(collegeName);
        const allUsers = simpleStore.state.users || [];
        
        this.evaluations = Array.isArray(evaluations) ? evaluations : [];
        this.listenRecords = Array.isArray(listenRecords) ? listenRecords : [];
        this.collegeTeachers = Array.isArray(allUsers) 
          ? allUsers.filter(u => u && u.college === collegeName && u.role === 'teacher')
          : [];
      } catch (error) {
        console.error('加载数据失败:', error);
        // 静默处理错误，设置默认值，避免影响用户体验
        this.evaluations = [];
        this.listenRecords = [];
        this.collegeTeachers = [];
      }
    },
    getRankClass(rank) {
      if (rank === 1) return 'rank-gold';
      if (rank === 2) return 'rank-silver';
      if (rank === 3) return 'rank-bronze';
      return 'rank-normal';
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
    handleExport() {
      uni.showToast({
        title: '导出功能待接入后端',
        icon: 'none'
      });
    },
    handleLogout() {
      simpleStore.logout();
      uni.redirectTo({
        url: '/pages/login/login'
      });
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
  color: #1f2933; /* 添加字体颜色 */
}

.desc {
  font-size: 14px;
  color: #666;
  display: block;
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
  margin-bottom: 16px;
}

.panel-title-text {
  font-size: 20px;
  font-weight: bold;
  display: block;
  margin-bottom: 4px;
  color: #1f2933; /* 添加字体颜色 */
}

.panel-desc {
  font-size: 14px;
  color: #666;
  display: block;
}

.chart-placeholder {
  height: 300px;
  background: #eef2ff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #c7d2fe;
}

.placeholder-text {
  color: #1f2933;
  font-size: 16px;
}

.data-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.data-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #e4e9f1;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.export-btn {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.stat-card {
  background: #eef2ff;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e4e9f1;
  text-align: center;
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
  color: #4f46e5;
  display: block;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e9f1;
}

.rank-badge {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.rank-gold {
  background: #fbbf24;
  color: white;
}

.rank-silver {
  background: #9ca3af;
  color: white;
}

.rank-bronze {
  background: #d97706;
  color: white;
}

.rank-normal {
  background: #e4e9f1;
  color: #666;
}

.rank-number {
  font-size: 18px;
}

.teacher-info {
  flex: 1;
}

.teacher-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2933;
  display: block;
  margin-bottom: 8px;
}

.teacher-stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stat-text {
  font-size: 12px;
  color: #666;
}

.score-display {
  text-align: right;
}

.score-value {
  font-size: 24px;
  font-weight: 700;
  color: #4f46e5;
  display: block;
}

.score-label {
  font-size: 12px;
  color: #666;
  display: block;
}

.problem-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.problem-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #fef3c7;
  border-radius: 8px;
  border-left: 4px solid #f59e0b;
}

.problem-text {
  flex: 1;
  font-size: 14px;
  color: #92400e;
}

.problem-count {
  font-size: 12px;
  color: #d97706;
  font-weight: 600;
}

.table-container {
  margin-top: 16px;
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: flex;
  padding: 12px;
  background: #eef2ff;
  font-weight: bold;
}

.table-row {
  display: flex;
  padding: 12px;
  border-bottom: 1px solid #e4e9f1;
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  flex: 1;
  padding: 4px 8px;
  color: #1f2933;
}

.level-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
}

.level-excellent {
  background: #d1fae5;
  color: #059669;
}

.level-good {
  background: #cffafe;
  color: #0891b2;
}

.level-normal {
  background: #fef3c7;
  color: #d97706;
}

.level-pass {
  background: #fee2e2;
  color: #dc2626;
}

.level-fail {
  background: #fee2e2;
  color: #991b1b;
}

.empty {
  text-align: center;
  padding: 40px 0;
  color: #999;
}
</style>