
package tech.bearboy.oppo.common;

import java.util.List;

import net.sf.json.JSONArray;
import net.sf.json.JSONObject;
import tech.bearboy.oppo.client.Photo;
/**
 * <p>通用方法类 </p>
 * <p>项目名称: oppo </p> 
 * <p>文件名称: Common.java </p> 
 * <p>创建时间: 2019年3月4日 </p>
 * @author 常前前
 * @version v1.0
 */
public class Common {

	/**
	 * list对象转json字符串
	 * @param list 代表Photo对象的集合
	 * @return 返回所有Photo对象的json字符串
	 */
	public String listToJSON(List<Photo> list) {
		JSONArray jsonArray = JSONArray.fromObject(list);
		return jsonArray.toString();
	}
	
	/**
	 * json字符串转对象
	 * @param jsonStr 代表json字符串
	 * @return 返回对象
	 */
	public JSONObject jsonToObject(String jsonStr){
		JSONObject jsonObject = JSONObject.fromObject(jsonStr);
		return jsonObject;
	}
	/**
	 * bean对象转json字符串
	 * @param p 代表一张图片
	 * @return 返回json字符串
	 */
	public String beanToJSON(Photo p) {
		JSONObject jsonObject = JSONObject.fromObject(p);
		return jsonObject.toString();
	}

}
