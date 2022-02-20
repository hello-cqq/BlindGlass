package tech.bearboy.oppo.request;

import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.web.context.WebApplicationContext;
import org.springframework.web.context.support.WebApplicationContextUtils;

import tech.bearboy.oppo.dao.PhotoDAO;

/**
 * Servlet implementation class GetMsgServlet
 * app请求当天保存在数据库的所有图片并展示，需要经过这个servlet
 */
@WebServlet("/GetMsgServlet")
public class GetMsgServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;

	/**
	 * @see HttpServlet#HttpServlet()
	 */
	public GetMsgServlet() {
		super();
		// TODO Auto-generated constructor stub
	}

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse
	 *      response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {
		// TODO Auto-generated method stub
		response.getWriter().append("Served at: ").append(request.getContextPath());
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse
	 *      response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {
		// TODO Auto-generated method stub
		request.setCharacterEncoding("utf-8");
		String today = request.getParameter("today");
		System.out.println(today);
		//获取spring容器实例并实现数据库查询操作
		WebApplicationContext ctx = WebApplicationContextUtils
				.getWebApplicationContext(getServletConfig().getServletContext());
		String msg = ctx.getBean("photoDAO", PhotoDAO.class).todayMsgJson(today);
		response.setContentType("text/html;charset=utf-8");
		response.getWriter().write(msg);
	}

}
