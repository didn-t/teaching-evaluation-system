<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">督导端</text>
        <text class="title">评教汇总统计</text>
        <text class="desc">负责范围内教师的评教数据汇总</text>
      </view>
      <view class="header-badges">
        <button @click="handleExport" class="export-btn">导出报表</button>
        <button @click="navigateBack" class="badge">返回</button>
      </view>
    </view>

    <!-- 总体统计 -->
    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">总体统计</text>
      </view>
      <view class="stats-grid">
        <view class="stat-card">
          <text class="stat-label">负责教师数</text>
          <text class="stat-value">{{ summaryData.length }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">总评价数</text>
          <text class="stat-value">{{ totalEvaluations }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">平均分</text>
          <text class="stat-value">{{ overallAverage.toFixed(1) }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">最高分</text>
          <text class="stat-value">{{ maxScore.toFixed(1) }}</text>
        </view>
      </view>
    </view>

    <!-- 教师排名 -->
    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">教师排名</text>
        <text class="panel-desc">按平均分排序</text>
      </view>
      <view v-if="summaryData.length === 0" class="empty">暂无数据</view>
      <view v-else class="ranking-list">
        <view v-for="(item, index) in summaryData" :key="item.teacherId" class="ranking-item">
          <view class="rank-badge" :class="getRankClass(index + 1)">
            <text class="rank-number">{{ index + 1 }}</text>
          </view>
          <view class="teacher-info">
            <text class="teacher-name">{{ item.teacherName }}</text>
            <view class="teacher-stats">
              <text class="stat-text">评价数：{{ item.totalEvaluations }}</text>
              <text class="stat-text">平均分：{{ item.averageScore.toFixed(1) }}</text>
              <text class="stat-text">总分：{{ item.totalScore.toFixed(1) }}</text>
            </view>
          </view>
          <view class="score-display">
            <text class="score-value">{{ item.averageScore.toFixed(1) }}</text>
            <text class="score-label">平均分</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 问题统计 -->
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
  </view>
</template>

<script>
import { simpleStore } from '../../utils/simpleStore';

export default {
  data() {
    return {
      currentUser: {},
      summaryData: [],
      problemStats: []
    };
  },
  onLoad() {
    this.loadUserData();
    this.loadStatistics();
  },
  computed: {
    totalEvaluations() {
      try {
        if (!this.summaryData || !Array.isArray(this.summaryData) || this.summaryData.length === 0) {
          return 0;
        }
        return this.summaryData.reduce((sum, item) => {
          if (!item || typeof item.totalEvaluations !== 'number') return sum;
          return sum + item.totalEvaluations;
        }, 0);
      } catch (error) {
        console.error('计算总评价数失败:', error);
        return 0;
      }
    },
    overallAverage() {
      try {
        if (!this.summaryData || !Array.isArray(this.summaryData) || this.summaryData.length === 0) {
          return 0;
        }
        let totalScore = 0;
        let totalCount = 0;
        this.summaryData.forEach(item => {
          if (item && typeof item.averageScore === 'number' && typeof item.totalEvaluations === 'number') {
            totalScore += item.averageScore * item.totalEvaluations;
            totalCount += item.totalEvaluations;
          }
        });
        return totalCount > 0 ? totalScore / totalCount : 0;
      } catch (error) {
        console.error('计算平均分失败:', error);
        return 0;
      }
    },
    maxScore() {
      try {
        if (!this.summaryData || !Array.isArray(this.summaryData) || this.summaryData.length === 0) {
          return 0;
        }
        const scores = this.summaryData
          .filter(item => item && typeof item.averageScore === 'number')
          .map(item => item.averageScore);
        return scores.length > 0 ? Math.max(...scores) : 0;
      } catch (error) {
        console.error('计算最高分失败:', error);
        return 0;
      }
    }
  },
  methods: {
    loadUserData() {
      this.currentUser = simpleStore.state.currentUser || {};
    },
    loadStatistics() {
      // 从本地存储加载统计数据，不进行服务器连接检测
      // TODO: 后期接入后端接口时，可在此处调用API获取统计数据
      // 示例：
      // try {
      //   const userId = this.currentUser.id || this.currentUser._id;
      //   const response = await uni.request({ 
      //     url: `/api/supervisor/evaluations/summary?supervisorId=${userId}`,
      //     timeout: 10000
      //   });
      //   this.summaryData = response.data;
      //   
      //   const problemResponse = await uni.request({ 
      //     url: `/api/supervisor/problems/statistics?supervisorId=${userId}`,
      //     timeout: 10000
      //   });
      //   this.problemStats = problemResponse.data;
      // } catch (error) {
      //   console.error('加载统计数据失败:', error);
      //   // 失败时使用本地数据作为降级方案
      //   this.summaryData = simpleStore.getSupervisorEvaluationsSummary(userId);
      //   this.loadProblemStats();
      // }
      
      try {
        const userId = this.currentUser.id || this.currentUser._id;
        
        if (!userId) {
          console.warn('用户ID不存在，无法加载统计数据');
          this.summaryData = [];
          this.problemStats = [];
          return;
        }
        
        // 使用本地存储数据，不进行网络请求
        // 合并evaluations和listenRecords，统一处理所有评教记录
        const summary = simpleStore.getSupervisorEvaluationsSummary(userId);
        this.summaryData = Array.isArray(summary) ? summary : [];
        
        // 确保数据格式正确
        if (this.summaryData.length > 0) {
          this.summaryData = this.summaryData.map(item => {
            if (!item) return null;
            return {
              teacherId: item.teacherId || '',
              teacherName: item.teacherName || '未知',
              totalEvaluations: typeof item.totalEvaluations === 'number' ? item.totalEvaluations : 0,
              totalScore: typeof item.totalScore === 'number' ? item.totalScore : 0,
              averageScore: typeof item.averageScore === 'number' ? item.averageScore : 0
            };
          }).filter(item => item !== null);
        }
        
        this.loadProblemStats();
      } catch (error) {
        console.error('加载统计数据失败:', error);
        // 静默处理错误，设置默认值
        this.summaryData = [];
        this.problemStats = [];
      }
    },
    loadProblemStats() {
      try {
        // 从评价建议中提取问题关键词（简化版，实际应该由后端分析）
        const userId = this.currentUser.id || this.currentUser._id;
        if (!userId) {
          this.problemStats = [];
          return;
        }
        
        const teachers = simpleStore.getSupervisorTeachers(userId) || [];
        const teacherIds = teachers.map(t => (t.id || t._id)).filter(id => id);
        
        if (teacherIds.length === 0) {
          this.problemStats = [];
          return;
        }
        
        // 统一获取所有评教记录（evaluations和listenRecords）
        const allEvaluations = simpleStore.getAllEvaluations() || [];
        const allListenRecords = simpleStore.state.listenRecords || [];
        const allRecords = [...allEvaluations, ...allListenRecords];
        
        const evaluations = allRecords.filter(e => {
          if (!e || !e.teacherId) return false;
          if (!teacherIds.includes(e.teacherId)) return false;
          // 检查是否有建议内容（支持新旧格式）
          const hasSuggestion = e.suggestion || (e.suggestions && (
            e.suggestions.problems || 
            e.suggestions.improvements || 
            e.suggestions.advantages
          ));
          return hasSuggestion;
        });
        
        // 简单的问题统计（实际应该由后端进行更复杂的分析）
        const problemKeywords = ['问题', '不足', '建议', '改进', '需要', '希望'];
        const problemMap = {};
        
        evaluations.forEach(evaluation => {
          // 优先使用新格式的suggestions，否则使用旧格式的suggestion
          let suggestionText = '';
          if (evaluation.suggestions) {
            // 合并新格式的建议
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
        
        this.problemStats = Object.entries(problemMap)
          .map(([text, count]) => ({ text, count }))
          .sort((a, b) => b.count - a.count)
          .slice(0, 10);
      } catch (error) {
        console.error('加载问题统计失败:', error);
        this.problemStats = [];
      }
    },
    getRankClass(rank) {
      if (rank === 1) return 'rank-gold';
      if (rank === 2) return 'rank-silver';
      if (rank === 3) return 'rank-bronze';
      return 'rank-normal';
    },
    handleExport() {
      // TODO: 后期接入后端接口时，可在此处调用导出API
      // 示例：
      // try {
      //   const response = await uni.request({ 
      //     url: `/api/supervisor/export/listen-records?supervisorId=${this.currentUser.id}`,
      //     method: 'GET',
      //     responseType: 'blob',
      //     timeout: 30000 // 导出可能需要更长时间
      //   });
      //   // 处理文件下载
      //   // uni.downloadFile({ url: response.data.url });
      //   uni.showToast({
      //     title: '导出成功',
      //     icon: 'success'
      //   });
      // } catch (error) {
      //   console.error('导出失败:', error);
      //   uni.showToast({
      //     title: '导出失败，请稍后重试',
      //     icon: 'none'
      //   });
      // }
      
      uni.showToast({
        title: '导出功能待接入后端',
        icon: 'none'
      });
    },
    navigateBack() {
      uni.navigateBack();
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
  border: none;
  margin-left: 8px;
}

.export-btn {
  background-color: #10b981;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  border: none;
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

.empty {
  text-align: center;
  padding: 40px 0;
  color: #999;
}
</style>

