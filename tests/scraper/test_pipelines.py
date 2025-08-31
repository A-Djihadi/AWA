"""
Tests pour les pipelines de traitement
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from tjm_scraper.pipelines import ValidationPipeline, DuplicatesPipeline, SupabasePipeline
from tjm_scraper.items import TjmOfferItem


class TestValidationPipeline:
    """Tests pour le pipeline de validation"""
    
    def setup_method(self):
        self.pipeline = ValidationPipeline()
        self.spider = Mock()
    
    def test_valid_item(self):
        """Test avec un item valide"""
        item = TjmOfferItem(
            source='test_source',
            source_id='123',
            title='Test Job',
            tjm_min=400,
            tjm_max=600,
            technologies=['Python', 'Django']
        )
        
        result = self.pipeline.process_item(item, self.spider)
        
        assert result == item
        assert 'scraped_at' in result
        assert result['technologies'] == ['Python', 'Django']
    
    def test_missing_required_field(self):
        """Test avec champ obligatoire manquant"""
        item = TjmOfferItem(
            source='test_source',
            # source_id manquant
            title='Test Job'
        )
        
        with pytest.raises(ValueError, match="Missing required field: source_id"):
            self.pipeline.process_item(item, self.spider)
    
    def test_invalid_tjm_negative(self):
        """Test avec TJM négatif"""
        item = TjmOfferItem(
            source='test_source',
            source_id='123',
            title='Test Job',
            tjm_min=-100
        )
        
        with pytest.raises(ValueError, match="Invalid tjm_min"):
            self.pipeline.process_item(item, self.spider)
    
    def test_invalid_tjm_range(self):
        """Test avec fourchette TJM invalide"""
        item = TjmOfferItem(
            source='test_source',
            source_id='123',
            title='Test Job',
            tjm_min=600,
            tjm_max=400
        )
        
        with pytest.raises(ValueError, match="tjm_min.*> tjm_max"):
            self.pipeline.process_item(item, self.spider)
    
    def test_normalize_technologies(self):
        """Test normalisation des technologies"""
        item = TjmOfferItem(
            source='test_source',
            source_id='123',
            title='Test Job',
            technologies=['python', 'DJANGO', ' React ', 'react', '']
        )
        
        result = self.pipeline.process_item(item, self.spider)
        
        # Devrait supprimer les doublons et normaliser
        expected_techs = ['Python', 'Django', 'React']
        assert sorted(result['technologies']) == sorted(expected_techs)


class TestDuplicatesPipeline:
    """Tests pour le pipeline de déduplication"""
    
    def setup_method(self):
        self.pipeline = DuplicatesPipeline()
        self.spider = Mock()
    
    def test_unique_items(self):
        """Test avec des items uniques"""
        item1 = TjmOfferItem(source='source1', source_id='123', title='Job 1')
        item2 = TjmOfferItem(source='source1', source_id='456', title='Job 2')
        
        result1 = self.pipeline.process_item(item1, self.spider)
        result2 = self.pipeline.process_item(item2, self.spider)
        
        assert result1 == item1
        assert result2 == item2
    
    def test_duplicate_items(self):
        """Test avec des items dupliqués"""
        item1 = TjmOfferItem(source='source1', source_id='123', title='Job 1')
        item2 = TjmOfferItem(source='source1', source_id='123', title='Job 1 Updated')
        
        result1 = self.pipeline.process_item(item1, self.spider)
        result2 = self.pipeline.process_item(item2, self.spider)
        
        assert result1 == item1
        assert result2 is None  # Dupliqué, doit être filtré


class TestSupabasePipeline:
    """Tests pour le pipeline Supabase"""
    
    def setup_method(self):
        self.pipeline = SupabasePipeline(
            supabase_url='https://test.supabase.co',
            supabase_key='test_key'
        )
        self.spider = Mock()
        self.spider.logger = Mock()
    
    @patch('tjm_scraper.pipelines.create_client')
    def test_open_spider_success(self, mock_create_client):
        """Test initialisation réussie du client Supabase"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        self.pipeline.open_spider(self.spider)
        
        assert self.pipeline.client == mock_client
        mock_create_client.assert_called_once_with(
            'https://test.supabase.co',
            'test_key'
        )
    
    @patch('tjm_scraper.pipelines.create_client')
    def test_open_spider_failure(self, mock_create_client):
        """Test échec d'initialisation du client"""
        mock_create_client.side_effect = Exception("Connection failed")
        
        self.pipeline.open_spider(self.spider)
        
        assert self.pipeline.client is None
        self.spider.logger.error.assert_called()
    
    def test_process_item_no_client(self):
        """Test traitement sans client initialisé"""
        item = TjmOfferItem(source='test', source_id='123', title='Test')
        
        result = self.pipeline.process_item(item, self.spider)
        
        assert result == item  # Item retourné inchangé
    
    def test_process_item_with_client(self):
        """Test traitement avec client Supabase"""
        # Setup mock client
        mock_client = Mock()
        mock_table = Mock()
        mock_upsert = Mock()
        mock_execute = Mock()
        
        mock_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_upsert
        mock_upsert.execute.return_value.data = [{'id': 'test-id'}]
        
        self.pipeline.client = mock_client
        
        item = TjmOfferItem(
            source='test_source',
            source_id='123',
            title='Test Job',
            tjm_min=500,
            technologies=['Python']
        )
        
        result = self.pipeline.process_item(item, self.spider)
        
        # Vérifier les appels
        mock_client.table.assert_called_with('offers')
        mock_table.upsert.assert_called_once()
        
        # Vérifier les données envoyées
        upsert_call_args = mock_table.upsert.call_args[0][0]
        assert upsert_call_args['source'] == 'test_source'
        assert upsert_call_args['source_id'] == '123'
        assert upsert_call_args['title'] == 'Test Job'
        assert upsert_call_args['tjm_min'] == 500
        
        assert result == item
    
    def test_process_item_database_error(self):
        """Test gestion d'erreur base de données"""
        mock_client = Mock()
        mock_client.table.side_effect = Exception("Database error")
        
        self.pipeline.client = mock_client
        
        item = TjmOfferItem(source='test', source_id='123', title='Test')
        
        result = self.pipeline.process_item(item, self.spider)
        
        # L'item doit être retourné même en cas d'erreur
        assert result == item
        self.spider.logger.error.assert_called()


class TestPipelineIntegration:
    """Tests d'intégration des pipelines"""
    
    def test_pipeline_chain(self):
        """Test chaîne complète des pipelines"""
        # Setup
        validation_pipeline = ValidationPipeline()
        duplicates_pipeline = DuplicatesPipeline()
        spider = Mock()
        
        # Item valide
        item = TjmOfferItem(
            source='test_source',
            source_id='123',
            title='Test Job',
            tjm_min=400,
            tjm_max=600,
            technologies=['python', 'django']
        )
        
        # Passage dans la chaîne
        result = validation_pipeline.process_item(item, spider)
        result = duplicates_pipeline.process_item(result, spider)
        
        # Vérifications
        assert result is not None
        assert result['technologies'] == ['Python', 'Django']
        assert 'scraped_at' in result
        
        # Test doublon
        duplicate_item = TjmOfferItem(
            source='test_source',
            source_id='123',  # Même ID
            title='Test Job Updated'
        )
        
        duplicate_result = duplicates_pipeline.process_item(duplicate_item, spider)
        assert duplicate_result is None  # Filtré comme doublon
