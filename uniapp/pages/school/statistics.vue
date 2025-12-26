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
      <view class="panel-header">
        <view>
          <text class="panel-title-text">全校统计概览</text>
          <text class="panel-desc">整体教学质量情况</text>
        </view>
        <button @click="handleExport" class="export-btn">导出报表</button>
      </view>
      <view class="stats-grid">
        <view class="stat-card">
          <text class="stat-label">学院数</text>
          <text class="stat-value">{{ colleges.length }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">教师总数</text>
          <text class="stat-value">{{ allTeachers.length }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">总评价数</text>
          <text class="stat-value">{{ allEvaluations.length }}</text>
        </view>
        <view class="stat-card">
          <text class="stat-label">全校平均分</text>
          <text class="stat-value">{{ schoolAverageScore.toFixed(1) }}</text>
        </view>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">学院排名</text>
        <text class="panel-desc">按平均分排序</text>
      </view>
      <view class="table-container">
        <view class="table-header">
          <view class="table-cell">排名</view>
          <view class="table-cell">学院</view>
          <view class="table-cell">教师数</view>
          <view class="table-cell">评价数</view>
          <view class="table-cell">平均分</view>
        </view>
        <view v-for="(college, index) in collegeRanking" :key="college.id" class="table-row">
          <view class="table-cell">{{ index + 1 }}</view>
          <view class="table-cell">{{ college.name }}</view>
          <view class="table-cell">{{ college.teacherCount }}</view>
          <view class="table-cell">{{ college.evalCount }}</view>
          <view class="table-cell">{{ college.avgScore.toFixed(1) }}</view>
        </view>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">全校教师排名（Top 20）</text>
        <text class="panel-desc">按平均分排序</text>
      </view>
      <view class="table-container">
        <view class="table-header">
          <view class="table-cell">排名</view>
          <view class="table-cell">姓名</view>
          <view class="table-cell">学院</view>
          <view class="table-cell">评价数</view>
          <view class="table-cell">平均分</view>
          <view class="table-cell">等级</view>
        </view>
        <view v-for="(teacher, index) in teacherRanking.slice(0, 20)" :key="teacher.id" class="table-row">
          <view class="table-cell">{{ index + 1 }}</view>
          <view class="table-cell">{{ teacher.name }}</view>
          <view class="table-cell">{{ teacher.college }}</view>
          <view class="table-cell">{{ teacher.count }}</view>
          <view class="table-cell">{{ teacher.avgScore.toFixed(1) }}</view>
          <view class="table-cell">
            <text class="level-badge" :class="getLevelClass(teacher.level)">{{ teacher.level }}</text>
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
      this.colleges = simpleStore.state.colleges || [];
      this.allTeachers = simpleStore.state.users.filter(u => u.role === 'teacher') || [];
      this.allEvaluations = simpleStore.state.evaluations || [];
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
</style>