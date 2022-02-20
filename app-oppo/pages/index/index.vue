<template>
	<view class="index">
		<view class="pi_camera">
			<video src="http://live.bearboy.tech/pi_app/pi_stream.m3u8?auth_key=1553662055-0-0-fe00918194afd3ca7970155d3a950869"></video>
		</view>
		<scroll-view :scroll-y="true" class="msg_container">
			<view class="msg_list" v-for="(p,index) in msgList" :key="index" @click="goDetail(p)">
				<view class="msg_title">
					<view class="title_child">
						<view>
							<image class="time_icon" src="../../static/icon/time.png"></image>
						</view>
						<view class="word">
							{{p.time}}
						</view>
					</view>
					<view class="title_child">
						<view>
							<image class="location_icon" src="../../static/icon/location.png"></image>
						</view>
						<view class="word">
							{{p.location}}
						</view>
					</view>
				</view>
				<view class="msg_img_container">
					<image class="msg_img" :src="p.imgUrl"></image>
				</view>
				<view class="btn_detail">
					详细
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script>
	
	export default {
		data() {
			return {
				msgList:[
					{
						imgUrl:'https://bearboy.tech/oppo/photos/20190131140225.jpg',
						time:'13:20:21',
						location:'地球',
						text:'黑龙江饺子馆',
						target:'饭店;人;',
						msg:'暂无'	
					}
				]			
			}
		},
		onLoad:function(){
			this.getList();
			this.getData();
		},
		
		// components: {uniCard},
		methods: {
			getList:function(){
				let tempList = this.msgList;
				let temp = new Date();
				uni.request({
					url: 'http://www.bearboy.tech/oppo/GetMsgServlet',
					method: 'POST',
					data: {
						today:'2019-4-16'//temp.getFullYear()+'-'+(temp.getMonth()+1)+'-'+temp.getDate()
					},
					header:{
						'content-type':'application/x-www-form-urlencoded'
					},
					success: res => {
						if (res.statusCode == 200) {
							res.data.forEach((d) => {
								tempList.unshift(d);
							})
							console.log(tempList);
							
						}
					},
				});
			},
			goDetail:function(detail) {
				uni.navigateTo({
					url: '/pages/msg/msg?time=' + detail.time+'&location='+detail.location+'&imgUrl='+detail.imgUrl+'&target='+detail.target+'&text='+detail.text+'&msg='+detail.msg
				});
			},
			getData:function(){
				let tempList = this.msgList;
				if(typeof(EventSource)!=="undefined"){
					console.log('yes');
					var es = new EventSource("http://www.bearboy.tech/oppo/SSEServlet");
					es.onmessage = function(event){
						console.log(JSON.parse(event.data));
						tempList.unshift(JSON.parse(event.data));
					}
				}
			}
		}
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
		flex-direction:column;
		width:100%;
		height:100%;
		margin: 0;
		overflow: hidden;
	}
	.pi_camera{
		margin: 20upx;
		width: 710upx;
		height: 200px;
	}
	.pi_camera video{
		width: 100%;
		height: 100%;
	}
	.msg_container{
		flex: 1;
		display: flex;
		flex-direction: column;
		margin-left: 20upx;
		width: 710upx;
		/* border-left-color: #FF80AB;
		border-left-style: solid; */
	}
	.msg_list{
		width: 100%;
		margin-top: 5px;
		display: flex;
		flex-direction: column;
		height: 300px;
		border-radius: 6px;
		box-shadow: 0 3px 3px 0 rgba(0,0,0,0.2);
		transition: 0.3s;
		background-color: #ffffcc;
	}
	.msg_title{
		width: 100%;
		height: 30px;
		display: flex;
		flex-direction: row;
		justify-content: space-between;
		font-size: 14px;
		text-align: center;
		line-height: 20px;
		padding-top: 3px;
	}
	.title_child{
		height: 100%;
		width: 50%;
		display: flex;
		text-align: center;
	}
	.title_child:last-child{
		justify-content: flex-end;
	}
	.word{
		line-height: 25px;
		color: #555555;
	}
	.time_icon{
		width: 20px;
		height: 20px;
	}
	.location_icon{
		width: 25px;
		height: 25px;
	}
	.msg_img_container{
		text-align: center;
		width: 100%;
		height: 240px;
	}
	.msg_img{
		text-align: center;
		width: 100%;
		height: 100%;
	}
	.btn_detail{
		width: 100%;
		height: 30px;
		text-align: right;
		font-size: 14px;
		color: #007AFF;
		letter-spacing: 5px;
		line-height: 20px;
		padding-top: 5px;
	}
</style>
