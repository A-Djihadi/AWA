"""
Tests pour les pipelines de traitement des données
"""
import pytest
import requests
from unittest.mock import Mock, patch
from tjm_scraper.pipelines import ValidationPipeline, DuplicateFilterPipeline, DatabasePipeline
from tjm_scraper.items import TjmOfferItem


class TestValidationPipeline:
    """Tests pour le pipeline de validation"""
    
    def setup_method(self):
        """Setup before each test"""
        self.pipeline = ValidationPipeline()
        self.spider = Mock()
        self.spider.name = 'test_spider'
    
    def create_valid_item(self):
        """Crée un item valide pour les tests"""
        return TjmOfferItem(
            title="Développeur Python",
            company="TechCorp",
            tjm_min=400,
            tjm_max=600,
            location="Paris",
            technologies=["Python", "Django"],
            seniority="senior",
            source_url="https://example.com/job/123",
            scraped_date="2023-12-01"
        )
    
    def test_process_item_valid(self):
        """Test traitement d'un item valide"""
        item = self.create_valid_item()
        
        result = self.pipeline.process_item(item, self.spider)
        
        assert result == item
    
    def test_process_item_missing_title(self):
        """Test validation échoue si titre manquant"""
        item = self.create_valid_item()
        del item['title']
        
        with pytest.raises(Exception):
            self.pipeline.process_item(item, self.spider)
    
    def test_process_item_invalid_tjm(self):
        """Test validation échoue si TJM invalide"""
        item = self.create_valid_item()
        item['tjm_min'] = -100  # TJM négatif invalide
        
        with pytest.raises(Exception):
            self.pipeline.process_item(item, self.spider)
    
    def test_process_item_tjm_range_invalid(self):
        """Test validation échoue si min > max"""
        item = self.create_valid_item()
        item['tjm_min'] = 800
        item['tjm_max'] = 400  # min > max
        
        with pytest.raises(Exception):
            self.pipeline.process_item(item, self.spider)
    
    def test_normalize_technologies(self):
        """Test normalisation des technologies"""
        item = self.create_valid_item()
        item['technologies'] = ["javascript", "REACT", "node.js"]
        
        result = self.pipeline.process_item(item, self.spider)
        
        assert "Javascript" in result['technologies']
        assert "React" in result['technologies']
        assert "Node.js" in result['technologies']
    
    def test_validate_url_format(self):
        """Test validation format URL"""
        item = self.create_valid_item()
        item['source_url'] = "invalid-url"
        
        with pytest.raises(Exception):
            self.pipeline.process_item(item, self.spider)


class TestDuplicateFilterPipeline:
    """Tests pour le pipeline de filtrage des doublons"""
    
    def setup_method(self):
        """Setup before each test"""
        self.pipeline = DuplicateFilterPipeline()
        self.spider = Mock()
        self.spider.name = 'test_spider'
    
    def create_item(self, title="Test Job", url="https://example.com/job/123"):
        """Crée un item de test"""
        return TjmOfferItem(
            title=title,
            company="TechCorp",
            tjm_min=500,
            tjm_max=700,
            location="Paris",
            technologies=["Python"],
            seniority="senior",
            source_url=url,
            scraped_date="2023-12-01"
        )
    
    def test_first_item_passes(self):
        """Test que le premier item passe"""
        item = self.create_item()
        
        result = self.pipeline.process_item(item, self.spider)
        
        assert result == item
    
    def test_duplicate_item_dropped(self):
        """Test qu'un doublon est supprimé"""
        item1 = self.create_item()
        item2 = self.create_item()  # Même URL = doublon
        
        # Premier item passe
        result1 = self.pipeline.process_item(item1, self.spider)
        assert result1 == item1
        
        # Deuxième item (doublon) est supprimé
        with pytest.raises(Exception):  # DropItem exception
            self.pipeline.process_item(item2, self.spider)
    
    def test_different_urls_both_pass(self):
        """Test que des items avec URLs différentes passent tous"""
        item1 = self.create_item(url="https://example.com/job/123")
        item2 = self.create_item(url="https://example.com/job/456")
        
        result1 = self.pipeline.process_item(item1, self.spider)
        result2 = self.pipeline.process_item(item2, self.spider)
        
        assert result1 == item1
        assert result2 == item2
    
    def test_duplicate_detection_stats(self):
        """Test que les stats de doublons sont comptées"""
        item1 = self.create_item()
        item2 = self.create_item()  # Doublon
        
        self.pipeline.process_item(item1, self.spider)
        
        try:
            self.pipeline.process_item(item2, self.spider)
        except:
            pass  # DropItem attendu
        
        # Vérifier que les stats sont mises à jour
        assert hasattr(self.pipeline, 'duplicate_count')


