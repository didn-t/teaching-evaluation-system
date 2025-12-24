<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">教师端</text>
        <text class="title">进行评教</text>
        <text class="desc">对课程进行教学质量评价</text>
      </view>
      <view class="header-badges">
        <button @click="navigateBack" class="badge">返回</button>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">选择课程</text>
      </view>
      <view class="form-grid">
        <view class="field">
          <text class="label">选择课程</text>
          <picker mode="selector" :range="courseOptions" :range-key="'name'" @change="onCourseChange">
            <view class="picker-text">{{ selectedCourseName || '请选择课程' }}</view>
          </picker>
        </view>
        <view class="field">
          <text class="label">评价人角色</text>
          <picker mode="selector" :range="roleOptions" @change="onRoleChange">
            <view class="picker-text">{{ selectedRoleLabel }}</view>
          </picker>
          <text class="help-text">可选择以学生或教师身份进行评价</text>
        </view>
      </view>
    </view>

    <view v-if="selectedCourseId" class="panel">
      <evaluation-form :show-anonymous="showAnonymous" @submit="handleSubmit" @cancel="handleCancel" />
    </view>
  </view>
</template>

<script>
import EvaluationForm from '../../components/evaluation-form.vue';
import { simpleStore } from '../../utils/simpleStore';

export default {
  components: {
    EvaluationForm
  },
  data() {
    return {
      selectedCourseId: '',
      selectedCourseName: '',
      evaluatorRole: 'student',
      selectedRoleLabel: '👨‍🎓 学生',
      courseOptions: [],
      roleOptions: [
        { label: '👨‍🎓 学生', value: 'student' },
        { label: '👨‍🏫 教师', value: 'teacher' }
      ],
      evaluationType: 'evaluation' // 默认是普通评教，也可以是听课评价(listen)
    };
  },
  computed: {
    showAnonymous() {
      // 简化处理，始终显示匿名选项
      return true;
    }
  },
  onLoad(options) {
    // 检查是否是听课评价
    if (options && options.type === 'listen') {
      this.evaluationType = 'listen';
    }
    this.loadCourses();
    
    // 更新标题
    this.$scope && this.$scope.$page && (this.$scope.$page.navigationBarTitleText = 
      this.evaluationType === 'listen' ? '教师端-听课评价' : '教师端-进行评教');
  },
  methods: {
    loadCourses() {
      try {
        const courses = simpleStore.getCourses();
        this.courseOptions = courses.map(course => ({
          ...course,
          name: `${course.name} - ${course.teacherName} (${course.semester})`
        }));
      } catch (error) {
        console.error('加载课程失败:', error);
      }
    },
    onCourseChange(e) {
      const selectedIndex = e.detail.value;
      const selectedCourse = this.courseOptions[selectedIndex];
      this.selectedCourseId = selectedCourse.id || selectedCourse._id;
      this.selectedCourseName = selectedCourse.name;
    },
    onRoleChange(e) {
      const selectedIndex = e.detail.value;
      this.evaluatorRole = this.roleOptions[selectedIndex].value;
      this.selectedRoleLabel = this.roleOptions[selectedIndex].label;
    },
    handleSubmit(evaluationData) {
      if (!this.selectedCourseId) {
        uni.showToast({
          title: '请选择课程',
          icon: 'none'
        });
        return;
      }

      const course = this.courseOptions.find(c => (c.id || c._id) == this.selectedCourseId);
      if (!course) {
        uni.showToast({
          title: '课程信息错误',
          icon: 'none'
        });
        return;
      }

      const evaluation = {
        courseId: course.id || course._id,
        courseName: course.name,
        teacherId: course.teacherId || course.teacherId,
        teacherName: course.teacherName,
        evaluatorRole: this.evaluatorRole,
        anonymous: evaluationData.anonymous,
        scores: evaluationData.scores,
        totalScore: evaluationData.totalScore,
        level: evaluationData.level,
        suggestion: evaluationData.suggestion,
        createdAt: new Date().toISOString(),
        id: Date.now() // 简单生成唯一ID
      };

      try {
        if (this.evaluationType === 'listen') {
          // 听课评价存储到听课记录中
          const listenRecords = simpleStore.state.listenRecords || [];
          listenRecords.push(evaluation);
          simpleStore.state.listenRecords = listenRecords;
        } else {
          // 普通评价存储到评价记录中
          const evaluations = simpleStore.state.evaluations || [];
          evaluations.push(evaluation);
          simpleStore.state.evaluations = evaluations;
        }
        
        simpleStore.saveAllToStorage();

        uni.showToast({
          title: '评价提交成功！',
          icon: 'success'
        });

        setTimeout(() => {
          uni.navigateBack();
        }, 1500);
      } catch (error) {
        uni.showToast({
          title: '评价提交失败',
          icon: 'none'
        });
      }
    },
    handleCancel() {
      uni.navigateBack();
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
  margin-bottom: 16px;
}

.panel-title-text {
  font-size: 20px;
  font-weight: bold;
  display: block;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label {
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

.help-text {
  margin: 4px 0 0;
  font-size: 12px;
  color: #1f2933;
}
</style>