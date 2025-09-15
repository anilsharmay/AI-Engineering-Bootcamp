import os
import re
from typing import List, Dict, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable


class TextFileLoader:
    def __init__(self, path: str, encoding: str = "utf-8"):
        self.documents = []
        self.path = path
        self.encoding = encoding

    def load(self):
        if os.path.isdir(self.path):
            self.load_directory()
        elif os.path.isfile(self.path) and self.path.endswith(".txt"):
            self.load_file()
        else:
            raise ValueError(
                "Provided path is neither a valid directory nor a .txt file."
            )

    def load_file(self):
        with open(self.path, "r", encoding=self.encoding) as f:
            self.documents.append(f.read())

    def load_directory(self):
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".txt"):
                    with open(
                        os.path.join(root, file), "r", encoding=self.encoding
                    ) as f:
                        self.documents.append(f.read())

    def load_documents(self):
        self.load()
        return self.documents


class CharacterTextSplitter:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        assert (
            chunk_size > chunk_overlap
        ), "Chunk size must be greater than chunk overlap"

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> List[str]:
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunks.append(text[i : i + self.chunk_size])
        return chunks

    def split_texts(self, texts: List[str]) -> List[str]:
        chunks = []
        for text in texts:
            chunks.extend(self.split(text))
        return chunks


class YouTubeTranscriptLoader:
    """
    A class to load transcripts from a single YouTube video using the YouTube Transcript API.
    """
    
    def __init__(self):
        self.document = ""
        self.metadata = {}
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID or None if not found
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def load_youtube_transcript(self, url: str, languages: List[str] = ['en']) -> Dict:
        """
        Load transcript from a YouTube video.
        
        Args:
            url: YouTube video URL
            languages: List of language codes to try (default: ['en'])
            
        Returns:
            Dictionary containing transcript and metadata
        """
        try:
            # Extract video ID
            video_id = self._extract_video_id(url)
            if not video_id:
                return {
                    'transcript': '',
                    'metadata': {},
                    'success': False,
                    'error': 'Could not extract video ID from URL'
                }
            
            # Get transcript using the correct API
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id=video_id)
            transcript_list = transcript_list.find_transcript(languages)
            transcript_list = transcript_list.fetch()
            
            # Combine transcript segments into full text
            transcript_text = ' '.join([segment.text for segment in transcript_list])
            
            # Create metadata
            metadata = {
                'video_id': video_id,
                'url': url,
                'transcript_length': len(transcript_text),
                'segment_count': len(transcript_list),
                'language': languages[0] if languages else 'unknown',
                'source_type': 'youtube_transcript'
            }
            
            # Store document and metadata
            self.document = transcript_text
            self.metadata = metadata
            
            return {
                'transcript': transcript_text,
                'metadata': metadata,
                'success': True
            }
            
        except NoTranscriptFound:
            return {
                'transcript': '',
                'metadata': {},
                'success': False,
                'error': 'No transcript is available for this video. This video cannot be processed.'
            }
        except TranscriptsDisabled:
            return {
                'transcript': '',
                'metadata': {},
                'success': False,
                'error': 'Transcripts are disabled for this video. This video cannot be processed.'
            }
        except VideoUnavailable:
            return {
                'transcript': '',
                'metadata': {},
                'success': False,
                'error': 'Video is unavailable (private, deleted, or restricted). This video cannot be processed.'
            }
        except Exception as e:
            return {
                'transcript': '',
                'metadata': {},
                'success': False,
                'error': f'Unexpected error: {str(e)}. This video cannot be processed.'
            }
    
    def get_document(self) -> str:
        """Get the loaded document."""
        return self.document
    
    def get_metadata(self) -> Dict:
        """Get the metadata."""
        return self.metadata
    
    def get_document_with_metadata(self) -> Dict:
        """
        Get document with its associated metadata.
        
        Returns:
            Dictionary with 'text' and 'metadata' keys
        """
        return {
            'text': self.document,
            'metadata': self.metadata
        }


if __name__ == "__main__":
    # Test with text files
    loader = TextFileLoader("data/KingLear.txt")
    loader.load()
    splitter = CharacterTextSplitter()
    chunks = splitter.split_texts(loader.documents)
    print(len(chunks))
    print(chunks[0])
    print("--------")
    print(chunks[1])
    print("--------")
    print(chunks[-2])
    print("--------")
    print(chunks[-1])
    
    # Test with YouTube transcript (uncomment to test)
    # youtube_loader = YouTubeTranscriptLoader()
    # result = youtube_loader.load_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    # print(result)
