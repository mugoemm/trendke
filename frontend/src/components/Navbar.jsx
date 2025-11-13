import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { FiHome, FiCompass, FiPlusSquare, FiUser, FiLogOut, FiMenu, FiX, FiTrendingUp, FiHeart, FiMessageCircle } from 'react-icons/fi';
import { BiCoinStack } from 'react-icons/bi';
import { getBalance } from '../api/giftsApi';
import toast from 'react-hot-toast';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [coinBalance, setCoinBalance] = useState(0);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    fetchBalance();
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    setUser(userData);
  }, []);

  const fetchBalance = async () => {
    try {
      const response = await getBalance();
      setCoinBalance(response.coin_balance);
    } catch (error) {
      console.error('Failed to fetch balance:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    toast.success('Logged out successfully');
    navigate('/login');
  };

  return (
    <>
      {/* Top Navbar - Desktop & Mobile */}
      <nav className="fixed top-0 left-0 right-0 bg-white dark:bg-black border-b border-gray-100 dark:border-gray-900 z-50 backdrop-blur-xl bg-opacity-95 dark:bg-opacity-95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2 group">
              <div className="relative">
                <span className="text-2xl md:text-3xl font-black bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 bg-clip-text text-transparent">
                  TrendKe
                </span>
                <div className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-pink-500 to-purple-500 group-hover:w-full transition-all duration-300"></div>
              </div>
            </Link>

            {/* Right Side */}
            <div className="flex items-center space-x-3">
              {/* Upload Button - Desktop */}
              <Link
                to="/upload"
                className="hidden md:flex items-center space-x-2 px-5 py-2.5 bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                <FiPlusSquare className="w-5 h-5" />
                <span className="hidden xl:block">Upload</span>
              </Link>

              {/* Coins - Desktop */}
              <div className="hidden md:flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-amber-400 to-orange-500 rounded-full shadow-md hover:shadow-lg transition-all cursor-pointer">
                <BiCoinStack className="w-5 h-5 text-white" />
                <span className="text-white font-bold">{coinBalance}</span>
              </div>

              {/* Profile - Desktop */}
              <Link to="/profile" className="hidden md:block relative group">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-500 to-purple-600 p-0.5 hover:scale-110 transition-transform">
                  {user?.avatar_url ? (
                    <img src={user.avatar_url} alt="Profile" className="w-full h-full rounded-full object-cover" />
                  ) : (
                    <div className="w-full h-full rounded-full bg-gray-800 flex items-center justify-center">
                      <FiUser className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>
              </Link>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setIsOpen(!isOpen)}
                className="md:hidden p-2 text-gray-700 dark:text-gray-300 hover:text-pink-500 transition-colors"
              >
                {isOpen ? <FiX className="w-6 h-6" /> : <FiMenu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {isOpen && (
          <div className="md:hidden bg-white dark:bg-black border-t border-gray-100 dark:border-gray-900">
            <div className="px-4 py-4 space-y-3">
              <MobileNavLink to="/upload" icon={<FiPlusSquare />} label="Upload" onClick={() => setIsOpen(false)} />
              <MobileNavLink to="/profile" icon={<FiUser />} label="Profile" onClick={() => setIsOpen(false)} />
              
              <div className="pt-3 border-t border-gray-200 dark:border-gray-800">
                <div className="flex items-center justify-between p-3 bg-gradient-to-r from-amber-400 to-orange-500 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <BiCoinStack className="w-5 h-5 text-white" />
                    <span className="text-white font-bold">Coins</span>
                  </div>
                  <span className="text-white font-bold text-lg">{coinBalance}</span>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="w-full flex items-center space-x-3 p-3 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
              >
                <FiLogOut className="w-5 h-5" />
                <span className="font-medium">Logout</span>
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Bottom Navigation - All Screens */}
      <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-black border-t border-gray-100 dark:border-gray-900 z-50 backdrop-blur-xl bg-opacity-95 dark:bg-opacity-95">
        <div className="flex justify-around items-center h-16 px-2">
          <BottomNavLink to="/" icon={<FiHome className="w-6 h-6" />} label="For You" />
          <BottomNavLink to="/following" icon={<FiHeart className="w-6 h-6" />} label="Following" />
          <BottomNavLink to="/explore" icon={<FiTrendingUp className="w-6 h-6" />} label="Trending" />
          <BottomNavLink to="/dashboard" icon={<FiCompass className="w-6 h-6" />} label="LIVE" />
        </div>
      </div>
    </>
  );
};

// Mobile Dropdown Link
const MobileNavLink = ({ to, icon, label, onClick }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      to={to}
      onClick={onClick}
      className={`flex items-center space-x-3 p-3 rounded-lg transition-all ${
        isActive
          ? 'bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900/20 dark:to-purple-900/20 text-pink-500'
          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-900'
      }`}
    >
      <div className="text-xl">{icon}</div>
      <span className="font-medium">{label}</span>
    </Link>
  );
};

// Bottom Navigation Link
const BottomNavLink = ({ to, icon, label }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      to={to}
      className="flex flex-col items-center space-y-1 flex-1 py-2"
    >
      <div className={`transition-all duration-200 ${
        isActive ? 'text-pink-500 scale-110' : 'text-gray-600 dark:text-gray-400'
      }`}>
        {icon}
      </div>
      <span className={`text-xs font-medium ${
        isActive ? 'text-pink-500' : 'text-gray-600 dark:text-gray-400'
      }`}>
        {label}
      </span>
    </Link>
  );
};

export default Navbar;
