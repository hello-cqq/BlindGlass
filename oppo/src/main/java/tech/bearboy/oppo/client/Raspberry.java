package tech.bearboy.oppo.client;

public class Raspberry {
	private static Raspberry pi;

	public String name;
	public String doType;
	public String id;

	private Raspberry(String name, String id) {
		this.name = name;
		this.id = id;
	}

	public static Raspberry getPi(String name, String id) {
		if (pi == null) {
			pi = new Raspberry(name, id);
		}
		return pi;
	}

	@Override
	public String toString() {
		return this.doType;
	}
}
