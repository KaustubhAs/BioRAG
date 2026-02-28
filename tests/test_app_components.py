"""
Tests for application components (CLI, UI, main)
"""
import pytest
import sys
import os
import networkx as nx
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from app.cli import CLI
from app.streamlit_app import initialize_system, create_interactive_graph
from main import main


class TestCLI:
    """Test CLI functionality."""

    @pytest.mark.unit
    def test_cli_initialization(self, sample_graph):
        """Test CLI initialization."""
        mock_rag = Mock()
        cli = CLI(mock_rag)

        assert cli.rag_system == mock_rag

    @pytest.mark.unit
    @patch('builtins.input')
    @patch('builtins.print')
    def test_cli_run_exit_command(self, mock_print, mock_input, sample_graph):
        """Test CLI exit command."""
        mock_rag = Mock()
        mock_input.return_value = 'exit'

        cli = CLI(mock_rag)
        cli.run()

        # Should call input once and then exit
        mock_input.assert_called_once()
        mock_print.assert_called()

    @pytest.mark.unit
    @patch('builtins.input')
    @patch('builtins.print')
    def test_cli_run_with_query(self, mock_print, mock_input, sample_graph):
        """Test CLI with actual query."""
        mock_rag = Mock()
        mock_rag.answer_query.return_value = "Diabetes symptoms include fever and fatigue."

        # First query, then exit
        mock_input.side_effect = ['What are diabetes symptoms?', 'exit']

        cli = CLI(mock_rag)
        cli.run()

        # Should process the query
        mock_rag.answer_query.assert_called_once_with(
            'What are diabetes symptoms?')
        assert mock_print.call_count >= 2  # At least query and response

    @pytest.mark.unit
    @patch('builtins.input')
    @patch('builtins.print')
    def test_cli_run_with_quit_command(self, mock_print, mock_input,
                                       sample_graph):
        """Test CLI quit command."""
        mock_rag = Mock()
        mock_input.return_value = 'quit'

        cli = CLI(mock_rag)
        cli.run()

        # Should exit on 'quit'
        mock_input.assert_called_once()


class TestStreamlitApp:
    """Test Streamlit app functionality."""

    @pytest.mark.unit
    @patch('app.streamlit_app.preprocess_data')
    @patch('app.streamlit_app.build_graph')
    @patch('app.streamlit_app.BiomedicalRAG')
    def test_initialize_system_success(self, mock_rag, mock_build,
                                       mock_preprocess, sample_data):
        """Test successful system initialization."""
        # Mock the dependencies
        mock_preprocess.return_value = (sample_data['diseases'],
                                        sample_data['symptoms'],
                                        sample_data['relationships'])

        mock_graph = Mock()
        mock_build.return_value = mock_graph

        mock_rag_instance = Mock()
        mock_rag.return_value = mock_rag_instance

        # Mock streamlit session state
        with patch.dict('app.streamlit_app.st.session_state', {}, clear=True):
            with patch('app.streamlit_app.st.spinner') as mock_spinner:
                with patch('app.streamlit_app.st.success') as mock_success:
                    result = initialize_system()

                    assert result is True
                    mock_success.assert_called_once()
                    msg = mock_success.call_args[0][0]
                    assert msg.startswith("System initialized successfully!")
                    assert "Data source:" in msg

    @pytest.mark.unit
    @patch('app.streamlit_app.preprocess_data')
    def test_initialize_system_missing_dataset(self, mock_preprocess):
        """Test system initialization with missing dataset."""
        with patch('app.streamlit_app.os.path.exists', return_value=False):
            with patch('app.streamlit_app.st.error') as mock_error:
                result = initialize_system()

                assert result is False
                mock_error.assert_called_once()

    @pytest.mark.unit
    @patch('app.streamlit_app.preprocess_data')
    def test_initialize_system_processing_error(self, mock_preprocess):
        """Test system initialization with processing error."""
        mock_preprocess.side_effect = Exception("Processing error")

        with patch('app.streamlit_app.os.path.exists', return_value=True):
            with patch('app.streamlit_app.st.error') as mock_error:
                result = initialize_system()

                assert result is False
                mock_error.assert_called_once()

    @pytest.mark.unit
    def test_create_interactive_graph(self, sample_graph):
        """Test interactive graph creation."""
        # Test with all nodes visible
        graph_obj = create_interactive_graph(sample_graph,
                                             show_diseases=True,
                                             show_symptoms=True)

        # Should return a Plotly figure object
        assert graph_obj is not None

    @pytest.mark.unit
    def test_create_interactive_graph_no_diseases(self, sample_graph):
        """Test graph creation with diseases hidden."""
        graph_obj = create_interactive_graph(sample_graph,
                                             show_diseases=False,
                                             show_symptoms=True)

        # Should still return a figure object
        assert graph_obj is not None

    @pytest.mark.unit
    def test_create_interactive_graph_with_search(self, sample_graph):
        """Test graph creation with search term."""
        graph_obj = create_interactive_graph(sample_graph,
                                             show_diseases=True,
                                             show_symptoms=True,
                                             search_term="diabetes")

        # Should return a figure object
        assert graph_obj is not None

    @pytest.mark.unit
    def test_create_interactive_graph_empty_graph(self):
        """Test graph creation with empty graph."""
        empty_graph = nx.Graph()
        graph_obj = create_interactive_graph(empty_graph)

        # Should handle empty graph gracefully
        assert graph_obj is None


