<template>
	<view class="evaluation-submit-container">
		<!-- 课程信息 -->
		<view class="course-info">
			<view class="info-item">
				<text class="info-label">课程名称</text>
				<text class="info-value">{{ courseInfo.course_name || '加载中...' }}</text>
			</view>
			<view class="info-item">
				<text class="info-label">授课教师</text>
				<text class="info-value">{{ courseInfo.teacher_name || '加载中...' }}</text>
			</view>
			<view class="info-item">
				<text class="info-label">上课地点</text>
				<text class="info-value">{{ courseInfo.classroom || '加载中...' }}</text>
			</view>
			<view class="info-item">
				<text class="info-label">上课时间</text>
				<text class="info-value">{{ courseInfo.teaching_time || '加载中...' }}</text>
			</view>
		</view>

		<!-- 评分维度 -->
		<view class="evaluation-section">
			<text class="section-title">评分维度（总分：{{ calculateTotalScore() }}分）</text>

			<!-- 1. 教学态度 -->
			<view class="dimension-group">
				<view class="dimension-group-header">
					<text class="dimension-group-name">教学态度（{{ calculateDimensionScore('teachingAttitude') }}/20分）</text>
				</view>

				<view class="sub-dimension-item" v-for="(item, index) in dimensionConfig.teachingAttitude.items" :key="index">
					<view class="sub-dimension-header">
						<text class="sub-dimension-name">{{ item.name }}</text>
						<text class="sub-dimension-score">{{ scores.teachingAttitude[item.key] }}/{{ item.max }}分</text>
					</view>

					<!--  修复：slider 不用 v-model，用 value + change/changing -->
					<slider
						:value="scores.teachingAttitude[item.key]"
						:min="0"
						:max="item.max"
						:step="1"
						activeColor="#3E5C76"
						backgroundColor="#E4E7ED"
						block-size="24"
						@changing="onScoreChanging('teachingAttitude', item.key, $event)"
						@change="onScoreChanging('teachingAttitude', item.key, $event)"
					/>
				</view>
			</view>

			<!-- 2. 教学内容 -->
			<view class="dimension-group">
				<view class="dimension-group-header">
					<text class="dimension-group-name">教学内容（{{ calculateDimensionScore('content') }}/50分）</text>
				</view>

				<view class="sub-dimension-item" v-for="(item, index) in dimensionConfig.content.items" :key="index">
					<view class="sub-dimension-header">
						<text class="sub-dimension-name">{{ item.name }}</text>
						<text class="sub-dimension-score">{{ scores.content[item.key] }}/{{ item.max }}分</text>
					</view>

					<slider
						:value="scores.content[item.key]"
						:min="0"
						:max="item.max"
						:step="1"
						activeColor="#3E5C76"
						backgroundColor="#E4E7ED"
						block-size="24"
						@changing="onScoreChanging('content', item.key, $event)"
						@change="onScoreChanging('content', item.key, $event)"
					/>
				</view>
			</view>

			<!-- 3. 教学方法与手段 -->
			<view class="dimension-group">
				<view class="dimension-group-header">
					<text class="dimension-group-name">教学方法与手段（{{ calculateDimensionScore('method') }}/15分）</text>
				</view>

				<view class="sub-dimension-item" v-for="(item, index) in dimensionConfig.method.items" :key="index">
					<view class="sub-dimension-header">
						<text class="sub-dimension-name">{{ item.name }}</text>
						<text class="sub-dimension-score">{{ scores.method[item.key] }}/{{ item.max }}分</text>
					</view>

					<slider
						:value="scores.method[item.key]"
						:min="0"
						:max="item.max"
						:step="1"
						activeColor="#3E5C76"
						backgroundColor="#E4E7ED"
						block-size="24"
						@changing="onScoreChanging('method', item.key, $event)"
						@change="onScoreChanging('method', item.key, $event)"
					/>
				</view>
			</view>

			<!-- 4. 教学效果 -->
			<view class="dimension-group">
				<view class="dimension-group-header">
					<text class="dimension-group-name">教学效果（{{ calculateDimensionScore('effect') }}/15分）</text>
				</view>

				<view class="sub-dimension-item" v-for="(item, index) in dimensionConfig.effect.items" :key="index">
					<view class="sub-dimension-header">
						<text class="sub-dimension-name">{{ item.name }}</text>
						<text class="sub-dimension-score">{{ scores.effect[item.key] }}/{{ item.max }}分</text>
					</view>

					<slider
						:value="scores.effect[item.key]"
						:min="0"
						:max="item.max"
						:step="1"
						activeColor="#3E5C76"
						backgroundColor="#E4E7ED"
						block-size="24"
						@changing="onScoreChanging('effect', item.key, $event)"
						@change="onScoreChanging('effect', item.key, $event)"
					/>
				</view>
			</view>
		</view>

		<!-- 听课信息 -->
		<view class="evaluation-section">
			<text class="section-title">听课信息</text>

			<view class="form-item">
				<text class="form-label">听课日期</text>
				<input :value="form.listen_date" type="date" class="input" placeholder-class="placeholder" @input="handleListenDateInput" />
			</view>

			<view class="form-row">
				<view class="form-item half">
					<text class="form-label">听课时长（分钟）</text>
					<input
						:value="form.listen_duration"
						type="number"
						class="input"
						placeholder="45"
						placeholder-class="placeholder"
						@input="handleDurationChange"
					/>
				</view>

				<view class="form-item half">
					<text class="form-label">是否匿名</text>
					<view class="switch-container">
						<switch :checked="form.is_anonymous" color="#3E5C76" @change="handleAnonymousChange" />
						<text class="switch-label">{{ form.is_anonymous ? '是' : '否' }}</text>
					</view>
				</view>
			</view>

			<view class="form-item">
				<text class="form-label">听课地点</text>
				<input
					:value="form.listen_location"
					type="text"
					class="input"
					placeholder="教学楼A101"
					placeholder-class="placeholder"
					@input="handleLocationChange"
				/>
			</view>
		</view>

		<!-- 总体评价 -->
		<view class="evaluation-section">
			<text class="section-title">总体评价</text>

			<view class="textarea-item">
				<text class="textarea-label">优点</text>
				<textarea
					:value="form.advantage_content"
					placeholder="请输入课程优点"
					class="textarea"
					placeholder-class="placeholder"
					:maxlength="200"
					auto-height
					@input="handleAdvantageContentInput"
				/>
				<text class="char-count">{{ form.advantage_content.length }}/200</text>
			</view>

			<view class="textarea-item">
				<text class="textarea-label">问题</text>
				<textarea
					:value="form.problem_content"
					placeholder="请输入课程存在的问题"
					class="textarea"
					placeholder-class="placeholder"
					:maxlength="200"
					auto-height
					@input="handleProblemContentInput"
				/>
				<text class="char-count">{{ form.problem_content.length }}/200</text>
			</view>

			<view class="textarea-item">
				<text class="textarea-label">改进建议</text>
				<textarea
					:value="form.improve_suggestion"
					placeholder="请输入改进建议"
					class="textarea"
					placeholder-class="placeholder"
					:maxlength="200"
					auto-height
					@input="handleImproveSuggestionInput"
				/>
				<text class="char-count">{{ form.improve_suggestion.length }}/200</text>
			</view>
		</view>

		<!-- 提交按钮 -->
		<button @tap="submitEvaluation" class="submit-btn" :loading="loading" :disabled="loading">
			提交评教
		</button>
	</view>
