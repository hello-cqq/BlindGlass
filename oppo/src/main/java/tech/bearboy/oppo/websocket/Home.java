package tech.bearboy.oppo.websocket;

import java.io.IOException;
import java.util.Set;
import java.util.concurrent.CopyOnWriteArraySet;

import javax.websocket.OnClose;
import javax.websocket.OnError;
import javax.websocket.OnMessage;
import javax.websocket.OnOpen;
import javax.websocket.Session;
import javax.websocket.server.PathParam;
import javax.websocket.server.ServerEndpoint;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.log4j.Logger;

import net.sf.json.JSONObject;
import tech.bearboy.oppo.common.Common;
/**
 * websocket类，表示一个聊天室，注册了树莓派-raspberry，监护人-app，盲人伴随app-master,跑算法的-gpu，服务器根据不同命令实现消息转发
 * @author 常前前
 *
 */
@ServerEndpoint(value = "/websocket/{name}")
public class Home{
	
	// 计数
	// private static final AtomicInteger connectionIds = new AtomicInteger(0);
	// 集合保存所有websocket客户端
	private static final Set<Home> clientSet = new CopyOnWriteArraySet<>();
	private static Home app;
	private static Home raspberry;
	private static Home gpu;
	private static Home master;
	// 不同客户端名字
	private String name;
	// 每个客户端会话session
	private Session session;
	Logger logger = Logger.getLogger(this.getClass());
	Log log = LogFactory.getLog(this.getClass());
	
	
	@OnOpen
	/**
	 * websocket打开
	 * @param session 代表当前用户的会话
	 * @param name 代表当前用户的名字
	 */
	public void start(Session session, @PathParam("name") String name) {
		//System.out.println(System.getProperty("catalina.home"));
		this.name = name;
		this.session = session;
		if (name.equals("app")) {
			app = this;
		} else if (name.equals("raspberry")) {
			raspberry = this;
		} else if (name.equals("gpu")) {
			gpu = this;
		}
		else if (name.equals("master")) {
			master = this;
		}
		clientSet.add(this);
		String message = "{\"fromWho\": \""+name+"\",\"msg\": \"已做好准备\"}";
		logger.info(message);
		// System.out.println(message);
		if (app != null) {
			try {
				app.session.getBasicRemote().sendText(message);
			} catch (IOException e) {
				// TODO: handle exception
			}

		}
	}
	@OnClose
	/**
	 * websocket关闭
	 */
	public void end() {
		clientSet.remove(this);
		String message = name + "关闭";
		System.out.println(message);
		switch(this.name) {
			case "app":
				app = null;
				break;
			case "raspberry":
				raspberry = null;
				break;
			case "gpu":
				gpu = null;
				break;
			case "master":
				master = null;
				break;
		}
		logger.info(message);
		if (app != null) {
			try {
				app.session.getBasicRemote().sendText("{\"fromWho\": \""+this.name+"\",\"msg\": \""+message+"\"}");
			} catch (IOException e) {
				// TODO: handle exception
			}

		}
	}
	/**
	 * 接收消息
	 * @param message 接收的消息，必须是json字符串
	 * @param session 当前会话
	 */
	@OnMessage
	public void incoming(String message, Session session) {
		String filteredMessage = filter(message);// 
		broadcast(filteredMessage);
	}

	@OnError
	/**
	 * websocket异常
	 * @param t 异常
	 * @throws Throwable
	 */
	public void onError(Throwable t) throws Throwable {
		System.out.println("WebSocket服务端错误" + t);
	}
	//服务器向客户端转发消息的实现方法
	private void broadcast(String message) {
		
		JSONObject jsonObject = new Common().jsonToObject(message);
		try {
			if(jsonObject.get("fromWho").equals("raspberry")&&jsonObject.get("toWho").equals("gpu")&&gpu!=null) {
				gpu.session.getBasicRemote().sendText(message);
				logger.info("raspberry"+"->"+"gpu:"+message);
			}
			else if(jsonObject.get("fromWho").equals("raspberry")&&jsonObject.get("toWho").equals("app")&&app!=null) {
				app.session.getBasicRemote().sendText(message);
				logger.info("raspberry"+"->"+"app:"+message);
			}
			else if(jsonObject.get("fromWho").equals("raspberry")&&jsonObject.get("toWho").equals("master")&&app!=null) {
				master.session.getBasicRemote().sendText(message);
				logger.info("raspberry"+"->"+"master:"+message);
			}
			else if(jsonObject.get("fromWho").equals("master")&&jsonObject.get("toWho").equals("raspberry")&&app!=null) {
				raspberry.session.getBasicRemote().sendText(message);
				logger.info("master"+"->"+"raspberry:"+message);
			}
			else if(jsonObject.get("fromWho").equals("gpu")&&jsonObject.get("toWho").equals("raspberry")&&raspberry!=null) {
				String msg = resultHandle(jsonObject);
				raspberry.session.getBasicRemote().sendText(msg);
				logger.info("gpu"+"->"+"raspberry:"+msg);
			}
			else if(jsonObject.get("fromWho").equals("app")&&jsonObject.get("toWho").equals("raspberry")) {
				if(raspberry!=null)
					raspberry.session.getBasicRemote().sendText(message);
				if(app!=null)
					app.session.getBasicRemote().sendText(message);
				
				logger.info("app"+"->"+"raspberry:"+message);
			}
		} catch (IOException e) {
			System.out.println("错误");
			logger.info("websocket send error");
		}

	}
	
	private String resultHandle(JSONObject jsonObject) {
		try {
			
		}catch(Exception e) {
			
		}
		return jsonObject.toString();
	}

	private static String filter(String message) {
		return message;
	}
}
