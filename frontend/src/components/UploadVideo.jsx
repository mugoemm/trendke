import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiUpload, FiX, FiCheck } from 'react-icons/fi';
import { uploadVideo } from '../api/videoApi';
import toast from 'react-hot-toast';

const UploadVideo = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    hashtags: '',
  });
  const [videoFile, setVideoFile] = useState(null);
  const [videoPreview, setVideoPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleVideoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 100 * 1024 * 1024) { // 100MB limit
        toast.error('Video file must be less than 100MB');
        return;
      }

      setVideoFile(file);
      const preview = URL.createObjectURL(file);
      setVideoPreview(preview);
    }
  };

  const handleRemoveVideo = () => {
    setVideoFile(null);
    if (videoPreview) {
      URL.revokeObjectURL(videoPreview);
      setVideoPreview(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!videoFile) {
      toast.error('Please select a video file');
      return;
    }

    if (!formData.title.trim()) {
      toast.error('Please enter a title');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    
    // Simulate upload progress
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 300);

    try {
      const data = new FormData();
      data.append('video_file', videoFile);
      data.append('title', formData.title);
      if (formData.description) data.append('description', formData.description);
      if (formData.hashtags) data.append('hashtags', formData.hashtags);

      await uploadVideo(data);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      setTimeout(() => {
        toast.success('Video uploaded successfully!');
        navigate('/profile');
      }, 500);
    } catch (error) {
      clearInterval(progressInterval);
      toast.error('Failed to upload video');
      setUploadProgress(0);
    } finally {
      setTimeout(() => setUploading(false), 500);
    }
  };

  return (
    <div className="min-h-screen pt-20 pb-10 px-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Upload Video</h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Video Upload */}
          {!videoFile ? (
            <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center">
              <input
                type="file"
                accept="video/*"
                onChange={handleVideoChange}
                className="hidden"
                id="video-upload"
              />
              <label
                htmlFor="video-upload"
                className="cursor-pointer flex flex-col items-center space-y-4"
              >
                <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center">
                  <FiUpload className="text-pink-500" size={32} />
                </div>
                <div>
                  <p className="text-white font-semibold mb-2">Click to upload video</p>
                  <p className="text-gray-400 text-sm">MP4, MOV, AVI up to 100MB</p>
                </div>
              </label>
            </div>
          ) : (
            <div className="relative bg-gray-800 rounded-lg overflow-hidden">
              <video
                src={videoPreview}
                controls
                className="w-full h-64 object-contain"
              />
              <button
                type="button"
                onClick={handleRemoveVideo}
                className="absolute top-2 right-2 bg-black/50 text-white rounded-full p-2 hover:bg-black/70"
              >
                <FiX size={20} />
              </button>
            </div>
          )}

          {/* Title */}
          <div>
            <label htmlFor="title" className="block text-white font-semibold mb-2">
              Title *
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              placeholder="Enter video title"
              className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-pink-500"
              required
            />
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-white font-semibold mb-2">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Tell viewers about your video"
              rows={4}
              className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-pink-500 resize-none"
            />
          </div>

          {/* Hashtags */}
          <div>
            <label htmlFor="hashtags" className="block text-white font-semibold mb-2">
              Hashtags
            </label>
            <input
              type="text"
              id="hashtags"
              name="hashtags"
              value={formData.hashtags}
              onChange={handleInputChange}
              placeholder="dance, viral, trending (comma separated)"
              className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-pink-500"
            />
            <p className="text-gray-400 text-sm mt-2">
              Separate hashtags with commas
            </p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={uploading || !videoFile}
            className={`w-full py-3 rounded-lg font-semibold transition ${
              uploading || !videoFile
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-pink-500 to-purple-500 text-white hover:opacity-90'
            }`}
          >
            {uploading ? (
              <div className="flex items-center justify-center space-x-2">
                {uploadProgress === 100 ? (
                  <>
                    <FiCheck className="animate-bounce" />
                    <span>Upload Complete!</span>
                  </>
                ) : (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                    <span>Uploading... {uploadProgress}%</span>
                  </>
                )}
              </div>
            ) : (
              'Upload Video'
            )}
          </button>

          {/* Progress Bar */}
          {uploading && (
            <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-pink-500 to-purple-500 h-full transition-all duration-300 ease-out"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default UploadVideo;