</template>

<script>
import { request } from '../../common/request.js';

export default {
	name: 'evaluation-submit',
	data() {
		return {
			courseInfo: {},
			dimensionConfig: {
				teachingAttitude: {
					name: '教学态度',
					max: 20,
					items: [
						{ key: 'onTime', name: '按时上、下课，无迟到、拖堂等现象', max: 5 },
						{ key: 'classManagement', name: '严格课堂管理，检查学生出勤情况', max: 5 },
						{ key: 'teachingEthics', name: '仪态大方、精神饱满、富有感染力', max: 10 }
					]
				},
				content: {
					name: '教学内容',
					max: 50,
					items: [
						{ key: 'clearObjectives', name: '教学目标明确，符合教学大纲', max: 10 },
						{ key: 'familiarContent', name: '熟悉教学内容，节奏流畅，重点难点突出', max: 10 },
						{ key: 'innovativeDesign', name: '教学理念/设计/改革具有高阶性、创新性、挑战度', max: 10 },
						{ key: 'ideologicalContent', name: '课程思政融入明显', max: 10 },
						{ key: 'practicalApplication', name: '理论联系实际，注重能力培养', max: 10 }
					]
				},
				method: {
					name: '教学方法与手段',
					max: 15,
					items: [
						{ key: 'boardAndPPT', name: '板书合理、课件规范', max: 5 },
						{ key: 'interactiveTeaching', name: '启发式/讨论式教学，注重互动', max: 10 }
					]
				},
				effect: {
					name: '教学效果',
					max: 15,
					items: [
						{ key: 'activeClassroom', name: '课堂气氛活跃，听课率高', max: 10 },
						{ key: 'innovativeInspiration', name: '能启发学生创新，收获大', max: 5 }
					]
				}
			},

			//初始分数
			scores: {
				teachingAttitude: { onTime: 3, classManagement: 3, teachingEthics: 6 },
				content: { clearObjectives: 6, familiarContent: 6, innovativeDesign: 6, ideologicalContent: 6, practicalApplication: 6 },
				method: { boardAndPPT: 3, interactiveTeaching: 6 },
				effect: { activeClassroom: 6, innovativeInspiration: 3 }
			},

			form: {
				advantage_content: '',
				problem_content: '',
				improve_suggestion: '',
				listen_date: new Date().toISOString().split('T')[0],
				listen_duration: 45,
				listen_location: '',
				is_anonymous: false
			},

			loading: false,
			timetableId: ''
		};
	},

	onLoad(options) {
		this.timetableId = options.timetable_id || '';
		if (this.timetableId) {
			this.getCourseInfo();
		} else {
			uni.showToast({ title: '缺少课程信息', icon: 'none', duration: 2000 });
			setTimeout(() => uni.navigateBack(), 1500);
		}
	},

	methods: {
		//  修复：slider 更新分数（changing/change 都走这里）
		onScoreChanging(dimensionKey, itemKey, e) {
			const v = Number(e?.detail?.value ?? 0);
			this.scores[dimensionKey][itemKey] = v;
		},

		async getCourseInfo() {
			try {
				const res = await request({
					url: `/org/org/timetable/${this.timetableId}`,
					method: 'GET'
				});

				if (res) {
					this.courseInfo = {
						course_name: res.course_name,
						teacher_name: res.teacher_name || '未知教师',
						classroom: res.classroom,
						teaching_time: `${res.weekday_text} ${res.period}`
					};
				} else {
					this.courseInfo = {
						course_name: '未知课程',
						teacher_name: '未知教师',
						classroom: '未知地点',
						teaching_time: '未知时间'
					};
				}
			} catch (error) {
				console.error('获取课程信息失败:', error);
				uni.showToast({ title: '获取课程信息失败', icon: 'none', duration: 2000 });
				this.courseInfo = {
					course_name: '未知课程',
					teacher_name: '未知教师',
					classroom: '未知地点',
					teaching_time: '未知时间'
				};
			}
		},

		calculateDimensionScore(dimensionKey) {
			const dimension = this.scores[dimensionKey];
			if (!dimension) return 0;
			return Object.values(dimension).reduce((sum, score) => sum + Number(score || 0), 0);
		},

		calculateTotalScore() {
			return (
				this.calculateDimensionScore('teachingAttitude') +
				this.calculateDimensionScore('content') +
				this.calculateDimensionScore('method') +
				this.calculateDimensionScore('effect')
			);
		},

		// 兼容 web 和微信小程序的输入处理
		handleListenDateInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.form.listen_date = value;
		},
		handleDurationChange(e) {
			// 兼容 web 和微信小程序
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			const numValue = parseInt(value);
			if (numValue > 480) {
				this.form.listen_duration = 480;
				uni.showToast({ title: '听课时长不能超过480分钟', icon: 'none', duration: 1500 });
			} else {
				this.form.listen_duration = numValue || 0;
			}
		},
		handleAnonymousChange(e) {
			// 兼容 web 和微信小程序
			const checked = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.checked : false);
			this.form.is_anonymous = checked;
		},
		handleLocationChange(e) {
			// 兼容 web 和微信小程序
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			if (value.length > 64) {
				this.form.listen_location = value.substring(0, 64);
				uni.showToast({ title: '听课地点不能超过64个字符', icon: 'none', duration: 1500 });
			} else {
				this.form.listen_location = value;
			}
		},
		handleAdvantageContentInput(e) {
			// 兼容 web 和微信小程序
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.form.advantage_content = value;
		},
		handleProblemContentInput(e) {
			// 兼容 web 和微信小程序
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.form.problem_content = value;
		},
		handleImproveSuggestionInput(e) {
			// 兼容 web 和微信小程序
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.form.improve_suggestion = value;
		},

		onAnonymousChange(e) {
			this.form.is_anonymous = e.detail.value;
		},

		async submitEvaluation() {
			if (!this.form.advantage_content || !this.form.problem_content || !this.form.improve_suggestion) {
				uni.showToast({ title: '请填写完整的评价内容', icon: 'none', duration: 2000 });
				return;
			}

			if (!this.form.listen_duration || this.form.listen_duration <= 0 || this.form.listen_duration > 480) {
				uni.showToast({ title: '请输入有效的听课时长（1-480分钟）', icon: 'none', duration: 2000 });
				return;
			}

			if (!this.form.listen_location) {
				uni.showToast({ title: '请输入听课地点', icon: 'none', duration: 2000 });
				return;
			}

			this.loading = true;

			try {
				const total_score = this.calculateTotalScore();

				const dimension_scores = {
					teachingAttitude: this.calculateDimensionScore('teachingAttitude'),
					content: this.calculateDimensionScore('content'),
					method: this.calculateDimensionScore('method'),
					effect: this.calculateDimensionScore('effect')
				};

				const submitData = {
					timetable_id: parseInt(this.timetableId),
					total_score,
					dimension_scores,
					advantage_content: this.form.advantage_content,
					problem_content: this.form.problem_content,
					improve_suggestion: this.form.improve_suggestion,
					listen_date: new Date(this.form.listen_date).toISOString(),
					listen_duration: this.form.listen_duration,
					listen_location: this.form.listen_location,
					is_anonymous: this.form.is_anonymous
				};

				console.log('提交数据:', submitData);

				//  修复：接口改成 submit
				await request({
					url: '/eval/submit',
					method: 'POST',
					data: submitData
				});

				uni.showToast({ title: '评教提交成功', icon: 'success', duration: 1500 });

				setTimeout(() => {
					uni.switchTab({ url: '/pages/evaluation/my-evaluations' });
				}, 1500);
			} catch (error) {
				console.error('提交评教失败:', error);
				uni.showToast({
					title: error?.msg || '提交评教失败，请重试',
					icon: 'none',
					duration: 2000
				});
			} finally {
				this.loading = false;
			}
		}
	}
};
</script>

