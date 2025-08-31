"""
Tests unitaires pour les spiders de scraping
"""
import pytest
from unittest.mock import Mock, patch
from scrapy.http import HtmlResponse, Request
from tjm_scraper.spiders.freelance_informatique import FreelanceInformatiqueSpider
from tjm_scraper.items import TjmOfferItem


class TestFreelanceInformatiqueSpider:
    """Tests pour le spider Freelance Informatique"""
    
    def setup_method(self):
        """Setup before each test"""
        self.spider = FreelanceInformatiqueSpider()
    
    def create_response(self, url, html_content):
        """Helper to create Scrapy response"""
        request = Request(url=url)
        return HtmlResponse(
            url=url,
            request=request,
            body=html_content.encode('utf-8'),
            encoding='utf-8'
        )
    
    def test_extract_tjm_simple(self):
        """Test extraction TJM simple"""
        response = self.create_response(
            'https://example.com/mission/123',
            '<div>TJM: 500€</div>'
        )
        
        tjm_info = self.spider.extract_tjm(response)
        
        assert tjm_info['min'] == 500
        assert tjm_info['max'] == 500
        assert tjm_info['currency'] == 'EUR'
    
    def test_extract_tjm_range(self):
        """Test extraction TJM avec fourchette"""
        response = self.create_response(
            'https://example.com/mission/123',
            '<div>TJM: 400€ - 600€</div>'
        )
        
        tjm_info = self.spider.extract_tjm(response)
        
        assert tjm_info['min'] == 400
        assert tjm_info['max'] == 600
        assert tjm_info['currency'] == 'EUR'
    
    def test_extract_tjm_with_k(self):
        """Test extraction TJM avec notation en milliers"""
        response = self.create_response(
            'https://example.com/mission/123',
            '<div>TJM: 0.5k€</div>'
        )
        
        tjm_info = self.spider.extract_tjm(response)
        
        assert tjm_info['min'] == 500
        assert tjm_info['max'] == 500
    
    def test_extract_tjm_not_found(self):
        """Test quand aucun TJM n'est trouvé"""
        response = self.create_response(
            'https://example.com/mission/123',
            '<div>Mission sans TJM mentionné</div>'
        )
        
        tjm_info = self.spider.extract_tjm(response)
        
        assert tjm_info['min'] is None
        assert tjm_info['max'] is None
        assert tjm_info['currency'] == 'EUR'
    
    def test_extract_technologies(self):
        """Test extraction des technologies"""
        response = self.create_response(
            'https://example.com/mission/123',
            '<div>Mission React JavaScript Python Docker</div>'
        )
        
        technologies = self.spider.extract_technologies(response)
        
        expected_techs = ['React', 'Javascript', 'Python', 'Docker']
        for tech in expected_techs:
            assert tech in technologies
    
    def test_extract_seniority_senior(self):
        """Test extraction séniorité senior"""
        response = self.create_response(
            'https://example.com/mission/123',
            '<div>Développeur senior expérimenté</div>'
        )
        
        seniority = self.spider.extract_seniority(response)
        assert seniority == 'senior'
    
    def test_extract_seniority_junior(self):
        """Test extraction séniorité junior"""
        response = self.create_response(
            'https://example.com/mission/123',
            '<div>Développeur junior débutant</div>'
        )
        
        seniority = self.spider.extract_seniority(response)
        assert seniority == 'junior'
    
    def test_extract_seniority_none(self):
        """Test quand aucune séniorité n'est trouvée"""
        response = self.create_response(
            'https://example.com/mission/123',
            '<div>Développeur</div>'
        )
        
        seniority = self.spider.extract_seniority(response)
        assert seniority is None
    
    def test_extract_remote_policy(self):
        """Test extraction politique télétravail"""
        test_cases = [
            ('<div>100% remote</div>', 'remote'),
            ('<div>télétravail partiel</div>', 'hybrid'),
            ('<div>sur site uniquement</div>', 'on-site'),
            ('<div>flexible</div>', 'flexible'),
        ]
        
        for html, expected in test_cases:
            response = self.create_response('https://example.com/mission/123', html)
            result = self.spider.extract_remote_policy(response)
            assert result == expected
    
    def test_extract_source_id_numeric(self):
        """Test extraction ID source depuis URL avec numéro"""
        url = 'https://example.com/mission/12345/details'
        source_id = self.spider.extract_source_id(url)
        assert source_id == '12345'
    
    def test_extract_source_id_slug(self):
        """Test extraction ID source depuis URL avec slug"""
        url = 'https://example.com/mission/react-developer-paris'
        source_id = self.spider.extract_source_id(url)
        assert source_id == 'react-developer-paris'
    
    def test_clean_text(self):
        """Test nettoyage du texte"""
        # Texte avec espaces multiples
        result = self.spider.clean_text('  Test   avec   espaces  ')
        assert result == 'Test avec espaces'
        
        # Texte None
        result = self.spider.clean_text(None)
        assert result is None
        
        # Texte vide
        result = self.spider.clean_text('   ')
        assert result is None
    
    @patch('tjm_scraper.spiders.freelance_informatique.TjmOfferItem')
    def test_parse_mission_complete(self, mock_item):
        """Test parsing complet d'une mission"""
        html_content = """
        <html>
            <h1>Développeur React Senior</h1>
            <div class="company-name">TechCorp</div>
            <div class="mission-description">
                Mission de développement React avec TypeScript.
                TJM: 600€
                Technologies: React, TypeScript, Node.js
                Senior requis
                100% remote
            </div>
        </html>
        """
        
        response = self.create_response(
            'https://example.com/mission/123',
            html_content
        )
        
        # Mock l'item
        mock_item_instance = Mock()
        mock_item.return_value = mock_item_instance
        
        # Exécuter le parsing
        result = list(self.spider.parse_mission(response))
        
        # Vérifier qu'un item a été créé
        assert len(result) == 1
        assert result[0] == mock_item_instance
        
        # Vérifier que l'item a été appelé avec les bons paramètres
        mock_item.assert_called_once()
        call_args = mock_item.call_args[1]  # kwargs
        
        assert call_args['source'] == 'freelance_informatique'
        assert call_args['title'] == 'Développeur React Senior'
        assert call_args['company'] == 'TechCorp'
        assert call_args['tjm_min'] == 600
        assert call_args['tjm_max'] == 600
        assert 'React' in call_args['technologies']
        assert call_args['seniority_level'] == 'senior'
        assert call_args['remote_policy'] == 'remote'


