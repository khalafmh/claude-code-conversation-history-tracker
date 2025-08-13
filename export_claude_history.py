#!/usr/bin/env python3
"""
Claude Code History Exporter
Extract and export conversation history from ~/.claude.json to markdown format

DISCLAIMER: This is an unofficial, third-party tool not affiliated with Anthropic.
Use at your own risk. See DISCLAIMER.md for important information.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import argparse
import sys
from typing import Dict, List, Optional, Tuple
import hashlib

class ClaudeHistoryExporter:
    def __init__(self, claude_json_path: Optional[Path] = None):
        """Initialize the exporter with the path to claude.json"""
        self.claude_json_path = claude_json_path or Path.home() / '.claude.json'
        self.data = None
        self.projects = {}
        
    def load_data(self) -> bool:
        """Load and parse the claude.json file"""
        if not self.claude_json_path.exists():
            print(f"Error: {self.claude_json_path} not found")
            return False
        
        try:
            with open(self.claude_json_path, 'r') as f:
                self.data = json.load(f)
            self.projects = self.data.get('projects', {})
            return True
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return False
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
    
    def get_projects_with_history(self) -> List[Tuple[str, int]]:
        """Get list of projects that have history, sorted by prompt count"""
        projects_list = []
        for project_path, project_data in self.projects.items():
            history = project_data.get('history', [])
            if history:
                projects_list.append((project_path, len(history)))
        
        # Sort by prompt count (descending) then by path
        projects_list.sort(key=lambda x: (-x[1], x[0]))
        return projects_list
    
    def display_projects_menu(self) -> Optional[str]:
        """Display interactive menu for project selection"""
        projects = self.get_projects_with_history()
        
        if not projects:
            print("No projects with conversation history found.")
            return None
        
        print("\n" + "="*60)
        print("CLAUDE CODE PROJECTS WITH HISTORY")
        print("="*60)
        
        for i, (path, count) in enumerate(projects, 1):
            # Shorten long paths for display
            display_path = path
            if len(path) > 50:
                parts = path.split('/')
                if len(parts) > 3:
                    display_path = f".../{'/'.join(parts[-3:])}"
            
            print(f"{i:3}. [{count:3} prompts] {display_path}")
        
        print("="*60)
        print("  0. Export ALL projects")
        print("  q. Quit")
        print("="*60)
        
        while True:
            choice = input("\nSelect project number: ").strip().lower()
            
            if choice == 'q':
                return None
            
            if choice == '0':
                return 'ALL'
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(projects):
                    return projects[idx][0]
                else:
                    print(f"Invalid choice. Please enter 1-{len(projects)}, 0, or q")
            except ValueError:
                print(f"Invalid input. Please enter a number, 0, or q")
    
    def get_project_metadata(self, project_path: str) -> Dict:
        """Extract additional metadata for a project"""
        project_data = self.projects.get(project_path, {})
        
        metadata = {
            'path': project_path,
            'project_name': os.path.basename(project_path) or 'root',
            'total_prompts': len(project_data.get('history', [])),
            'has_onboarding_completed': project_data.get('hasCompletedProjectOnboarding', False),
            'trust_dialog_accepted': project_data.get('hasTrustDialogAccepted', False),
            'allowed_tools': project_data.get('allowedTools', []),
            'mcp_servers': list(project_data.get('mcpServers', {}).keys()),
            'example_files': len(project_data.get('exampleFiles', [])),
        }
        
        return metadata
    
    def format_prompt_entry(self, entry: Dict, index: int, total: int) -> str:
        """Format a single prompt entry for markdown output"""
        prompt_text = entry.get('display', '')
        pasted_contents = entry.get('pastedContents')
        # Check if pastedContents actually has content (not just empty array)
        has_pasted = pasted_contents and len(pasted_contents) > 0
        
        # Calculate prompt number (reverse the index since history is reverse chronological)
        prompt_num = total - index
        
        output = f"### Prompt #{prompt_num}\n\n"
        
        if has_pasted:
            output += "> **Note:** This prompt included pasted content\n\n"
        
        # Format the prompt text
        if '\n' in prompt_text:
            # Multi-line prompt - use code block
            output += "```\n"
            output += prompt_text
            output += "\n```\n"
        else:
            # Single line prompt
            output += f"`{prompt_text}`\n"
        
        output += "\n---\n\n"
        return output
    
    def export_project_history(self, project_path: str, output_path: Optional[Path] = None) -> Path:
        """Export a single project's history to markdown"""
        project_data = self.projects.get(project_path, {})
        history = project_data.get('history', [])
        metadata = self.get_project_metadata(project_path)
        
        # Generate output filename if not provided
        if output_path is None:
            safe_name = os.path.basename(project_path) or 'root'
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = Path(f"claude_history_{safe_name}_{timestamp}.md")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# Claude Code Conversation History\n\n")
            f.write(f"## Project: {metadata['project_name']}\n\n")
            
            # Write metadata section
            f.write("### Metadata\n\n")
            f.write(f"- **Full Path:** `{metadata['path']}`\n")
            f.write(f"- **Total Prompts:** {metadata['total_prompts']}\n")
            f.write(f"- **Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            if metadata['allowed_tools']:
                f.write(f"- **Allowed Tools:** {', '.join(metadata['allowed_tools'])}\n")
            if metadata['mcp_servers']:
                f.write(f"- **MCP Servers:** {', '.join(metadata['mcp_servers'])}\n")
            if metadata['example_files'] > 0:
                f.write(f"- **Example Files:** {metadata['example_files']}\n")
            
            f.write("\n---\n\n")
            
            # Write conversation history
            f.write("## Conversation History\n\n")
            f.write("> **Note:** Prompts are shown in chronological order (oldest first)\n\n")
            
            # Reverse the history to get chronological order
            reversed_history = list(reversed(history))
            
            for i, entry in enumerate(reversed_history):
                f.write(self.format_prompt_entry(entry, i, len(history)))
            
            # Write footer
            f.write("\n---\n\n")
            f.write(f"*Generated by Claude History Exporter on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        return output_path
    
    def export_all_projects(self, output_dir: Optional[Path] = None) -> List[Path]:
        """Export all projects with history to separate markdown files"""
        if output_dir is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = Path(f"claude_history_export_{timestamp}")
        
        output_dir.mkdir(exist_ok=True)
        exported_files = []
        
        projects = self.get_projects_with_history()
        
        for project_path, _ in projects:
            safe_name = project_path.replace('/', '_').strip('_') or 'root'
            output_path = output_dir / f"{safe_name}.md"
            
            exported_path = self.export_project_history(project_path, output_path)
            exported_files.append(exported_path)
            print(f"  ✓ Exported {project_path}")
        
        # Create index file
        index_path = output_dir / "INDEX.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# Claude Code History Export Index\n\n")
            f.write(f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Projects:** {len(projects)}\n\n")
            f.write("## Projects\n\n")
            
            total_prompts = 0
            for project_path, count in projects:
                safe_name = project_path.replace('/', '_').strip('_') or 'root'
                f.write(f"- [{project_path}](./{safe_name}.md) - {count} prompts\n")
                total_prompts += count
            
            f.write(f"\n**Total Prompts:** {total_prompts}\n")
        
        exported_files.append(index_path)
        return exported_files
    
    def get_prompt_hash(self, prompt_text: str) -> str:
        """Generate a hash for a prompt for deduplication"""
        return hashlib.sha256(prompt_text.encode('utf-8')).hexdigest()[:16]
    
    def sync_project_json(self, project_path: str, output_dir: Optional[Path] = None) -> Tuple[Path, Dict]:
        """Sync a project's history to a JSON file with deduplication"""
        if output_dir is None:
            output_dir = Path("claude_history_json")
        
        output_dir.mkdir(exist_ok=True)
        
        # Generate safe filename
        safe_name = project_path.replace('/', '_').strip('_') or 'root'
        json_path = output_dir / f"{safe_name}_history.json"
        
        # Load existing data if file exists
        existing_data = {
            "project_path": project_path,
            "project_name": os.path.basename(project_path) or 'root',
            "last_updated": None,
            "prompts": []
        }
        
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                print(f"  ⚠ Warning: Could not read existing file {json_path}, starting fresh")
        
        # Get current history from claude.json
        project_data = self.projects.get(project_path, {})
        current_history = project_data.get('history', [])
        
        # Current timestamp for new prompts
        current_timestamp = datetime.now().isoformat()
        
        # Reverse to get chronological order (oldest first)
        current_prompts = []
        for entry in reversed(current_history):
            prompt_text = entry.get('display', '')
            if prompt_text:  # Skip empty prompts
                current_prompts.append({
                    "text": prompt_text,
                    "hash": self.get_prompt_hash(prompt_text),
                    "has_pasted_content": bool(entry.get('pastedContents') and len(entry.get('pastedContents', [])) > 0),
                    "first_seen": current_timestamp  # Will be set properly when adding
                })
        
        # Build hash set for existing prompts
        existing_hashes = {p['hash'] for p in existing_data['prompts']}
        
        # Find the overlap point and new prompts
        new_prompts = []
        overlap_found = False
        
        for i, prompt in enumerate(current_prompts):
            if not overlap_found and prompt['hash'] in existing_hashes:
                # Found where sequences overlap - check if rest matches
                overlap_start = i
                existing_tail = [p['hash'] for p in existing_data['prompts'][-len(current_prompts)+i:]]
                current_tail = [p['hash'] for p in current_prompts[i:]]
                
                if existing_tail == current_tail[:len(existing_tail)]:
                    # Sequences match from this point
                    overlap_found = True
                    # Add any prompts before the overlap that aren't in existing
                    for j in range(i):
                        if current_prompts[j]['hash'] not in existing_hashes:
                            prompt_to_add = current_prompts[j].copy()
                            prompt_to_add['first_seen'] = current_timestamp
                            new_prompts.append(prompt_to_add)
                    # Add any new prompts after the existing sequence
                    if len(current_tail) > len(existing_tail):
                        for prompt in current_prompts[i+len(existing_tail):]:
                            prompt_to_add = prompt.copy()
                            prompt_to_add['first_seen'] = current_timestamp
                            new_prompts.append(prompt_to_add)
                    break
        
        if not overlap_found:
            # No overlap found - add all prompts that aren't duplicates
            for prompt in current_prompts:
                if prompt['hash'] not in existing_hashes:
                    prompt_to_add = prompt.copy()
                    prompt_to_add['first_seen'] = current_timestamp
                    new_prompts.append(prompt_to_add)
        
        # Merge: append new prompts to existing
        stats = {
            "previous_count": len(existing_data['prompts']),
            "current_count": len(current_prompts),
            "new_count": len(new_prompts),
            "total_count": len(existing_data['prompts']) + len(new_prompts)
        }
        
        existing_data['prompts'].extend(new_prompts)
        existing_data['last_updated'] = current_timestamp
        
        # Save updated data
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        return json_path, stats
    
    def sync_all_projects_json(self, output_dir: Optional[Path] = None) -> List[Tuple[Path, Dict]]:
        """Sync all projects to JSON files with deduplication"""
        if output_dir is None:
            output_dir = Path("claude_history_json")
        
        output_dir.mkdir(exist_ok=True)
        results = []
        
        projects = self.get_projects_with_history()
        
        for project_path, _ in projects:
            json_path, stats = self.sync_project_json(project_path, output_dir)
            results.append((json_path, stats))
            
            if stats['new_count'] > 0:
                print(f"  ✓ {project_path}: +{stats['new_count']} new prompts (total: {stats['total_count']})")
            else:
                print(f"  - {project_path}: no new prompts (total: {stats['total_count']})")
        
        return results

def main():
    parser = argparse.ArgumentParser(
        description='Export Claude Code conversation history to markdown or JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Interactive mode - select project from menu
  %(prog)s --list             # List all projects with history
  %(prog)s --all              # Export all projects to separate markdown files
  %(prog)s --search "keyword" # Search for prompts containing keyword
  %(prog)s --stats            # Show statistics about all projects
  %(prog)s --sync             # Sync current history to JSON files (with deduplication)
  %(prog)s --sync-all         # Sync all projects to JSON files
        """
    )
    
    parser.add_argument('--list', '-l', action='store_true',
                       help='List all projects with conversation history')
    parser.add_argument('--all', '-a', action='store_true',
                       help='Export all projects to separate markdown files')
    parser.add_argument('--output', '-o', type=Path,
                       help='Output file or directory path')
    parser.add_argument('--search', '-s', type=str,
                       help='Search for prompts containing this text (case-insensitive)')
    parser.add_argument('--stats', action='store_true',
                       help='Show statistics about conversation history')
    parser.add_argument('--sync', action='store_true',
                       help='Sync project history to JSON file with deduplication (interactive)')
    parser.add_argument('--sync-all', action='store_true',
                       help='Sync all projects to JSON files with deduplication')
    parser.add_argument('--json-path', type=Path,
                       help='Path to claude.json file (default: ~/.claude.json)')
    
    args = parser.parse_args()
    
    # Initialize exporter
    exporter = ClaudeHistoryExporter(args.json_path)
    
    # Load data
    if not exporter.load_data():
        sys.exit(1)
    
    # Handle different modes
    if args.list:
        # List mode
        projects = exporter.get_projects_with_history()
        if not projects:
            print("No projects with conversation history found.")
        else:
            print(f"\nFound {len(projects)} projects with history:\n")
            for path, count in projects:
                print(f"  {count:3} prompts - {path}")
    
    elif args.stats:
        # Statistics mode
        projects = exporter.get_projects_with_history()
        total_prompts = sum(count for _, count in projects)
        
        print("\n" + "="*60)
        print("CLAUDE CODE STATISTICS")
        print("="*60)
        print(f"Total projects with history: {len(projects)}")
        print(f"Total prompts across all projects: {total_prompts}")
        
        if projects:
            avg_prompts = total_prompts / len(projects)
            max_project = projects[0] if projects else None
            
            print(f"Average prompts per project: {avg_prompts:.1f}")
            if max_project:
                print(f"Most active project: {max_project[0]} ({max_project[1]} prompts)")
        print("="*60)
    
    elif args.search:
        # Search mode
        keyword = args.search.lower()
        found_prompts = []
        
        for project_path, project_data in exporter.projects.items():
            history = project_data.get('history', [])
            for entry in history:
                prompt = entry.get('display', '')
                if keyword in prompt.lower():
                    found_prompts.append((project_path, prompt))
        
        if found_prompts:
            print(f"\nFound {len(found_prompts)} prompts containing '{args.search}':\n")
            for project, prompt in found_prompts:
                print(f"[{project}]")
                print(f"  {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
                print()
        else:
            print(f"No prompts found containing '{args.search}'")
    
    elif args.all:
        # Export all mode
        print("\nExporting all projects with history...")
        exported = exporter.export_all_projects(args.output)
        
        if exported:
            export_dir = exported[0].parent
            print(f"\n✅ Successfully exported {len(exported)-1} projects")
            print(f"📁 Files saved in: {export_dir}")
            print(f"📄 Index file: {export_dir}/INDEX.md")
        else:
            print("No projects to export.")
    
    elif args.sync_all:
        # Sync all projects to JSON
        print("\nSyncing all projects to JSON files...")
        results = exporter.sync_all_projects_json(args.output)
        
        if results:
            output_dir = results[0][0].parent if results else Path("claude_history_json")
            total_new = sum(stats['new_count'] for _, stats in results)
            total_prompts = sum(stats['total_count'] for _, stats in results)
            
            print(f"\n✅ Synced {len(results)} projects")
            print(f"📁 JSON files saved in: {output_dir}")
            print(f"📊 Total new prompts added: {total_new}")
            print(f"📝 Total prompts stored: {total_prompts}")
        else:
            print("No projects to sync.")
    
    elif args.sync:
        # Interactive sync mode
        project_path = exporter.display_projects_menu()
        
        if project_path is None:
            print("Sync cancelled.")
            sys.exit(0)
        
        if project_path == 'ALL':
            # Sync all
            print("\nSyncing all projects to JSON files...")
            results = exporter.sync_all_projects_json(args.output)
            
            if results:
                output_dir = results[0][0].parent if results else Path("claude_history_json")
                total_new = sum(stats['new_count'] for _, stats in results)
                total_prompts = sum(stats['total_count'] for _, stats in results)
                
                print(f"\n✅ Synced {len(results)} projects")
                print(f"📁 JSON files saved in: {output_dir}")
                print(f"📊 Total new prompts added: {total_new}")
                print(f"📝 Total prompts stored: {total_prompts}")
        else:
            # Sync single project
            print(f"\nSyncing history for: {project_path}")
            json_path, stats = exporter.sync_project_json(project_path, args.output)
            
            print(f"\n✅ Successfully synced to: {json_path}")
            print(f"📊 Previous prompts: {stats['previous_count']}")
            print(f"📝 Current prompts in ~/.claude.json: {stats['current_count']}")
            print(f"➕ New prompts added: {stats['new_count']}")
            print(f"📄 Total prompts stored: {stats['total_count']}")
    
    else:
        # Interactive mode
        project_path = exporter.display_projects_menu()
        
        if project_path is None:
            print("Export cancelled.")
            sys.exit(0)
        
        if project_path == 'ALL':
            # Export all
            print("\nExporting all projects with history...")
            exported = exporter.export_all_projects(args.output)
            
            if exported:
                export_dir = exported[0].parent
                print(f"\n✅ Successfully exported {len(exported)-1} projects")
                print(f"📁 Files saved in: {export_dir}")
                print(f"📄 Index file: {export_dir}/INDEX.md")
        else:
            # Export single project
            print(f"\nExporting history for: {project_path}")
            output_path = exporter.export_project_history(project_path, args.output)
            
            print(f"\n✅ Successfully exported to: {output_path}")
            print(f"📄 Total prompts: {len(exporter.projects[project_path].get('history', []))}")

if __name__ == "__main__":
    main()