import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Register from './pages/Register';
import Login from './pages/Login';
import Organizations from './pages/Organizations';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        
        {/* Protected Routes */}
        <Route
          path="/organizations"
          element={
            <ProtectedRoute>
              <Organizations />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        
        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/organizations" replace />} />
        
        {/* 404 */}
        <Route path="*" element={<Navigate to="/organizations" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;