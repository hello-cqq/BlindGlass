package tech.bearboy.oppo.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

import javax.sql.DataSource;

import tech.bearboy.oppo.client.Photo;
import tech.bearboy.oppo.common.Common;
/**
 * <p>spring--数据访问对象类，执行数据库操作 </p>
 * <p>项目名称: oppo </p> 
 * <p>文件名称: PhotoDAO.java </p> 
 * <p>创建时间: 2019年3月4日 </p>
 * @author 常前前
 * @version v1.0
 */
public class PhotoDAO {
	/**
	 * 代表数据源对象，在applicationContext.xml内定义该bean
	 */
	private DataSource dataSource;

	public void setDataSource(DataSource dataSource) {
		this.dataSource = dataSource;
	}
	/**
	 * 查询时间为今天的所有图片
	 * @param date 今天的日期
	 * @return 返回所有查询结果的json字符串
	 */
	public String todayMsgJson(String date) {
		String s = "https://bearboy.tech/oppo/photos/";
		String jsonData = "";
		List<Photo> photos = new ArrayList<Photo>();
		String sql = "select * from photo where date=?";
		Connection conn = null;
		try {
			conn = dataSource.getConnection();
			PreparedStatement ps = conn.prepareStatement(sql);
			ps.setString(1, date);
			ResultSet rs = ps.executeQuery();
			while (rs.next()) {
				Photo photo = new Photo();
				photo.setImgUrl(s + rs.getString("name") + ".jpg");
				photo.setMsg(rs.getString("msg"));
				photo.setTime(rs.getTime("time").toString());
				photo.setLocation(rs.getString("location"));
				photo.setText(rs.getString("text"));
				photo.setTarget(rs.getString("target"));
				photos.add(photo);
			}
			jsonData = new Common().listToJSON(photos);
			
			rs.close();
			ps.close();
		} catch (SQLException e) {
			throw new RuntimeException(e);
		} finally {
			if (conn != null) {
				try {
					conn.close();
				} catch (SQLException e) {
				}
			}
		}
		return jsonData;
	}
	/**
	 * 每当数据库新保存一张图片（即每拍摄一张图片），就立即更新给app
	 * @param id 新保存图片的id，primary key
	 * @return 返回最后一张图片的json字符串
	 */
	public String currentImgJson(int id) {
		String s = "https://bearboy.tech/oppo/photos/";
		String jsonData = "";
		String sql = "select * from photo where id=?";
		Connection conn = null;
		try {
			conn = dataSource.getConnection();
			PreparedStatement ps = conn.prepareStatement(sql);
			ps.setInt(1, id);
			ResultSet rs = ps.executeQuery();
			Photo photo = new Photo();
			if (rs.next()) {
				photo.setImgUrl(s + rs.getString("name") + ".jpg");
				photo.setMsg(rs.getString("msg"));
				photo.setTime(rs.getTime("time").toString());
				photo.setLocation(rs.getString("location"));
				photo.setText(rs.getString("text"));
				photo.setTarget(rs.getString("target"));
			}
			jsonData = new Common().beanToJSON(photo);
			
			rs.close();
			ps.close();
		} catch (SQLException e) {
			throw new RuntimeException(e);
		} finally {
			if (conn != null) {
				try {
					conn.close();
				} catch (SQLException e) {
				}
			}
		}
		return jsonData;
	}
	/**
	 * 保存当前识别的图片到数据库
	 * @param s 图片的属性，包括名字，时间，地点，识别结果
	 * @return 返回保存后该图片的id，即上个方法的输入参数
	 */
	public int insertOneImg(String...s) {
		int id = 0;
		String sql = "insert into photo (name,text,target,msg,time,date,location) values (?,?,?,?,?,?,?)";
		Connection conn = null;
		PreparedStatement ps = null;
		ResultSet rs = null;
		try {
			conn = dataSource.getConnection();
			ps = conn.prepareStatement(sql,Statement.RETURN_GENERATED_KEYS);
			ps.setString(1, s[0]);
			ps.setString(2, s[1]);
			ps.setString(3, s[2]);
			ps.setString(4, s[3]);
			ps.setString(5, s[4]);
			ps.setString(6, s[5]);
			ps.setString(7, s[6]);
			ps.executeUpdate();
			rs = ps.getGeneratedKeys();
			if(rs.next())
				id = rs.getInt(1);
			rs.close();
			ps.close();
			
		} catch (SQLException e) {
			throw new RuntimeException(e);
		} finally {
			if (conn != null) {
				try {
					conn.close();
				} catch (SQLException e) {
				}
			}
		}
		return id;
	}
}
