#!/usr/bin/env python3
"""
Unit tests for Claude Code History Exporter
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open, call
import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime
import io
import argparse
from typing import Dict, List, Tuple

# Import the module to test
import export_claude_history
from export_claude_history import ClaudeHistoryExporter, main


class TestClaudeHistoryExporter(unittest.TestCase):
    """Test cases for ClaudeHistoryExporter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_claude_json = {
            "projects": {
                "/home/user/project1": {
                    "history": [
                        {"display": "Latest prompt", "pastedContents": []},
                        {"display": "Middle prompt", "pastedContents": ["some content"]},
                        {"display": "Oldest prompt", "pastedContents": None}
                    ],
                    "hasCompletedProjectOnboarding": True,
                    "hasTrustDialogAccepted": True,
                    "allowedTools": ["Read", "Write", "Edit"],
                    "mcpServers": {"server1": {}},
                    "exampleFiles": ["file1.py", "file2.js"]
                },
                "/home/user/project2": {
                    "history": [
                        {"display": "Project 2 prompt", "pastedContents": []}
                    ]
                },
                "/home/user/empty_project": {
                    "history": []
                }
            }
        }
        
        self.temp_dir = Path(tempfile.mkdtemp())
        self.claude_json_path = self.temp_dir / ".claude.json"
        
        # Write sample data to temp file
        with open(self.claude_json_path, 'w') as f:
            json.dump(self.sample_claude_json, f)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_default_path(self):
        """Test initialization with default path"""
        exporter = ClaudeHistoryExporter()
        self.assertEqual(exporter.claude_json_path, Path.home() / '.claude.json')
        self.assertIsNone(exporter.data)
        self.assertEqual(exporter.projects, {})
    
    def test_init_custom_path(self):
        """Test initialization with custom path"""
        custom_path = Path("/custom/path/.claude.json")
        exporter = ClaudeHistoryExporter(custom_path)
        self.assertEqual(exporter.claude_json_path, custom_path)
    
    def test_load_data_success(self):
        """Test successful data loading"""
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        result = exporter.load_data()
        
        self.assertTrue(result)
        self.assertIsNotNone(exporter.data)
        self.assertEqual(len(exporter.projects), 3)
        self.assertIn("/home/user/project1", exporter.projects)
    
    def test_load_data_file_not_found(self):
        """Test loading when file doesn't exist"""
        exporter = ClaudeHistoryExporter(Path("/nonexistent/file.json"))
        
        with patch('builtins.print') as mock_print:
            result = exporter.load_data()
            
        self.assertFalse(result)
        mock_print.assert_called_with("Error: /nonexistent/file.json not found")
    
    def test_load_data_invalid_json(self):
        """Test loading with invalid JSON"""
        invalid_json_path = self.temp_dir / "invalid.json"
        with open(invalid_json_path, 'w') as f:
            f.write("{ invalid json }")
        
        exporter = ClaudeHistoryExporter(invalid_json_path)
        
        with patch('builtins.print') as mock_print:
            result = exporter.load_data()
            
        self.assertFalse(result)
        self.assertTrue(any("Error parsing JSON" in str(call) for call in mock_print.call_args_list))
    
    def test_get_projects_with_history(self):
        """Test getting projects with history"""
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        exporter.load_data()
        
        projects = exporter.get_projects_with_history()
        
        # Should have 2 projects with history (project1 and project2)
        self.assertEqual(len(projects), 2)
        
        # Should be sorted by prompt count (descending)
        self.assertEqual(projects[0][0], "/home/user/project1")
        self.assertEqual(projects[0][1], 3)  # 3 prompts
        self.assertEqual(projects[1][0], "/home/user/project2")
        self.assertEqual(projects[1][1], 1)  # 1 prompt
    
    @patch('builtins.input', side_effect=['1'])
    def test_display_projects_menu_select_project(self, mock_input):
        """Test project menu selection"""
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        exporter.load_data()
        
        with patch('builtins.print'):
            result = exporter.display_projects_menu()
        
        self.assertEqual(result, "/home/user/project1")
    
    @patch('builtins.input', side_effect=['0'])
    def test_display_projects_menu_select_all(self, mock_input):
        """Test selecting all projects"""
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        exporter.load_data()
        
        with patch('builtins.print'):
            result = exporter.display_projects_menu()
        
        self.assertEqual(result, 'ALL')
    
    @patch('builtins.input', side_effect=['q'])
    def test_display_projects_menu_quit(self, mock_input):
        """Test quitting the menu"""
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        exporter.load_data()
        
        with patch('builtins.print'):
            result = exporter.display_projects_menu()
        
        self.assertIsNone(result)
    
    @patch('builtins.input', side_effect=['invalid', '10', '1'])
    def test_display_projects_menu_invalid_input(self, mock_input):
        """Test handling invalid menu input"""
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        exporter.load_data()
        
        with patch('builtins.print') as mock_print:
            result = exporter.display_projects_menu()
        
        # Should handle invalid input gracefully
        self.assertEqual(result, "/home/user/project1")
        # Check for error messages
        error_messages = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("Invalid" in msg for msg in error_messages))
    
    def test_display_projects_menu_no_projects(self):
        """Test menu with no projects"""
        empty_json = {"projects": {}}
        empty_path = self.temp_dir / "empty.json"
        with open(empty_path, 'w') as f:
            json.dump(empty_json, f)
        
        exporter = ClaudeHistoryExporter(empty_path)
        exporter.load_data()
        
        with patch('builtins.print') as mock_print:
            result = exporter.display_projects_menu()
        
        self.assertIsNone(result)
        mock_print.assert_any_call("No projects with conversation history found.")
    
    def test_get_project_metadata(self):
        """Test getting project metadata"""
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        exporter.load_data()
        
        metadata = exporter.get_project_metadata("/home/user/project1")
        
        self.assertEqual(metadata['path'], "/home/user/project1")
        self.assertEqual(metadata['project_name'], "project1")
        self.assertEqual(metadata['total_prompts'], 3)
        self.assertTrue(metadata['has_onboarding_completed'])
        self.assertTrue(metadata['trust_dialog_accepted'])
        self.assertEqual(metadata['allowed_tools'], ["Read", "Write", "Edit"])
        self.assertEqual(metadata['mcp_servers'], ["server1"])
        self.assertEqual(metadata['example_files'], 2)
    
    def test_get_project_metadata_nonexistent(self):
        """Test getting metadata for nonexistent project"""
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        exporter.load_data()
        
        metadata = exporter.get_project_metadata("/nonexistent/project")
        
        self.assertEqual(metadata['path'], "/nonexistent/project")
        self.assertEqual(metadata['project_name'], "project")
        self.assertEqual(metadata['total_prompts'], 0)
        self.assertFalse(metadata['has_onboarding_completed'])
    
    def test_format_prompt_entry_simple(self):
        """Test formatting a simple prompt entry"""
        exporter = ClaudeHistoryExporter()
        
        entry = {"display": "Simple prompt", "pastedContents": []}
        result = exporter.format_prompt_entry(entry, 0, 3)
        
        self.assertIn("### Prompt #3", result)
        self.assertIn("`Simple prompt`", result)
        self.assertNotIn("Note:", result)
    
    def test_format_prompt_entry_with_pasted_content(self):
        """Test formatting prompt with pasted content"""
        exporter = ClaudeHistoryExporter()
        
        entry = {"display": "Prompt", "pastedContents": ["content"]}
        result = exporter.format_prompt_entry(entry, 1, 3)
        
        self.assertIn("### Prompt #2", result)
        self.assertIn("**Note:** This prompt included pasted content", result)
    
    def test_format_prompt_entry_multiline(self):
        """Test formatting multiline prompt"""
        exporter = ClaudeHistoryExporter()
        
        entry = {"display": "Line 1\nLine 2", "pastedContents": []}
        result = exporter.format_prompt_entry(entry, 0, 1)
        
        self.assertIn("```\nLine 1\nLine 2\n```", result)
    
    def test_get_prompt_hash(self):
        """Test prompt hash generation"""
        exporter = ClaudeHistoryExporter()
        
        hash1 = exporter.get_prompt_hash("test prompt")
        hash2 = exporter.get_prompt_hash("test prompt")
        hash3 = exporter.get_prompt_hash("different prompt")
        
        # Same input should produce same hash
        self.assertEqual(hash1, hash2)
        # Different input should produce different hash
        self.assertNotEqual(hash1, hash3)
        # Hash should be 16 characters
        self.assertEqual(len(hash1), 16)
    
    @patch('export_claude_history.datetime')
    def test_export_project_history(self, mock_datetime):
        """Test exporting project history to markdown"""
        mock_datetime.now.return_value.strftime.return_value = "20250813_120000"
        
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        exporter.load_data()
        
        output_file = self.temp_dir / "test_export.md"
        output_path = exporter.export_project_history("/home/user/project1", output_file)
        
        # Check file was created
        self.assertTrue(output_file.exists())
        self.assertEqual(output_path, output_file)
        
        # Read and check content
        with open(output_file, 'r') as f:
            content = f.read()
        
        # Check content includes expected elements
        self.assertIn("# Claude Code Conversation History", content)
        self.assertIn("## Project: project1", content)
        self.assertIn("### Metadata", content)
        self.assertIn("**Total Prompts:** 3", content)
        self.assertIn("## Conversation History", content)
        self.assertIn("Oldest prompt", content)
        self.assertIn("Middle prompt", content)
        self.assertIn("Latest prompt", content)
    
    @patch('builtins.open', new_callable=mock_open)
    def test_export_project_history_custom_output(self, mock_file):
        """Test exporting with custom output path"""
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        exporter.load_data()
        
        custom_path = Path("/custom/output.md")
        result = exporter.export_project_history("/home/user/project1", custom_path)
        
        self.assertEqual(result, custom_path)
    
    @patch('export_claude_history.datetime')
    def test_export_all_projects(self, mock_datetime):
        """Test exporting all projects"""
        mock_datetime.now.return_value.strftime.return_value = "20250813_120000"
        
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        exporter.load_data()
        
        output_dir = self.temp_dir / "export_test"
        
        with patch('builtins.print'):
            results = exporter.export_all_projects(output_dir)
        
        # Should export 2 projects with history + 1 index file
        self.assertEqual(len(results), 3)
        
        # Check files were created
        self.assertTrue((output_dir / "home_user_project1.md").exists())
        self.assertTrue((output_dir / "home_user_project2.md").exists())
        self.assertTrue((output_dir / "INDEX.md").exists())
    
    def test_sync_project_json_new_file(self):
        """Test syncing project to new JSON file"""
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        exporter.load_data()
        
        output_dir = self.temp_dir / "json_output"
        
        with patch('builtins.open', new_callable=mock_open()) as mock_file:
            with patch('pathlib.Path.exists', return_value=False):
                with patch('pathlib.Path.mkdir'):
                    json_path, stats = exporter.sync_project_json("/home/user/project1", output_dir)
        
        # Check stats
        self.assertEqual(stats['previous_count'], 0)
        self.assertEqual(stats['current_count'], 3)
        self.assertEqual(stats['new_count'], 3)
        self.assertEqual(stats['total_count'], 3)
    
    def test_sync_project_json_with_existing_data(self):
        """Test syncing with deduplication"""
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        exporter.load_data()
        
        # Simulate existing data with some overlap
        existing_data = {
            "project_path": "/home/user/project1",
            "project_name": "project1",
            "last_updated": "2025-08-12T10:00:00",
            "prompts": [
                {
                    "text": "Oldest prompt",
                    "hash": exporter.get_prompt_hash("Oldest prompt"),
                    "has_pasted_content": False,
                    "first_seen": "2025-08-12T10:00:00"
                }
            ]
        }
        
        output_dir = self.temp_dir / "json_output"
        json_file_content = json.dumps(existing_data)
        
        with patch('builtins.open', mock_open(read_data=json_file_content)) as mock_file:
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.mkdir'):
                    json_path, stats = exporter.sync_project_json("/home/user/project1", output_dir)
        
        # Should detect the overlap and only add new prompts
        self.assertEqual(stats['previous_count'], 1)
        self.assertEqual(stats['current_count'], 3)
        self.assertEqual(stats['new_count'], 2)  # Only 2 new prompts
        self.assertEqual(stats['total_count'], 3)
    
    def test_sync_project_json_sequence_overlap(self):
        """Test deduplication with sequence overlap detection"""
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        exporter.load_data()
        
        # Create existing data that represents a previous sync
        existing_prompts = []
        for prompt_text in ["Oldest prompt", "Middle prompt"]:
            existing_prompts.append({
                "text": prompt_text,
                "hash": exporter.get_prompt_hash(prompt_text),
                "has_pasted_content": False,
                "first_seen": "2025-08-12T10:00:00"
            })
        
        existing_data = {
            "project_path": "/home/user/project1",
            "project_name": "project1",
            "last_updated": "2025-08-12T10:00:00",
            "prompts": existing_prompts
        }
        
        output_dir = self.temp_dir / "json_output"
        json_file_content = json.dumps(existing_data)
        
        with patch('builtins.open', mock_open(read_data=json_file_content)) as mock_file:
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.mkdir'):
                    json_path, stats = exporter.sync_project_json("/home/user/project1", output_dir)
        
        # Should detect sequence overlap and add only truly new prompts
        self.assertEqual(stats['previous_count'], 2)
        self.assertEqual(stats['current_count'], 3)
        self.assertEqual(stats['new_count'], 1)  # Only "Latest prompt" is new
        self.assertEqual(stats['total_count'], 3)
    
    @patch('export_claude_history.ClaudeHistoryExporter.sync_project_json')
    def test_sync_all_projects_json(self, mock_sync):
        """Test syncing all projects to JSON"""
        mock_sync.return_value = (Path("synced.json"), {
            'previous_count': 0,
            'current_count': 3,
            'new_count': 3,
            'total_count': 3
        })
        
        exporter = ClaudeHistoryExporter(self.claude_json_path)
        exporter.load_data()
        
        with patch('builtins.print'):
            with patch('pathlib.Path.mkdir'):
                results = exporter.sync_all_projects_json()
        
        # Should sync 2 projects with history
        self.assertEqual(len(results), 2)
        self.assertEqual(mock_sync.call_count, 2)


