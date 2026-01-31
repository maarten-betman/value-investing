import { useState } from "react";
import axios from "axios";
import { useAuthStore } from "@/store/auth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const setTokens = useAuthStore((s) => s.setTokens);
  const setUser = useAuthStore((s) => s.setUser);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isRegister) {
        await axios.post("/api/auth/register", { email, password });
      }

      const { data } = await axios.post("/api/auth/login", {
        email,
        password,
      });
      setTokens(data.access_token, data.refresh_token);

      const { data: user } = await axios.get("/api/auth/me", {
        headers: { Authorization: `Bearer ${data.access_token}` },
      });
      setUser(user);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || "Authentication failed");
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md space-y-8 rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 rounded-xl bg-brand-600 flex items-center justify-center">
            <span className="text-white font-bold text-lg">VI</span>
          </div>
          <h2 className="mt-4 text-2xl font-bold text-gray-900">
            Value Investing Tracker
          </h2>
          <p className="mt-2 text-sm text-gray-500">
            {isRegister ? "Create your account" : "Sign in to your account"}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {loading
              ? "Loading..."
              : isRegister
                ? "Create Account"
                : "Sign In"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500">
          {isRegister ? "Already have an account?" : "First time here?"}{" "}
          <button
            onClick={() => setIsRegister(!isRegister)}
            className="font-medium text-brand-600 hover:text-brand-500"
          >
            {isRegister ? "Sign in" : "Create account"}
          </button>
        </p>
      </div>
    </div>
  );
}
