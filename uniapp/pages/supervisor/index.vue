<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">督导端</text>
        <text class="title">督导工作台</text>
        <text class="desc">欢迎，{{ currentUser.name }}</text>
      </view>
      <view class="header-badges">
        <text class="badge">{{ currentUser.college || '督导老师' }}</text>
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </view>
    </view>

    <!-- 快速统计 -->
    <view class="panel">
      <view class="panel-title">
        <view>
          <text class="panel-title-text">负责范围统计</text>
          <text class="panel-desc">您负责范围内的教学评价情况</text>
        </view>
      </view>
      <view class="stats-grid">
        <view class="stat-card">
          <text class="stat-label">负责教师数</text>
          <text class="stat-value">{{ responsibleTeachers.length }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">负责课程数</text>
          <text class="stat-value">{{ responsibleCourses.length }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">总评价数</text>
          <text class="stat-value">{{ totalEvaluations }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">平均分</text>
          <text class="stat-value">{{ overallAverageScore.toFixed(1) }}</text>
        </view>
      </view>
    </view>

    <!-- 功能入口 -->
    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">功能入口</text>
      </view>
      <view class="actions-grid">
        <view class="action-card" @click="navigateTo('/pages/supervisor/schedule')">
          <text class="action-icon">📅</text>
          <text class="action-title">查看课表</text>
          <text class="action-desc">查看负责范围内教师课表</text>
        </view>
        <view class="action-card" @click="navigateTo('/pages/supervisor/evaluate')">
          <text class="action-icon">✍️</text>
          <text class="action-title">进行评教</text>
          <text class="action-desc">参与听课并提交评分</text>
        </view>
        <view class="action-card" @click="navigateTo('/pages/supervisor/statistics')">
          <text class="action-icon">📊</text>
          <text class="action-title">统计汇总</text>
          <text class="action-desc">查看评教汇总数据</text>
        </view>
      </view>
    </view>

    <!-- 最近评价记录 -->
    <view class="panel">
      <view class="panel-title">
        <view>
          <text class="panel-title-text">最近评价记录</text>
          <text class="panel-desc">您最近提交的评价</text>
        </view>
      </view>
      <view v-if="recentEvaluations.length === 0" class="empty">暂无评价记录</view>
      <view v-else class="list">
        <view v-for="evaluation in recentEvaluations" :key="evaluation.id" class="card">
          <view class="card-head">
            <view>
              <text class="name">{{ evaluation.courseName }}</text>
              <text class="title">授课教师：{{ evaluation.teacherName }}</text>
              <view class="meta">
                <text>评价时间：{{ formatDate(evaluation.createdAt) }}</text>
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
        </view>
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
      responsibleTeachers: [],
      responsibleCourses: [],
      recentEvaluations: []
    };
  },
  onLoad() {
    // 页面加载时直接加载数据，不进行服务器连接检测
    // 与其他账号（如教师端）使用相同的登录逻辑
    this.loadUserData();
    this.loadData();
  },
  onShow() {
    // 页面显示时刷新数据（如果需要），但不进行服务器连接检测
    // 确保与教师端逻辑一致
    try {
      if (this.currentUser && (this.currentUser.id || this.currentUser._id)) {
        this.loadData();
      }
    } catch (error) {
      console.error('页面显示时加载数据失败:', error);
      // 静默处理错误，不影响页面显示
    }
  },
  computed: {
    totalEvaluations() {
      // 从本地存储计算总评价数，不进行服务器连接
      // 与其他账号（如教师端）使用相同的逻辑，直接从本地存储获取
      // TODO: 后期接入后端接口时，可在此处调用API
      // const response = await uni.request({ 
      //   url: `/api/supervisor/evaluations/count?supervisorId=${this.currentUser.id}`,
      //   timeout: 10000
      // });
      // return response.data.count;
      try {
        if (!this.currentUser || (!this.currentUser.id && !this.currentUser._id)) {
          return 0;
        }
        const userId = this.currentUser.id || this.currentUser._id;
        const summary = simpleStore.getSupervisorEvaluationsSummary(userId);
        if (!summary || !Array.isArray(summary) || summary.length === 0) {
          return 0;
        }
        return summary.reduce((sum, item) => {
          if (!item || typeof item.totalEvaluations !== 'number') return sum;
          return sum + item.totalEvaluations;
        }, 0);
      } catch (error) {
        console.error('计算总评价数失败:', error);
        return 0;
      }
    },
    overallAverageScore() {
      // 从本地存储计算平均分，不进行服务器连接
      // 与其他账号（如教师端）使用相同的逻辑，直接从本地存储获取
      // TODO: 后期接入后端接口时，可在此处调用API
      // const response = await uni.request({ 
      //   url: `/api/supervisor/evaluations/average?supervisorId=${this.currentUser.id}`,
      //   timeout: 10000
      // });
      // return response.data.average;
      try {
        if (!this.currentUser || (!this.currentUser.id && !this.currentUser._id)) {
          return 0;
        }
        const userId = this.currentUser.id || this.currentUser._id;
        const summary = simpleStore.getSupervisorEvaluationsSummary(userId);
        if (!summary || !Array.isArray(summary) || summary.length === 0) {
          return 0;
        }
        let totalScore = 0;
        let totalCount = 0;
        summary.forEach(item => {
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
    }
  },
  methods: {
    loadUserData() {
      this.currentUser = simpleStore.state.currentUser || {};
    },
    loadData() {
      // 直接从本地存储加载数据，不进行服务器连接检测
      // 与其他账号（如教师端）使用相同的登录逻辑，直接从本地存储获取数据
      // TODO: 后期接入后端接口时，可在此处调用API获取数据
      // 示例：
      // try {
      //   const userId = this.currentUser.id || this.currentUser._id;
      //   const teachersResponse = await uni.request({ 
      //     url: `/api/supervisor/teachers?supervisorId=${userId}`,
      //     timeout: 10000 // 设置超时时间
      //   });
      //   this.responsibleTeachers = teachersResponse.data;
      // } catch (error) {
      //   console.error('获取教师列表失败:', error);
      //   // 失败时使用本地数据作为降级方案
      //   this.responsibleTeachers = simpleStore.getSupervisorTeachers(userId);
      // }
      
      // 确保用户数据存在
      if (!this.currentUser || (!this.currentUser.id && !this.currentUser._id)) {
        console.warn('用户数据不存在，无法加载数据');
        this.responsibleTeachers = [];
        this.responsibleCourses = [];
        this.recentEvaluations = [];
        return;
      }
      
      try {
        const userId = this.currentUser.id || this.currentUser._id;
        
        if (!userId) {
          console.warn('用户ID不存在，无法加载数据');
          this.responsibleTeachers = [];
          this.responsibleCourses = [];
          this.recentEvaluations = [];
          return;
        }
        
        // 使用本地存储数据，不进行网络请求，与其他账号逻辑一致
        const teachers = simpleStore.getSupervisorTeachers(userId);
        const courses = simpleStore.getSupervisorCourses(userId);
        this.responsibleTeachers = Array.isArray(teachers) ? teachers : [];
        this.responsibleCourses = Array.isArray(courses) ? courses : [];
        
        // 获取最近的评价记录（从本地存储）
        const allEvaluations = simpleStore.getAllEvaluations() || [];
        const allListenRecords = simpleStore.getSupervisorListenRecords(userId) || [];
        
        // 安全地合并和过滤记录
        // 统一处理所有评教记录，不再区分evaluations和listenRecords
        const allRecords = (Array.isArray(allEvaluations) ? allEvaluations : [])
          .filter(e => {
            if (!e || !e.evaluatorId) return false;
            return e.evaluatorId == userId;
          })
          .sort((a, b) => {
            try {
              const dateA = a.createdAt ? new Date(a.createdAt).getTime() : 0;
              const dateB = b.createdAt ? new Date(b.createdAt).getTime() : 0;
              return dateB - dateA;
            } catch (e) {
              return 0;
            }
          })
          .slice(0, 5);
        this.recentEvaluations = allRecords || [];
      } catch (error) {
        console.error('加载数据失败:', error);
        // 静默处理错误，设置默认值，避免影响用户体验
        this.responsibleTeachers = [];
        this.responsibleCourses = [];
        this.recentEvaluations = [];
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
    navigateTo(url) {
      uni.navigateTo({
        url: url
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

.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.action-card {
  background: #f8f9fa;
  border: 1px solid #e4e9f1;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  /* #ifdef H5 */
  cursor: pointer;
  transition: all 0.3s;
  /* #endif */
}

.action-card:active {
  background: #eef2ff;
  transform: scale(0.98);
}

.action-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
}

.action-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2933;
  display: block;
  margin-bottom: 4px;
}

.action-desc {
  font-size: 12px;
  color: #666;
  display: block;
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

.empty {
  text-align: center;
  padding: 40px 0;
  color: #999;
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
</style>

