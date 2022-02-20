<template>
	<view class="index">
		<view class="msg_container">
			<input type="text" v-model="msg" @focus="hideTabBarFun()" @blur="showTabBarFun()"/>
			<button @click="sendMsg()">发送</button>
		</view>
		<scroll-view :scroll-y="true" class="chat_container">
			<view class="msg_row" v-for="(m,index) in msgList" :key="index">
				<label>{{m}}</label>
			</view>
		</scroll-view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				msgList:[],
				msg:'',
				show:true
			};
		},
		onLoad() {
			this.getMsg();
		},
		
		methods: {
			getMsg:function(){
				let temp = this.msgList;
				uni.connectSocket({
					// url:'ws://localhost:8080/oppo/websocket/app'
					url: 'ws://www.bearboy.tech/oppo/websocket/app'
				});
				uni.onSocketOpen(function (res) {
				  console.log('WebSocket连接已打开！');
				});
				uni.onSocketError(function (res) {
				  console.log('WebSocket连接打开失败，请检查！');
				});
				uni.onSocketMessage(function (res) {
					var v = JSON.parse(res.data)
					temp.push(v.fromWho+':'+v.msg);
					console.log('收到服务器内容：' + res.data);
				});
			},
			sendMsg:function(){
				var m = JSON.stringify({
					fromWho:'app',
					toWho:'raspberry',
					msg:this.msg
				});
				uni.sendSocketMessage({
				  data: m
				});
			},
			hideTabBarFun:function(){
				uni.hideTabBar({
					
				});
				this.show=false;
			},
			showTabBarFun:function(){
				uni.showTabBar({
					
				});
				this.show=true;
			}
		},
	}
</script>

<style>
	page {
		width: 100%;
		height: 100%;
		display: flex;
		flex-wrap: wrap;
		align-items: flex-start;
		justify-content: center;
		/* background: rgba(249, 249, 249, 1); */
	}
	.index {
		display:flex;
		flex-direction:column-reverse;
		justify-content: space-between;
		width:100%;
		height:100%;
		margin: 0;
		overflow: hidden;
		background-color: #ffcccc;
	}
	.chat_container{
		margin: 20upx;
		width: 710upx;
		flex: 1;
		border-radius: 5upx;
		display: flex;
		flex-direction: column;
	}
	.msg_container{
		width: 710upx;
		display: flex;
		flex-direction: row;
		margin-left: 20upx;
		margin-bottom: 5upx;
		height: 90upx;
		justify-content: space-between;
	}
	.msg_container input{
		width: 570upx;
		height: 76%;
		background-color: #FFFFFF;
		border-style: solid;
		border-color: #FFFFFF;
	}
	.msg_container button{
		width: 125upx;
		height: 90%;
		background-color: #33CCFF;
		margin-right: 0;
		font-size: 16px;
		opacity: 0.8;
	}
	.msg_row{
		padding: 5upx;
		margin-bottom: 20upx;
	}
	label{
		background-color: #00FF99;
		border-radius: 10upx;
		padding: 5upx;
		opacity: 0.7;
	}
</style>