class TestMainModule:
    """Test main module functionality."""

    @pytest.mark.unit
    @patch('subprocess.run')
    def test_main_ui_mode(self, mock_subprocess):
        """Test main function in UI mode."""
        with patch('sys.argv', ['main.py', '--mode', 'ui']):
            with patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_args = Mock()
                mock_args.mode = 'ui'
                mock_args.port = 8501
                mock_parse.return_value = mock_args

                # Mock subprocess to avoid actually launching Streamlit
                mock_subprocess.return_value = Mock()

                # Should not raise exceptions
                try:
                    main()
                except SystemExit:
                    pass  # Expected when subprocess is mocked

    @pytest.mark.unit
    @patch('os.path.exists')
    def test_main_cli_mode_missing_dataset(self, mock_exists):
        """Test main function in CLI mode with missing dataset."""
        mock_exists.return_value = False

        with patch('sys.argv', ['main.py', '--mode', 'cli']):
            with patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_args = Mock()
                mock_args.mode = 'cli'
                mock_parse.return_value = mock_args

                # Should handle missing dataset gracefully
                try:
                    main()
                except SystemExit:
                    pass  # Expected when dataset is missing

    # @pytest.mark.unit
    # @patch('sentence_transformers.SentenceTransformer')
    # @patch('knowledge_graph.data_processor.preprocess_data')
    # @patch('knowledge_graph.graph_builder.build_graph')
    # @patch('rag.biomedical_rag.BiomedicalRAG')
    # @patch('app.cli.CLI')
    # def test_main_cli_mode_success(self, mock_cli, mock_rag, mock_build, mock_preprocess, mock_sentence_transformer, sample_data):
    #     """Test main function in CLI mode with successful execution."""
    #     # Mock all dependencies
    #     mock_preprocess.return_value = (
    #         sample_data['diseases'],
    #         sample_data['symptoms'],
    #         sample_data['relationships']
    #     )

    #     mock_graph = Mock()
    #     mock_build.return_value = mock_graph

    #     mock_rag_instance = Mock()
    #     mock_rag.return_value = mock_rag_instance

    #     mock_cli_instance = Mock()
    #     mock_cli.return_value = mock_cli_instance

    #     with patch('os.path.exists', return_value=True):
    #         with patch('sys.argv', ['main.py', '--mode', 'cli']):
    #             with patch('argparse.ArgumentParser.parse_args') as mock_parse:
    #                 mock_args = Mock()
    #                 mock_args.mode = 'cli'
    #                 mock_parse.return_value = mock_args

    #                 # Should execute CLI successfully
    #                 try:
    #                     main()
    #                 except SystemExit:
    #                     pass  # Expected when CLI.run() is mocked


@pytest.mark.integration
class TestAppIntegration:
    """Integration tests for application components."""

    def test_cli_rag_integration(self, sample_graph):
        """Test CLI integration with RAG system."""
        mock_rag = Mock()
        mock_rag.answer_query.return_value = "Test response"

        cli = CLI(mock_rag)

        # Test that CLI can use RAG system
        assert cli.rag_system == mock_rag
        assert hasattr(cli, 'run')

    def test_streamlit_initialization_integration(self, mock_dataset_path):
        """Test Streamlit app initialization integration."""
        # This test would require more complex mocking of Streamlit components
        # For now, just test that the function exists and is callable
        assert callable(initialize_system)
        assert callable(create_interactive_graph)


@pytest.mark.ui
class TestUIComponents:
    """Tests specifically for UI components."""

    def test_streamlit_page_config(self):
        """Test Streamlit page configuration."""
        # Test that page config is properly set
        # This would require mocking Streamlit more extensively
        pass

    def test_session_state_management(self):
        """Test session state management."""
        # Test that session state is properly initialized and managed
        pass


@pytest.mark.api
class TestAPIEndpoints:
    """Tests for API-like functionality."""

    def test_query_processing_api(self, sample_graph):
        """Test query processing as an API endpoint."""
        from rag.biomedical_rag import BiomedicalRAG

        rag_system = BiomedicalRAG(sample_graph)

        # Test API-like behavior
        queries = [
            "What are diabetes symptoms?", "What causes fever?",
            "Tell me about hypertension"
        ]

        for query in queries:
            response = rag_system.answer_query(query)
            assert isinstance(response, str)
            assert len(response) > 0
