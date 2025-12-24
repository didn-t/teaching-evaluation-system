<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">学院管理员</text>
        <text class="title">学院管理</text>
        <text class="desc">欢迎，{{ currentUser.name }} - {{ currentUser.college }}</text>
      </view>
      <view class="header-badges">
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <view>
          <text class="panel-title-text">学院统计概览</text>
          <text class="panel-desc">{{ currentUser.college }}的整体评价情况</text>
        </view>
      </view>
      <view class="stats-grid">
        <view class="stat-card">
          <text class="stat-label">学院教师数</text>
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
          <text class="stat-label">听课完成率</text>
          <text class="stat-value">{{ listenCompletionRate.toFixed(0) }}%</text>
        </view>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <view>
          <text class="panel-title-text">教师排名</text>
          <text class="panel-desc">按平均分排序</text>
        </view>
      </view>
      <view class="table-container">
        <view v-for="(teacher, index) in teacherRanking" :key="teacher.id" class="table-row">
          <view class="table-cell">{{ index + 1 }}</view>
          <view class="table-cell">{{ teacher.name }}</view>
          <view class="table-cell">{{ teacher.count }}</view>
          <view class="table-cell">{{ teacher.avgScore.toFixed(1) }}</view>
          <view class="table-cell">
            <text class="level-badge" :class="getLevelClass(teacher.level)">{{ teacher.level }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">快速操作</text>
      </view>
      <view class="actions">
        <button @click="navigateTo('/pages/college/statistics')" class="action-button primary">
          统计分析
        </button>
        <button @click="navigateTo('/pages/college/data')" class="action-button ghost">
          数据管理
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
      listenRecords: [],
      collegeTeachers: []
    };
  },
  onLoad() {
    this.loadUserData();
    this.loadData();
  },
  computed: {
    collegeAverageScore() {
      if (this.evaluations.length === 0) return 0;
      const sum = this.evaluations.reduce((acc, e) => acc + e.totalScore, 0);
      return sum / this.evaluations.length;
    },
    listenCompletionRate() {
      if (this.collegeTeachers.length === 0) return 0;
      const teachersWithListen = new Set(this.listenRecords.map(r => r.teacherId));
      return (teachersWithListen.size / this.collegeTeachers.length) * 100;
    },
    teacherRanking() {
      const teacherStats = this.collegeTeachers.map(teacher => {
        const teacherEvals = this.evaluations.filter(e => e.teacherId === teacher.id);
        const count = teacherEvals.length;
        const avgScore = count > 0
          ? teacherEvals.reduce((acc, e) => acc + e.totalScore, 0) / count
          : 0;
        const level = avgScore >= 90 ? '优秀' : avgScore >= 80 ? '良好' : avgScore >= 70 ? '一般' : avgScore >= 60 ? '合格' : '不合格';
        return {
          id: teacher.id,
          name: teacher.name,
          count,
          avgScore,
          level
        };
      });
      return teacherStats.sort((a, b) => b.avgScore - a.avgScore);
    }
  },
  methods: {
    loadUserData() {
      this.currentUser = simpleStore.state.currentUser || {};
    },
    loadData() {
      this.evaluations = simpleStore.getCollegeEvaluations(this.currentUser.college);
      this.listenRecords = simpleStore.getCollegeListenRecords(this.currentUser.college);
      this.collegeTeachers = simpleStore.state.users.filter(
        u => u.college === this.currentUser.college && u.role === 'teacher'
      );
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
  color: #1f2933;
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
  color: #1f2933;
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

.table-container {
  margin-top: 16px;
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  overflow: hidden;
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
</style>