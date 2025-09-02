"""
Tests unitaires pour les spiders AWA
Tests pour freework et collective_work spiders
"""
import pytest
from unittest.mock import Mock, patch
from scrapy.http import HtmlResponse, Request
from tjm_scraper.spiders.freework import FreeworkSpider
from tjm_scraper.spiders.collective_work import CollectiveWorkSpider
from tjm_scraper.items import TjmOfferItem


class TestFreeworkSpider:
    """Tests pour le spider FreeWork"""
    
    def setup_method(self):
        """Setup before each test"""
        self.spider = FreeworkSpider()
    
    def create_response(self, url, html_content):
        """Helper to create Scrapy response"""
        request = Request(url=url)
        return HtmlResponse(
            url=url,
            request=request,
            body=html_content.encode('utf-8'),
            encoding='utf-8'
        )
    
    def test_spider_name(self):
        """Test spider name"""
        assert self.spider.name == 'freework'
    
    def test_allowed_domains(self):
        """Test allowed domains"""
        assert 'freework.fr' in self.spider.allowed_domains
    
    def test_start_urls(self):
        """Test start URLs are configured"""
        assert len(self.spider.start_urls) > 0
        assert any('freework.fr' in url for url in self.spider.start_urls)
    
    def test_extract_tjm_simple(self):
        """Test extraction TJM simple"""
        html = '''
        <div class="mission-card">
            <div class="tjm">TJM: 500€</div>
        </div>
        '''
        response = self.create_response('https://www.freework.fr/mission/123', html)
        
        tjm_info = self.spider.extract_tjm(response)
        
        assert tjm_info['min'] == 500
        assert tjm_info['max'] == 500
        assert tjm_info['currency'] == 'EUR'
    
    def test_extract_tjm_range(self):
        """Test extraction TJM avec fourchette"""
        html = '''
        <div class="mission-card">
            <div class="tjm">TJM: 400€ - 600€</div>
        </div>
        '''
        response = self.create_response('https://www.freework.fr/mission/123', html)
        
        tjm_info = self.spider.extract_tjm(response)
        
        assert tjm_info['min'] == 400
        assert tjm_info['max'] == 600
        assert tjm_info['currency'] == 'EUR'
    
    def test_extract_technologies(self):
        """Test extraction des technologies"""
        html = '''
        <div class="mission-details">
            <p>Technologies: React, JavaScript, Python, Docker</p>
        </div>
        '''
        response = self.create_response('https://www.freework.fr/mission/123', html)
        
        technologies = self.spider.extract_technologies(response)
        
        expected_techs = ['React', 'Javascript', 'Python', 'Docker']
        for tech in expected_techs:
            assert tech in technologies
    
    def test_extract_seniority_senior(self):
        """Test extraction séniorité senior"""
        html = '''
        <div class="mission-description">
            <p>Recherche développeur senior avec 5+ années d'expérience</p>
        </div>
        '''
        response = self.create_response('https://www.freework.fr/mission/123', html)
        
        seniority = self.spider.extract_seniority(response)
        assert seniority == 'senior'
    
    def test_extract_seniority_junior(self):
        """Test extraction séniorité junior"""
        html = '''
        <div class="mission-description">
            <p>Poste idéal pour junior ou débutant</p>
        </div>
        '''
        response = self.create_response('https://www.freework.fr/mission/123', html)
        
        seniority = self.spider.extract_seniority(response)
        assert seniority == 'junior'


