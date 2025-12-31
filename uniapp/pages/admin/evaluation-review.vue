<template>
	<view class="admin-container">
		<view class="admin-header">
			<text class="header-title">评教审核</text>
		</view>
		
		<view class="admin-content">
			<view class="empty-state">
				<text class="empty-text">评教审核功能开发中...</text>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	name: 'evaluation-review',
	data() {
		return {
			// 页面数据
		};
	},
	onLoad() {
		// 页面加载时执行
	}
};
</script>

<style scoped>
.admin-container {
	background-color: #F5F7FA;
	min-height: 100vh;
}

.admin-header {
	background-color: #3E5C76;
	color: #FFFFFF;
	padding: 30rpx;
	border-bottom: 2rpx solid #E4E7ED;
}

.header-title {
	font-size: 32rpx;
	font-weight: bold;
}

.admin-content {
	padding: 30rpx;
}

.empty-state {
	display: flex;
	justify-content: center;
	align-items: center;
	height: 400rpx;
}

.empty-text {
	font-size: 28rpx;
	color: #999999;
}
</style>