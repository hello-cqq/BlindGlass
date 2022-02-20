
package tech.bearboy.oppo.client;
/**
 * <p>表示图片的bean类  </p>
 * <p>项目名称: oppo </p> 
 * <p>文件名称: Photo.java </p> 
 * <p>创建时间: 2019年3月4日 </p>
 * @author 常前前
 * @version v1.0
 */
public class Photo {
	/**
	 * 图片url
	 */
	String imgUrl;//图片url
	/**
	 * 图片识别后的描述性信息
	 */
	String msg;//图片识别后的描述性信息
	/**
	 * 时间
	 */
	String time;//时间
	/**
	 * 地点
	 */
	String location;//地点
	/**
	 * 文本检测结果
	 */
	String text;//文本检测结果
	/**
	 * 目标检测结果
	 */
	String target;//目标检测结果

	public void setImgUrl(String url) {
		this.imgUrl = url;
	}

	public String getImgUrl() {
		return this.imgUrl;
	}

	public void setMsg(String msg) {
		this.msg = msg;
	}

	public String getMsg() {
		return this.msg;
	}

	public void setTime(String time) {
		this.time = time;
	}

	public String getTime() {
		return this.time;
	}

	public void setLocation(String location) {
		this.location = location;
	}

	public String getLocation() {
		return this.location;
	}

	public void setText(String text) {
		this.text = text;
	}

	public String getText() {
		return this.text;
	}

	public void setTarget(String target) {
		this.target = target;
	}

	public String getTarget() {
		return this.target;
	}
}
