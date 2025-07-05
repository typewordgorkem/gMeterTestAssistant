"""
AI Test Automation Assistant - Usage Examples
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.orchestrator.main_orchestrator import MainOrchestrator, ExecutionConfig


async def example_full_automation():
    """Example: Full automation workflow"""
    print("🚀 Example: Full Automation Workflow")
    
    # Initialize orchestrator
    orchestrator = MainOrchestrator()
    
    # Create execution config
    config = ExecutionConfig(
        url="https://example.com",
        ai_model="llama2",
        output_dir="example_output",
        headless=True,
        parallel_tests=True,
        generate_reports=True,
        save_artifacts=True
    )
    
    # Execute automation
    result = await orchestrator.execute_full_automation(config)
    
    if result.success:
        print(f"✅ Automation completed successfully in {result.execution_time:.2f}s")
        print(f"📊 Generated {len(result.reports)} reports")
    else:
        print(f"❌ Automation failed: {result.error_message}")


async def example_quick_test():
    """Example: Quick test"""
    print("\n⚡ Example: Quick Test")
    
    # Initialize orchestrator
    orchestrator = MainOrchestrator()
    
    # Run quick test
    result = await orchestrator.quick_test("https://example.com", "llama2")
    
    if result['success']:
        print(f"✅ Quick test completed for: {result['url']}")
        print(f"📄 Page title: {result['title']}")
        print(f"📝 Forms found: {result['forms_count']}")
        print(f"🔗 Links found: {result['links_count']}")
        print(f"🔘 Buttons found: {result['buttons_count']}")
    else:
        print(f"❌ Quick test failed: {result['error']}")


async def example_individual_components():
    """Example: Using individual components"""
    print("\n🔧 Example: Individual Components")
    
    from src.ai.ai_client import AIClient
    from src.scraper.web_scraper import WebScraper
    from src.bdd.bdd_generator import BDDGenerator
    
    # Initialize components
    ai_client = AIClient()
    web_scraper = WebScraper()
    bdd_generator = BDDGenerator()
    
    # Example: Web scraping
    print("🌐 Scraping website...")
    scraped_data = await web_scraper.scrape_website("https://example.com")
    print(f"✅ Scraped: {scraped_data.title}")
    
    # Example: AI analysis
    print("🤖 AI analysis...")
    ai_response = await ai_client.analyze_html(scraped_data.html_content[:1000], scraped_data.url)
    print(f"✅ AI analysis completed: {ai_response.tokens_used} tokens used")
    
    # Cleanup
    web_scraper.close()


def example_list_models():
    """Example: List available AI models"""
    print("\n🤖 Example: List Available Models")
    
    # Initialize orchestrator
    orchestrator = MainOrchestrator()
    
    # Get available models
    models = orchestrator.get_available_ai_models()
    
    if models:
        print("Available AI Models:")
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model}")
    else:
        print("No AI models found. Make sure your AI service is running.")


def example_validate_config():
    """Example: Validate configuration"""
    print("\n⚙️ Example: Validate Configuration")
    
    # Initialize orchestrator
    orchestrator = MainOrchestrator()
    
    # Validate config
    if orchestrator.validate_config():
        print("✅ Configuration is valid!")
    else:
        print("❌ Configuration validation failed!")


async def main():
    """Run all examples"""
    print("🎯 AI Test Automation Assistant - Examples")
    print("=" * 50)
    
    try:
        # Example 1: Quick test
        await example_quick_test()
        
        # Example 2: Individual components
        await example_individual_components()
        
        # Example 3: List models
        example_list_models()
        
        # Example 4: Validate config
        example_validate_config()
        
        # Example 5: Full automation (commented out as it takes longer)
        # await example_full_automation()
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("Make sure your AI service (like Ollama) is running and accessible.")


if __name__ == "__main__":
    asyncio.run(main()) 