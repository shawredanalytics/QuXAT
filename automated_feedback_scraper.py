"""
Automated Patient Feedback Scraper for QuXAT Healthcare Quality Scoring
This module scrapes patient feedback from various online platforms and social media
to provide real-time sentiment analysis for healthcare organizations.
"""

import requests
import json
import time
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics
from textblob import TextBlob
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScrapedFeedback:
    """Represents a scraped patient feedback from online platforms"""
    organization_name: str
    platform: str  # 'google', 'facebook', 'twitter', 'healthgrades', 'yelp'
    rating: Optional[float]  # 1-5 scale if available
    review_text: str
    sentiment_score: float  # -1 to 1 (negative to positive)
    timestamp: datetime
    reviewer_name: Optional[str] = None
    verified: bool = False

@dataclass
class FeedbackSummary:
    """Summary of all scraped feedback for an organization"""
    organization_name: str
    total_reviews: int
    average_rating: float
    sentiment_score: float  # Overall sentiment (-1 to 1)
    platform_breakdown: Dict[str, int]  # Count per platform
    recent_trend: str  # 'improving', 'stable', 'declining'
    confidence_score: float  # 0-1 based on review volume and recency
    last_updated: datetime

class AutomatedFeedbackScraper:
    """Main class for scraping and analyzing patient feedback from multiple platforms"""
    
    def __init__(self):
        self.platforms = {
            'google': self._scrape_google_reviews,
            'facebook': self._scrape_facebook_reviews,
            'twitter': self._scrape_twitter_mentions,
            'healthgrades': self._scrape_healthgrades_reviews,
            'yelp': self._scrape_yelp_reviews
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_organization_feedback(self, organization_name: str, location: str = "") -> FeedbackSummary:
        """
        Scrape feedback for a healthcare organization from all available platforms
        
        Args:
            organization_name: Name of the healthcare organization
            location: Location to help with search accuracy
            
        Returns:
            FeedbackSummary with aggregated feedback data
        """
        logger.info(f"Starting feedback scraping for: {organization_name}")
        
        all_feedback = []
        platform_counts = {}
        
        for platform_name, scraper_func in self.platforms.items():
            try:
                logger.info(f"Scraping {platform_name} for {organization_name}")
                feedback_list = scraper_func(organization_name, location)
                all_feedback.extend(feedback_list)
                platform_counts[platform_name] = len(feedback_list)
                
                # Rate limiting to avoid being blocked
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error scraping {platform_name}: {str(e)}")
                platform_counts[platform_name] = 0
        
        if not all_feedback:
            logger.warning(f"No feedback found for {organization_name}")
            return self._create_empty_summary(organization_name)
        
        return self._analyze_feedback(organization_name, all_feedback, platform_counts)
    
    def _scrape_google_reviews(self, org_name: str, location: str) -> List[ScrapedFeedback]:
        """Scrape Google Reviews using Google Places API simulation"""
        feedback_list = []
        
        try:
            # Simulate Google Places search
            search_query = f"{org_name} {location} hospital reviews"
            
            # For demonstration, we'll simulate some realistic feedback
            # In production, you would use Google Places API or web scraping
            simulated_reviews = self._generate_simulated_google_reviews(org_name)
            
            for review_data in simulated_reviews:
                sentiment = self._analyze_sentiment(review_data['text'])
                
                feedback = ScrapedFeedback(
                    organization_name=org_name,
                    platform='google',
                    rating=review_data['rating'],
                    review_text=review_data['text'],
                    sentiment_score=sentiment,
                    timestamp=review_data['date'],
                    reviewer_name=review_data.get('author', 'Anonymous'),
                    verified=True
                )
                feedback_list.append(feedback)
                
        except Exception as e:
            logger.error(f"Google Reviews scraping error: {str(e)}")
        
        return feedback_list
    
    def _scrape_facebook_reviews(self, org_name: str, location: str) -> List[ScrapedFeedback]:
        """Scrape Facebook reviews and posts mentioning the organization"""
        feedback_list = []
        
        try:
            # Simulate Facebook reviews
            simulated_reviews = self._generate_simulated_facebook_reviews(org_name)
            
            for review_data in simulated_reviews:
                sentiment = self._analyze_sentiment(review_data['text'])
                
                feedback = ScrapedFeedback(
                    organization_name=org_name,
                    platform='facebook',
                    rating=review_data.get('rating'),
                    review_text=review_data['text'],
                    sentiment_score=sentiment,
                    timestamp=review_data['date'],
                    reviewer_name=review_data.get('author', 'Anonymous'),
                    verified=False
                )
                feedback_list.append(feedback)
                
        except Exception as e:
            logger.error(f"Facebook scraping error: {str(e)}")
        
        return feedback_list
    
    def _scrape_twitter_mentions(self, org_name: str, location: str) -> List[ScrapedFeedback]:
        """Scrape Twitter/X mentions of the organization"""
        feedback_list = []
        
        try:
            # Simulate Twitter mentions
            simulated_tweets = self._generate_simulated_twitter_mentions(org_name)
            
            for tweet_data in simulated_tweets:
                sentiment = self._analyze_sentiment(tweet_data['text'])
                
                feedback = ScrapedFeedback(
                    organization_name=org_name,
                    platform='twitter',
                    rating=None,  # Twitter doesn't have ratings
                    review_text=tweet_data['text'],
                    sentiment_score=sentiment,
                    timestamp=tweet_data['date'],
                    reviewer_name=tweet_data.get('author', 'Anonymous'),
                    verified=tweet_data.get('verified', False)
                )
                feedback_list.append(feedback)
                
        except Exception as e:
            logger.error(f"Twitter scraping error: {str(e)}")
        
        return feedback_list
    
    def _scrape_healthgrades_reviews(self, org_name: str, location: str) -> List[ScrapedFeedback]:
        """Scrape Healthgrades reviews"""
        feedback_list = []
        
        try:
            # Simulate Healthgrades reviews
            simulated_reviews = self._generate_simulated_healthgrades_reviews(org_name)
            
            for review_data in simulated_reviews:
                sentiment = self._analyze_sentiment(review_data['text'])
                
                feedback = ScrapedFeedback(
                    organization_name=org_name,
                    platform='healthgrades',
                    rating=review_data['rating'],
                    review_text=review_data['text'],
                    sentiment_score=sentiment,
                    timestamp=review_data['date'],
                    reviewer_name=review_data.get('author', 'Anonymous'),
                    verified=True
                )
                feedback_list.append(feedback)
                
        except Exception as e:
            logger.error(f"Healthgrades scraping error: {str(e)}")
        
        return feedback_list
    
    def _scrape_yelp_reviews(self, org_name: str, location: str) -> List[ScrapedFeedback]:
        """Scrape Yelp reviews"""
        feedback_list = []
        
        try:
            # Simulate Yelp reviews
            simulated_reviews = self._generate_simulated_yelp_reviews(org_name)
            
            for review_data in simulated_reviews:
                sentiment = self._analyze_sentiment(review_data['text'])
                
                feedback = ScrapedFeedback(
                    organization_name=org_name,
                    platform='yelp',
                    rating=review_data['rating'],
                    review_text=review_data['text'],
                    sentiment_score=sentiment,
                    timestamp=review_data['date'],
                    reviewer_name=review_data.get('author', 'Anonymous'),
                    verified=False
                )
                feedback_list.append(feedback)
                
        except Exception as e:
            logger.error(f"Yelp scraping error: {str(e)}")
        
        return feedback_list
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of review text using TextBlob"""
        try:
            blob = TextBlob(text)
            # TextBlob returns polarity from -1 (negative) to 1 (positive)
            return blob.sentiment.polarity
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return 0.0
    
    def _analyze_feedback(self, org_name: str, feedback_list: List[ScrapedFeedback], 
                         platform_counts: Dict[str, int]) -> FeedbackSummary:
        """Analyze all collected feedback and create summary"""
        
        # Calculate metrics
        total_reviews = len(feedback_list)
        
        # Average rating (only from platforms that provide ratings)
        ratings = [f.rating for f in feedback_list if f.rating is not None]
        avg_rating = statistics.mean(ratings) if ratings else 0.0
        
        # Overall sentiment score
        sentiment_scores = [f.sentiment_score for f in feedback_list]
        overall_sentiment = statistics.mean(sentiment_scores) if sentiment_scores else 0.0
        
        # Calculate trend based on recent vs older reviews
        recent_trend = self._calculate_trend(feedback_list)
        
        # Confidence score based on volume and recency
        confidence = self._calculate_confidence_score(feedback_list)
        
        return FeedbackSummary(
            organization_name=org_name,
            total_reviews=total_reviews,
            average_rating=avg_rating,
            sentiment_score=overall_sentiment,
            platform_breakdown=platform_counts,
            recent_trend=recent_trend,
            confidence_score=confidence,
            last_updated=datetime.now()
        )
    
    def _calculate_trend(self, feedback_list: List[ScrapedFeedback]) -> str:
        """Calculate if sentiment is improving, stable, or declining"""
        if len(feedback_list) < 4:
            return 'stable'
        
        # Sort by timestamp
        sorted_feedback = sorted(feedback_list, key=lambda x: x.timestamp)
        
        # Split into recent and older halves
        mid_point = len(sorted_feedback) // 2
        older_half = sorted_feedback[:mid_point]
        recent_half = sorted_feedback[mid_point:]
        
        # Calculate average sentiment for each half
        older_sentiment = statistics.mean([f.sentiment_score for f in older_half])
        recent_sentiment = statistics.mean([f.sentiment_score for f in recent_half])
        
        # Determine trend
        difference = recent_sentiment - older_sentiment
        
        if difference > 0.1:
            return 'improving'
        elif difference < -0.1:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_confidence_score(self, feedback_list: List[ScrapedFeedback]) -> float:
        """Calculate confidence score based on review volume and recency"""
        if not feedback_list:
            return 0.0
        
        # Volume factor (more reviews = higher confidence)
        volume_factor = min(len(feedback_list) / 50.0, 1.0)  # Max at 50 reviews
        
        # Recency factor (recent reviews = higher confidence)
        now = datetime.now()
        recent_reviews = [f for f in feedback_list 
                         if (now - f.timestamp).days <= 90]  # Last 90 days
        recency_factor = len(recent_reviews) / len(feedback_list)
        
        # Platform diversity factor
        platforms = set(f.platform for f in feedback_list)
        diversity_factor = min(len(platforms) / 3.0, 1.0)  # Max at 3 platforms
        
        # Combined confidence score
        confidence = (volume_factor * 0.4 + recency_factor * 0.4 + diversity_factor * 0.2)
        return min(confidence, 1.0)
    
    def _create_empty_summary(self, org_name: str) -> FeedbackSummary:
        """Create empty summary when no feedback is found"""
        return FeedbackSummary(
            organization_name=org_name,
            total_reviews=0,
            average_rating=0.0,
            sentiment_score=0.0,
            platform_breakdown={},
            recent_trend='stable',
            confidence_score=0.0,
            last_updated=datetime.now()
        )
    
    def calculate_patient_feedback_score(self, summary: FeedbackSummary) -> Dict[str, float]:
        """
        Calculate patient feedback score for QuXAT integration (0-15 points)
        
        Args:
            summary: FeedbackSummary object
            
        Returns:
            Dictionary with detailed scoring breakdown
        """
        if summary.total_reviews == 0:
            return {
                'patient_feedback_score': 0.0,
                'volume_score': 0.0,
                'sentiment_score': 0.0,
                'rating_score': 0.0,
                'trend_score': 0.0,
                'confidence_multiplier': 0.0
            }
        
        # Volume Score (0-4 points) - Based on number of reviews
        if summary.total_reviews >= 100:
            volume_score = 4.0
        elif summary.total_reviews >= 50:
            volume_score = 3.0
        elif summary.total_reviews >= 20:
            volume_score = 2.0
        elif summary.total_reviews >= 10:
            volume_score = 1.0
        else:
            volume_score = 0.5
        
        # Sentiment Score (0-5 points) - Based on overall sentiment
        # Convert sentiment (-1 to 1) to score (0 to 5)
        sentiment_score = max(0, (summary.sentiment_score + 1) * 2.5)
        
        # Rating Score (0-4 points) - Based on average rating
        if summary.average_rating > 0:
            rating_score = (summary.average_rating / 5.0) * 4.0
        else:
            rating_score = sentiment_score * 0.8  # Use sentiment if no ratings
        
        # Trend Score (0-2 points) - Based on recent trend
        trend_scores = {
            'improving': 2.0,
            'stable': 1.0,
            'declining': 0.0
        }
        trend_score = trend_scores.get(summary.recent_trend, 1.0)
        
        # Base score
        base_score = volume_score + sentiment_score + rating_score + trend_score
        
        # Apply confidence multiplier
        final_score = base_score * summary.confidence_score
        
        # Cap at 15 points
        final_score = min(final_score, 15.0)
        
        return {
            'patient_feedback_score': round(final_score, 2),
            'volume_score': round(volume_score, 2),
            'sentiment_score': round(sentiment_score, 2),
            'rating_score': round(rating_score, 2),
            'trend_score': round(trend_score, 2),
            'confidence_multiplier': round(summary.confidence_score, 2)
        }
    
    # Simulation methods for demonstration (replace with real scraping in production)
    def _generate_simulated_google_reviews(self, org_name: str) -> List[Dict]:
        """Generate simulated Google reviews for demonstration"""
        import random
        
        positive_reviews = [
            "Excellent care and professional staff. Highly recommend this hospital.",
            "Great experience with the medical team. Clean facilities and efficient service.",
            "Outstanding treatment and compassionate doctors. Thank you for everything.",
            "Professional healthcare with modern equipment. Very satisfied with the care.",
            "Exceptional service and knowledgeable staff. Will definitely return."
        ]
        
        negative_reviews = [
            "Long waiting times and poor communication from staff.",
            "Disappointing experience with unprofessional behavior.",
            "Overpriced services and inadequate facilities.",
            "Poor customer service and lack of attention to patients.",
            "Unsatisfactory treatment and rude staff members."
        ]
        
        neutral_reviews = [
            "Average experience. Nothing exceptional but adequate care.",
            "Standard healthcare service. Could be better but acceptable.",
            "Decent facilities but room for improvement in service quality.",
            "Okay experience overall. Some good points and some areas to improve."
        ]
        
        reviews = []
        num_reviews = random.randint(15, 40)
        
        for i in range(num_reviews):
            # 60% positive, 25% neutral, 15% negative
            rand = random.random()
            if rand < 0.6:
                text = random.choice(positive_reviews)
                rating = random.uniform(4.0, 5.0)
            elif rand < 0.85:
                text = random.choice(neutral_reviews)
                rating = random.uniform(2.5, 4.0)
            else:
                text = random.choice(negative_reviews)
                rating = random.uniform(1.0, 2.5)
            
            reviews.append({
                'text': text,
                'rating': round(rating, 1),
                'date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'author': f'User{i+1}'
            })
        
        return reviews
    
    def _generate_simulated_facebook_reviews(self, org_name: str) -> List[Dict]:
        """Generate simulated Facebook reviews"""
        import random
        
        reviews = []
        num_reviews = random.randint(8, 25)
        
        sample_texts = [
            "Had a great experience at this hospital. Staff was very helpful.",
            "Thank you for the excellent care during my stay.",
            "Could improve on waiting times but overall good service.",
            "Not satisfied with the treatment received. Expected better.",
            "Wonderful medical team and clean environment."
        ]
        
        for i in range(num_reviews):
            reviews.append({
                'text': random.choice(sample_texts),
                'rating': random.uniform(1.0, 5.0) if random.random() < 0.7 else None,
                'date': datetime.now() - timedelta(days=random.randint(1, 180)),
                'author': f'FacebookUser{i+1}'
            })
        
        return reviews
    
    def _generate_simulated_twitter_mentions(self, org_name: str) -> List[Dict]:
        """Generate simulated Twitter mentions"""
        import random
        
        tweets = []
        num_tweets = random.randint(5, 15)
        
        sample_tweets = [
            f"Great experience at {org_name}! Professional staff and excellent care. #healthcare",
            f"Disappointed with the service at {org_name}. Long wait times and poor communication.",
            f"Thank you {org_name} for the wonderful treatment. Highly recommend! #hospital",
            f"Average experience at {org_name}. Could be better but acceptable care.",
            f"Outstanding medical team at {org_name}. Very satisfied with the treatment."
        ]
        
        for i in range(num_tweets):
            tweets.append({
                'text': random.choice(sample_tweets),
                'date': datetime.now() - timedelta(days=random.randint(1, 90)),
                'author': f'@TwitterUser{i+1}',
                'verified': random.random() < 0.1
            })
        
        return tweets
    
    def _generate_simulated_healthgrades_reviews(self, org_name: str) -> List[Dict]:
        """Generate simulated Healthgrades reviews"""
        import random
        
        reviews = []
        num_reviews = random.randint(10, 30)
        
        for i in range(num_reviews):
            rating = random.uniform(2.0, 5.0)
            if rating >= 4.0:
                text = "Excellent medical care and professional staff. Highly recommend."
            elif rating >= 3.0:
                text = "Good healthcare service with room for improvement."
            else:
                text = "Below average experience. Expected better quality care."
            
            reviews.append({
                'text': text,
                'rating': round(rating, 1),
                'date': datetime.now() - timedelta(days=random.randint(1, 270)),
                'author': f'Patient{i+1}'
            })
        
        return reviews
    
    def _generate_simulated_yelp_reviews(self, org_name: str) -> List[Dict]:
        """Generate simulated Yelp reviews"""
        import random
        
        reviews = []
        num_reviews = random.randint(5, 20)
        
        for i in range(num_reviews):
            rating = random.uniform(1.0, 5.0)
            if rating >= 4.0:
                text = "Great hospital with excellent service and care."
            elif rating >= 3.0:
                text = "Decent healthcare facility. Average experience overall."
            else:
                text = "Poor service and unprofessional staff. Not recommended."
            
            reviews.append({
                'text': text,
                'rating': round(rating, 1),
                'date': datetime.now() - timedelta(days=random.randint(1, 200)),
                'author': f'YelpUser{i+1}'
            })
        
        return reviews

# Example usage
if __name__ == "__main__":
    scraper = AutomatedFeedbackScraper()
    
    # Test with a sample organization
    summary = scraper.scrape_organization_feedback("Apollo Hospital", "Chennai")
    scores = scraper.calculate_patient_feedback_score(summary)
    
    print(f"\nAutomated Patient Feedback Analysis for {summary.organization_name}")
    print(f"Total Reviews: {summary.total_reviews}")
    print(f"Average Rating: {summary.average_rating:.1f}/5.0")
    print(f"Sentiment Score: {summary.sentiment_score:.2f}")
    print(f"Recent Trend: {summary.recent_trend}")
    print(f"Confidence Score: {summary.confidence_score:.2f}")
    print(f"Platform Breakdown: {summary.platform_breakdown}")
    print(f"\nQuXAT Patient Feedback Score: {scores['patient_feedback_score']:.1f}/15")
    print(f"Score Breakdown:")
    print(f"  - Volume Score: {scores['volume_score']:.1f}")
    print(f"  - Sentiment Score: {scores['sentiment_score']:.1f}")
    print(f"  - Rating Score: {scores['rating_score']:.1f}")
    print(f"  - Trend Score: {scores['trend_score']:.1f}")
    print(f"  - Confidence Multiplier: {scores['confidence_multiplier']:.2f}")