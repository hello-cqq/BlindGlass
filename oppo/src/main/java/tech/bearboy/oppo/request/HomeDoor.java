package tech.bearboy.oppo.request;

import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import tech.bearboy.oppo.client.Monitor;
import tech.bearboy.oppo.client.Raspberry;

/**
 * Servlet implementation class HomeDoor
 * 该类没有任何用处，忽略即可
 */
@WebServlet("/HomeDoor")
public class HomeDoor extends HttpServlet {
	private static final long serialVersionUID = 1L;

	/**
	 * @see HttpServlet#HttpServlet()
	 */
	public HomeDoor() {
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
		String key = request.getParameter("key");
		String doType = request.getParameter("doType");
		String id = request.getParameter("id");
		HttpSession session = request.getSession();
		String msg = "";
		if (key.equals("1")) {
			Monitor monitor = Monitor.getMonitor("宝宝", id);
			monitor.doType = doType;
			String m = (String) session.getAttribute("monitor");
			if (m == null) {
				session.setAttribute("monitor", monitor.doType);
			}
			System.out.println(session.getAttribute("monitor"));
			msg = "{'status':'success','name':'宝宝'}";

		} else if (key.equals("0")) {
			Raspberry pi = Raspberry.getPi("贝贝", id);
			pi.doType = doType;
			String p = (String) session.getAttribute("pi");
			if (p == null) {
				session.setAttribute("pi", pi.doType);
			}
			System.out.println(session.getAttribute("pi"));
			msg = "{'status':'success','name':'宝宝'}";
		}
		response.setContentType("text/html;charset=utf-8");
		response.getWriter().write(msg);
	}

}
