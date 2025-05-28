import time

class DiscogsService:
    def get_metadata(self, file_info):
        """
        Get metadata from Discogs
        
        Args:
            file_info (dict): File information
            
        Returns:
            tuple: (metadata dict, success bool, response time)
        """
        if not self.available or not self.discogs_token:
            # Skip if Discogs is not available or no token provided
            return {}, False, 0
        
        start_time = time.time()
        
        try:
            # Extract existing metadata
            metadata = file_info.get('metadata', {})
            artist = metadata.get('artist', '')
            title = metadata.get('title', '')
            album = metadata.get('album', '')
            
            if not artist and not title:
                return {}, False, time.time() - start_time
            
            # Try search by artist and title first
            if artist and title:
                search_query = f"{artist} {title}"
                results = self._search_with_retry(search_query)
                
                if results:
                    metadata = self._extract_metadata_from_results(results)
                    return metadata, bool(metadata), time.time() - start_time
            
            # Try search by album if available
            if album:
                search_query = album
                results = self._search_with_retry(search_query)
                
                if results:
                    metadata = self._extract_metadata_from_results(results)
                    return metadata, bool(metadata), time.time() - start_time
            
            return {}, False, time.time() - start_time
        
        except Exception as e:
            # If we get an authentication error, disable the service
            if "401: Invalid consumer token" in str(e):
                self.available = False
                print(f"Discogs authentication failed. Service disabled.")
            else:
                print(f"Discogs search error: {str(e)}")
            return {}, False, time.time() - start_time 