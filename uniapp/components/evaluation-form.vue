<template>
  <view class="evaluation-form">
    <view class="form-section">
      <text class="section-title">教学态度（共20分）</text>
      <score-input
        v-model="scores.teachingAttitude.punctuality"
        label="按时上、下课，无迟到、拖堂等现象（5分）"
        :min="0"
        :max="5"
        :step="0.5"
      />
      <score-input
        v-model="scores.teachingAttitude.management"
        label="严格课堂管理，检查学生出勤情况（5分）"
        :min="0"
        :max="5"
        :step="0.5"
      />
      <score-input
        v-model="scores.teachingAttitude.appearance"
        label="仪态大方、精神饱满、富有感染力（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <view class="section-total">小计：{{ teachingAttitudeTotal }}分</view>
    </view>

    <view class="form-section">
      <text class="section-title">教学内容（共50分）</text>
      <score-input
        v-model="scores.content.objectives"
        label="教学目标明确，符合教学大纲（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <score-input
        v-model="scores.content.familiarity"
        label="熟悉教学内容、节奏流畅、重点难点突出（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <score-input
        v-model="scores.content.innovation"
        label="教学理念/设计/改革具有高阶性、创新性（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <score-input
        v-model="scores.content.ideology"
        label="课程思政融入明显（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <score-input
        v-model="scores.content.practice"
        label="理论联系实际，注重能力素质培养（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <view class="section-total">小计：{{ contentTotal }}分</view>
    </view>

    <view class="form-section">
      <text class="section-title">教学方法与手段（共15分）</text>
      <score-input
        v-model="scores.method.materials"
        label="板书合理、课件规范（5分）"
        :min="0"
        :max="5"
        :step="0.5"
      />
      <score-input
        v-model="scores.method.interaction"
        label="启发式、讨论式教学，注重互动（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <view class="section-total">小计：{{ methodTotal }}分</view>
    </view>

    <view class="form-section">
      <text class="section-title">教学效果（共15分）</text>
      <score-input
        v-model="scores.effect.atmosphere"
        label="课堂气氛活跃、听课率高（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <score-input
        v-model="scores.effect.inspiration"
        label="能启发学生创新、收获大（5分）"
        :min="0"
        :max="5"
        :step="0.5"
      />
      <view class="section-total">小计：{{ effectTotal }}分</view>
    </view>

    <view class="form-section summary">
      <text class="section-title">总分及等级</text>
      <view class="summary-info">
        <view class="total-score">总分：<text class="score-number">{{ totalScore }}</text>分</view>
        <view class="level">等级：<text :class="['level-text', levelClass]">{{ level }}</text></view>
      </view>
    </view>

    <view class="form-section">
      <text class="section-title">意见与建议</text>
      <textarea v-model="suggestion" placeholder="请输入您的意见与建议..." class="suggestion-textarea"></textarea>
    </view>

    <view v-if="showAnonymous" class="form-section">
      <view class="switch">
        <label class="switch-label">
          <switch v-model="anonymous" />
          <text>匿名评价</text>
        </label>
      </view>
    </view>

    <view class="actions">
      <button @click="handleCancel" class="ghost">取消</button>
      <button @click="handleSubmit" class="primary" :disabled="!isValid">提交评价</button>
    </view>
  </view>
</template>

<script>
import ScoreInput from './score-input.vue';

export default {
  components: {
    ScoreInput
  },
  props: {
    showAnonymous: {
      type: Boolean,
      default: true
    },
    initialData: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      scores: {
        teachingAttitude: {
          punctuality: 0,
          management: 0,
          appearance: 0
        },
        content: {
          objectives: 0,
          familiarity: 0,
          innovation: 0,
          ideology: 0,
          practice: 0
        },
        method: {
          materials: 0,
          interaction: 0
        },
        effect: {
          atmosphere: 0,
          inspiration: 0
        }
      },
      suggestion: '',
      anonymous: false
    };
  },
  computed: {
    teachingAttitudeTotal() {
      return (this.scores.teachingAttitude.punctuality || 0) +
             (this.scores.teachingAttitude.management || 0) +
             (this.scores.teachingAttitude.appearance || 0);
    },
    contentTotal() {
      return (this.scores.content.objectives || 0) +
             (this.scores.content.familiarity || 0) +
             (this.scores.content.innovation || 0) +
             (this.scores.content.ideology || 0) +
             (this.scores.content.practice || 0);
    },
    methodTotal() {
      return (this.scores.method.materials || 0) +
             (this.scores.method.interaction || 0);
    },
    effectTotal() {
      return (this.scores.effect.atmosphere || 0) +
             (this.scores.effect.inspiration || 0);
    },
    totalScore() {
      return this.teachingAttitudeTotal + this.contentTotal + this.methodTotal + this.effectTotal;
    },
    level() {
      const score = this.totalScore;
      if (score >= 90) return '优秀';
      if (score >= 80) return '良好';
      if (score >= 70) return '一般';
      if (score >= 60) return '合格';
      return '不合格';
    },
    levelClass() {
      const score = this.totalScore;
      if (score >= 90) return 'level-excellent';
      if (score >= 80) return 'level-good';
      if (score >= 70) return 'level-normal';
      if (score >= 60) return 'level-pass';
      return 'level-fail';
    },
    isValid() {
      return this.totalScore > 0;
    }
  },
  methods: {
    handleSubmit() {
      const evaluationData = {
        scores: {
          teachingAttitude: this.teachingAttitudeTotal,
          content: this.contentTotal,
          method: this.methodTotal,
          effect: this.effectTotal,
          detail: this.scores
        },
        totalScore: this.totalScore,
        level: this.level,
        suggestion: this.suggestion,
        anonymous: this.anonymous
      };
      this.$emit('submit', evaluationData);
    },
    handleCancel() {
      this.$emit('cancel');
    }
  }
};
</script>

<style scoped>
.evaluation-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  background: #eef2ff;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e4e9f1;
}

.section-title {
  display: block;
  margin: 0 0 16px;
  font-size: 18px;
  color: #2d3643;
  font-weight: bold;
}

.section-total {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e9f1;
  text-align: right;
  font-weight: 600;
  color: #4f46e5;
}

.summary {
  background: linear-gradient(135deg, #dbeafe, #eef2ff);
  border-color: #c7d2fe;
}

.summary-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.total-score {
  font-size: 18px;
}

.score-number {
  font-size: 24px;
  color: #4f46e5;
  font-weight: bold;
}

.level {
  font-size: 18px;
}

.level-text {
  font-size: 20px;
  padding: 4px 12px;
  border-radius: 8px;
  font-weight: bold;
}

.level-excellent {
  color: #059669;
  background: #d1fae5;
}

.level-good {
  color: #0891b2;
  background: #cffafe;
}

.level-normal {
  color: #d97706;
  background: #fef3c7;
}

.level-pass {
  color: #dc2626;
  background: #fee2e2;
}

.level-fail {
  color: #991b1b;
  background: #fee2e2;
}

.suggestion-textarea {
  width: 100%;
  min-height: 100px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.switch-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 8px;
}

.primary {
  background: #4f46e5;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-weight: bold;
}

.ghost {
  background: #fff;
  border: 1px solid #d7deea;
  color: #1f2933;
  padding: 12px 24px;
  border-radius: 4px;
  font-weight: bold;
}

.primary:disabled {
  opacity: 0.5;
}

/* 移动端优化 */
@media (max-width: 640px) {
  .form-section {
    padding: 16px;
  }
  
  .section-title {
    font-size: 16px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .actions button {
    width: 100%;
  }
  
  .summary-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>