<style scoped>
.evaluation-submit-container {
	background-color: #F5F7FA;
	min-height: 100vh;
	padding: 30rpx;
}

/* 课程信息 */
.course-info {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.info-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.info-item:last-child {
	margin-bottom: 0;
}

.info-label {
	font-size: 28rpx;
	color: #666666;
	font-weight: 500;
}

.info-value {
	font-size: 28rpx;
	color: #333333;
	text-align: right;
	flex: 1;
	margin-left: 20rpx;
}

/* 评价部分 */
.evaluation-section {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 30rpx;
	display: block;
}

/* 评分维度组 */
.dimension-group {
	margin-bottom: 40rpx;
	padding: 20rpx;
	background-color: #F9FAFB;
	border-radius: 8rpx;
}

.dimension-group:last-child {
	margin-bottom: 0;
}

.dimension-group-header {
	margin-bottom: 20rpx;
	padding-bottom: 10rpx;
	border-bottom: 2rpx solid #E4E7ED;
}

.dimension-group-name {
	font-size: 28rpx;
	font-weight: 600;
	color: #333333;
}

/* 子维度项 */
.sub-dimension-item {
	margin-bottom: 30rpx;
}

.sub-dimension-item:last-child {
	margin-bottom: 0;
}

.sub-dimension-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 15rpx;
}