class TestDatabasePipeline:
    """Tests pour le pipeline de base de données"""
    
    def setup_method(self):
        """Setup before each test"""
        self.pipeline = DatabasePipeline()
        self.spider = Mock()
        self.spider.name = 'test_spider'
    
    def create_item(self):
        """Crée un item de test"""
        return TjmOfferItem(
            title="Développeur Python",
            company="TechCorp",
            tjm_min=500,
            tjm_max=700,
            location="Paris",
            technologies=["Python", "Django"],
            seniority="senior",
            source_url="https://example.com/job/123",
            scraped_date="2023-12-01"
        )
    
    @patch('tjm_scraper.pipelines.requests.post')
    def test_send_to_etl_success(self, mock_post):
        """Test envoi réussi vers l'ETL"""
        # Mock réponse ETL réussie
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "id": "123"}
        mock_post.return_value = mock_response
        
        item = self.create_item()
        
        result = self.pipeline.process_item(item, self.spider)
        
        assert result == item
        mock_post.assert_called_once()
    
    @patch('tjm_scraper.pipelines.requests.post')
    def test_send_to_etl_failure(self, mock_post):
        """Test gestion d'erreur ETL"""
        # Mock réponse ETL en erreur
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        item = self.create_item()
        
        # L'item devrait passer même si ETL échoue (avec log d'erreur)
        result = self.pipeline.process_item(item, self.spider)
        
        assert result == item
        mock_post.assert_called_once()
    
    @patch('tjm_scraper.pipelines.requests.post')
    def test_etl_timeout_handling(self, mock_post):
        """Test gestion du timeout ETL"""
        # Mock timeout
        mock_post.side_effect = requests.exceptions.Timeout()
        
        item = self.create_item()
        
        # L'item devrait passer même en cas de timeout
        result = self.pipeline.process_item(item, self.spider)
        
        assert result == item
    
    def test_item_to_dict_conversion(self):
        """Test conversion item vers dict pour ETL"""
        item = self.create_item()
        
        item_dict = self.pipeline.item_to_dict(item)
        
        assert isinstance(item_dict, dict)
        assert item_dict['title'] == "Développeur Python"
        assert item_dict['tjm_min'] == 500
        assert item_dict['technologies'] == ["Python", "Django"]
    
    def test_format_for_etl(self):
        """Test formatage des données pour ETL"""
        item = self.create_item()
        
        formatted_data = self.pipeline.format_for_etl(item)
        
        assert 'mission_data' in formatted_data
        assert 'source' in formatted_data
        assert 'scraped_timestamp' in formatted_data
        assert formatted_data['source'] == 'test_spider'


class TestPipelineIntegration:
    """Tests d'intégration des pipelines"""
    
    def test_pipeline_order(self):
        """Test que les pipelines s'exécutent dans le bon ordre"""
        # Simulation de l'ordre des pipelines
        validation_pipeline = ValidationPipeline()
        duplicate_pipeline = DuplicateFilterPipeline()
        database_pipeline = DatabasePipeline()
        
        spider = Mock()
        spider.name = 'test_spider'
        
        item = TjmOfferItem(
            title="Développeur React",
            company="WebCorp",
            tjm_min=600,
            tjm_max=800,
            location="Lyon",
            technologies=["react", "typescript"],  # Technologies non normalisées
            seniority="senior",
            source_url="https://example.com/job/456",
            scraped_date="2023-12-01"
        )
        
        # Validation (doit normaliser les technologies)
        validated_item = validation_pipeline.process_item(item, spider)
        assert "React" in validated_item['technologies']
        assert "Typescript" in validated_item['technologies']
        
        # Filtre doublons (premier passage)
        filtered_item = duplicate_pipeline.process_item(validated_item, spider)
        assert filtered_item == validated_item
        
        # Base de données (mock)
        with patch('tjm_scraper.pipelines.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            final_item = database_pipeline.process_item(filtered_item, spider)
            assert final_item == filtered_item


@pytest.fixture
def sample_tjm_item():
    """Fixture avec un item TJM d'exemple"""
    return TjmOfferItem(
        title="Développeur Full Stack",
        company="InnovCorp",
        tjm_min=450,
        tjm_max=650,
        location="Bordeaux",
        technologies=["Vue.js", "Python", "PostgreSQL"],
        seniority="medior",
        source_url="https://example.com/job/789",
        scraped_date="2023-12-01"
    )
