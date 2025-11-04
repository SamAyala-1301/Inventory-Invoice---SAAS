export default function AuthLayout({ children, title, subtitle }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary-600 mb-2">
            Inventory SaaS
          </h1>
          <p className="text-gray-600">
            Multi-tenant Inventory & Invoice Management
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
          {subtitle && (
            <p className="text-gray-600 mb-6">{subtitle}</p>
          )}
          
          {children}
        </div>

        <div className="text-center mt-6 text-sm text-gray-600">
          <p>&copy; 2024 Inventory SaaS. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
}