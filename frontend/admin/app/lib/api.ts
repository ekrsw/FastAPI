import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  is_admin: boolean;
}

export const login = async (username: string, password: string): Promise<LoginResponse> => {
  const data = new URLSearchParams();
  data.append('username', username);
  data.append('password', password);

  const response = await api.post<LoginResponse>('/auth/token', data, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });
  return response.data;
};

export const getCurrentUser = async (): Promise<User> => {
  // ログインユーザー自身の情報を取得するため、/users/name/{username}エンドポイントを使用
  const token = localStorage.getItem('token');
  if (!token) throw new Error('認証トークンがありません');
  
  // JWTトークンからユーザー名を取得
  const payload = JSON.parse(atob(token.split('.')[1]));
  const username = payload.sub;
  
  const response = await api.get<User>(`/users/name/${username}`);
  return response.data;
};

export default api;
