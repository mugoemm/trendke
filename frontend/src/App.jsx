import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Profile from './pages/Profile';
import Dashboard from './pages/Dashboard';
import Following from './pages/Following';
import Explore from './pages/Explore';
import Login from './pages/Login';
import Signup from './pages/Signup';
import UploadVideo from './components/UploadVideo';
import LiveRoomEnhanced from './components/LiveRoomEnhanced';

// Protected route wrapper
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  return (
    <Router>
      <div className="App">
        <Toaster
          position="top-center"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#1f2937',
              color: '#fff',
            },
          }}
        />
        
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          
          {/* Public home - browse videos without login */}
          <Route
            path="/"
            element={
              <>
                <Navbar />
                <Home />
              </>
            }
          />
          
          {/* Protected routes */}
          <Route
            path="/profile/:userId?"
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <Profile />
                </>
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <Dashboard />
                </>
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/following"
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <Following />
                </>
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/explore"
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <Explore />
                </>
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/upload"
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <UploadVideo />
                </>
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/live/:sessionId"
            element={
              <ProtectedRoute>
                <LiveRoomEnhanced />
              </ProtectedRoute>
            }
          />
          
          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
