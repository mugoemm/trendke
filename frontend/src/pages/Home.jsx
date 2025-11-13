import React from 'react';
import { useLocation } from 'react-router-dom';
import VideoFeed from '../components/VideoFeed';

const Home = () => {
  const location = useLocation();
  const targetVideoId = location.state?.videoId;

  return (
    <div className="w-full h-screen">
      <VideoFeed initialVideoId={targetVideoId} />
    </div>
  );
};

export default Home;
