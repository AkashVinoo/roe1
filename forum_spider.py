from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import json
import time
import logging
from config import AuthConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TDSContentCrawler:
    def __init__(self, auth_config: AuthConfig = None):
        """Initialize the crawler with optional authentication"""
        self.auth_config = auth_config or AuthConfig.load()
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        # Initialize the driver
        logger.info("Initializing Chrome driver...")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 20)
        logger.info("Chrome driver initialized successfully")
    
    def login_to_course(self):
        """Login to the course website"""
        if not self.auth_config.is_course_configured():
            logger.warning("Course credentials not configured, skipping login")
            return False
            
        try:
            logger.info("Attempting to log in to course website...")
            self.driver.get('https://tds.s-anand.net/login')
            
            # Wait for login form
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, 'username'))
            )
            password_field = self.driver.find_element(By.NAME, 'password')
            
            # Enter credentials
            username_field.send_keys(self.auth_config.course_username)
            password_field.send_keys(self.auth_config.course_password)
            
            # Submit form
            password_field.submit()
            
            # Wait for successful login
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'user-menu'))
                )
                logger.info("Successfully logged in to course website")
                
                # Save session cookie
                self.auth_config.course_session = self.driver.get_cookie('session')['value']
                self.auth_config.save()
                return True
                
            except TimeoutException:
                logger.error("Failed to log in to course website - invalid credentials?")
                return False
                
        except Exception as e:
            logger.error(f"Error logging in to course website: {str(e)}")
            return False
    
    def login_to_discourse(self):
        """Login to the Discourse forum"""
        if not self.auth_config.is_discourse_configured():
            logger.warning("Discourse credentials not configured, skipping login")
            return False
            
        try:
            logger.info("Attempting to log in to Discourse forum...")
            self.driver.get('https://discourse.onlinedegree.iitm.ac.in/login')
            
            # Wait for login form
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, 'login-account-name'))
            )
            password_field = self.driver.find_element(By.ID, 'login-account-password')
            
            # Enter credentials
            username_field.send_keys(self.auth_config.discourse_username)
            password_field.send_keys(self.auth_config.discourse_password)
            
            # Click login button
            login_button = self.driver.find_element(By.ID, 'login-button')
            login_button.click()
            
            # Wait for successful login
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'current-user'))
                )
                logger.info("Successfully logged in to Discourse forum")
                
                # Save session cookie
                self.auth_config.discourse_session = self.driver.get_cookie('_t')['value']
                self.auth_config.save()
                return True
                
            except TimeoutException:
                logger.error("Failed to log in to Discourse forum - invalid credentials?")
                return False
                
        except Exception as e:
            logger.error(f"Error logging in to Discourse forum: {str(e)}")
            return False
    
    def crawl_course_content(self):
        """Crawl the course content from tds.s-anand.net"""
        content_data = []
        
        # Try to login first
        if not self.login_to_course():
            logger.warning("Proceeding with public content only")
        
        try:
            logger.info("Attempting to access course website...")
            self.driver.get('https://tds.s-anand.net')
            
            # Take screenshot for debugging
            self.driver.save_screenshot('course_page.png')
            logger.info("Course website accessed, saved screenshot")
            
            # Wait for sidebar to load
            logger.info("Waiting for sidebar to load...")
            try:
                sidebar = self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'sidebar'))
                )
                logger.info("Sidebar loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load sidebar: {str(e)}")
                logger.info(f"Page source: {self.driver.page_source[:500]}...")
                return content_data
            
            # Get all links from sidebar
            links = sidebar.find_elements(By.TAG_NAME, 'a')
            logger.info(f"Found {len(links)} links in sidebar")
            
            for i, link in enumerate(links):
                try:
                    href = link.get_attribute('href')
                    if not href:
                        continue
                    
                    logger.info(f"Processing link {i+1}/{len(links)}: {href}")
                    
                    # Navigate to the page
                    self.driver.get(href)
                    time.sleep(2)
                    
                    # Wait for content to load
                    main_content = self.wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'content'))
                    )
                    
                    # Extract content
                    page_content = main_content.text
                    logger.info(f"Successfully extracted content from {href} ({len(page_content)} chars)")
                    
                    content_data.append({
                        'url': href,
                        'title': self.driver.title,
                        'content': page_content,
                        'source': 'course',
                        'timestamp': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing page {href}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error crawling course content: {str(e)}")
            
        logger.info(f"Completed course content crawl, collected {len(content_data)} pages")
        return content_data
    
    def crawl_discourse_forum(self):
        """Crawl the Discourse forum content"""
        forum_data = []
        
        # Try to login first
        if not self.login_to_discourse():
            logger.warning("Cannot access forum without authentication")
            return forum_data
        
        try:
            base_url = 'https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34'
            logger.info(f"Attempting to access forum at {base_url}")
            
            # Navigate to forum
            self.driver.get(base_url)
            time.sleep(3)
            
            # Take screenshot for debugging
            self.driver.save_screenshot('forum_page.png')
            logger.info(f"Current URL: {self.driver.current_url}")
            
            # Check if we're still on login page
            if 'login' in self.driver.current_url.lower():
                logger.error("Forum requires authentication")
                return forum_data
            
            # Wait for topics to load
            try:
                logger.info("Waiting for topics to load...")
                topics = self.wait.until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'topic-list-item'))
                )
                logger.info(f"Found {len(topics)} topics")
            except Exception as e:
                logger.error(f"Failed to load topics: {str(e)}")
                logger.info(f"Page source: {self.driver.page_source[:500]}...")
                return forum_data
            
            for i, topic in enumerate(topics):
                try:
                    logger.info(f"Processing topic {i+1}/{len(topics)}")
                    
                    # Get topic link
                    topic_link = topic.find_element(By.CLASS_NAME, 'title').find_element(By.TAG_NAME, 'a')
                    topic_url = topic_link.get_attribute('href')
                    
                    # Get topic date
                    date_str = topic.find_element(By.CLASS_NAME, 'last-posting-date').text
                    topic_date = datetime.strptime(date_str, '%b %d, %Y')
                    
                    # Only process topics from Jan 1, 2025 to Apr 14, 2025
                    start_date = datetime(2025, 1, 1)
                    end_date = datetime(2025, 4, 14)
                    
                    if start_date <= topic_date <= end_date:
                        logger.info(f"Topic date {topic_date} is within range, processing...")
                        
                        # Navigate to topic
                        self.driver.get(topic_url)
                        time.sleep(2)
                        
                        # Wait for posts to load
                        posts = self.wait.until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, 'topic-post'))
                        )
                        
                        # Extract content from all posts
                        topic_content = []
                        for post in posts:
                            post_content = post.find_element(By.CLASS_NAME, 'post-content').text
                            topic_content.append(post_content)
                        
                        logger.info(f"Extracted {len(topic_content)} posts from topic")
                        
                        forum_data.append({
                            'url': topic_url,
                            'title': self.driver.title,
                            'content': '\n\n'.join(topic_content),
                            'source': 'forum',
                            'timestamp': topic_date.isoformat()
                        })
                    else:
                        logger.info(f"Topic date {topic_date} is outside target range, skipping")
                        
                except Exception as e:
                    logger.error(f"Error processing topic: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error crawling forum content: {str(e)}")
            
        logger.info(f"Completed forum crawl, collected {len(forum_data)} topics")
        return forum_data
    
    def crawl_all_content(self):
        """Crawl both course content and forum data"""
        try:
            # Crawl course content
            logger.info("Starting course content crawl...")
            course_data = self.crawl_course_content()
            
            # Crawl forum content
            logger.info("Starting forum content crawl...")
            forum_data = self.crawl_discourse_forum()
            
            # Combine all data
            all_data = course_data + forum_data
            
            # Save to JSONL file
            output_file = 'tds_content.jsonl'
            logger.info(f"Saving {len(all_data)} items to {output_file}")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in all_data:
                    f.write(json.dumps(item) + '\n')
                    
            logger.info(f"Successfully crawled and saved {len(all_data)} pages")
            
        except Exception as e:
            logger.error(f"Error during crawling: {str(e)}")
        
        finally:
            self.driver.quit()

if __name__ == '__main__':
    # Load config and check if credentials are provided
    config = AuthConfig.load()
    if not (config.is_course_configured() and config.is_discourse_configured()):
        logger.warning("""
        No credentials found in auth_config.json. Please create this file with:
        {
            "course_username": "your_username",
            "course_password": "your_password",
            "discourse_username": "your_forum_username",
            "discourse_password": "your_forum_password"
        }
        """)
    
    crawler = TDSContentCrawler(config)
    crawler.crawl_all_content() 