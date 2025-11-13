"""
Cloudinary Video Upload Service
Handles video upload, transcoding, and thumbnail generation
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


class VideoUploadService:
    """Service for uploading and managing videos on Cloudinary"""
    
    @staticmethod
    async def upload_video(
        video_file,
        user_id: str,
        title: str,
        public_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Upload video to Cloudinary with automatic transcoding
        
        Args:
            video_file: Video file object
            user_id: User ID for folder organization
            title: Video title for metadata
            public_id: Optional custom public ID
            
        Returns:
            Dict with video_url, thumbnail_url, duration, format
        """
        try:
            # Read file content
            file_content = await video_file.read()
            
            # Upload video with transformations
            result = cloudinary.uploader.upload(
                file_content,
                resource_type="video",
                folder=f"trendke/videos/{user_id}",
                public_id=public_id,
                overwrite=True,
                # Video transformations for optimal streaming
                eager=[
                    # HD version (720p)
                    {
                        "width": 720,
                        "height": 1280,
                        "crop": "limit",
                        "quality": "auto:good",
                        "fetch_format": "mp4",
                        "video_codec": "h264"
                    },
                    # Mobile version (480p)
                    {
                        "width": 480,
                        "height": 854,
                        "crop": "limit",
                        "quality": "auto:eco",
                        "fetch_format": "mp4",
                        "video_codec": "h264"
                    }
                ],
                eager_async=True,  # Process in background
                # Generate thumbnail at 2 seconds
                eager_notification_url=None,  # Add webhook URL if needed
                context={
                    "title": title,
                    "user_id": user_id
                }
            )
            
            # Generate thumbnail URL
            thumbnail_url = cloudinary.CloudinaryImage(result['public_id']).build_url(
                resource_type="video",
                format="jpg",
                transformation=[
                    {"width": 400, "height": 711, "crop": "fill", "gravity": "center"},
                    {"start_offset": "2"}  # Thumbnail at 2 seconds
                ]
            )
            
            return {
                "video_url": result['secure_url'],
                "thumbnail_url": thumbnail_url,
                "public_id": result['public_id'],
                "duration": result.get('duration', 0),
                "format": result.get('format', 'mp4'),
                "bytes": result.get('bytes', 0),
                "width": result.get('width', 0),
                "height": result.get('height', 0)
            }
            
        except Exception as e:
            print(f"Video upload error: {e}")
            raise Exception(f"Failed to upload video: {str(e)}")
    
    @staticmethod
    async def delete_video(public_id: str) -> bool:
        """Delete video from Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id, resource_type="video")
            return result.get('result') == 'ok'
        except Exception as e:
            print(f"Video deletion error: {e}")
            return False
    
    @staticmethod
    def get_video_url(public_id: str, quality: str = "auto") -> str:
        """
        Get optimized video URL
        
        Args:
            public_id: Cloudinary public ID
            quality: auto, best, good, eco, low
        """
        return cloudinary.CloudinaryVideo(public_id).build_url(
            resource_type="video",
            transformation=[
                {"quality": quality, "fetch_format": "auto"}
            ]
        )


# Alternative: AWS S3 Implementation
class S3VideoUploadService:
    """
    AWS S3 Video Upload Service (for reference)
    Requires: pip install boto3
    """
    
    def __init__(self):
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.bucket_name = os.getenv('AWS_S3_BUCKET')
        except ImportError:
            print("boto3 not installed. Install with: pip install boto3")
            self.s3_client = None
            self.bucket_name = None
    
    async def upload_video(self, video_file, user_id: str, video_id: str):
        """Upload to S3"""
        if not self.s3_client:
            raise Exception("boto3 not installed")
        
        file_content = await video_file.read()
        key = f"videos/{user_id}/{video_id}.mp4"
        
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=file_content,
            ContentType='video/mp4'
        )
        
        # Generate public URL (if bucket is public) or signed URL
        url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
        return url
