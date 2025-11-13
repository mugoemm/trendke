import React, { useState, useEffect } from 'react';
import { FiGift } from 'react-icons/fi';
import { getGiftTypes, sendGift, getBalance } from '../api/giftsApi';
import toast from 'react-hot-toast';

const GiftButton = ({ receiverId }) => {
  const [showModal, setShowModal] = useState(false);
  const [giftTypes, setGiftTypes] = useState([]);
  const [selectedGift, setSelectedGift] = useState(null);
  const [balance, setBalance] = useState(0);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (showModal) {
      fetchGiftTypes();
      fetchBalance();
    }
  }, [showModal]);

  const fetchGiftTypes = async () => {
    try {
      const types = await getGiftTypes();
      setGiftTypes(types);
    } catch (error) {
      toast.error('Failed to load gifts');
    }
  };

  const fetchBalance = async () => {
    try {
      const response = await getBalance();
      setBalance(response.coin_balance);
    } catch (error) {
      console.error('Failed to fetch balance:', error);
    }
  };

  const handleSendGift = async () => {
    if (!selectedGift) return;

    if (balance < selectedGift.coin_cost) {
      toast.error('Insufficient coins');
      return;
    }

    setSending(true);
    try {
      await sendGift(receiverId, selectedGift.id);
      toast.success(`Sent ${selectedGift.name}!`);
      setBalance(prev => prev - selectedGift.coin_cost);
      setShowModal(false);
      setSelectedGift(null);
      
      // Show floating gift animation
      showGiftAnimation(selectedGift);
    } catch (error) {
      toast.error('Failed to send gift');
    } finally {
      setSending(false);
    }
  };

  const showGiftAnimation = (gift) => {
    const giftElement = document.createElement('div');
    giftElement.className = 'fixed animate-float z-50';
    giftElement.style.left = `${Math.random() * 80 + 10}%`;
    giftElement.style.bottom = '20%';
    giftElement.style.fontSize = '3rem';
    giftElement.textContent = gift.emoji;
    document.body.appendChild(giftElement);

    setTimeout(() => {
      document.body.removeChild(giftElement);
    }, 2000);
  };

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="flex flex-col items-center space-y-1"
      >
        <FiGift className="text-white" size={32} />
        <span className="text-white text-xs">Gift</span>
      </button>

      {showModal && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-end justify-center md:items-center">
          <div className="bg-gray-900 w-full md:w-auto md:min-w-[500px] rounded-t-3xl md:rounded-3xl p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-white text-xl font-bold">Send a Gift</h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="mb-6 p-4 bg-gray-800 rounded-lg">
              <p className="text-gray-400 text-sm mb-2">Your Balance</p>
              <p className="text-white text-2xl font-bold">{balance} Coins</p>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-6">
              {giftTypes.map((gift) => (
                <button
                  key={gift.id}
                  onClick={() => setSelectedGift(gift)}
                  className={`p-4 rounded-xl transition-all ${
                    selectedGift?.id === gift.id
                      ? 'bg-gradient-to-r from-pink-500 to-purple-500 scale-105'
                      : 'bg-gray-800 hover:bg-gray-700'
                  }`}
                >
                  <div className="text-4xl mb-2">{gift.emoji}</div>
                  <p className="text-white text-sm font-semibold mb-1">{gift.name}</p>
                  <p className="text-yellow-400 text-xs">{gift.coin_cost} coins</p>
                </button>
              ))}
            </div>

            {selectedGift && (
              <div className="mb-4 p-4 bg-gray-800 rounded-lg">
                <p className="text-gray-400 text-sm mb-1">Selected Gift</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-3xl">{selectedGift.emoji}</span>
                    <div>
                      <p className="text-white font-semibold">{selectedGift.name}</p>
                      <p className="text-yellow-400 text-sm">{selectedGift.coin_cost} coins</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <button
              onClick={handleSendGift}
              disabled={!selectedGift || sending || balance < selectedGift?.coin_cost}
              className={`w-full py-3 rounded-full font-semibold transition ${
                !selectedGift || sending || balance < selectedGift?.coin_cost
                  ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-pink-500 to-purple-500 text-white hover:opacity-90'
              }`}
            >
              {sending ? 'Sending...' : 'Send Gift'}
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default GiftButton;
