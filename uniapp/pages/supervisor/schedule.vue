<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">督导端</text>
        <text class="title">教师课表</text>
        <text class="desc">查看负责范围内教师的课程安排</text>
      </view>
      <view class="header-badges">
        <button @click="navigateBack" class="badge">返回</button>
      </view>
    </view>

    <!-- 筛选条件 -->
    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">筛选条件</text>
      </view>
      <view class="filters">
        <view class="filter-item">
          <text class="filter-label">选择教师</text>
          <picker mode="selector" :range="teacherOptions" :range-key="'name'" @change="onTeacherChange">
            <view class="picker-text">{{ selectedTeacherName || '全部教师' }}</view>
          </picker>
        </view>
        <view class="filter-item">
          <text class="filter-label">选择学期</text>
          <picker mode="selector" :range="semesterOptions" @change="onSemesterChange">
            <view class="picker-text">{{ selectedSemester || '全部学期' }}</view>
          </picker>
        </view>
      </view>
    </view>

    <!-- 课表列表 -->
    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">课程列表</text>
        <text class="panel-desc">共 {{ filteredCourses.length }} 门课程</text>
      </view>
      <view v-if="filteredCourses.length === 0" class="empty">暂无课程数据</view>
      <view v-else class="course-list">
        <view v-for="course in filteredCourses" :key="course.id" class="course-card">
          <view class="course-header">
            <view class="course-info">
              <text class="course-name">{{ course.name }}</text>
              <text class="course-meta">{{ course.semester }} · {{ course.college }}</text>
            </view>
            <view class="course-actions">
              <button @click="startEvaluation(course)" class="action-btn primary">进行评教</button>
            </view>
          </view>
          <view class="course-details">
            <view class="detail-item">
              <text class="detail-label">授课教师：</text>
              <text class="detail-value">{{ course.teacherName }}</text>
            </view>
            <view class="detail-item">
              <text class="detail-label">课程ID：</text>
              <text class="detail-value">{{ course.id }}</text>
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
      allCourses: [],
      allTeachers: [],
      selectedTeacherId: '',
      selectedTeacherName: '',
      selectedSemester: '',
      semesterOptions: ['全部学期', '2025春', '2025秋', '2024春', '2024秋']
    };
  },
  onLoad() {
    this.loadUserData();
    this.loadData();
  },
  computed: {
    teacherOptions() {
      return [{ id: '', name: '全部教师' }, ...this.allTeachers];
    },
    filteredCourses() {
      let result = [...this.allCourses];
      
      if (this.selectedTeacherId) {
        result = result.filter(c => c.teacherId == this.selectedTeacherId);
      }
      
      if (this.selectedSemester && this.selectedSemester !== '全部学期') {
        result = result.filter(c => c.semester === this.selectedSemester);
      }
      
      return result;
    }
  },
  methods: {
    loadUserData() {
      this.currentUser = simpleStore.state.currentUser || {};
    },
    loadData() {
      // 直接从本地存储加载数据，不进行服务器连接检测
      // TODO: 后期接入后端接口时，可在此处调用API获取数据
      // 示例：
      // try {
      //   const userId = this.currentUser.id || this.currentUser._id;
      //   const response = await uni.request({ 
      //     url: `/api/supervisor/courses?supervisorId=${userId}`,
      //     timeout: 10000
      //   });
      //   this.allCourses = response.data;
      // } catch (error) {
      //   console.error('获取课程列表失败:', error);
      //   // 失败时使用本地数据作为降级方案
      //   this.allCourses = simpleStore.getSupervisorCourses(userId);
      // }
      
      try {
        const userId = this.currentUser.id || this.currentUser._id;
        
        // 使用本地存储数据，不进行网络请求
        this.allCourses = simpleStore.getSupervisorCourses(userId);
        this.allTeachers = simpleStore.getSupervisorTeachers(userId);
      } catch (error) {
        console.error('加载数据失败:', error);
        // 静默处理错误，不显示提示
      }
    },
    onTeacherChange(e) {
      const selectedIndex = e.detail.value;
      const selectedTeacher = this.teacherOptions[selectedIndex];
      this.selectedTeacherId = selectedTeacher.id || '';
      this.selectedTeacherName = selectedTeacher.name || '全部教师';
    },
    onSemesterChange(e) {
      const selectedIndex = e.detail.value;
      this.selectedSemester = this.semesterOptions[selectedIndex];
    },
    startEvaluation(course) {
      // 跳转到评教页面，传递课程信息
      uni.navigateTo({
        url: `/pages/supervisor/evaluate?courseId=${course.id}&courseName=${encodeURIComponent(course.name)}&teacherId=${course.teacherId}&teacherName=${encodeURIComponent(course.teacherName)}`
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

.filters {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-weight: 500;
  font-size: 14px;
  color: #333;
}

.picker-text {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 12px;
  font-size: 14px;
  background: white;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}

.course-card {
  background: #f8f9fa;
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  padding: 16px;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.course-info {
  flex: 1;
}

.course-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2933;
  display: block;
  margin-bottom: 4px;
}

.course-meta {
  font-size: 14px;
  color: #666;
  display: block;
}

.course-actions {
  margin-left: 16px;
}

.action-btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  border: none;
  white-space: nowrap;
}

.action-btn.primary {
  background: #4f46e5;
  color: #fff;
}

.course-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #e4e9f1;
}

.detail-item {
  display: flex;
  gap: 8px;
  font-size: 14px;
}

.detail-label {
  color: #666;
  font-weight: 500;
}

.detail-value {
  color: #1f2933;
}

.empty {
  text-align: center;
  padding: 40px 0;
  color: #999;
}
</style>

