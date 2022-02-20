<template>
	<view class="index">
		<view class="detail-inf">
			<view class="msg_title">
				<view class="title_child">
					<view>
						<image class="time_icon" src="../../static/icon/time.png"></image>
					</view>
					<view class="word">
						{{inf.time}}
					</view>
				</view>
				<view class="title_child">
					<view>
						<image class="location_icon" src="../../static/icon/location.png"></image>
					</view>
					<view class="word">
						{{inf.location}}
					</view>
				</view>
			</view>
			<view class="msg_img_container">
				<image class="msg_img" :src="inf.imgUrl"></image>
			</view>
			<view class="target">
				<label style="color: #6600FF;">目标</label>
				<label v-for="(p,index) in inf.target" :key="index" v-if="p!=null||p!=''">{{p}}</label>
			</view>
			<view class="text">
				<label style="color: #00FF00;">文本</label>
				<label v-for="(p,index) in inf.text" :key="index" v-if="p!=null||p!=''">{{p}}</label>
			</view>
			<view class="msg">
				<label style="color: #FF0066;">描述</label>
				<label>{{inf.msg}}</label>
				
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				inf:{}
			};
		},
		onLoad(event) {
			this.inf={
				time:event.time,
				location:event.location,
				imgUrl:event.imgUrl,
				target:[],
				text:[],
				msg:event.msg
			};
			this.inf.target = this.strToArray(event.target);
			this.inf.text = this.strToArray(event.text);
		},
		methods:{
			strToArray:function(e){
				return e.split(';');
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
	}
	.detail-inf{
		flex: 1;
		width: 715upx;
		margin: 20upx;
		display: flex;
		flex-direction: column;
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
	.target,.text,.msg{
		display: flex;
		flex-wrap: wrap;
		align-items: flex-start;
	}
	label{
		margin:20upx;
		border-radius: 5upx;
	}
</style>