.sub-dimension-name {
	font-size: 26rpx;
	color: #333333;
	flex: 1;
}

.sub-dimension-score {
	font-size: 24rpx;
	color: #3E5C76;
	font-weight: 500;
}

/* 评分滑块 */
slider {
	margin-bottom: 5rpx;
}

/* 表单样式 */
.form-item {
	margin-bottom: 30rpx;
}

.form-item.half {
	flex: 1;
	margin-right: 20rpx;
}

.form-item.half:last-child {
	margin-right: 0;
}

.form-row {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
}

.form-label {
	display: block;
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
	margin-bottom: 15rpx;
}

.input {
	width: 100%;
	height: 80rpx;
	border: 2rpx solid #E4E7ED;
	border-radius: 8rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
	color: #333333;
	background-color: #FFFFFF;
}

.input:focus {
	border-color: #3E5C76;
}

/* 开关样式 */
.switch-container {
	display: flex;
	flex-direction: row;
	align-items: center;
}

.switch-label {
	margin-left: 20rpx;
	font-size: 28rpx;
	color: #333333;
}

/* 文本域 */
.textarea-item {
	margin-bottom: 30rpx;
}

.textarea-item:last-child {
	margin-bottom: 0;
}

.textarea-label {
	display: block;
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
	margin-bottom: 15rpx;
}

.textarea {
	width: 100%;
	min-height: 120rpx;
	border: 2rpx solid #E4E7ED;
	border-radius: 8rpx;
	padding: 20rpx;
	font-size: 26rpx;
	color: #333333;
	background-color: #F5F7FA;
	line-height: 1.5;
}

.textarea:focus {
	border-color: #3E5C76;
	background-color: #FFFFFF;
}

.placeholder {
	color: #C0C4CC;
}

.char-count {
	display: block;
	text-align: right;
	font-size: 22rpx;
	color: #999999;
	margin-top: 10rpx;
}

/* 提交按钮 */
.submit-btn {
	width: 100%;
	height: 88rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
	font-size: 32rpx;
	font-weight: bold;
	border-radius: 44rpx;
	margin-top: 40rpx;
}

.submit-btn::after {
	border: none;
}

.submit-btn:active {
	background-color: #2D455A;
}
</style>