class TestCollectiveWorkSpider:
    """Tests pour le spider Collective.work"""
    
    def setup_method(self):
        """Setup before each test"""
        self.spider = CollectiveWorkSpider()
    
    def create_response(self, url, html_content):
        """Helper to create Scrapy response"""
        request = Request(url=url)
        return HtmlResponse(
            url=url,
            request=request,
            body=html_content.encode('utf-8'),
            encoding='utf-8'
        )
    
    def test_spider_name(self):
        """Test spider name"""
        assert self.spider.name == 'collective_work'
    
    def test_allowed_domains(self):
        """Test allowed domains"""
        assert 'collective.work' in self.spider.allowed_domains
    
    def test_start_urls(self):
        """Test start URLs are configured"""
        assert len(self.spider.start_urls) > 0
        assert any('collective.work' in url for url in self.spider.start_urls)
    
    def test_extract_tjm_from_salary_range(self):
        """Test extraction TJM à partir d'un range de salaire"""
        html = '''
        <div class="job-card">
            <div class="salary">400€ - 800€ / jour</div>
        </div>
        '''
        response = self.create_response('https://collective.work/jobs/123', html)
        
        tjm_info = self.spider.extract_tjm(response)
        
        assert tjm_info['min'] == 400
        assert tjm_info['max'] == 800
        assert tjm_info['currency'] == 'EUR'
    
    def test_extract_tjm_single_value(self):
        """Test extraction TJM valeur unique"""
        html = '''
        <div class="job-card">
            <div class="salary">650€/jour</div>
        </div>
        '''
        response = self.create_response('https://collective.work/jobs/123', html)
        
        tjm_info = self.spider.extract_tjm(response)
        
        assert tjm_info['min'] == 650
        assert tjm_info['max'] == 650
        assert tjm_info['currency'] == 'EUR'
    
    def test_extract_technologies_from_tags(self):
        """Test extraction technologies depuis les tags"""
        html = '''
        <div class="job-tags">
            <span class="tag">React</span>
            <span class="tag">TypeScript</span>
            <span class="tag">Node.js</span>
            <span class="tag">MongoDB</span>
        </div>
        '''
        response = self.create_response('https://collective.work/jobs/123', html)
        
        technologies = self.spider.extract_technologies(response)
        
        expected_techs = ['React', 'Typescript', 'Node.js', 'MongoDB']
        for tech in expected_techs:
            assert tech in technologies
    
    def test_parse_job_card_creates_item(self):
        """Test que parse_job_card crée un TjmOfferItem valide"""
        html = '''
        <div class="job-card">
            <h3>Développeur Full Stack React/Node.js</h3>
            <div class="salary">500€ - 700€ / jour</div>
            <div class="location">Paris</div>
            <div class="job-tags">
                <span class="tag">React</span>
                <span class="tag">Node.js</span>
            </div>
            <div class="description">Mission de développement d'une application web</div>
        </div>
        '''
        response = self.create_response('https://collective.work/jobs/123', html)
        
        # Mock la création d'item
        with patch.object(self.spider, 'create_item') as mock_create_item:
            mock_item = TjmOfferItem()
            mock_create_item.return_value = mock_item
            
            result = list(self.spider.parse_job_card(response))
            
            assert len(result) == 1
            mock_create_item.assert_called_once()


class TestSharedSpiderFunctionality:
    """Tests pour les fonctionnalités partagées entre spiders"""
    
    def test_technology_normalization(self):
        """Test la normalisation des technologies"""
        from tjm_scraper.spiders.freework import FreeworkSpider
        
        spider = FreeworkSpider()
        
        # Test normalisation JavaScript variations
        assert spider.normalize_technology('javascript') == 'Javascript'
        assert spider.normalize_technology('JS') == 'Javascript'
        assert spider.normalize_technology('VueJS') == 'Vue.js'
        assert spider.normalize_technology('reactjs') == 'React'
    
    def test_tjm_parsing_edge_cases(self):
        """Test parsing TJM cas limites"""
        from tjm_scraper.spiders.freework import FreeworkSpider
        
        spider = FreeworkSpider()
        
        # Test différents formats
        assert spider.parse_tjm_amount('500€') == 500
        assert spider.parse_tjm_amount('0.5k€') == 500
        assert spider.parse_tjm_amount('1.2k€') == 1200
        assert spider.parse_tjm_amount('invalide') is None
    
    def test_seniority_detection_keywords(self):
        """Test détection séniorité avec mots-clés"""
        from tjm_scraper.spiders.collective_work import CollectiveWorkSpider
        
        spider = CollectiveWorkSpider()
        
        # Tests pour différents niveaux
        text_senior = "Développeur senior avec 8 ans d'expérience"
        assert spider.detect_seniority_from_text(text_senior) == 'senior'
        
        text_junior = "Poste parfait pour un développeur junior débutant"
        assert spider.detect_seniority_from_text(text_junior) == 'junior'
        
        text_lead = "Tech lead recherché pour équipe de 5 développeurs"
        assert spider.detect_seniority_from_text(text_lead) == 'senior'


@pytest.fixture
def mock_response():
    """Fixture pour créer des réponses de test"""
    def _create_response(url, html_content):
        request = Request(url=url)
        return HtmlResponse(
            url=url,
            request=request,
            body=html_content.encode('utf-8'),
            encoding='utf-8'
        )
    return _create_response


@pytest.fixture
def sample_mission_html():
    """Fixture avec HTML d'exemple pour une mission"""
    return '''
    <div class="mission-card">
        <h2>Développeur Full Stack React/Node.js</h2>
        <div class="tjm-info">
            <span>TJM: 500€ - 700€</span>
        </div>
        <div class="location">Paris (75)</div>
        <div class="duration">6 mois</div>
        <div class="technologies">
            <span class="tech-tag">React</span>
            <span class="tech-tag">Node.js</span>
            <span class="tech-tag">MongoDB</span>
            <span class="tech-tag">TypeScript</span>
        </div>
        <div class="description">
            <p>Recherche développeur senior pour mission de refonte d'application web</p>
        </div>
    </div>
    '''