class TestMainFunction(unittest.TestCase):
    """Test cases for the main() function and CLI handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_claude_json = {
            "projects": {
                "/home/user/project1": {
                    "history": [
                        {"display": "Test prompt", "pastedContents": []}
                    ]
                }
            }
        }
        
        self.temp_dir = Path(tempfile.mkdtemp())
        self.claude_json_path = self.temp_dir / ".claude.json"
        
        with open(self.claude_json_path, 'w') as f:
            json.dump(self.sample_claude_json, f)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('sys.argv', ['script', '--list', '--json-path', 'test.json'])
    @patch('export_claude_history.ClaudeHistoryExporter.load_data')
    @patch('export_claude_history.ClaudeHistoryExporter.get_projects_with_history')
    @patch('builtins.print')
    def test_main_list_mode(self, mock_print, mock_get_projects, mock_load):
        """Test main function in list mode"""
        mock_load.return_value = True
        mock_get_projects.return_value = [("/project1", 5), ("/project2", 3)]
        
        main()
        
        mock_load.assert_called_once()
        mock_get_projects.assert_called_once()
        mock_print.assert_any_call("\nFound 2 projects with history:\n")
    
    @patch('sys.argv', ['script', '--stats', '--json-path', 'test.json'])
    @patch('export_claude_history.ClaudeHistoryExporter.load_data')
    @patch('export_claude_history.ClaudeHistoryExporter.get_projects_with_history')
    @patch('builtins.print')
    def test_main_stats_mode(self, mock_print, mock_get_projects, mock_load):
        """Test main function in stats mode"""
        mock_load.return_value = True
        mock_get_projects.return_value = [("/project1", 10), ("/project2", 5)]
        
        main()
        
        mock_load.assert_called_once()
        mock_get_projects.assert_called_once()
        
        # Check for stats output
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("CLAUDE CODE STATISTICS" in call for call in print_calls))
        self.assertTrue(any("Total prompts across all projects: 15" in call for call in print_calls))
    
    @patch('sys.argv', ['script', '--search', 'keyword', '--json-path', 'test.json'])
    @patch('export_claude_history.ClaudeHistoryExporter.load_data')
    @patch('builtins.print')
    def test_main_search_mode(self, mock_print, mock_load):
        """Test main function in search mode"""
        # Create a mock exporter with projects
        mock_exporter = MagicMock()
        mock_exporter.projects = {
            "/project1": {"history": [{"display": "Find this keyword here"}]},
            "/project2": {"history": [{"display": "No match"}]}
        }
        
        with patch('export_claude_history.ClaudeHistoryExporter', return_value=mock_exporter):
            mock_load.return_value = True
            mock_exporter.load_data.return_value = True
            main()
        
        mock_exporter.load_data.assert_called_once()
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("keyword" in call for call in print_calls))
    
    @patch('sys.argv', ['script', '--all', '--json-path', 'test.json'])
    @patch('export_claude_history.ClaudeHistoryExporter.load_data')
    @patch('export_claude_history.ClaudeHistoryExporter.export_all_projects')
    @patch('builtins.print')
    def test_main_export_all_mode(self, mock_print, mock_export_all, mock_load):
        """Test main function in export all mode"""
        mock_load.return_value = True
        mock_export_all.return_value = [Path("export1.md"), Path("export2.md")]
        
        main()
        
        mock_load.assert_called_once()
        mock_export_all.assert_called_once()
        mock_print.assert_any_call("\nExporting all projects with history...")
    
    @patch('sys.argv', ['script', '--sync-all', '--json-path', 'test.json'])
    @patch('export_claude_history.ClaudeHistoryExporter.load_data')
    @patch('export_claude_history.ClaudeHistoryExporter.sync_all_projects_json')
    @patch('builtins.print')
    def test_main_sync_all_mode(self, mock_print, mock_sync_all, mock_load):
        """Test main function in sync all mode"""
        mock_load.return_value = True
        mock_sync_all.return_value = [
            (Path("sync1.json"), {'new_count': 5, 'total_count': 10}),
            (Path("sync2.json"), {'new_count': 3, 'total_count': 8})
        ]
        
        main()
        
        mock_load.assert_called_once()
        mock_sync_all.assert_called_once()
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("Syncing all projects" in call for call in print_calls))
        self.assertTrue(any("Total new prompts added: 8" in call for call in print_calls))
    
    @patch('sys.argv', ['script', '--sync', '--json-path', 'test.json'])
    @patch('export_claude_history.ClaudeHistoryExporter.load_data')
    @patch('export_claude_history.ClaudeHistoryExporter.display_projects_menu')
    @patch('export_claude_history.ClaudeHistoryExporter.sync_project_json')
    @patch('builtins.print')
    def test_main_sync_interactive(self, mock_print, mock_sync, mock_menu, mock_load):
        """Test main function in interactive sync mode"""
        mock_load.return_value = True
        mock_menu.return_value = "/project1"
        mock_sync.return_value = (Path("sync.json"), {
            'previous_count': 5,
            'current_count': 8,
            'new_count': 3,
            'total_count': 8
        })
        
        main()
        
        mock_load.assert_called_once()
        mock_menu.assert_called_once()
        mock_sync.assert_called_once_with("/project1", None)
    
    @patch('sys.argv', ['script', '--sync', '--json-path', 'test.json'])
    @patch('export_claude_history.ClaudeHistoryExporter.load_data')
    @patch('export_claude_history.ClaudeHistoryExporter.display_projects_menu')
    @patch('builtins.print')
    def test_main_sync_cancelled(self, mock_print, mock_menu, mock_load):
        """Test cancelling interactive sync"""
        mock_load.return_value = True
        mock_menu.return_value = None
        
        with self.assertRaises(SystemExit) as cm:
            main()
        
        self.assertEqual(cm.exception.code, 0)
        mock_print.assert_any_call("Sync cancelled.")
    
    @patch('sys.argv', ['script', '--json-path', 'test.json'])
    @patch('export_claude_history.ClaudeHistoryExporter.load_data')
    @patch('export_claude_history.ClaudeHistoryExporter.display_projects_menu')
    @patch('export_claude_history.ClaudeHistoryExporter.export_project_history')
    @patch('builtins.print')
    def test_main_interactive_export(self, mock_print, mock_export, mock_menu, mock_load):
        """Test main function in default interactive mode"""
        mock_load.return_value = True
        mock_menu.return_value = "/project1"
        mock_export.return_value = Path("export.md")
        
        # Create mock exporter with projects attribute
        mock_exporter = MagicMock()
        mock_exporter.projects = {"/project1": {"history": [{"display": "prompt"}]}}
        mock_exporter.load_data.return_value = True
        mock_exporter.display_projects_menu.return_value = "/project1"
        mock_exporter.export_project_history.return_value = Path("export.md")
        
        with patch('export_claude_history.ClaudeHistoryExporter', return_value=mock_exporter):
            main()
        
        mock_exporter.load_data.assert_called_once()
        mock_exporter.display_projects_menu.assert_called_once()
        mock_exporter.export_project_history.assert_called_once_with("/project1", None)
    
    @patch('sys.argv', ['script', '--json-path', 'nonexistent.json'])
    @patch('export_claude_history.ClaudeHistoryExporter.load_data')
    def test_main_load_failure(self, mock_load):
        """Test main function when data loading fails"""
        mock_load.return_value = False
        
        with self.assertRaises(SystemExit) as cm:
            main()
        
        self.assertEqual(cm.exception.code, 1)
        mock_load.assert_called_once()
    
    @patch('sys.argv', ['script', '--search', 'test', '--stats'])
    def test_main_argument_parsing(self):
        """Test argument parsing combinations"""
        with patch('export_claude_history.ClaudeHistoryExporter.load_data', return_value=True):
            with patch('export_claude_history.ClaudeHistoryExporter.get_projects_with_history', return_value=[]):
                with patch('builtins.print'):
                    # Should execute stats mode (last in the if/elif chain that matches)
                    main()
                    # This test primarily ensures argument parsing doesn't crash


class TestAdditionalCoverage(unittest.TestCase):
    """Additional tests to improve code coverage"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.claude_json_path = self.temp_dir / ".claude.json"
        
        self.sample_data = {
            "projects": {
                "/test/project": {
                    "history": [
                        {"display": "test prompt", "pastedContents": []}
                    ]
                }
            }
        }
        
        with open(self.claude_json_path, 'w') as f:
            json.dump(self.sample_data, f)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('sys.argv', ['script', '--list'])
    def test_main_list_no_projects(self):
        """Test list mode with no projects"""
        empty_json = {"projects": {}}
        empty_path = self.temp_dir / "empty.json"
        with open(empty_path, 'w') as f:
            json.dump(empty_json, f)
        
        with patch('sys.argv', ['script', '--list', '--json-path', str(empty_path)]):
            with patch('builtins.print') as mock_print:
                main()
                
        mock_print.assert_any_call("No projects with conversation history found.")
    
    @patch('sys.argv', ['script', '--search', 'nomatch', '--json-path'])
    def test_main_search_no_results(self, ):
        """Test search with no matching results"""
        with patch('sys.argv', ['script', '--search', 'nomatch', '--json-path', str(self.claude_json_path)]):
            with patch('builtins.print') as mock_print:
                main()
                
        mock_print.assert_any_call("No prompts found containing 'nomatch'")
    
    @patch('sys.argv', ['script', '--all', '--json-path'])
    def test_main_export_all_no_projects(self):
        """Test export all with no projects"""
        empty_json = {"projects": {}}
        empty_path = self.temp_dir / "empty.json"
        with open(empty_path, 'w') as f:
            json.dump(empty_json, f)
        
        with patch('sys.argv', ['script', '--all', '--json-path', str(empty_path)]):
            with patch('builtins.print') as mock_print:
                main()
                
        # When there are no projects with history, it still creates an empty export
        mock_print.assert_any_call("\nExporting all projects with history...")
    
    @patch('sys.argv', ['script', '--sync-all', '--json-path'])
    def test_main_sync_all_no_results(self):
        """Test sync all with no results"""
        empty_json = {"projects": {}}
        empty_path = self.temp_dir / "empty.json"
        with open(empty_path, 'w') as f:
            json.dump(empty_json, f)
        
        with patch('sys.argv', ['script', '--sync-all', '--json-path', str(empty_path)]):
            with patch('builtins.print') as mock_print:
                main()
                
        mock_print.assert_any_call("No projects to sync.")
    
    @patch('sys.argv', ['script', '--json-path'])
    @patch('export_claude_history.ClaudeHistoryExporter.display_projects_menu')
    def test_main_interactive_export_all(self, mock_menu):
        """Test interactive mode selecting ALL"""
        mock_menu.return_value = 'ALL'
        
        with patch('sys.argv', ['script', '--json-path', str(self.claude_json_path)]):
            with patch('builtins.print'):
                main()
        
        mock_menu.assert_called_once()
    
    @patch('sys.argv', ['script', '--sync', '--json-path'])
    @patch('export_claude_history.ClaudeHistoryExporter.display_projects_menu')
    def test_main_sync_select_all(self, mock_menu):
        """Test sync mode selecting ALL"""
        mock_menu.return_value = 'ALL'
        
        with patch('sys.argv', ['script', '--sync', '--json-path', str(self.claude_json_path)]):
            with patch('builtins.print'):
                main()
        
        mock_menu.assert_called_once()


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_empty_prompt_handling(self):
        """Test handling of empty prompts"""
        exporter = ClaudeHistoryExporter()
        
        # Empty display field
        entry = {"display": "", "pastedContents": []}
        result = exporter.format_prompt_entry(entry, 0, 1)
        self.assertIn("``", result)  # Should still format, even if empty
    
    def test_very_long_prompt_formatting(self):
        """Test formatting very long prompts"""
        exporter = ClaudeHistoryExporter()
        
        long_prompt = "x" * 10000
        entry = {"display": long_prompt, "pastedContents": []}
        result = exporter.format_prompt_entry(entry, 0, 1)
        
        # Should handle long prompts without error
        self.assertIn(long_prompt, result)
    
    def test_special_characters_in_prompt(self):
        """Test handling special markdown characters in prompts"""
        exporter = ClaudeHistoryExporter()
        
        special_prompt = "Test `code` and **bold** and [link](url)"
        entry = {"display": special_prompt, "pastedContents": []}
        result = exporter.format_prompt_entry(entry, 0, 1)
        
        # Should preserve special characters
        self.assertIn(special_prompt, result)
    
    def test_project_path_with_spaces(self):
        """Test handling project paths with spaces"""
        data = {
            "projects": {
                "/home/user/my project/with spaces": {
                    "history": [{"display": "test", "pastedContents": []}]
                }
            }
        }
        
        temp_file = Path(tempfile.mktemp(suffix=".json"))
        with open(temp_file, 'w') as f:
            json.dump(data, f)
        
        exporter = ClaudeHistoryExporter(temp_file)
        exporter.load_data()
        
        projects = exporter.get_projects_with_history()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0][0], "/home/user/my project/with spaces")
        
        temp_file.unlink()
    
    def test_unicode_in_prompts(self):
        """Test handling Unicode characters in prompts"""
        exporter = ClaudeHistoryExporter()
        
        unicode_prompt = "Test with emoji 🎉 and special chars: ñ, ü, 中文"
        entry = {"display": unicode_prompt, "pastedContents": []}
        result = exporter.format_prompt_entry(entry, 0, 1)
        
        self.assertIn(unicode_prompt, result)
    
    def test_none_pasted_contents(self):
        """Test handling None value for pastedContents"""
        exporter = ClaudeHistoryExporter()
        
        entry = {"display": "Test", "pastedContents": None}
        result = exporter.format_prompt_entry(entry, 0, 1)
        
        # Should not show pasted content note
        self.assertNotIn("Note:", result)
    
    def test_missing_display_field(self):
        """Test handling missing display field"""
        exporter = ClaudeHistoryExporter()
        
        entry = {"pastedContents": []}  # Missing 'display' field
        result = exporter.format_prompt_entry(entry, 0, 1)
        
        # Should handle gracefully
        self.assertIn("### Prompt #1", result)
    
    @patch('pathlib.Path.mkdir')
    def test_output_directory_creation(self, mock_mkdir):
        """Test that output directories are created when needed"""
        exporter = ClaudeHistoryExporter()
        
        with patch('builtins.open', new_callable=mock_open()):
            with patch.object(exporter, 'projects', {"/test": {"history": []}}):
                exporter.export_all_projects()
        
        mock_mkdir.assert_called_with(exist_ok=True)
    
    def test_sync_with_corrupted_existing_file(self):
        """Test sync when existing JSON file is corrupted"""
        temp_dir = Path(tempfile.mkdtemp())
        exporter = ClaudeHistoryExporter()
        exporter.projects = {"/test": {"history": [{"display": "test"}]}}
        
        # Create corrupted JSON file
        json_path = temp_dir / "test_history.json"
        with open(json_path, 'w') as f:
            f.write("{corrupted json")
        
        with patch('builtins.print') as mock_print:
            with patch('pathlib.Path.exists', return_value=True):
                with patch('builtins.open', side_effect=[
                    open(json_path, 'r'),  # First open for reading (will fail)
                    mock_open()()  # Second open for writing
                ]):
                    json_path, stats = exporter.sync_project_json("/test", temp_dir)
        
        # Should handle corrupted file and start fresh
        self.assertEqual(stats['previous_count'], 0)
        
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    # Run tests with coverage if coverage module is available
    try:
        import coverage
        
        # Start coverage
        cov = coverage.Coverage()
        cov.start()
        
        # Run tests
        unittest.main(argv=[''], exit=False, verbosity=2)
        
        # Stop coverage and print report
        cov.stop()
        cov.save()
        
        print("\n" + "="*70)
        print("COVERAGE REPORT")
        print("="*70)
        
        # Generate coverage report
        cov.report(include=["export_claude_history.py"])
        
    except ImportError:
        # Run tests without coverage
        unittest.main(verbosity=2)