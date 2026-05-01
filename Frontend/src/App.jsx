import React from 'react'

function App() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-900">
      <div className="p-8 bg-white rounded-2xl shadow-2xl border-t-4 border-blue-500 w-96 text-center">
        <h1 className="text-3xl font-extrabold text-slate-800 mb-2">
          Budget App 💰
        </h1>
        <p className="text-slate-500 mb-6">مرحباً بك يا أحمد في تطبيق الميزانية</p>
        
        <div className="bg-blue-50 p-4 rounded-xl mb-4">
          <p className="text-sm text-blue-600 font-semibold uppercase">الرصيد المتاح</p>
          <h2 className="text-2xl font-bold text-slate-900">15,500 ج.م</h2>
        </div>

        <button className="w-full bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700 transition-all active:scale-95 shadow-lg shadow-blue-200">
          إضافة عملية جديدة
        </button>
      </div>
    </div>
  )
}

export default App