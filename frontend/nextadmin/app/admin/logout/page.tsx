'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Logout() {
  const router = useRouter();

  useEffect(() => {
    // ローカルストレージからトークンを削除
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');

    // 3秒後にログイン画面にリダイレクト
    const timer = setTimeout(() => {
      router.push('/admin/login');
    }, 3000);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg text-center">
        <h2 className="text-3xl font-extrabold text-gray-900">
          ログアウトしました
        </h2>
        <p className="mt-2 text-sm text-gray-600">
          3秒後にログイン画面に移動します...
        </p>
      </div>
    </div>
  );
}
