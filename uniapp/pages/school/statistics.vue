<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">学校管理员</text>
        <text class="title">统计分析</text>
        <text class="desc">欢迎，{{ currentUser.name }}</text>
      </view>
      <view class="header-badges">
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">全校统计图表</text>
        <text class="panel-desc">全校教学质量综合分析</text>
      </view>
      
      <view class="chart-placeholder">
        <text class="placeholder-text">图表展示区域</text>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">学院数据对比</text>
      </view>
      
      <view class="table-container">
        <view class="table-header">
          <view class="table-cell">学院</view>
          <view class="table-cell">教师数</view>
          <view class="table-cell">评价数</view>
          <view class="table-cell">平均分</view>
        </view>
        <view v-for="college in collegeRanking" :key="college.id" class="table-row">
          <view class="table-cell">{{ college.name }}</view>
          <view class="table-cell">{{ college.teacherCount }}</view>
          <view class="table-cell">{{ college.evalCount }}</view>
          <view class="table-cell">{{ college.avgScore.toFixed(1) }}</view>
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
      colleges: [],
      allTeachers: [],
      allEvaluations: []
    };
  },
  onLoad() {
    this.loadUserData();
    this.loadData();
  },
  computed: {
    collegeRanking() {
      return this.colleges.map(college => {
        const collegeTeachers = this.allTeachers.filter(t => t.college === college.name);
        const collegeEvals = this.allEvaluations.filter(e => {
          const teacher = this.allTeachers.find(t => t.id === e.teacherId);
          return teacher && teacher.college === college.name;
        });
        const avgScore = collegeEvals.length > 0
          ? collegeEvals.reduce((acc, e) => acc + e.totalScore, 0) / collegeEvals.length
          : 0;
        return {
          id: college.id,
          name: college.name,
          teacherCount: collegeTeachers.length,
          evalCount: collegeEvals.length,
          avgScore
        };
      }).sort((a, b) => b.avgScore - a.avgScore);
    }
  },
  methods: {
    loadUserData() {
      this.currentUser = simpleStore.state.currentUser || {};
    },
    loadData() {
      this.colleges = simpleStore.state.colleges;
      this.allTeachers = simpleStore.state.users.filter(u => u.role === 'teacher');
      this.allEvaluations = simpleStore.state.evaluations;
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
  color: #1f2933; /* 添加字体颜色 */
}
</style>