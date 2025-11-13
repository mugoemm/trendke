import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { giftsApi, paymentsApi } from '../api/giftsApi';
import { liveApi } from '../api/liveApi';
import { FaCoins, FaChartLine, FaBroadcastTower } from 'react-icons/fa';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const navigate = useNavigate();
  const [balance, setBalance] = useState(null);
  const [giftHistory, setGiftHistory] = useState([]);
  const [packages, setPackages] = useState([]);
  const [showPurchaseModal, setShowPurchaseModal] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [balanceData, history, coinPackages] = await Promise.all([
        giftsApi.getBalance(),
        giftsApi.getGiftHistory(20),
        paymentsApi.getPackages(),
      ]);
      
      setBalance(balanceData);
      setGiftHistory(history);
      setPackages(coinPackages);
    } catch (error) {
      toast.error('Failed to load dashboard data');
    }
  };

  const handlePurchaseCoins = async (packageId) => {
    try {
      const result = await paymentsApi.initiatePurchase({
        coin_package_id: packageId,
        payment_method: 'pesapal',
      });
      
      window.open(result.payment_url, '_blank');
      toast.success('Redirecting to payment...');
      setShowPurchaseModal(false);
    } catch (error) {
      toast.error('Failed to initiate purchase');
    }
  };

  const handleStartLive = async (sessionType) => {
    try {
      const session = await liveApi.startLive({
        title: 'My Live Session',
        description: 'Join me live!',
        session_type: sessionType,
        max_participants: 50,
      });
      
      console.log('Live session started:', session);
      navigate(`/live/${session.id}`);
    } catch (error) {
      console.error('Failed to start live session:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to start live session';
      toast.error(errorMsg);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6 pb-20">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Creator Dashboard</h1>

        {/* Stats cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-800 p-6 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white/60">Coin Balance</h3>
              <FaCoins className="text-yellow-400 text-2xl" />
            </div>
            <p className="text-3xl font-bold text-white">
              {balance?.coin_balance || 0}
            </p>
            <button
              onClick={() => setShowPurchaseModal(true)}
              className="mt-4 w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
            >
              Buy Coins
            </button>
          </div>

          <div className="bg-gray-800 p-6 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white/60">Total Earnings</h3>
              <FaChartLine className="text-green-400 text-2xl" />
            </div>
            <p className="text-3xl font-bold text-white">
              ${balance?.total_earnings?.toFixed(2) || '0.00'}
            </p>
            <p className="text-white/60 text-sm mt-2">
              From gifts received
            </p>
          </div>

          <div className="bg-gray-800 p-6 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white/60">Go Live</h3>
              <FaBroadcastTower className="text-red-500 text-2xl" />
            </div>
            <div className="space-y-2 mt-4">
              <button
                onClick={() => handleStartLive('voice')}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg"
              >
                Voice Only
              </button>
              <button
                onClick={() => handleStartLive('camera')}
                className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg"
              >
                Camera
              </button>
              <button
                onClick={() => handleStartLive('studio')}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-lg"
              >
                Studio
              </button>
            </div>
          </div>
        </div>

        {/* Recent gifts */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Recent Gifts</h2>
          <div className="space-y-3">
            {giftHistory.slice(0, 10).map((gift) => (
              <div
                key={gift.id}
                className="flex items-center justify-between bg-gray-700 p-3 rounded-lg"
              >
                <div>
                  <p className="text-white font-semibold">
                    {gift.sender_username} → {gift.recipient_username}
                  </p>
                  <p className="text-white/60 text-sm">
                    {gift.amount}x {gift.gift_name}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-yellow-400 font-semibold">
                    {gift.total_coins} coins
                  </p>
                  {gift.creator_earnings && (
                    <p className="text-green-400 text-sm">
                      +${gift.creator_earnings.toFixed(2)}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>

          {giftHistory.length === 0 && (
            <p className="text-white/60 text-center py-8">
              No gift transactions yet
            </p>
          )}
        </div>

        {/* Purchase modal */}
        {showPurchaseModal && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-lg w-full max-w-md p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-white">Buy Coins</h3>
                <button
                  onClick={() => setShowPurchaseModal(false)}
                  className="text-white text-3xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-3">
                {packages.map((pkg) => (
                  <button
                    key={pkg.id}
                    onClick={() => handlePurchaseCoins(pkg.id)}
                    className="w-full bg-gray-800 hover:bg-gray-700 p-4 rounded-lg text-left transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-white font-bold">{pkg.name}</p>
                        <p className="text-yellow-400 text-sm">
                          {pkg.coin_amount} coins
                          {pkg.bonus_coins > 0 && (
                            <span className="text-green-400">
                              {' '}+ {pkg.bonus_coins} bonus
                            </span>
                          )}
                        </p>
                      </div>
                      <p className="text-white font-bold text-lg">
                        KES {pkg.price_kes}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
