package tech.bearboy.oppo.client;

public class Monitor {

	private static Monitor monitor;
	public String name;
	public String doType;
	public String id;

	private Monitor(String name, String id) {
		this.name = name;
		this.id = id;
	}

	public static Monitor getMonitor(String name, String id) {
		if (monitor == null)
			monitor = new Monitor(name, id);
		return monitor;
	}

	@Override
	public String toString() {
		return this.doType;
	}
}
