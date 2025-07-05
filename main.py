#!/usr/bin/env python3
"""
AI Test Automation Assistant
Main entry point for the application
"""

import argparse
import asyncio
import sys
from pathlib import Path
from loguru import logger
import yaml
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.orchestrator.main_orchestrator import MainOrchestrator, ExecutionConfig


def setup_logging():
    """Setup logging configuration"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/automation.log",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )


def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🤖 AI Test Automation Assistant 🤖                    ║
    ║                                                              ║
    ║     Lokal AI ile Web Sitesi Otomatik Test Üretimi           ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="🤖 AI Test Automation Assistant",
        epilog="Örnek: python main.py --url https://example.com --ai-model llama3:latest"
    )
    
    # Main arguments
    parser.add_argument('--url', type=str, help='Test edilecek website URL\'si')
    parser.add_argument('--full-automation', type=str, help='Full automation workflow için URL')
    parser.add_argument('--ai-model', type=str, help='Kullanılacak AI model')
    parser.add_argument('--output-dir', type=str, default='reports', help='Çıktı dosyalarının kaydedileceği dizin')
    
    # Test options
    parser.add_argument('--headless', action='store_true', help='Headless modda çalıştır')
    parser.add_argument('--no-parallel', action='store_true', help='Paralel test çalıştırmayı devre dışı bırak')
    parser.add_argument('--no-reports', action='store_true', help='Rapor üretmeyi devre dışı bırak')
    parser.add_argument('--no-artifacts', action='store_true', help='Artifact üretmeyi devre dışı bırak')
    
    # Utility options
    parser.add_argument('--quick-test', action='store_true', help='Sadece hızlı test çalıştır')
    parser.add_argument('--list-models', action='store_true', help='Mevcut AI modellerini listele')
    parser.add_argument('--validate-config', action='store_true', help='Konfigürasyon dosyasını doğrula')
    parser.add_argument('--config', type=str, default='config/config.yaml', help='Konfigürasyon dosyası yolu')
    parser.add_argument('--verbose', action='store_true', help='Detaylı log çıktısı')
    
    return parser.parse_args()


def run_full_automation(args):
    """Run full automation workflow"""
    logger.info("Starting full automation workflow")
    
    # Initialize orchestrator
    orchestrator = MainOrchestrator(args.config)
    
    # Execute automation
    try:
        result = orchestrator.execute_full_automation(args.url)
        
        # Print results
        if result:
            logger.info("✅ Automation completed successfully!")
            print(f"\n🎉 Automation completed successfully!")
            print(f"📊 Check the reports directory for generated files")
        else:
            logger.error("❌ Automation failed!")
            print(f"\n💥 Automation failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error during automation: {e}")
        print(f"\n💥 Automation failed: {e}")
        sys.exit(1)


def run_quick_test(args):
    """Run quick test"""
    logger.info("Starting quick test")
    
    # Initialize orchestrator
    orchestrator = MainOrchestrator(args.config)
    
    # Run quick test
    try:
        result = orchestrator.quick_test(args.url, args.ai_model)
        
        # Print results
        if result:
            print(f"\n✅ Quick test completed for: {args.url}")
            print(f"🤖 AI model used: {args.ai_model}")
            print(f"📄 Analysis completed successfully")
        else:
            print("\n⚠️  Quick test completed with warnings")
            
    except Exception as e:
        logger.error(f"Error during quick test: {e}")
        print(f"\n💥 Quick test failed: {e}")
        sys.exit(1)


def list_models(args):
    """List available AI models"""
    logger.info("Listing available AI models")
    
    try:
        # Initialize orchestrator
        orchestrator = MainOrchestrator(args.config)
        
        # Get available models
        models = orchestrator.get_available_ai_models()
        
        if models:
            print("\n🤖 Available AI Models:")
            for i, model in enumerate(models, 1):
                print(f"  {i}. {model}")
        else:
            print("\n⚠️  No AI models found. Make sure your AI service is running.")
            
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        print(f"\n💥 Error listing models: {e}")
        sys.exit(1)


def validate_config(args):
    """Validate configuration"""
    logger.info("Validating configuration")
    
    try:
        # Initialize orchestrator
        orchestrator = MainOrchestrator(args.config)
        
        # Validate config
        if orchestrator.validate_config():
            print("\n✅ Configuration is valid!")
        else:
            print("\n❌ Configuration validation failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error validating config: {e}")
        print(f"\n💥 Error validating config: {e}")
        sys.exit(1)


def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import selenium
        import requests
        import bs4  # beautifulsoup4 imports as bs4
        import yaml
        import loguru
        print("✅ All dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False


def main():
    """Main function"""
    print_banner()
    
    # Setup logging
    setup_logging()
    
    # Parse arguments
    args = parse_arguments()
    
    # Set verbose logging
    if args.verbose:
        logger.remove()
        logger.add(sys.stdout, level="DEBUG")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Handle different commands
    try:
        if args.list_models:
            list_models(args)
        elif args.validate_config:
            validate_config(args)
        elif args.quick_test:
            if not args.url:
                logger.error("URL is required for quick test")
                print("❌ URL is required for quick test. Use --url parameter.")
                sys.exit(1)
            run_quick_test(args)
        elif args.full_automation:
            # Full automation with specific URL
            args.url = args.full_automation
            run_full_automation(args)
        else:
            # Full automation
            if not args.url:
                logger.error("URL is required for full automation")
                print("❌ URL is required. Use --url parameter.")
                sys.exit(1)
            run_full_automation(args)
            
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\n👋 Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Run main function
    main() 