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
          <text class="help-text">以教师身份进行评价</text>
        </view>
        <view class="field">
          <text class="label">提交状态</text>
          <picker mode="selector" :range="statusOptions" :range-key="'label'" @change="onStatusChange">
            <view class="picker-text">{{ selectedStatusLabel }}</view>
          </picker>
          <text class="help-text">选择课中或课后提交</text>
        </view>
      </view>
    </view>

    <view v-if="selectedCourseId" class="panel">
      <evaluation-form 
        :show-anonymous="showAnonymous" 
        :submit-status="submitStatus"
        @submit="handleSubmit" 
        @cancel="handleCancel" 
      />
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
      evaluatorRole: 'teacher', // 普通老师默认以教师身份进行评价
      selectedRoleLabel: '👨‍🏫 教师',
      courseOptions: [],
      roleOptions: [
        { label: '👨‍🏫 教师', value: 'teacher' }
      ],
      submitStatus: 'after', // 提交状态：'during' 课中, 'after' 课后
      statusOptions: [
        { label: '⏱️ 课中', value: 'during' },
        { label: '✅ 课后', value: 'after' }
      ],
      selectedStatusLabel: '✅ 课后'
    };
  },
  computed: {
    showAnonymous() {
      // 根据学校管理员配置显示匿名选项
      const config = simpleStore.getConfig();
      if (config.anonymousMode === 'global' && config.globalAnonymous) {
        // 全局匿名模式，不显示选项
        return false;
      }
      // 可选匿名模式，显示选项
      return true;
    },
    defaultAnonymous() {
      // 根据配置返回默认匿名状态
      const config = simpleStore.getConfig();
      return config.anonymousMode === 'global' && config.globalAnonymous;
    }
  },
  onLoad(options) {
    // 普通老师和督导老师都可以进行评教，无需权限检查
    // 统一评教逻辑，不再区分普通评教和听课评教
    this.loadCourses();
    
    // 更新标题
    this.$scope && this.$scope.$page && (this.$scope.$page.navigationBarTitleText = '教师端-进行评教');
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
    onStatusChange(e) {
      const selectedIndex = e.detail.value;
      this.submitStatus = this.statusOptions[selectedIndex].value;
      this.selectedStatusLabel = this.statusOptions[selectedIndex].label;
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

      const currentUser = simpleStore.state.currentUser || {};
      
      // 获取课程所属学院信息，确保记录自动留存到各学院每位教师
      const courseInfo = simpleStore.state.courses.find(c => 
        (c.id || c._id) == (course.id || course._id)
      );
      const college = courseInfo ? courseInfo.college : (currentUser.college || '');
      
      const evaluation = {
        courseId: course.id || course._id,
        courseName: course.name,
        teacherId: course.teacherId || course.teacherId,
        teacherName: course.teacherName,
        college: college, // 保存学院信息，确保记录自动留存到各学院
        evaluatorRole: this.evaluatorRole,
        anonymous: this.defaultAnonymous || evaluationData.anonymous, // 根据配置设置匿名状态
        scores: evaluationData.scores,
        suggestions: evaluationData.suggestions || {}, // 保存详细的文字建议（优点、问题、改进方向）
        totalScore: evaluationData.totalScore,
        level: evaluationData.level,
        suggestion: evaluationData.suggestion, // 保留合并后的建议文本（兼容旧格式）
        submitStatus: this.submitStatus, // 保存提交状态（听课中/课后）
        createdAt: new Date().toISOString(),
        id: Date.now() // 简单生成唯一ID
      };

      try {
        // ========== 后端接入点：提交评教数据 ==========
        // TODO: 后期接入后端接口时，可在此处调用API提交评教数据
        // 示例：
        // const response = await uni.request({
        //   url: '/api/evaluations/submit',
        //   method: 'POST',
        //   data: evaluation,
        //   header: {
        //     'Authorization': 'Bearer ' + token
        //   }
        // });
        // if (response.data.success) {
        //   // 提交成功
        // } else {
        //   // 处理错误
        // }
        // ============================================
        
        // 统一评教逻辑：所有评教都保存到evaluations中，不再区分普通评教和听课评教
        // 添加评价者信息
        evaluation.evaluatorId = currentUser.id || currentUser._id;
        evaluation.evaluatorName = currentUser.name || '未知';
        
        const evaluations = simpleStore.state.evaluations || [];
        evaluations.push(evaluation);
        simpleStore.state.evaluations = evaluations;
        
        // 自动保存记录到各学院每位教师（记录已包含学院和教师信息）
        simpleStore.saveAllToStorage();

        uni.showToast({
          title: '评价提交成功！记录已自动保存，提交后不可修改',
          icon: 'success',
          duration: 2000
        });

        setTimeout(() => {
          // 提交成功后返回首页（使用switchTab因为这是tabBar页面）
          uni.switchTab({
            url: '/pages/teacher/index'
          });
        }, 2000);
      } catch (error) {
        uni.showToast({
          title: '评价提交失败',
          icon: 'none'
        });
      }
    },
    handleCancel() {
      // 取消时返回首页（使用switchTab因为这是tabBar页面）
      uni.switchTab({
        url: '/pages/teacher/index'
      });
    },
    navigateBack() {
      // 返回首页（使用switchTab因为这是tabBar页面）
      uni.switchTab({
        url: '/pages/teacher/index'
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