class TestTjmExtractionPatterns:
    """Tests spécifiques pour les patterns d'extraction TJM"""
    
    def setup_method(self):
        self.spider = FreelanceInformatiqueSpider()
    
    def test_various_tjm_patterns(self):
        """Test différents patterns de TJM"""
        test_cases = [
            ('TJM: 500€', 500, 500),
            ('TJM 400-600€', 400, 600),
            ('Taux journalier: 550€', 550, 550),
            ('500€/jour', 500, 500),
            ('400 à 600 euros par jour', 400, 600),
            ('TJM de 0.5k€', 500, 500),
            ('Budget: 450€ par jour', 450, 450),
        ]
        
        for text, expected_min, expected_max in test_cases:
            response = Mock()
            response.css.return_value.getall.return_value = [text]
            
            tjm_info = self.spider.extract_tjm(response)
            
            assert tjm_info['min'] == expected_min, f"Failed for: {text}"
            assert tjm_info['max'] == expected_max, f"Failed for: {text}"
    
    def test_invalid_tjm_patterns(self):
        """Test patterns TJM invalides"""
        invalid_cases = [
            'Pas de TJM mentionné',
            'Contact pour tarif',
            'TJM: négociable',
            'Salaire: 50k€/an',
        ]
        
        for text in invalid_cases:
            response = Mock()
            response.css.return_value.getall.return_value = [text]
            
            tjm_info = self.spider.extract_tjm(response)
            
            assert tjm_info['min'] is None, f"Should not extract TJM from: {text}"
            assert tjm_info['max'] is None, f"Should not extract TJM from: {text}"
