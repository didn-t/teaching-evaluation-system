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
      <view class="panel-title">
        <text class="panel-title-text">统计图表</text>
        <text class="panel-desc">学院整体教学质量分析</text>
      </view>
      
      <view class="chart-placeholder">
        <text class="placeholder-text">图表展示区域</text>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">数据分析</text>
      </view>
      
      <view class="data-list">
        <view class="data-item">
          <text class="label">教师总数:</text>
          <text class="value">{{ collegeTeachers.length }}</text>
        </view>
        <view class="data-item">
          <text class="label">评价总数:</text>
          <text class="value">{{ evaluations.length }}</text>
        </view>
        <view class="data-item">
          <text class="label">平均得分:</text>
          <text class="value">{{ collegeAverageScore.toFixed(1) }}</text>
        </view>
        <view class="data-item">
          <text class="label">听课完成率:</text>
          <text class="value">{{ listenCompletionRate.toFixed(0) }}%</text>
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

.data-item:last-child {
  border-bottom: none;
}

.label {
  font-size: 16px;
  color: #1f2933; /* 添加字体颜色 */
}

.value {
  font-size: 16px;
  font-weight: 600;
  color: #4f46e5;
}
</style>